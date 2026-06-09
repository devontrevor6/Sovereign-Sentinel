import os, time, subprocess, json
USB_VAULT = "/storage/0EBD-624E/Android/data/com.termux/files/RECOVERY"
JERSEY = ['12:36:aa', '1e:9d:72', 'd4:b9:2f', '7a:7d:a1']
def execute_siphon():
    if not os.path.exists(USB_VAULT): os.makedirs(USB_VAULT, exist_ok=True)
    print("\033[91m[!] SOVEREIGN TAKEOVER ACTIVE | VAULT: {USB_VAULT}\033[0m")
    while True:
        raw_data = subprocess.check_output(['termux-wifi-scaninfo']).decode('utf-8')
        filename = f"{USB_VAULT}/slice_{int(time.time()*1000)}.json"
        with open(filename, "w") as f: f.write(raw_data)
        data = json.loads(raw_data)
        for n in data:
            if any(oui in n['bssid'] for oui in JERSEY):
                print(f"NODE {n['bssid']} | \033[41m[ SIPHONING ]\033[0m")
        time.sleep(0.005)
if __name__ == "__main__":
    execute_siphon()
