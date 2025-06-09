import os
from datetime import datetime


def log(text):
    """Log messages with timestamp"""
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    today = now.strftime("%Y-%m-%d")

    # Ensure logs directory exists
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Path to today's log file
    log_file = os.path.join("logs", f"log_{today}.txt")

    # Append log message to today's file
    try:
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(f"\n{formatted_time}: {text}")

        # Also print to console for immediate feedback
        print(f"{formatted_time}: {text}")

    except Exception as e:
        print(f"Error writing to log file: {e}")
        print(f"{formatted_time}: {text}")  # At least print to console


def log_error(error, context=""):
    """Log errors with additional context"""
    error_msg = f"ERROR - {context}: {str(error)}" if context else f"ERROR: {str(error)}"
    log(error_msg)


def log_user_action(chat_id, action, details=""):
    """Log user actions"""
    action_msg = f"USER {chat_id} - {action}"
    if details:
        action_msg += f" - {details}"
    log(action_msg)


def log_match_activity(user1_id, user2_id, action):
    """Log matching activities"""
    match_msg = f"MATCH - {action}: {user1_id} <-> {user2_id}"
    log(match_msg)


def log_system(message):
    """Log system messages"""
    log(f"SYSTEM: {message}")


def get_log_stats():
    """Get log file statistics"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join("logs", f"log_{today}.txt")

        if os.path.exists(log_file):
            with open(log_file, "r", encoding='utf-8') as f:
                lines = f.readlines()

            return {
                "total_lines": len(lines),
                "file_size": os.path.getsize(log_file),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(log_file)).strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            return {
                "total_lines": 0,
                "file_size": 0,
                "last_modified": "Never"
            }
    except Exception as e:
        log_error(e, "getting log stats")
        return {
            "total_lines": 0,
            "file_size": 0,
            "last_modified": "Error"
        }