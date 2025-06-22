import json
import os
from send_updates import send_message
from lobby import remove_from_lobby
from user_json import user_read
from log import log
from referral import check_membership_expiry, expire_vip_membership

# File to store active matches
matches_filepath = os.path.join(os.path.dirname(__file__), "Json Files", "matches.json")
lobby_filepath = os.path.join(os.path.dirname(__file__), "Json Files", "lobby.json")

def initialize_matches_file():
    """Initialize matches file if it doesn't exist"""
    if not os.path.exists(matches_filepath):
        os.makedirs(os.path.dirname(matches_filepath), exist_ok=True)
        with open(matches_filepath, 'w') as f:
            json.dump({}, f)

def get_matches():
    """Get all current matches"""
    initialize_matches_file()
    try:
        with open(matches_filepath, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_matches(matches_data):
    """Save matches to file"""
    initialize_matches_file()
    with open(matches_filepath, 'w') as f:
        json.dump(matches_data, f, indent=4)

def check_matched(chat_id):
    """Check if user is currently matched with someone"""
    matches = get_matches()
    chat_id_str = str(chat_id)

    # Check if user is in matches as key
    if chat_id_str in matches:
        return matches[chat_id_str]

    # Check if user is matched as a value
    for user_id, partner_id in matches.items():
        if str(partner_id) == chat_id_str:
            return user_id

    return None

def create_match(user1_id, user2_id):
    """Create a match between two users"""
    matches = get_matches()
    user1_str = str(user1_id)
    user2_str = str(user2_id)

    # Add both directions for easy lookup
    matches[user1_str] = user2_str
    matches[user2_str] = user1_str

    save_matches(matches)
    log(f"Match created: {user1_id} <-> {user2_id}")

def unmatch(chat_id):
    """Remove user from matches"""
    matches = get_matches()
    chat_id_str = str(chat_id)
    partner_id = None

    # Find and remove the match
    if chat_id_str in matches:
        partner_id = matches[chat_id_str]
        del matches[chat_id_str]

        # Also remove the reverse mapping
        if partner_id in matches:
            del matches[partner_id]

    save_matches(matches)
    log(f"User {chat_id} unmatched from {partner_id}")
    return partner_id

def get_lobby_data():
    """Get current lobby data"""
    if not os.path.exists(lobby_filepath):
        return {}
    try:
        with open(lobby_filepath, 'r') as f:
            return json.load(f)
    except:
        return {}

def is_compatible(user1_data, user2_data, user1_id=None, user2_id=None):
    """Check if two users are compatible for matching"""
    # Check gender preferences
    user1_gender = user1_data.get("gender")
    user1_prefer = user1_data.get("prefer", "Any")
    user2_gender = user2_data.get("gender")
    user2_prefer = user2_data.get("prefer", "Any")

    # Check if user1's preference matches user2's gender
    user1_compatible = user1_prefer == "Any" or user1_prefer == user2_gender

    # Check if user2's preference matches user1's gender
    user2_compatible = user2_prefer == "Any" or user2_prefer == user1_gender

    # Check organization matching preference
    user1_match_org = user1_data.get("match_org", False)
    user2_match_org = user2_data.get("match_org", False)

    # If both users want to match within organization, check email domains
    if user1_match_org and user2_match_org and user1_id and user2_id:
        try:
            user1_full_data = user_read(user1_id)
            user2_full_data = user_read(user2_id)

            user1_email = user1_full_data.get("email", "")
            user2_email = user2_full_data.get("email", "")

            # Extract domains
            user1_domain = user1_email.split("@")[1] if "@" in user1_email else None
            user2_domain = user2_email.split("@")[1] if "@" in user2_email else None

            # Check if domains match
            domains_match = user1_domain and user2_domain and user1_domain == user2_domain

            # Both gender preferences match AND domains match
            return user1_compatible and user2_compatible and domains_match
        except Exception as e:
            log(f"Error checking email domains for compatibility: {e}")
            # Fall back to just gender preference if there's an error
            return user1_compatible and user2_compatible

    # If one wants organization matching but other doesn't, they're incompatible
    if user1_match_org != user2_match_org:
        return False

    # If both don't want organization matching (open category), just check gender preferences
    return user1_compatible and user2_compatible

def get_user_priority(user_data, user_id):
    """Get user priority for matching (higher number = higher priority)"""
    user_type = user_data.get("type", "Free")

    # Check if VIP membership is still valid
    if user_type == "VIP":
        if check_membership_expiry(user_id):
            # VIP membership expired, downgrade user
            expire_vip_membership(user_id)
            return 1  # Free user priority
        else:
            return 10  # VIP user priority

    return 1  # Free user priority

def sort_users_by_priority(lobby_users):
    """Sort lobby users by priority (VIP first, then Free)"""
    priority_users = []

    for user_id, user_data in lobby_users:
        try:
            # Get user info to check VIP status
            user_info = user_read(user_id)
            priority = get_user_priority(user_info, user_id)
            priority_users.append((user_id, user_data, priority))
        except Exception as e:
            log(f"Error getting priority for user {user_id}: {e}")
            # Default to free user priority if error
            priority_users.append((user_id, user_data, 1))

    # Sort by priority (highest first)
    priority_users.sort(key=lambda x: x[2], reverse=True)
    return priority_users

def get_matched():
    """Find and create matches from lobby with VIP priority"""
    lobby_data = get_lobby_data()
    if len(lobby_data) < 2:
        return

    lobby_users = list(lobby_data.items())

    # Sort users by priority (VIP users first)
    priority_sorted_users = sort_users_by_priority(lobby_users)

    matched_users = []

    # Try to find compatible pairs, prioritizing VIP users
    for i in range(len(priority_sorted_users)):
        if priority_sorted_users[i][0] in matched_users:
            continue

        user1_id, user1_data, user1_priority = priority_sorted_users[i]

        # For VIP users, try to match with other VIP users first
        if user1_priority > 1:  # VIP user
            # First, try to match with other VIP users
            for j in range(len(priority_sorted_users)):
                if i == j or priority_sorted_users[j][0] in matched_users:
                    continue

                user2_id, user2_data, user2_priority = priority_sorted_users[j]

                # Prefer VIP-VIP matches
                if user2_priority > 1 and is_compatible(user1_data, user2_data, user1_id, user2_id):
                    if create_match_pair(user1_id, user2_id, user1_data, user2_data):
                        matched_users.extend([user1_id, user2_id])
                        break

            # If no VIP match found, try with Free users
            if user1_id not in matched_users:
                for j in range(len(priority_sorted_users)):
                    if i == j or priority_sorted_users[j][0] in matched_users:
                        continue

                    user2_id, user2_data, user2_priority = priority_sorted_users[j]

                    if is_compatible(user1_data, user2_data, user1_id, user2_id):
                        if create_match_pair(user1_id, user2_id, user1_data, user2_data):
                            matched_users.extend([user1_id, user2_id])
                            break

        else:  # Free user
            # Try to match with any compatible user not already matched
            for j in range(i + 1, len(priority_sorted_users)):
                if priority_sorted_users[j][0] in matched_users:
                    continue

                user2_id, user2_data, user2_priority = priority_sorted_users[j]

                if is_compatible(user1_data, user2_data, user1_id, user2_id):
                    if create_match_pair(user1_id, user2_id, user1_data, user2_data):
                        matched_users.extend([user1_id, user2_id])
                        break

def create_match_pair(user1_id, user2_id, user1_data, user2_data):
    """Create a match between two specific users"""
    try:
        # Create the match
        create_match(user1_id, user2_id)

        # Remove both users from lobby
        remove_from_lobby(user1_id)
        remove_from_lobby(user2_id)

        # Get user names for messages
        try:
            user1_info = user_read(user1_id)
            user2_info = user_read(user2_id)

            user1_type = user1_info.get("type", "Free")
            user2_type = user2_info.get("type", "Free")

            user1_gender_emoji = "🧒" if user1_info["gender"] == "Female" else "👦"
            user2_gender_emoji = "🧒" if user2_info["gender"] == "Female" else "👦"

            # Create match messages with VIP indicators
            user1_message = f"🎉 Match found! You're now connected with a {user2_info['gender'].lower()}. {user2_gender_emoji}"
            user2_message = f"🎉 Match found! You're now connected with a {user1_info['gender'].lower()}. {user1_gender_emoji}"

            # Add VIP status indicators
            if user2_type == "VIP":
                user1_message += "\n✨ Your partner is a VIP member!"
            if user1_type == "VIP":
                user2_message += "\n✨ Your partner is a VIP member!"

            # Add organization matching indicators
            if user1_data.get("match_org") and user2_data.get("match_org"):
                user1_email = user1_info.get("email", "")
                user2_email = user2_info.get("email", "")
                if user1_email and user2_email:
                    domain = user1_email.split("@")[1]
                    user1_message += f"\n🏛️ You're matched with someone from @{domain}!"
                    user2_message += f"\n🏛️ You're matched with someone from @{domain}!"

            user1_message += "\n\nStart chatting! Use /next to find a new partner or /disconnect to end chat."
            user2_message += "\n\nStart chatting! Use /next to find a new partner or /disconnect to end chat."

            # Notify both users
            send_message(chat_id=int(user1_id), text=user1_message)
            send_message(chat_id=int(user2_id), text=user2_message)

        except Exception as e:
            log(f"Error getting user info for match notification: {e}")
            # Send generic messages if user info fails
            send_message(chat_id=int(user1_id), text="🎉 Match found! Start chatting!")
            send_message(chat_id=int(user2_id), text="🎉 Match found! Start chatting!")

        log(f"Successfully matched {user1_id} ({user1_data.get('type', 'Free')}) with {user2_id} ({user2_data.get('type', 'Free')})")
        return True

    except Exception as e:
        log(f"Error creating match between {user1_id} and {user2_id}: {e}")
        return False

def get_lobby_stats():
    """Get lobby statistics including VIP/Free breakdown"""
    try:
        lobby_data = get_lobby_data()

        stats = {
            "total_users": len(lobby_data),
            "vip_users": 0,
            "free_users": 0
        }

        for user_id, user_data in lobby_data.items():
            user_type = user_data.get("type", "Free")
            if user_type == "VIP":
                # Verify VIP membership is still valid
                if not check_membership_expiry(user_id):
                    stats["vip_users"] += 1
                else:
                    stats["free_users"] += 1
            else:
                stats["free_users"] += 1

        return stats

    except Exception as e:
        log(f"Error getting lobby stats: {e}")
        return {"total_users": 0, "vip_users": 0, "free_users": 0}