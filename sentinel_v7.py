import os
from datetime import datetime
def reset_dms():
    checkin_path = os.path.expanduser("~/Sentinel_Project/.last_checkin")
    with open(checkin_path, "w") as f:
        f.write(datetime.now().isoformat())
    return "SWITCH RESET: 7 DAYS REMAINING"
if __name__ == "__main__":
    print("Sentinel v7: Sandbox escape monitoring enabled.")
