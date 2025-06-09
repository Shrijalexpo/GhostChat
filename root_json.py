import json
import os
from datetime import datetime

filepath = os.path.join(os.path.dirname(__file__), "Json Files", "root.json")


def initialize_root_file():
    """Initialize root.json with default values if it doesn't exist"""
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        default_data = {
            "BASE_URL": "https://api.telegram.org/bot<YOUR_BOT_TOKEN>",
            "offset": 0,
            "Commands": "/",
            "Total Users": 0,
            "Bot Started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Version": "1.0"
        }
        with open(filepath, 'w') as f:
            json.dump(default_data, f, indent=4)


def root_read(tag):
    """Read specific value from root.json"""
    try:
        initialize_root_file()
        with open(filepath, 'r') as rootfile:
            json_object = json.load(rootfile)
        return json_object[tag]
    except KeyError:
        raise KeyError(f"Tag '{tag}' not found in root.json")
    except Exception as e:
        raise Exception(f"Error reading root.json: {e}")


def root_read_untagged():
    """Read all data from root.json"""
    try:
        initialize_root_file()
        with open(filepath, 'r') as rootfile:
            json_object = json.load(rootfile)
        return json_object
    except Exception as e:
        raise Exception(f"Error reading root.json: {e}")


def root_write(tag, data):
    """Write specific value to root.json"""
    try:
        dictionary = root_read_untagged()
        dictionary[tag] = data
        dictionary["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(filepath, 'w') as rootfile:
            json.dump(dictionary, rootfile, indent=4)

    except Exception as e:
        raise Exception(f"Error writing to root.json: {e}")


def root_update_multiple(updates_dict):
    """Update multiple values at once"""
    try:
        dictionary = root_read_untagged()
        dictionary.update(updates_dict)
        dictionary["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(filepath, 'w') as rootfile:
            json.dump(dictionary, rootfile, indent=4)

    except Exception as e:
        raise Exception(f"Error updating root.json: {e}")


def setup_bot_token(bot_token):
    """Setup bot token in root.json"""
    try:
        base_url = f"https://api.telegram.org/bot{bot_token}"
        root_write("BASE_URL", base_url)
        print(f"Bot token configured successfully!")
        return True
    except Exception as e:
        print(f"Error setting up bot token: {e}")
        return False


def get_bot_info():
    """Get bot configuration info"""
    try:
        data = root_read_untagged()
        return {
            "base_url": data.get("BASE_URL", "Not configured"),
            "total_users": data.get("Total Users", 0),
            "bot_started": data.get("Bot Started", "Unknown"),
            "version": data.get("Version", "Unknown"),
            "last_updated": data.get("Last Updated", "Never")
        }
    except Exception as e:
        return {"error": str(e)}


def reset_offset():
    """Reset update offset to 0"""
    try:
        root_write("offset", 0)
        return True
    except Exception as e:
        print(f"Error resetting offset: {e}")
        return False