"""Scheduled market-data processing job."""
from __future__ import annotations
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo
import requests
VERSION = '1.1.1'
NY_TZ = ZoneInfo('America/New_York')
OUT = Path('output')
LIVE_PATH = OUT / 'crypto_watchlist_live.json'
FINAL_PATH = OUT / 'crypto_watchlist_latest.json'
CONFIG = {'quote_asset': 'USDT', 'contract_types': {'PERPETUAL', 'TRADIFI_PERPETUAL'}, 'volume_24h_min_usd': 100000000.0, 'avg_volume_10d_min_usd': 200000000.0, 'volatility_1w_min_pct': 6.0, 'adr14_min_pct': 5.0, 'min_active_universe': 600, 'kline_limit': 20, 'max_workers': 8, 'session_rollover_hour_utc': 23, 'market_data_bases': ['https://www.binance.com', 'https://fapi.binance.com', 'https://api.pipai.org']}
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json,text/plain,*/*'}

def request_json(session: requests.Session, url: str, *, params: dict[str, Any] | None=None, attempts: int=4, timeout: float=18.0) -> Any:
    last: Exception | None = None
    delays = (1.0, 2.5, 5.0)
    for attempt in range(attempts):
        try:
            r = session.get(url, params=params, headers=HEADERS, timeout=timeout)
            if r.status_code >= 400:
                raise RuntimeError(f'HTTP {r.status_code}')
            return r.json()
        except Exception as exc:
            last = RuntimeError(f'{url}: {type(exc).__name__}: {exc}')
            if attempt + 1 < attempts:
                time.sleep(delays[min(attempt, len(delays) - 1)])
    raise RuntimeError(str(last) if last else f'{url}: request failed')

def choose_market_base(session: requests.Session) -> tuple[str, dict[str, Any]]:
    for base in CONFIG['market_data_bases']:
        try:
            payload = request_json(session, f'{base}/fapi/v1/exchangeInfo')
            if not isinstance(payload, dict) or not isinstance(payload.get('symbols'), list):
                raise RuntimeError('unexpected exchangeInfo shape')
            return (base, payload)
        except Exception:
            continue
    raise RuntimeError('market-data source unavailable')

def avg_volume_usd_10d(klines: list[list[Any]]) -> float:
    if len(klines) < 10:
        raise ValueError('need >=10 daily bars')
    bars = klines[-10:]
    return sum((float(k[4]) * float(k[5]) for k in bars)) / 10.0

def volatility_1w_pct(klines: list[list[Any]]) -> float:
    if len(klines) < 7:
        raise ValueError('need >=7 daily bars')
    vals: list[float] = []
    for k in klines[-7:]:
        high, low = (float(k[2]), float(k[3]))
        if low == 0:
            raise ValueError('zero low')
        vals.append((high - low) / abs(low) * 100.0)
    return sum(vals) / len(vals)

def adr14_pct(klines: list[list[Any]]) -> float:
    if len(klines) < 14:
        raise ValueError('need >=14 daily bars')
    bars = klines[-14:]
    sma_high = sum((float(k[2]) for k in bars)) / 14.0
    sma_low = sum((float(k[3]) for k in bars)) / 14.0
    close = float(klines[-1][4])
    if close == 0:
        raise ValueError('zero close')
    return (sma_high - sma_low) / close * 100.0

def fetch_klines(base: str, symbol: str, limit: int) -> tuple[str, list[list[Any]]]:
    with requests.Session() as worker_session:
        data = request_json(worker_session, f'{base}/fapi/v1/klines', params={'symbol': symbol, 'interval': '1d', 'limit': limit})
    if not isinstance(data, list):
        raise RuntimeError('bad kline response')
    return (symbol, data)

def scan_once(now_utc: datetime) -> dict[str, Any]:
    session = requests.Session()
    base, exchange_info = choose_market_base(session)
    active: dict[str, dict[str, Any]] = {}
    for item in exchange_info.get('symbols', []):
        if not isinstance(item, dict):
            continue
        if item.get('status') != 'TRADING':
            continue
        if item.get('contractType') not in CONFIG['contract_types']:
            continue
        if item.get('quoteAsset') != CONFIG['quote_asset']:
            continue
        symbol = item.get('symbol')
        if symbol:
            active[str(symbol)] = item
    errors: list[str] = []
    if len(active) < CONFIG['min_active_universe']:
        errors.append('active universe below minimum')
    tickers = request_json(session, f'{base}/fapi/v1/ticker/24hr')
    if not isinstance(tickers, list):
        raise RuntimeError('ticker endpoint returned unexpected shape')
    ticker_map = {str(t.get('symbol')): t for t in tickers if isinstance(t, dict) and t.get('symbol') in active}
    gate24: list[tuple[str, dict[str, Any], float]] = []
    for symbol, meta in active.items():
        ticker = ticker_map.get(symbol)
        if not ticker:
            continue
        try:
            qv = float(ticker.get('quoteVolume'))
        except (TypeError, ValueError):
            continue
        if qv >= CONFIG['volume_24h_min_usd']:
            gate24.append((symbol, meta, qv))
    kline_data: dict[str, list[list[Any]]] = {}
    kline_errors: dict[str, str] = {}
    kline_skipped_404: dict[str, str] = {}
    kline_skipped_transient: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=CONFIG['max_workers']) as pool:
        futures = {pool.submit(fetch_klines, base, symbol, CONFIG['kline_limit']): symbol for symbol, _, _ in gate24}
        for fut in as_completed(futures):
            symbol = futures[fut]
            try:
                sym, data = fut.result()
                kline_data[sym] = data
            except Exception as exc:
                message = f'{type(exc).__name__}: {exc}'[:300]
                if 'HTTP 404' in message:
                    kline_skipped_404[symbol] = message
                else:
                    kline_errors[symbol] = message
    effective_kline_total = max(0, len(gate24) - len(kline_skipped_404))
    kline_fetch_coverage = len(kline_data) / effective_kline_total if effective_kline_total else 1.0
    if kline_errors and len(kline_data) >= 10 and (kline_fetch_coverage >= 0.9):
        kline_skipped_transient.update(kline_errors)
        kline_errors.clear()
    rows: list[dict[str, Any]] = []
    insufficient: list[str] = []
    for symbol, meta, qv in gate24:
        klines = kline_data.get(symbol)
        if not klines:
            continue
        if len(klines) < 14:
            insufficient.append(symbol)
            continue
        try:
            avg10 = avg_volume_usd_10d(klines)
            vol1w = volatility_1w_pct(klines)
            adr = adr14_pct(klines)
        except Exception as exc:
            kline_errors[symbol] = f'{type(exc).__name__}: {exc}'[:300]
            continue
        if not avg10 > CONFIG['avg_volume_10d_min_usd']:
            continue
        if not vol1w > CONFIG['volatility_1w_min_pct']:
            continue
        if not adr >= CONFIG['adr14_min_pct']:
            continue
        rows.append({'symbol': f'{symbol}.P', 'tradingview': f'BINANCE:{symbol}.P'})
    rows.sort(key=lambda r: r['symbol'])
    if insufficient:
        errors.append(f"insufficient history: {len(insufficient)} symbols; sample={','.join(sorted(insufficient)[:10])}")
    if kline_errors:
        sample = '; '.join((f'{symbol}={message}' for symbol, message in sorted(kline_errors.items())[:8]))
        errors.append(f'metric request failure: {len(kline_errors)}/{len(gate24)} symbols; sample={sample}')
    diagnostics = {'market_data_base': base, 'active_universe_count': len(active), 'ticker_count': len(ticker_map), 'gate24_count': len(gate24), 'kline_success_count': len(kline_data), 'kline_error_count': len(kline_errors), 'kline_error_sample': [{'symbol': symbol, 'error': message} for symbol, message in sorted(kline_errors.items())[:20]], 'kline_skipped_404_count': len(kline_skipped_404), 'kline_skipped_404_sample': [{'symbol': symbol, 'error': message} for symbol, message in sorted(kline_skipped_404.items())[:20]], 'kline_fetch_coverage': round(kline_fetch_coverage, 4), 'kline_skipped_transient_count': len(kline_skipped_transient), 'kline_skipped_transient_sample': [{'symbol': symbol, 'error': message} for symbol, message in sorted(kline_skipped_transient.items())[:20]], 'insufficient_history_count': len(insufficient), 'insufficient_history_sample': sorted(insufficient)[:20]}
    return {'schema_version': '1.0', 'runner_version': VERSION, 'status': 'COMPLETE' if not errors else 'PARTIAL', 'generated_at_utc': now_utc.astimezone(timezone.utc).isoformat(), 'final_count': len(rows), 'errors': errors, 'diagnostics': diagnostics, 'rows': rows}

def scan_resilient(now_utc: datetime) -> dict[str, Any]:
    result: dict[str, Any] | None = None
    attempt_log: list[dict[str, Any]] = []
    for attempt_no, delay in enumerate((0.0, 2.0, 5.0), start=1):
        if delay:
            time.sleep(delay)
        try:
            result = scan_once(now_utc)
        except Exception as exc:
            result = {'schema_version': '1.0', 'runner_version': VERSION, 'status': 'FAILED', 'generated_at_utc': now_utc.astimezone(timezone.utc).isoformat(), 'final_count': 0, 'errors': [f'{type(exc).__name__}: {exc}'], 'diagnostics': {}, 'rows': []}
        attempt_log.append({'attempt': attempt_no, 'status': result.get('status'), 'final_count': int(result.get('final_count', 0) or 0), 'errors': list(result.get('errors') or []), 'diagnostics': result.get('diagnostics') or {}})
        if result.get('status') == 'COMPLETE':
            break
    assert result is not None
    result['retry_attempts'] = len(attempt_log)
    result['attempt_log'] = attempt_log
    return result

def session_date_from_utc(generated_at_utc: str) -> str:
    dt = datetime.fromisoformat(generated_at_utc).astimezone(timezone.utc)
    day = dt.date()
    if dt.hour >= CONFIG['session_rollover_hour_utc']:
        day += timedelta(days=1)
    return day.isoformat()

def load_live() -> dict[str, Any] | None:
    if not LIVE_PATH.exists():
        return None
    try:
        return json.loads(LIVE_PATH.read_text(encoding='utf-8'))
    except Exception:
        return None

def empty_union(session_date: str) -> dict[str, Any]:
    return {'schema_version': '1.0', 'runner_version': VERSION, 'session_date': session_date, 'updated_at_utc': None, 'latest_mode': None, 'latest_scan_status': None, 'latest_successful_scan_at_utc': None, 'union_count': 0, 'active_count': 0, 'symbols': [], 'scan_history': [], 'latest_scan_errors': [], 'latest_scan_diagnostics': {}, 'latest_scan_retry_attempts': 0}

def normalize_existing(existing: dict[str, Any] | None) -> dict[str, Any] | None:
    if not existing:
        return None
    state = json.loads(json.dumps(existing))
    state.pop('membership_rule', None)
    if 'updated_at_vn' in state and 'updated_at_utc' not in state:
        state['updated_at_utc'] = datetime.fromisoformat(state.pop('updated_at_vn')).astimezone(timezone.utc).isoformat()
    if 'latest_successful_scan_at_vn' in state and 'latest_successful_scan_at_utc' not in state:
        raw = state.pop('latest_successful_scan_at_vn')
        state['latest_successful_scan_at_utc'] = datetime.fromisoformat(raw).astimezone(timezone.utc).isoformat() if raw else None
    clean_rows = []
    for src in state.get('symbols', []):
        if not isinstance(src, dict) or not src.get('symbol'):
            continue
        row = {'symbol': src['symbol'], 'tradingview': src.get('tradingview') or f"BINANCE:{src['symbol']}", 'scan_count': int(src.get('scan_count', 0)), 'active_now': bool(src.get('active_now'))}
        for old, new in (('first_qualified_at_vn', 'first_qualified_at_utc'), ('last_qualified_at_vn', 'last_qualified_at_utc')):
            raw = src.get(new) or src.get(old)
            if raw:
                row[new] = datetime.fromisoformat(raw).astimezone(timezone.utc).isoformat()
        clean_rows.append(row)
    state['symbols'] = sorted(clean_rows, key=lambda x: x['symbol'])
    history = []
    for item in state.get('scan_history', []):
        if not isinstance(item, dict):
            continue
        raw = item.get('generated_at_utc') or item.get('generated_at_vn')
        history.append({'mode': item.get('mode'), 'generated_at_utc': datetime.fromisoformat(raw).astimezone(timezone.utc).isoformat() if raw else None, 'status': item.get('status'), 'qualified_count': int(item.get('qualified_count', 0) or 0), 'retry_attempts': int(item.get('retry_attempts', 0) or 0), 'errors': list(item.get('errors') or [])})
    state['scan_history'] = history[-32:]
    state['runner_version'] = VERSION
    return state

def merge_union(existing: dict[str, Any] | None, scan: dict[str, Any], mode: str) -> dict[str, Any]:
    session_date = session_date_from_utc(scan['generated_at_utc'])
    existing = normalize_existing(existing)
    if not existing or existing.get('session_date') != session_date:
        state = empty_union(session_date)
    else:
        state = existing
    state['runner_version'] = VERSION
    state['updated_at_utc'] = scan['generated_at_utc']
    state['latest_mode'] = mode
    state['latest_scan_status'] = scan.get('status')
    state['latest_scan_errors'] = list(scan.get('errors') or [])
    state['latest_scan_diagnostics'] = scan.get('diagnostics') or {}
    state['latest_scan_retry_attempts'] = int(scan.get('retry_attempts', 0) or 0)
    state['scan_history'].append({'mode': mode, 'generated_at_utc': scan['generated_at_utc'], 'status': scan.get('status'), 'qualified_count': int(scan.get('final_count', 0) or 0), 'retry_attempts': int(scan.get('retry_attempts', 0) or 0), 'errors': list(scan.get('errors') or [])})
    state['scan_history'] = state['scan_history'][-32:]
    if scan.get('status') != 'COMPLETE':
        return state
    current = {str(row['symbol']): row for row in state.get('symbols', []) if isinstance(row, dict) and row.get('symbol')}
    for row in current.values():
        row['active_now'] = False
    for src in scan.get('rows', []):
        symbol = str(src['symbol'])
        row = current.get(symbol)
        if row is None:
            row = {'symbol': symbol, 'tradingview': src.get('tradingview') or f'BINANCE:{symbol}', 'first_qualified_at_utc': scan['generated_at_utc'], 'last_qualified_at_utc': scan['generated_at_utc'], 'scan_count': 1, 'active_now': True}
            current[symbol] = row
        else:
            row['last_qualified_at_utc'] = scan['generated_at_utc']
            row['scan_count'] = int(row.get('scan_count', 0)) + 1
            row['active_now'] = True
    state['symbols'] = sorted(current.values(), key=lambda x: x['symbol'])
    state['union_count'] = len(state['symbols'])
    state['active_count'] = sum((1 for x in state['symbols'] if x.get('active_now')))
    state['latest_successful_scan_at_utc'] = scan['generated_at_utc']
    return state

def write_outputs(union: dict[str, Any], mode: str, status: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    LIVE_PATH.write_text(json.dumps(union, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if mode == 'preclose' and status == 'COMPLETE':
        final = json.loads(json.dumps(union))
        final['finalized'] = True
        final['finalized_by_mode'] = 'preclose'
        FINAL_PATH.write_text(json.dumps(final, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def minute_of_day(dt: datetime) -> int:
    return dt.hour * 60 + dt.minute

def resolve_auto_mode(now_utc: datetime) -> str | None:
    utc = now_utc.astimezone(timezone.utc)
    um = minute_of_day(utc)
    if 8 * 60 + 25 <= um <= 9 * 60:
        return 'crypto-refresh'
    ny = now_utc.astimezone(NY_TZ)
    nm = minute_of_day(ny)
    if ny.weekday() >= 5:
        return None
    if 9 * 60 + 55 <= nm <= 10 * 60 + 30:
        return 'main'
    if 12 * 60 + 40 <= nm <= 13 * 60 + 15:
        return 'final'
    if 15 * 60 + 40 <= nm <= 16 * 60 + 15:
        return 'preclose'
    return None

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['auto', 'manual', 'crypto-refresh', 'main', 'final', 'preclose'], default='auto')
    args = parser.parse_args()
    now_utc = datetime.now(timezone.utc)
    mode = resolve_auto_mode(now_utc) if args.mode == 'auto' else args.mode
    if mode is None:
        print('no-op')
        return 0
    scan = scan_resilient(now_utc)
    union = merge_union(load_live(), scan, mode)
    write_outputs(union, mode, str(scan.get('status')))
    print(json.dumps({'mode': mode, 'status': scan.get('status'), 'current_count': scan.get('final_count'), 'session_date': union.get('session_date'), 'union_count': union.get('union_count'), 'active_count': union.get('active_count'), 'retry_attempts': scan.get('retry_attempts'), 'errors': scan.get('errors'), 'diagnostics': scan.get('diagnostics')}, ensure_ascii=False, indent=2))
    return 0 if scan.get('status') == 'COMPLETE' else 2
if __name__ == '__main__':
    raise SystemExit(main())
