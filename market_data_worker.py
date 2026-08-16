#!/usr/bin/env python3
"""Generic Binance USD-M historical candle exporter.

This public worker contains no trading-system filters, thresholds, entry rules,
or portfolio logic. It only downloads requested raw USD-M futures klines from
Binance's public data archive and writes neutral JSONL files.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

BASE = "https://data.binance.vision/data/futures/um"
UA = "Mozilla/5.0 market-data-worker/1.2"


def parse_utc(value: str) -> datetime:
    x = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if x.tzinfo is None:
        x = x.replace(tzinfo=timezone.utc)
    return x.astimezone(timezone.utc)


def get_zip(session: requests.Session, url: str) -> bytes | None:
    r = session.get(url, headers={"User-Agent": UA}, timeout=45)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.content


def parse_zip(raw: bytes) -> list[list[str]]:
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = [n for n in zf.namelist() if not n.endswith("/")]
        if not names:
            return []
        text = zf.read(names[0]).decode("utf-8-sig")
    out: list[list[str]] = []
    for row in csv.reader(io.StringIO(text)):
        if not row:
            continue
        try:
            int(float(row[0]))
        except Exception:
            continue
        out.append(row)
    return out


def month_iter(start: date, end_exclusive: date):
    y, m = start.year, start.month
    while date(y, m, 1) < end_exclusive:
        yield y, m
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1


def next_month(y: int, m: int) -> date:
    return date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)


def fetch_symbol(session: requests.Session, symbol: str, interval: str, start: datetime, end: datetime):
    rows: list[list[str]] = []
    source_files: list[str] = []
    start_d, end_d = start.date(), end.date()
    for y, m in month_iter(date(start_d.year, start_d.month, 1), end_d + timedelta(days=1)):
        month_start = date(y, m, 1)
        month_end = next_month(y, m)
        overlap_start = max(start_d, month_start)
        overlap_end = min(end_d + timedelta(days=1), month_end)
        if overlap_start >= overlap_end:
            continue

        # A month is complete relative to requested end => prefer one monthly ZIP.
        if month_end <= end_d:
            name = f"{symbol}-{interval}-{y:04d}-{m:02d}.zip"
            url = f"{BASE}/monthly/klines/{symbol}/{interval}/{name}"
            raw = get_zip(session, url)
            if raw is not None:
                rows.extend(parse_zip(raw))
                source_files.append(url)
            continue

        # Partial final month: daily archives are published the following day.
        d = overlap_start
        while d < overlap_end:
            # end is exclusive; do not request the still-open UTC day.
            day_start = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
            if day_start >= end:
                break
            name = f"{symbol}-{interval}-{d.isoformat()}.zip"
            url = f"{BASE}/daily/klines/{symbol}/{interval}/{name}"
            raw = get_zip(session, url)
            if raw is not None:
                rows.extend(parse_zip(raw))
                source_files.append(url)
            d += timedelta(days=1)

    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    dedup: dict[int, list[str]] = {}
    for row in rows:
        t = int(float(row[0]))
        # Futures archives are millisecond timestamps; normalize defensively.
        if t > 10**15:
            t //= 1000
            row = [str(t), *row[1:]]
        if start_ms <= t < end_ms:
            dedup[t] = row
    return [dedup[k] for k in sorted(dedup)], source_files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--out", default="market_data_output")
    args = ap.parse_args()

    req = json.loads(Path(args.request).read_text(encoding="utf-8"))
    symbols = sorted({str(s).upper() for s in req.get("symbols", [])})
    interval = str(req.get("interval", "15m"))
    start = parse_utc(req["start_utc"])
    end = parse_utc(req["end_utc"])
    if not symbols or start >= end:
        raise SystemExit("invalid request")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    manifest = {
        "schema_version": "1.2",
        "purpose": "generic historical OHLCV export",
        "source": "Binance Public Data / USD-M Futures klines",
        "base": BASE,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "interval": interval,
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        "symbols": symbols,
        "results": [],
    }

    failures = 0
    for i, symbol in enumerate(symbols, 1):
        try:
            rows, source_files = fetch_symbol(session, symbol, interval, start, end)
            path = out / f"{symbol}_{interval}.jsonl"
            with path.open("w", encoding="utf-8") as fh:
                for row in rows:
                    fh.write(json.dumps(row, separators=(",", ":")) + "\n")
            manifest["results"].append({
                "symbol": symbol,
                "rows": len(rows),
                "status": "OK" if rows else "EMPTY",
                "file": path.name,
                "source_file_count": len(source_files),
            })
            print(f"[{i}/{len(symbols)}] {symbol}: {len(rows)} rows from {len(source_files)} files")
        except Exception as exc:
            failures += 1
            manifest["results"].append({"symbol": symbol, "rows": 0, "status": "ERROR", "error": str(exc)})
            print(f"[{i}/{len(symbols)}] {symbol}: ERROR {exc}")

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
