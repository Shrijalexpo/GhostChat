import json
import os
from datetime import datetime, timedelta
from log import log
from user_json import user_read, user_read_untagged, makeVIP
from send_updates import send_message

# File paths for referral data
referrals_filepath = os.path.join(os.path.dirname(__file__), "Json Files", "referrals.json")
memberships_filepath = os.path.join(os.path.dirname(__file__), "Json Files", "memberships.json")

def initialize_referral_file():
    """Initialize referral file if it doesn't exist"""
    if not os.path.exists(referrals_filepath):
        os.makedirs(os.path.dirname(referrals_filepath), exist_ok=True)
        with open(referrals_filepath, 'w') as f:
            json.dump({}, f)

def initialize_membership_file():
    """Initialize membership file if it doesn't exist"""
    if not os.path.exists(memberships_filepath):
        os.makedirs(os.path.dirname(memberships_filepath), exist_ok=True)
        with open(memberships_filepath, 'w') as f:
            json.dump({}, f)

def generate_referral_code(chat_id):
    """Generate a unique referral code for a user"""
    try:
        # Use chat_id as base for referral code to ensure uniqueness
        referral_code = str(chat_id)
        return referral_code
    except Exception as e:
        log(f"Error generating referral code for {chat_id}: {e}")
        return None

def create_referral_link(chat_id, bot_username):
    """Create a referral link for a user"""
    try:
        referral_code = generate_referral_code(chat_id)
        if referral_code:
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"
            return referral_link, referral_code
        return None, None
    except Exception as e:
        log(f"Error creating referral link for {chat_id}: {e}")
        return None, None

