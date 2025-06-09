import time
import requests
import get_updates
import root_json
from log import log
from lobby import tot_lobby
from match import get_matched
from referral import process_membership_expiries
from datetime import datetime

BASE_URL = root_json.root_read("BASE_URL")
TimeOut = 10

# Track last membership check time
last_membership_check = datetime.now()
MEMBERSHIP_CHECK_INTERVAL = 3600  # Check every hour (3600 seconds)

def set_bot_commands():
    url = f"{BASE_URL}/setMyCommands"
    commands = [
        {"command": "start", "description": "To Start the bot"},
        {"command": "help", "description": "To Show help message"},
        {"command": "connect", "description": "To get paired with random user"},
        {"command": "refer", "description": "Get your referral link"},
        {"command": "stats", "description": "View your referral statistics"},
        {"command": "disconnect", "description": "To end the current chat"},
        {"command": "next", "description": "To skip and find a new partner"},
        {"command": "report", "description": "To report the current partner"},
        {"command": "settings", "description": "To manage your settings"},
        {"command": "issue", "description": "To Report a bug"}
    ]

    data = {"commands": commands}
    try:
        response = requests.post(url, json=data)
        log("Commands set: " + str(response.json()))
    except Exception as e:
        log(f"Error setting commands: {e}")

def check_membership_expiries():
    """Check and process VIP membership expiries"""
    global last_membership_check
    current_time = datetime.now()

    # Check if enough time has passed since last check
    time_diff = (current_time - last_membership_check).total_seconds()

    if time_diff >= MEMBERSHIP_CHECK_INTERVAL:
        try:
            expired_count = process_membership_expiries()
            log(f"Membership expiry check completed. Expired memberships: {expired_count}")
            last_membership_check = current_time
        except Exception as e:
            log(f"Error during membership expiry check: {e}")

if __name__ == "__main__":
    log("Bot started with referral system and VIP priority matching")

    # Set bot commands on startup
    set_bot_commands()

    while True:
        try:
            # Read and process messages
            get_updates.read_msg(TIMEOUT=TimeOut)

            # Check for matches if lobby has users
            if tot_lobby() > 1:
                get_matched()

            # Periodically check for membership expiries
            check_membership_expiries()

            time.sleep(1)

        except KeyboardInterrupt:
            log("Bot stopped by user")
            break
        except Exception as e:
            log(f"Main loop error: {e}")
            time.sleep(5)  # Wait before retrying
