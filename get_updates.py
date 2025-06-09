import requests
import os
import root_json
from log import log
from send_updates import send_message
import user_json
from lobby import add_to_lobby
import match
from referral import add_referral, create_referral_link, get_user_referrals

def read_msg(TIMEOUT):
    BASE_URL = root_json.root_read("BASE_URL")
    offset = root_json.root_read("offset")

    try:
        resp = requests.get(f"{BASE_URL}/getUpdates", params={"offset": offset, "timeout": TIMEOUT},
                           timeout=TIMEOUT + 5)
        resp.raise_for_status()
        data = resp.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        log(f"Error fetching updates: {e}")
        return

    for result in data.get('result', []):
        try:
            # Handle message
            message = result.get('message')
            if message and 'text' in message:
                text = message['text']
                chat_id = message['from']['id']

                if text.startswith("/"):
                    commands(text, chat_id)
                elif match.check_matched(chat_id) is not None:
                    # Forward message to matched partner
                    partner_id = match.check_matched(chat_id)
                    if partner_id:
                        try:
                            data = user_json.user_read(str(chat_id))
                            gender = data["gender"]
                            emoji = "🧒" if gender == "Female" else "👦"
                            send_message(chat_id=partner_id, text=(emoji + " " + text))
                        except Exception as e:
                            log(f"Error forwarding message: {e}")
                            send_message(chat_id=chat_id, text="Error sending message to partner")
                else:
                    log(f"Unknown command from {chat_id}: {text}")
                    send_message(chat_id=chat_id,
                               text="Please use /connect to find a chat partner or /help for available commands")

                root_json.root_write("offset", result["update_id"] + 1)

            # Handle callback Query
            elif 'callback_query' in result:
                cb = result['callback_query']
                item = cb['data']
                callback(text=item, result=cb)
                root_json.root_write("offset", result["update_id"] + 1)

        except Exception as e:
            log(f"Error processing update: {e}")
            if 'update_id' in result:
                root_json.root_write("offset", result["update_id"] + 1)

def callback(text, result):
    if text.startswith("gender:"):
        try:
            gender = text.split(":", 1)[1]
            chat_id = result["from"]["id"]
            first_name = result["from"].get("first_name", "")
            last_name = result["from"].get("last_name", "")
            username = result["from"].get("username", "")

            user_json.add_user(
                chat_id=str(chat_id),
                first_name=first_name,
                last_name=last_name,
                username=username,
                gender=gender
            )

            send_message(chat_id=chat_id,
                       text=f"Gender '{gender}' selected. You can now use /connect to find a chat partner!")
            log(f"Gender selected and user added: {chat_id}, {gender}")
        except Exception as e:
            log(f"Error handling gender callback for {result.get('from', {}).get('id', 'Unknown')}: {e}")

    elif text.startswith("settings:"):
        try:
            chat_id = result["from"]["id"]
            setting_type = text.split(":", 1)[1]

            if setting_type == "Preference":
                pref_buttons = {
                    "inline_keyboard": [
                        [{"text": "Match with Boys", "callback_data": "pref:Male"}],
                        [{"text": "Match with Girls", "callback_data": "pref:Female"}],
                        [{"text": "Match with Anyone", "callback_data": "pref:Any"}]
                    ]
                }
                send_message(chat_id=chat_id, text="Select your gender preference:", reply_markup=pref_buttons)

            elif setting_type == "Status":
                try:
                    user_data = user_json.user_read(str(chat_id))
                    user_type = user_data.get("type", "Free")
                    referral_count = get_user_referrals(chat_id)

                    status_text = f"Your current membership: {user_type} User\n"
                    status_text += f"Total referrals: {referral_count}\n"

                    if user_type == "Free":
                        remaining = 5 - referral_count
                        if remaining > 0:
                            status_text += f"Refer {remaining} more users to earn VIP membership!"

                    send_message(chat_id=chat_id, text=status_text)
                except:
                    send_message(chat_id=chat_id, text="Your current membership: Free User")

            elif setting_type == "Verify":
                send_message(chat_id=chat_id,
                           text="To get verified, please contact @admin or complete 10 successful chats.")

        except Exception as e:
            log(f"Error handling settings callback for {result.get('from', {}).get('id', 'Unknown')}: {e}")

    elif text.startswith("pref:"):
        try:
            preference = text.split(":", 1)[1]
            chat_id = result["from"]["id"]
            user_json.changePrefer(chat_id=str(chat_id), prefer=preference)
            send_message(chat_id=chat_id, text=f"Preference set to '{preference}'.")
        except Exception as e:
            log(f"Error handling preference callback for {result.get('from', {}).get('id', 'Unknown')}: {e}")