def get_referral_data():
    """Get all referral data"""
    initialize_referral_file()
    try:
        with open(referrals_filepath, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_referral_data(data):
    """Save referral data to file"""
    initialize_referral_file()
    with open(referrals_filepath, 'w') as f:
        json.dump(data, f, indent=4)

def add_referral(referrer_id, referred_id):
    """Add a new referral relationship"""
    try:
        referral_data = get_referral_data()

        # Initialize referrer's data if doesn't exist
        if str(referrer_id) not in referral_data:
            referral_data[str(referrer_id)] = {
                "referrals": [],
                "total_referrals": 0,
                "vip_earned": False,
                "last_referral": None
            }

        # Check if this referral already exists
        if str(referred_id) not in referral_data[str(referrer_id)]["referrals"]:
            referral_data[str(referrer_id)]["referrals"].append(str(referred_id))
            referral_data[str(referrer_id)]["total_referrals"] += 1
            referral_data[str(referrer_id)]["last_referral"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            save_referral_data(referral_data)

            # Check if user qualifies for VIP (5 referrals)
            if referral_data[str(referrer_id)]["total_referrals"] >= 5 and not referral_data[str(referrer_id)]["vip_earned"]:
                grant_vip_membership(referrer_id)
                referral_data[str(referrer_id)]["vip_earned"] = True
                save_referral_data(referral_data)

            log(f"Referral added: {referrer_id} referred {referred_id}")
            return True
        else:
            log(f"Referral already exists: {referrer_id} -> {referred_id}")
            return False

    except Exception as e:
        log(f"Error adding referral {referrer_id} -> {referred_id}: {e}")
        return False

def get_user_referrals(chat_id):
    """Get referral count for a specific user"""
    try:
        referral_data = get_referral_data()
        if str(chat_id) in referral_data:
            return referral_data[str(chat_id)]["total_referrals"]
        return 0
    except Exception as e:
        log(f"Error getting referrals for {chat_id}: {e}")
        return 0

def grant_vip_membership(chat_id, days=30):
    """Grant VIP membership to a user"""
    try:
        # First upgrade user to VIP in user_json
        makeVIP(chat_id)

        # Add membership expiration tracking
        membership_data = get_membership_data()
        expiry_date = datetime.now() + timedelta(days=days)

        membership_data[str(chat_id)] = {
            "type": "VIP",
            "granted_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S"),
            "days": days,
            "reason": "referral_reward"
        }

        save_membership_data(membership_data)

        # Notify user
        send_message(
            chat_id=int(chat_id),
            text=f"🎉 Congratulations! You've earned VIP membership for {days} days by referring 5 users!\n\n✨ VIP Benefits:\n• Higher match priority\n• Faster connections\n• Premium features\n\nYour VIP membership expires on: {expiry_date.strftime('%Y-%m-%d')}"
        )

        log(f"VIP membership granted to {chat_id} for {days} days")
        return True

    except Exception as e:
        log(f"Error granting VIP membership to {chat_id}: {e}")
        return False

def get_membership_data():
    """Get all membership data"""
    initialize_membership_file()
    try:
        with open(memberships_filepath, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_membership_data(data):
    """Save membership data to file"""
    initialize_membership_file()
    with open(memberships_filepath, 'w') as f:
        json.dump(data, f, indent=4)

def check_membership_expiry(chat_id):
    """Check if user's VIP membership has expired"""
    try:
        membership_data = get_membership_data()
        if str(chat_id) in membership_data:
            expiry_date = datetime.strptime(membership_data[str(chat_id)]["expiry_date"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > expiry_date:
                return True  # Expired
            return False  # Still valid
        return True  # No membership record = expired
    except Exception as e:
        log(f"Error checking membership expiry for {chat_id}: {e}")
        return True

def expire_vip_membership(chat_id):
    """Expire VIP membership and downgrade user to Free"""
    try:
        # Get user data
        users = user_read_untagged()
        if str(chat_id) in users:
            user_data = users[str(chat_id)]

            # Update user to Free status
            users[str(chat_id)]["type"] = "Free"

            # Save updated user data
            with open(os.path.join(os.path.dirname(__file__), "Json Files", "user.json"), 'w') as f:
                json.dump(users, f, indent=4)

            # Remove from membership tracking
            membership_data = get_membership_data()
            if str(chat_id) in membership_data:
                del membership_data[str(chat_id)]
                save_membership_data(membership_data)

            # Notify user
            send_message(
                chat_id=int(chat_id),
                text="Your VIP membership has expired. You've been downgraded to Free status.\n\nTo regain VIP membership, refer 5 more users to the bot!"
            )

            log(f"VIP membership expired for {chat_id}")
            return True
    except Exception as e:
        log(f"Error expiring VIP membership for {chat_id}: {e}")
        return False

def process_membership_expiries():
    """Check all VIP memberships and expire those that have ended"""
    try:
        membership_data = get_membership_data()
        current_time = datetime.now()
        expired_users = []

        for chat_id, membership_info in membership_data.items():
            expiry_date = datetime.strptime(membership_info["expiry_date"], "%Y-%m-%d %H:%M:%S")
            if current_time > expiry_date:
                expired_users.append(chat_id)

        for chat_id in expired_users:
            expire_vip_membership(chat_id)

        log(f"Processed {len(expired_users)} membership expiries")
        return len(expired_users)

    except Exception as e:
        log(f"Error processing membership expiries: {e}")
        return 0

def get_referral_stats():
    """Get overall referral statistics"""
    try:
        referral_data = get_referral_data()
        stats = {
            "total_referrers": len(referral_data),
            "total_referrals": sum(data["total_referrals"] for data in referral_data.values()),
            "vip_earned_count": sum(1 for data in referral_data.values() if data["vip_earned"]),
            "top_referrers": []
        }

        # Get top 10 referrers
        sorted_referrers = sorted(
            referral_data.items(),
            key=lambda x: x[1]["total_referrals"],
            reverse=True
        )[:10]

        for chat_id, data in sorted_referrers:
            try:
                user_info = user_read(chat_id)
                stats["top_referrers"].append({
                    "chat_id": chat_id,
                    "name": f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip(),
                    "referrals": data["total_referrals"]
                })
            except:
                stats["top_referrers"].append({
                    "chat_id": chat_id,
                    "name": "Unknown User",
                    "referrals": data["total_referrals"]
                })

        return stats
    except Exception as e:
        log(f"Error getting referral stats: {e}")
        return {
            "total_referrers": 0,
            "total_referrals": 0,
            "vip_earned_count": 0,
            "top_referrers": []
        }