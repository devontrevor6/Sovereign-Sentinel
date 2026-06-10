import time, os, subprocess, sys, select

# --- SYSTEM CONFIG ---
INTERVAL = 0.16
HEARTBEAT_FILE = "guardian_v2.sh"
FEATURES = {
    "1": {"name": "SILENT-SENTRY", "script": "guardian_v2.sh", "active": False},
    "2": {"name": "MAC-RECON", "script": "mac_recon.sh", "active": False},
    "3": {"name": "BT-SNIFFER", "script": "bt_sniffer.sh", "active": False},
}
history = []

def sync_core():
    check = subprocess.run(["pgrep", "-f", HEARTBEAT_FILE], capture_output=True)
    is_active = check.returncode == 0
    history.append(1 if is_active else 0)
    if len(history) > 20: history.pop(0)
    return is_active, (sum(history) / len(history)) * 100

def draw_hud(active, stability):
    os.system('clear')
    print(f"\033[1;34m ARCHITECT COMMAND CENTER v4.5 \033[0m")
    print("="*50)
    for k, v in FEATURES.items():
        state = "\033[1;32m[ON]\033[0m" if v["active"] else "\033[1;31m[OFF]\033[0m"
        print(f" ({k}) > {v['name']:<15} {state}")
    print("="*50)
    bar_len = 20
    filled = int(stability / 100 * bar_len)
    bar = "█" * filled + "-" * (bar_len - filled)
    color = "\033[92m" if stability > 70 else "\033[93m" if stability > 30 else "\033[91m"
    status = "SECURE" if active else "VULNERABLE"
    print(f"CORE STABILITY: {color}[{bar}] {stability:.1f}% \033[0m")
    print(f"SYSTEM STATUS: {status} | PULSE: {INTERVAL}s")
    print("="*50)
    print("COMMAND (1-3 or Q to Exit) > ", end="", flush=True)

try:
    while True:
        is_active, stability = sync_core()
        draw_hud(is_active, stability)
        r, _, _ = select.select([sys.stdin], [], [], INTERVAL)
        if r:
            cmd = sys.stdin.readline().strip().upper()
            if cmd == 'Q': break
            if cmd in FEATURES:
                f = FEATURES[cmd]
                f["active"] = not f["active"]
                if f["active"]:
                    subprocess.Popen(["bash", f["script"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.run(["pkill", "-f", f["script"]])
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
print("\n\033[1;33m ARCHITECT SYSTEM DISCONNECTED \033[0m")
