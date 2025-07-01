import time
import requests
import get_updates
import root_json
from log import log
from lobby import tot_lobby
from match import get_matched
from referral import process_membership_expiries
from datetime import datetime
import os
import re
from send_updates import send_message

BASE_URL = root_json.root_read("BASE_URL")
TimeOut = 10

# Track last membership check time
last_membership_check = datetime.now()
last_reminder_sent = datetime.now()
MEMBERSHIP_CHECK_INTERVAL = 3600  # Check every hour (3600 seconds)
REMINDER_INTERVAL = 86400  # Check every day


def send_reminder():
    results = []
    for filename in os.listdir('.'):
        if filename.startswith('temp_context') and filename.endswith('.txt'):
            with open(filename, 'r') as file:
                content = file.read()
                # Extract chat_id as a string
                chat_id_match = re.search(r'"chat_id":\s*"([^"]+)"', content)
                chat_id = chat_id_match.group(1) if chat_id_match else None
                # Extract first_name and last_name
                first_name_match = re.search(r'"first_name":\s*"([^"]*)"', content)
                last_name_match = re.search(r'"last_name":\s*"([^"]*)"', content)
                first_name = first_name_match.group(1) if first_name_match else ''
                last_name = last_name_match.group(1) if last_name_match else ''
                name = (first_name + ' ' + last_name).strip()
                if chat_id and name:
                    send_message(chat_id=chat_id, text=f"Hey {name} , We were just started to enjoy having you but "
                                                       f"you have left us in middle\nPlease come back\nClick /start "
                                                       f"to complete your registration")
                    results.append({'filename': filename, 'chat_id': chat_id, 'name': name})
                else:
                    send_message(chat_id=chat_id,
                                 text="Hi click /start to complete your registration")
                    results.append({'filename': filename, 'chat_id': chat_id})
    return results


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
    except Exception as er:
        log(f"Error setting commands: {er}")


def check_interval_updates():
    """Check and process VIP membership expires"""
    global last_membership_check
    global last_reminder_sent
    current_time = datetime.now()

    # Check if enough time has passed since last check
    time_diff_member = (current_time - last_membership_check).total_seconds()
    time_diff_reminder = (current_time - last_reminder_sent).total_seconds()

    if time_diff_member >= MEMBERSHIP_CHECK_INTERVAL:
        try:
            expired_count = process_membership_expiries()
            log(f"Membership expiry check completed. Expired memberships: {expired_count}")
            last_membership_check = current_time
        except Exception as err:
            log(f"Error during membership expiry check: {err}")

    if time_diff_reminder >= REMINDER_INTERVAL:
        try:
            log(f"Sent reminder to {send_reminder()}")
            last_reminder_sent = current_time
        except Exception as err:
            log(f"Error during sending reminder: {err}")


if __name__ == "__main__":
    log("Bot started")

    # Set bot commands on startup
    set_bot_commands()
    log(f"Sent reminder to {send_reminder()}")

    while True:
        try:
            # Read and process messages
            get_updates.read_msg(TIMEOUT=TimeOut)

            # Check for matches if lobby has users
            if tot_lobby() > 1:
                get_matched()

            # Periodically check for membership expires
            check_interval_updates()

            time.sleep(1)

        except KeyboardInterrupt:
            log("Bot stopped by user")
            break
        except Exception as e:
            log(f"Main loop error: {e}")
            time.sleep(5)  # Wait before retrying
