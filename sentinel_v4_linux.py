#!/usr/bin/env python3
"""Linux-ready proximity monitor with optional mock data input.

Mock mode:
  python3 sentinel_v4_linux.py --mock-file fixtures/cell_scan_sample.json --max-iterations 3
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict

BAD_PCI = {"275", "434"}
BAD_TAC = "5135"
CRITICAL_RSSI_THRESHOLD = -46  # RSSI above this (less negative) is treated as extreme proximity


def parse_cell_snapshot(payload: Any) -> Dict[str, str]:
    """Parse cell data from dict/list payload into a normalized snapshot."""
    if isinstance(payload, list) and payload:
        payload = payload[0]

    if not isinstance(payload, dict):
        return {"pci": "0", "tac": "0", "rssi": "-120"}

    pci = str(payload.get("pci", "0"))
    tac = str(payload.get("tac", "0"))
    rssi = str(payload.get("rssi", "-120"))
    return {"pci": pci, "tac": tac, "rssi": rssi}


def load_mock_snapshot(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return parse_cell_snapshot(data)


def get_snapshot_from_command(command: str) -> Dict[str, str]:
    proc = subprocess.run(command, shell=True, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "cell data command failed")

    raw = proc.stdout.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("cell command output is not JSON") from exc

    return parse_cell_snapshot(data)


def should_alert(snapshot: Dict[str, str]) -> bool:
    return snapshot["pci"] in BAD_PCI and snapshot["tac"] == BAD_TAC


def append_log(snapshot: Dict[str, str], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat()
    with open(path, "a", encoding="utf-8") as f:
        f.write(
            f"{stamp} | TARGET_MATCH | PCI:{snapshot['pci']} | TAC:{snapshot['tac']} | RSSI:{snapshot['rssi']}\n"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Sentinel V4 Linux proximity monitor")
    parser.add_argument(
        "--data-command",
        default="",
        help="Shell command that outputs JSON with pci/tac/rssi (or list with first item)",
    )
    parser.add_argument("--mock-file", default="", help="JSON file with pci/tac/rssi sample")
    parser.add_argument("--interval", type=float, default=3.0, help="Polling interval seconds")
    parser.add_argument("--max-iterations", type=int, default=0, help="0 = run forever")
    parser.add_argument(
        "--log-file",
        default="follower_audit/blacklist_hits.log",
        help="Alert log path",
    )
    args = parser.parse_args()

    if not args.mock_file and not args.data_command:
        print(
            "Error: provide --mock-file for simulation or --data-command for real polling",
            file=sys.stderr,
        )
        return 2

    count = 0
    try:
        while True:
            count += 1
            if args.mock_file:
                snapshot = load_mock_snapshot(args.mock_file)
            else:
                snapshot = get_snapshot_from_command(args.data_command)

            if should_alert(snapshot):
                append_log(snapshot, args.log_file)
                print(
                    f"[ALERT] target match pci={snapshot['pci']} tac={snapshot['tac']} rssi={snapshot['rssi']}"
                )
                try:
                    if int(float(snapshot["rssi"])) > CRITICAL_RSSI_THRESHOLD:
                        print("[CRITICAL] extreme proximity")
                except ValueError:
                    pass
            else:
                print(
                    f"[OK] pci={snapshot['pci']} tac={snapshot['tac']} rssi={snapshot['rssi']}"
                )

            if args.max_iterations and count >= args.max_iterations:
                break
            time.sleep(max(args.interval, 0.1))
    except KeyboardInterrupt:
        print("\nStopping sentinel_v4_linux")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
