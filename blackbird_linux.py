#!/usr/bin/env python3
"""Linux-ready Wi-Fi monitor with optional mock data input.

Real mode:
  sudo python3 blackbird_linux.py --interface wlan1
Mock mode:
  python3 blackbird_linux.py --mock-file fixtures/wifi_scan_iw_sample.txt --max-iterations 1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List

DEFAULT_PREFIXES = ["12:36:aa", "1e:9d:72", "d4:b9:2f", "7a:7d:a1"]


@dataclass
class AccessPoint:
    bssid: str
    signal_dbm: float | None = None
    ssid: str = ""


def parse_iw_scan_output(text: str) -> List[AccessPoint]:
    aps: list[AccessPoint] = []
    current: AccessPoint | None = None

    bss_re = re.compile(r"^BSS\s+([0-9a-fA-F:]{17})\b")
    signal_re = re.compile(r"signal:\s*(-?\d+(?:\.\d+)?)\s*dBm")

    for line in text.splitlines():
        stripped = line.strip()
        bss_match = bss_re.match(stripped)
        if bss_match:
            if current:
                aps.append(current)
            current = AccessPoint(bssid=bss_match.group(1).lower())
            continue

        if not current:
            continue

        signal_match = signal_re.search(stripped)
        if signal_match:
            current.signal_dbm = float(signal_match.group(1))
            continue

        if stripped.startswith("SSID:"):
            current.ssid = stripped.split("SSID:", 1)[1].strip()

    if current:
        aps.append(current)

    return aps


def load_mock_aps(mock_file: str) -> List[AccessPoint]:
    with open(mock_file, "r", encoding="utf-8") as f:
        raw = f.read()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return parse_iw_scan_output(raw)

    aps: list[AccessPoint] = []
    if isinstance(parsed, list):
        for item in parsed:
            if not isinstance(item, dict):
                continue
            bssid = str(item.get("bssid", "")).lower()
            if not re.fullmatch(r"[0-9a-f]{2}(?::[0-9a-f]{2}){5}", bssid):
                continue
            signal = item.get("signal_dbm")
            try:
                signal_dbm = float(signal) if signal is not None else None
            except (TypeError, ValueError):
                signal_dbm = None
            ssid = str(item.get("ssid", ""))
            aps.append(AccessPoint(bssid=bssid, signal_dbm=signal_dbm, ssid=ssid))
    return aps


def scan_with_iw(interface: str) -> List[AccessPoint]:
    cmd = ["iw", "dev", interface, "scan"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "iw scan failed")
    return parse_iw_scan_output(proc.stdout)


def detect_targets(aps: Iterable[AccessPoint], prefixes: Iterable[str]) -> List[AccessPoint]:
    normalized = [p.lower() for p in prefixes]
    hits: list[AccessPoint] = []
    for ap in aps:
        if any(ap.bssid.startswith(prefix) for prefix in normalized):
            hits.append(ap)
    return hits


def log_hits_and_get_path(hits: List[AccessPoint], output_dir: str) -> str | None:
    if not hits:
        return None

    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, "blackbird_hits.log")
    with open(log_path, "a", encoding="utf-8") as f:
        for ap in hits:
            stamp = datetime.now(timezone.utc).isoformat()
            f.write(
                f"{stamp} | bssid={ap.bssid} | signal_dbm={ap.signal_dbm} | ssid={ap.ssid}\n"
            )
    return log_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Blackbird Linux Wi-Fi monitor")
    parser.add_argument("--interface", default="wlan1", help="Wireless interface name")
    parser.add_argument("--interval", type=float, default=2.0, help="Scan interval (seconds)")
    parser.add_argument("--max-iterations", type=int, default=0, help="0 = run forever")
    parser.add_argument("--output-dir", default="follower_audit", help="Output log directory")
    parser.add_argument(
        "--target-prefix",
        action="append",
        dest="target_prefixes",
        default=None,
        help="Target BSSID prefix (repeatable)",
    )
    parser.add_argument(
        "--mock-file",
        default="",
        help="Read scan data from file (JSON list or raw iw output) instead of hardware",
    )
    args = parser.parse_args()

    prefixes = args.target_prefixes or DEFAULT_PREFIXES
    iteration = 0

    try:
        while True:
            iteration += 1
            if args.mock_file:
                aps = load_mock_aps(args.mock_file)
            else:
                aps = scan_with_iw(args.interface)

            hits = detect_targets(aps, prefixes)
            if hits:
                log_path = log_hits_and_get_path(hits, args.output_dir)
                print(f"[ALERT] {len(hits)} target network(s) detected. Logged to {log_path}")
            else:
                print(f"[OK] scanned {len(aps)} networks; no targets detected")

            if args.max_iterations and iteration >= args.max_iterations:
                break
            time.sleep(max(args.interval, 0.1))
    except KeyboardInterrupt:
        print("\nStopping blackbird monitor")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
