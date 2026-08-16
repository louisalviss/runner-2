#!/usr/bin/env python3
"""Generic Binance USD-M historical candle exporter.

This utility intentionally contains no trading-system filters, thresholds, entry
logic, portfolio rules, or symbol-selection logic. It only downloads requested
historical OHLCV and writes neutral JSONL/manifest outputs.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

BASES = ("https://fapi.binance.com", "https://api.pipai.org")
UA = "Mozilla/5.0 market-data-worker/1.0"


def request_json(session: requests.Session, url: str, *, params: dict[str, Any] | None = None, attempts: int = 5):
    last = None
    for i in range(attempts):
        try:
            r = session.get(url, params=params, headers={"User-Agent": UA}, timeout=30)
            if r.status_code in (418, 429, 500, 502, 503, 504):
                raise RuntimeError(f"HTTP {r.status_code}")
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last = exc
            if i + 1 < attempts:
                time.sleep(min(8, 1.5 * (2**i)))
    raise RuntimeError(f"GET failed {url}: {last}")


def choose_base(session: requests.Session) -> tuple[str, dict[str, Any]]:
    errors = []
    for base in BASES:
        try:
            payload = request_json(session, f"{base}/fapi/v1/exchangeInfo", attempts=2)
            if isinstance(payload, dict) and isinstance(payload.get("symbols"), list):
                return base, payload
            raise RuntimeError("unexpected exchangeInfo payload")
        except Exception as exc:
            errors.append(f"{base}: {exc}")
    raise RuntimeError("no usable Binance-compatible endpoint: " + " | ".join(errors))


def parse_utc(value: str) -> datetime:
    x = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if x.tzinfo is None:
        x = x.replace(tzinfo=timezone.utc)
    return x.astimezone(timezone.utc)


def fetch_klines(session: requests.Session, base: str, symbol: str, interval: str, start_ms: int, end_ms: int):
    step_ms = {"1m": 60_000, "3m": 180_000, "5m": 300_000, "15m": 900_000, "1h": 3_600_000, "1d": 86_400_000}[interval]
    cursor = start_ms
    rows = []
    while cursor < end_ms:
        payload = request_json(
            session,
            f"{base}/fapi/v1/klines",
            params={"symbol": symbol, "interval": interval, "startTime": cursor, "endTime": end_ms - 1, "limit": 1500},
        )
        if not isinstance(payload, list):
            raise RuntimeError(f"bad kline payload for {symbol}")
        if not payload:
            break
        rows.extend(payload)
        nxt = int(payload[-1][0]) + step_ms
        if nxt <= cursor:
            raise RuntimeError(f"cursor stalled for {symbol}")
        cursor = nxt
        if len(payload) < 1500:
            break
        time.sleep(0.08)
    dedup = {int(r[0]): r for r in rows}
    return [dedup[k] for k in sorted(dedup)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--out", default="market_data_output")
    args = ap.parse_args()

    req = json.loads(Path(args.request).read_text(encoding="utf-8"))
    symbols = sorted({str(s).upper() for s in req["symbols"]})
    interval = str(req.get("interval", "15m"))
    if interval not in {"1m", "3m", "5m", "15m", "1h", "1d"}:
        raise SystemExit("unsupported interval")
    start = parse_utc(req["start_utc"])
    end = parse_utc(req["end_utc"])
    if start >= end:
        raise SystemExit("start must be before end")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    base, exchange_info = choose_base(session)
    known = {str(x.get("symbol")): x for x in exchange_info.get("symbols", []) if isinstance(x, dict) and x.get("symbol")}

    manifest = {
        "schema_version": "1.0",
        "purpose": "generic historical OHLCV export",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": base,
        "interval": interval,
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        "requested_symbols": symbols,
        "results": [],
    }
    failures = 0
    for idx, symbol in enumerate(symbols, 1):
        try:
            rows = fetch_klines(session, base, symbol, interval, int(start.timestamp() * 1000), int(end.timestamp() * 1000))
            path = out / f"{symbol}_{interval}.jsonl"
            with path.open("w", encoding="utf-8") as fh:
                for r in rows:
                    fh.write(json.dumps(r, separators=(",", ":")) + "\n")
            meta = known.get(symbol, {})
            manifest["results"].append({
                "symbol": symbol,
                "rows": len(rows),
                "status": "OK" if rows else "EMPTY",
                "contract_type_current": meta.get("contractType"),
                "onboard_date_current": meta.get("onboardDate"),
                "file": path.name,
            })
            print(f"[{idx}/{len(symbols)}] {symbol}: {len(rows)} rows")
        except Exception as exc:
            failures += 1
            manifest["results"].append({"symbol": symbol, "rows": 0, "status": "ERROR", "error": str(exc)})
            print(f"[{idx}/{len(symbols)}] {symbol}: ERROR {exc}")

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
