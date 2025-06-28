from user_json import user_read
import json
import os
from log import log
from match import check_matched
from send_updates import send_message

filepath = os.path.join(os.path.dirname(__file__), "Json Files", "lobby.json")


def initialize_lobby():
    """Initialize lobby file if it doesn't exist"""
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump({}, f)


def add_to_lobby(chat_id, match_org=False):
    """Add user to lobby for matching"""
    if check_matched(chat_id) == None:
        try:
            initialize_lobby()
            user_data = user_read(chat_id)
            gender = user_data["gender"]
            prefer = user_data.get("prefer", "Any")  # Default to Any if not set
            user_type = user_data.get("type", "Free")  # Default to Free if not set

            # Read current lobby data
            with open(filepath, 'r') as lobbyfile:
                lobby_data = json.load(lobbyfile)

            # Add or update entry
            lobby_data[str(chat_id)] = {
                "gender": gender,
                "prefer": prefer,
                "type": user_type,
                "match_org": match_org
            }

            # Save back to file
            with open(filepath, 'w') as lobby_file:
                json.dump(lobby_data, lobby_file, indent=4)

            log(f"Added user {chat_id} to lobby - Gender: {gender}, Prefer: {prefer}")

        except Exception as e:
            log(f"Error adding to lobby for chat_id {chat_id}: {e}")

        else:
            send_message(chat_id=chat_id, text="You are already matched\nClick /disconnect and try again")



def remove_from_lobby(chat_id):
    """Remove user from lobby"""
    try:
        initialize_lobby()
        chat_id_str = str(chat_id)

        with open(filepath, 'r') as lobbyfile:
            lobby_data = json.load(lobbyfile)

        # Remove user if they exist in lobby
        if chat_id_str in lobby_data:
            del lobby_data[chat_id_str]

            # Save updated lobby
            with open(filepath, 'w') as lobby_file:
                json.dump(lobby_data, lobby_file, indent=4)

            log(f"Removed user {chat_id} from lobby")

    except Exception as e:
        log(f"Error removing from lobby for chat_id {chat_id}: {e}")


def tot_lobby():
    """Get total number of users in lobby"""
    try:
        initialize_lobby()
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                lobby_data = json.load(f)
            return len(lobby_data)
        else:
            return 0
    except Exception as e:
        log(f"Error getting lobby count: {e}")
        return 0


def get_lobby_users():
    """Get all users currently in lobby"""
    try:
        initialize_lobby()
        with open(filepath, 'r') as f:
            lobby_data = json.load(f)
        return lobby_data
    except Exception as e:
        log(f"Error getting lobby users: {e}")
        return {}


def is_in_lobby(chat_id):
    """Check if user is currently in lobby"""
    try:
        lobby_data = get_lobby_users()
        return str(chat_id) in lobby_data
    except:
        return False