def commands(text, chat_id):
    if text.startswith("/start"):
        # Check for referral parameter
        referrer_id = None
        if len(text.split()) > 1:
            referral_code = text.split()[1]
            # Validate referral code (should be a user ID)
            try:
                referrer_id = int(referral_code)
                # Check if referrer exists
                if str(referrer_id) in user_json.user_read_untagged():
                    if referrer_id != chat_id:  # Prevent self-referral
                        log(f"Valid referral code detected: {referral_code} from {referrer_id}")
                    else:
                        referrer_id = None  # Self-referral not allowed
                else:
                    referrer_id = None  # Invalid referrer
            except ValueError:
                referrer_id = None  # Invalid referral code format

        start_text = """
🤖 Welcome to Anonymous Chat Bot!

Connect with random people and have anonymous conversations!

Available commands:
/connect - Find a chat partner
/refer - Get your referral link
/stats - View your referral stats
/help - Show help message
/settings - Manage your settings

Let's get started! Please select your gender below:
"""

        send_message(text=start_text, chat_id=chat_id)

        if str(chat_id) not in list(user_json.user_read_untagged().keys()):
            gender_buttons = {
                "inline_keyboard": [
                    [{"text": "Male", "callback_data": "gender:Male"}],
                    [{"text": "Female", "callback_data": "gender:Female"}]
                ]
            }
            send_message(chat_id=chat_id, text="Please select your gender:", reply_markup=gender_buttons)

            # If there's a valid referrer, we'll add the referral after gender selection
            if referrer_id:
                # Store referrer temporarily for processing after user registration
                temp_referral_file = f"temp_referral_{chat_id}.txt"
                with open(temp_referral_file, 'w') as f:
                    f.write(str(referrer_id))
        else:
            # User already exists, add to lobby
            send_message(text="Looking for a partner for you\nPlease wait patiently...", chat_id=chat_id)
            add_to_lobby(str(chat_id))

            # Process referral if new user from referral link
            if referrer_id:
                if add_referral(referrer_id, chat_id):
                    send_message(
                        chat_id=referrer_id,
                        text=f"🎉 Great news! Someone joined using your referral link.\nYour total referrals: {get_user_referrals(referrer_id)}"
                    )

    elif text.startswith("/refer"):
        try:
            if str(chat_id) not in user_json.user_read_untagged().keys():
                send_message(text="Please use /start first to set up your profile!", chat_id=chat_id)
                return

            bot_username = "ghostchat_iitm_bot"  # Your bot username
            referral_link, referral_code = create_referral_link(chat_id, bot_username)

            if referral_link:
                referral_count = get_user_referrals(chat_id)
                referral_text = f"""
🔗 Your Referral Link:
{referral_link}

📊 Your Stats:
• Total Referrals: {referral_count}/5
• Status: {"VIP" if referral_count >= 5 else "Free"}

💡 Share this link with friends!
When 5 people join using your link, you'll get VIP membership for 30 days!

✨ VIP Benefits:
• Higher match priority
• Faster connections
• Premium features
"""
                send_message(chat_id=chat_id, text=referral_text)
            else:
                send_message(chat_id=chat_id, text="Error generating referral link. Please try again.")
        except Exception as e:
            log(f"Error in refer command: {e}")
            send_message(chat_id=chat_id, text="Error generating referral link. Please try again.")

    elif text.startswith("/stats"):
        try:
            if str(chat_id) not in user_json.user_read_untagged().keys():
                send_message(text="Please use /start first to set up your profile!", chat_id=chat_id)
                return

            user_data = user_json.user_read(str(chat_id))
            referral_count = get_user_referrals(chat_id)
            user_type = user_data.get("type", "Free")

            stats_text = f"""
📊 Your Statistics:

👤 Profile:
• Name: {user_data.get('first_name', '')} {user_data.get('last_name', '')}
• Gender: {user_data.get('gender', 'Unknown')}
• Membership: {user_type}

🔗 Referrals:
• Total Referrals: {referral_count}
• VIP Status: {"Earned" if referral_count >= 5 else "Not Earned"}
• Needed for VIP: {max(0, 5 - referral_count)} more referrals

Use /refer to get your referral link!
"""
            send_message(chat_id=chat_id, text=stats_text)
        except Exception as e:
            log(f"Error in stats command: {e}")
            send_message(chat_id=chat_id, text="Error retrieving stats. Please try again.")

    elif text.startswith("/help"):
        help_text = """
🤖 Anonymous Chat Bot Help

Available Commands:
/start - Start the bot
/connect - Find a random chat partner
/refer - Get your referral link
/stats - View your profile and referral statistics
/disconnect - End current chat
/next - Skip current partner and find new one
/report - Report current partner
/settings - Manage your preferences
/issue - Report a bug

🔗 Referral System:
• Share your referral link with friends
• Earn VIP membership by referring 5 users
• VIP users get higher match priority

How to use:
1. Use /connect to find a chat partner
2. Start chatting anonymously
3. Use /next to find a new partner
4. Use /disconnect to end chat

Enjoy chatting! 🎉
"""
        send_message(text=help_text, chat_id=chat_id)

    elif text.startswith("/issue"):
        if text[7:].strip():
            issue = text[7:].strip()
            log("ISSUE: " + issue)
            send_message(text=f'Your issue: "{issue}" has been recorded. Thank you for the feedback!', chat_id=chat_id)
        else:
            send_message(
                text='Write your issue after "/issue" command.\n\nFor example: "/issue report command is not working"',
                chat_id=chat_id)

    elif text.startswith("/connect"):
        try:
            # Check if user exists
            if str(chat_id) not in user_json.user_read_untagged().keys():
                send_message(text="Please use /start first to set up your profile!", chat_id=chat_id)
                return

            # Check for pending referral
            temp_referral_file = f"temp_referral_{chat_id}.txt"
            if os.path.exists(temp_referral_file):
                try:
                    with open(temp_referral_file, 'r') as f:
                        referrer_id = int(f.read().strip())

                    if add_referral(referrer_id, chat_id):
                        send_message(
                            chat_id=referrer_id,
                            text=f"🎉 Great news! Someone joined using your referral link.\nYour total referrals: {get_user_referrals(referrer_id)}"
                        )
                        send_message(
                            chat_id=chat_id,
                            text="Welcome! You were successfully referred by another user. 🎉"
                        )

                    os.remove(temp_referral_file)
                except:
                    pass

            send_message(text="Looking for a new partner for you\nPlease wait patiently... 🔍", chat_id=chat_id)
            add_to_lobby(str(chat_id))
        except Exception as e:
            log(f"Error in connect command: {e}")
            send_message(text="Error connecting. Please try again later.", chat_id=chat_id)

    elif text.startswith("/disconnect"):
        try:
            if match.check_matched(chat_id):
                partner_id = match.check_matched(chat_id)
                match.unmatch(chat_id)
                send_message(text="Chat ended. Use /connect to find a new partner!", chat_id=chat_id)
                if partner_id:
                    send_message(text="Your partner has left the chat. Use /connect to find a new partner!",
                               chat_id=partner_id)
            else:
                send_message(text="You're not currently in a chat. Use /connect to find a partner!", chat_id=chat_id)
        except Exception as e:
            log(f"Error in disconnect: {e}")
            send_message(text="Error disconnecting. Please try again.", chat_id=chat_id)

    elif text.startswith("/next"):
        try:
            if match.check_matched(chat_id):
                partner_id = match.check_matched(chat_id)
                match.unmatch(chat_id)
                send_message(text="Chat ended. Looking for a new partner... 🔍", chat_id=chat_id)
                if partner_id:
                    send_message(text="Your partner has left the chat. Use /connect to find a new partner!",
                               chat_id=partner_id)
                add_to_lobby(str(chat_id))
            else:
                send_message(text="You're not currently in a chat. Use /connect to find a partner!", chat_id=chat_id)
        except Exception as e:
            log(f"Error in next command: {e}")
            send_message(text="Error finding new partner. Please try again.", chat_id=chat_id)

    elif text.startswith("/report"):
        if match.check_matched(chat_id):
            send_message(text="Thanks for reporting! We have shared the last few messages with our review team.",
                       chat_id=chat_id)
            log(f"User {chat_id} reported their partner {match.check_matched(chat_id)}")
        else:
            send_message(text="You're not currently in a chat. Nothing to report.", chat_id=chat_id)

    elif text.startswith("/settings"):
        try:
            # Check if user exists
            if str(chat_id) not in user_json.user_read_untagged().keys():
                send_message(text="Please use /start first to set up your profile!", chat_id=chat_id)
                return

            settings_buttons = {
                "inline_keyboard": [
                    [{"text": "Set Gender Preference", "callback_data": "settings:Preference"}],
                    [{"text": "Membership Status", "callback_data": "settings:Status"}],
                    [{"text": "Get Verified Badge", "callback_data": "settings:Verify"}]
                ]
            }
            send_message(chat_id=chat_id, text="⚙️ Settings - Please select an option:", reply_markup=settings_buttons)
        except Exception as e:
            log(f"Error in settings: {e}")
            send_message(text="Error loading settings. Please try again.", chat_id=chat_id)