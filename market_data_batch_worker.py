#!/usr/bin/env python3
"""Generic concurrent Binance USD-M archive exporter.

This public worker only lists/fetches raw market data. It contains no trading
filters, thresholds, strategy rules, scoring, or portfolio logic.
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests

from market_data_worker import fetch_symbol, parse_utc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols-index", required=True)
    ap.add_argument("--suffix", default="USDT")
    ap.add_argument("--interval", default="1d")
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out", default="market_data_batch_output")
    ap.add_argument("--workers", type=int, default=24)
    args = ap.parse_args()

    idx = json.loads(Path(args.symbols_index).read_text(encoding="utf-8"))
    suffix = str(args.suffix).upper()
    symbols = sorted({str(s).upper() for s in idx.get("symbols", []) if str(s).upper().endswith(suffix)})
    start, end = parse_utc(args.start), parse_utc(args.end)
    if not symbols or start >= end:
        raise SystemExit("invalid symbol index or date range")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "1.0",
        "purpose": "generic concurrent historical OHLCV export",
        "source": "Binance Public Data / USD-M Futures klines",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "interval": args.interval,
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        "suffix": suffix,
        "symbol_count": len(symbols),
        "results": [],
    }

    def one(symbol: str):
        session = requests.Session()
        rows, source_files = fetch_symbol(session, symbol, args.interval, start, end)
        path = out / f"{symbol}_{args.interval}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, separators=(",", ":")) + "\n")
        return {
            "symbol": symbol,
            "rows": len(rows),
            "status": "OK" if rows else "EMPTY",
            "file": path.name,
            "source_file_count": len(source_files),
        }

    failures = 0
    done = 0
    results = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futs = {pool.submit(one, s): s for s in symbols}
        for fut in as_completed(futs):
            s = futs[fut]
            done += 1
            try:
                r = fut.result()
            except Exception as exc:
                failures += 1
                r = {"symbol": s, "rows": 0, "status": "ERROR", "error": str(exc)}
            results[s] = r
            print(f"[{done}/{len(symbols)}] {s}: {r.get('rows', 0)} rows {r['status']}", flush=True)

    manifest["results"] = [results[s] for s in symbols]
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
