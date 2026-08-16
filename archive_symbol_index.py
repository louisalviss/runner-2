#!/usr/bin/env python3
"""Generic Binance Data Vision archive symbol indexer.

Lists USD-M Futures kline symbol directories from the public S3 archive.
No trading filters, thresholds, strategy rules, or private data are used.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET

import requests

S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
UA = "Mozilla/5.0 archive-symbol-index/1.0"


def list_common_prefixes(prefix: str) -> list[str]:
    session = requests.Session()
    marker = None
    out: list[str] = []
    while True:
        url = f"{S3}?delimiter=/&prefix={quote(prefix, safe='/')}"
        if marker:
            url += f"&marker={quote(marker, safe='/')}"
        r = session.get(url, headers={"User-Agent": UA}, timeout=45)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        prefixes = [x.text or "" for x in root.findall("s3:CommonPrefixes/s3:Prefix", ns)]
        out.extend(prefixes)
        trunc = (root.findtext("s3:IsTruncated", default="false", namespaces=ns) or "false").lower() == "true"
        if not trunc:
            break
        next_marker = root.findtext("s3:NextMarker", default="", namespaces=ns)
        if not next_marker:
            # With delimiter listings, fall back to the last common prefix.
            next_marker = prefixes[-1] if prefixes else ""
        if not next_marker or next_marker == marker:
            raise RuntimeError("S3 listing pagination stalled")
        marker = next_marker
    return sorted(set(out))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="archive_symbol_index.json")
    args = ap.parse_args()
    prefix = "data/futures/um/monthly/klines/"
    paths = list_common_prefixes(prefix)
    symbols = []
    for p in paths:
        tail = p[len(prefix):].strip("/") if p.startswith(prefix) else ""
        if tail:
            symbols.append(tail.upper())
    payload = {
        "schema_version": "1.0",
        "purpose": "generic Binance Data Vision USD-M Futures archive symbol index",
        "source": S3,
        "prefix": prefix,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol_count": len(symbols),
        "symbols": sorted(set(symbols)),
    }
    Path(args.out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"symbol_count": payload["symbol_count"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
