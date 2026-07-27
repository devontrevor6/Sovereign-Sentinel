# Sovereign-Sentinel

Security suite for network auditing and monitoring.

## What was added

This repo now includes Linux-ready scripts and hardware-free simulation paths:

- `blackbird_linux.py`
  - Wi-Fi monitor that scans APs, matches target BSSID prefixes, and logs detections.
  - Supports real interface mode (`iw`) and mock file mode.
- `sentinel_v4_linux.py`
  - Proximity monitor that checks `pci/tac/rssi` snapshots and logs target matches.
  - Supports real command mode and mock JSON mode.
- `fixtures/*`
  - Sample scan data for repeatable local tests.
- `tests/*`
  - Unit tests for parsing and detection logic.

## Quick start (mock/simulated)

Run from the repository root directory.

### 1) Run tests

```bash
python3 -m unittest discover -s tests -v
```

### 2) Run Blackbird monitor with mock scan data

```bash
python3 blackbird_linux.py \
  --mock-file fixtures/wifi_scan_iw_sample.txt \
  --max-iterations 1
```

### 3) Run Sentinel v4 monitor with mock cell data

```bash
python3 sentinel_v4_linux.py \
  --mock-file fixtures/cell_scan_sample.json \
  --max-iterations 1
```

Both commands should emit `[ALERT]` with the included sample fixtures.

## Real Linux usage (Kali/Ubuntu/Debian)

### Requirements

- Linux system with wireless tooling (`iw`) installed.
- Root privileges are typically required for active Wi-Fi scanning.
- A command or integration that outputs JSON `pci/tac/rssi` for cell monitoring if using `sentinel_v4_linux.py` in real mode.

### Blackbird real mode

```bash
sudo python3 blackbird_linux.py --interface wlan1
```

Optional custom targets:

```bash
sudo python3 blackbird_linux.py \
  --interface wlan1 \
  --target-prefix d4:b9:2f \
  --target-prefix 1e:9d:72
```

### Sentinel v4 real mode

Pass a command that emits JSON with keys `pci`, `tac`, `rssi` (or a list with first object containing those keys):

```bash
python3 sentinel_v4_linux.py \
  --data-command 'echo "[{"pci":275,"tac":5135,"rssi":-43}]"'
```

## Evidence and logs

- Blackbird detections: `follower_audit/blackbird_hits.log`
- Sentinel v4 detections: `follower_audit/blacklist_hits.log`

Use these logs for README evidence sections: timestamped detections, hit counts, and observed signal values.

## Known constraints

- GitHub Codespaces cannot access local USB Wi-Fi adapters.
- Monitor mode/injection requires a local Linux host with hardware access.
- Cell tower APIs are platform-dependent; `sentinel_v4_linux.py` expects normalized JSON input in real mode.
