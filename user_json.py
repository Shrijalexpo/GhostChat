import json
import os
from datetime import datetime
from log import log
import root_json

filepath = os.path.join(os.path.dirname(__file__), "Json Files", "user.json")
referral_path = os.path.join(os.path.dirname(__file__), "Json Files", "referral.json")


def initialize_user_file():
    """Initialize user file if it doesn't exist"""
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump({}, f)


def user_read_untagged():
    """Read all users data"""
    try:
        initialize_user_file()
        with open(filepath, 'r') as userfile:
            json_object = json.load(userfile)
        return json_object
    except Exception as e:
        log(f"Error reading users: {e}")
        return {}


def user_read(chat_id):
    """Read specific user data"""
    try:
        initialize_user_file()
        with open(filepath, 'r') as userfile:
            json_object = json.load(userfile)
            return json_object[str(chat_id)]
    except KeyError:
        raise KeyError(f"User {chat_id} not found")
    except Exception as e:
        log(f"Error reading user {chat_id}: {e}")
        raise


def add_user(chat_id, first_name, last_name, username, gender):
    """Add new user to database"""
    try:
        initialize_user_file()
        dictionary = user_read_untagged()

        now = datetime.now()
        formatted_date = now.strftime("%d-%m-%Y")

        dictionary[str(chat_id)] = {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "gender": gender,
            "prefer": "Any",  # Default preference
            "type": "Free",  # Default user type
            "date": formatted_date,
            "created_at": now.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to file
        with open(filepath, 'w') as userfile:
            json.dump(dictionary, userfile, indent=4)

        log(f"Added user {chat_id}, Name: {first_name} {last_name}, Gender: {gender}")

        # Update total users count
        try:
            current_total = root_json.root_read("Total Users")
            root_json.root_write("Total Users", current_total + 1)
        except Exception as e:
            log(f"Error updating total users count: {e}")

    except Exception as e:
        log(f"Error adding user {chat_id}: {e}")
        raise


def makeVIP(chat_id):
    """Upgrade user to VIP status"""
    try:
        now = datetime.now()
        formatted_date = now.strftime("%d-%m-%Y")
        dictionary = user_read_untagged()
        user_data = user_read(chat_id)

        dictionary[str(chat_id)] = {
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "username": user_data["username"],
            "gender": user_data["gender"],
            "type": "VIP",
            "prefer": user_data.get("prefer", "Any"),
            "date": formatted_date,
            "created_at": user_data.get("created_at", ""),
            "vip_upgraded": now.strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(filepath, 'w') as userfile:
            json.dump(dictionary, userfile, indent=4)

        log(f"User {chat_id} upgraded to VIP")

    except Exception as e:
        log(f"Error making user {chat_id} VIP: {e}")
        raise


def changePrefer(chat_id, prefer):
    """Change user's gender preference"""
    try:
        dictionary = user_read_untagged()
        user_data = user_read(chat_id)

        dictionary[str(chat_id)] = {
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "username": user_data["username"],
            "gender": user_data["gender"],
            "type": user_data.get("type", "Free"),
            "prefer": prefer,
            "date": user_data.get("date", ""),
            "created_at": user_data.get("created_at", ""),
            "preference_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if "vip_upgraded" in user_data:
            dictionary[str(chat_id)]["vip_upgraded"] = user_data["vip_upgraded"]

        with open(filepath, 'w') as userfile:
            json.dump(dictionary, userfile, indent=4)

        log(f"User {chat_id} preference changed to {prefer}")

    except Exception as e:
        log(f"Error changing preference for user {chat_id}: {e}")
        raise


def user_exists(chat_id):
    """Check if user exists in database"""
    try:
        users = user_read_untagged()
        return str(chat_id) in users
    except:
        return False


def get_user_stats():
    """Get user statistics"""
    try:
        users = user_read_untagged()
        total_users = len(users)

        stats = {
            "total_users": total_users,
            "male_users": 0,
            "female_users": 0,
            "vip_users": 0,
            "free_users": 0
        }

        for user_data in users.values():
            if user_data.get("gender") == "Male":
                stats["male_users"] += 1
            elif user_data.get("gender") == "Female":
                stats["female_users"] += 1

            if user_data.get("type") == "VIP":
                stats["vip_users"] += 1
            else:
                stats["free_users"] += 1

        return stats

    except Exception as e:
        log(f"Error getting user stats: {e}")
        return {
            "total_users": 0,
            "male_users": 0,
            "female_users": 0,
            "vip_users": 0,
            "free_users": 0
        }