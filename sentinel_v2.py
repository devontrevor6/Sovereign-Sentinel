import socket, time, os, random
LOG_PATH = "/data/data/com.termux/files/home/hidden_vault/Centipede_Final.log"
def start_harvest():
    print("\033[91m[!] INITIATING v2.0: HARVESTING DIRECT TO SD\033[0m")
    while True:
        try:
            time.sleep(0.00026)
            data_pulse = f"TS: {time.time()} | NODE: {random.randint(100,999)} | SIG: {os.urandom(4).hex()}\n"
            with open(LOG_PATH, "a") as f:
                f.write(data_pulse)
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            time.sleep(2)
            continue
if __name__ == "__main__":
    start_harvest()
