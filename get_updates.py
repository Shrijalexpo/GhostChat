import json
import requests
import os
import email_verification
import lobby
import root_json
from log import log
from send_updates import send_message, send_photo, send_document, send_voice, get_file, download_file, copy_message
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
            # Handle regular message
            message = result.get('message')
            if message:
                handle_message(message)

            # Handle edited message
            edited_message = result.get('edited_message')
            if edited_message:
                handle_edited_message(edited_message)

            # Handle callback query
            elif 'callback_query' in result:
                cb = result['callback_query']
                item = cb['data']
                callback(text=item, result=cb)

            root_json.root_write("offset", result["update_id"] + 1)

        except Exception as e:
            log(f"Error processing update: {e}")
            if 'update_id' in result:
                root_json.root_write("offset", result["update_id"] + 1)

def handle_message(message):
    """Handle incoming messages of all types"""
    chat_id = message['from']['id']

    # Handle text messages
    if 'text' in message:
            text = message['text']

            # Check if context file exists (waiting for email input)
            context_file = f"temp_context_{chat_id}.txt"

            # Check if waiting for OTP input
            if text.startswith("GC-") and not text.startswith("/"):
                # User is likely entering OTP
                otp = text.strip()

                # Create callback query with OTP
                callback_data = f"email_verify:{otp}"
                callback(text=callback_data, result={"from": {"id": chat_id}})

            elif os.path.exists(context_file) and not text.startswith("/"):
                # User is likely entering email
                email = text.strip()

                # Validate email format
                if email_verification.is_valid_email(email):
                    # Generate OTP
                    otp = email_verification.generate_otp()

                    # Send OTP to email
                    if email_verification.send_otp_email(email, otp):
                        # Store OTP for verification
                        email_verification.store_otp(chat_id, email, otp)

                        send_message(chat_id=chat_id,
                                     text=f"An OTP has been sent to {email}. Please enter the code: (Example: GC-XXXXXX)")
                    else:
                        send_message(chat_id=chat_id,
                                     text="Failed to send OTP. Please check your email address and try again.")
                else:
                    send_message(chat_id=chat_id,
                                 text="Invalid email format. Please enter a valid email address:")

            # Regular command handling
            elif text.startswith("/"):
                commands(text, chat_id)
            elif match.check_matched(chat_id) is not None:
                # Forward text message to matched partner
                forward_to_partner(chat_id, message, 'text')
            else:
                send_message(chat_id=chat_id,
                            text="Please use /connect to find a chat partner or /help for available commands")

    # Handle photo messages
    elif 'photo' in message:
        if match.check_matched(chat_id) is not None:
            forward_to_partner(chat_id, message, 'photo')
        else:
            send_message(chat_id=chat_id,
                         text="Please connect to a partner first using /connect to share photos")

    # Handle document messages
    elif 'document' in message:
        if match.check_matched(chat_id) is not None:
            forward_to_partner(chat_id, message, 'document')
        else:
            send_message(chat_id=chat_id,
                         text="Please connect to a partner first using /connect to share documents")

    # Handle voice messages
    elif 'voice' in message:
        if match.check_matched(chat_id) is not None:
            forward_to_partner(chat_id, message, 'voice')
        else:
            send_message(chat_id=chat_id,
                         text="Please connect to a partner first using /connect to share voice messages")

    # Handle video messages
    elif 'video' in message:
        if match.check_matched(chat_id) is not None:
            forward_to_partner(chat_id, message, 'video')
        else:
            send_message(chat_id=chat_id,
                         text="Please connect to a partner first using /connect to share videos")

    # Handle sticker messages
    elif 'sticker' in message:
        if match.check_matched(chat_id) is not None:
            forward_to_partner(chat_id, message, 'sticker')
        else:
            send_message(chat_id=chat_id,
                         text="Please connect to a partner first using /connect to share stickers")

    # Handle location messages
    elif 'location' in message:
        if match.check_matched(chat_id) is not None:
            forward_to_partner(chat_id, message, 'location')
        else:
            send_message(chat_id=chat_id,
                         text="Please connect to a partner first using /connect to share location")

def handle_edited_message(edited_message):
    """Handle edited messages"""
    chat_id = edited_message['from']['id']

    # Check if user is matched
    partner_id = match.check_matched(chat_id)
    if partner_id:
        try:
            # Get user gender for emoji
            data = user_json.user_read(str(chat_id))
            gender = data["gender"]
            emoji = "🧒" if gender == "Female" else "👦"

            if 'text' in edited_message:
                # Forward edited text message
                edited_text = edited_message['text']
                send_message(chat_id=partner_id,
                             text=f"{emoji} ✏️ (edited): {edited_text}")
            else:
                # For media messages, just notify about the edit
                send_message(chat_id=partner_id,
                             text=f"{emoji} ✏️ Your partner edited their message")

        except Exception as e:
            log(f"Error forwarding edited message: {e}")
            send_message(chat_id=chat_id, text="Error sending edited message to partner")

def forward_to_partner(chat_id, message, message_type):
    """Forward different types of messages to matched partner"""
    partner_id = match.check_matched(chat_id)
    if not partner_id:
        return

    try:
        # Get user gender for emoji
        data = user_json.user_read(str(chat_id))
        gender = data["gender"]
        emoji = "🧒" if gender == "Female" else "👦"

        if message_type == 'text':
            text = message['text']
            send_message(chat_id=partner_id, text=(emoji + " " + text))

        elif message_type == 'photo':
            # Get the largest photo size
            photo = message['photo'][-1]  # Last element is largest size
            file_id = photo['file_id']
            caption = message.get('caption', '')
            if caption:
                caption = f"{emoji} {caption}"
            else:
                caption = f"{emoji} sent a photo"
            send_photo(chat_id=partner_id, photo=file_id, caption=caption)

        elif message_type == 'document':
            document = message['document']
            file_id = document['file_id']
            caption = message.get('caption', '')
            if caption:
                caption = f"{emoji} {caption}"
            else:
                filename = document.get('file_name', 'document')
                caption = f"{emoji} sent a document"
            send_document(chat_id=partner_id, document=file_id, caption=caption)

        elif message_type == 'voice':
            voice = message['voice']
            file_id = voice['file_id']
            duration = voice.get('duration', 0)
            caption = f"{emoji} sent a voice message"
            send_voice(chat_id=partner_id, voice=file_id, caption=caption, duration=duration)

        elif message_type == 'video':
            # Use copy_message for video as it preserves format better
            copy_message(chat_id=partner_id, from_chat_id=chat_id,
                         message_id=message['message_id'], caption=f"{emoji} sent a video")

        elif message_type == 'sticker':
            # Use copy_message for stickers
            copy_message(chat_id=partner_id, from_chat_id=chat_id,
                         message_id=message['message_id'])
            send_message(chat_id=partner_id, text=f"{emoji} sent a sticker")

        elif message_type == 'location':
            # Use copy_message for location
            copy_message(chat_id=partner_id, from_chat_id=chat_id,
                         message_id=message['message_id'])
            send_message(chat_id=partner_id, text=f"{emoji} shared their location")

    except Exception as e:
        log(f"Error forwarding {message_type} message: {e}")
        send_message(chat_id=chat_id, text=f"Error sending {message_type} to partner")

def save_received_file(message, file_type):
    """Save received files to local storage"""
    try:
        file_info = None
        file_id = None

        if file_type == 'photo':
            # Get largest photo
            file_info = message['photo'][-1]
            file_id = file_info['file_id']
        elif file_type == 'document':
            file_info = message['document']
            file_id = file_info['file_id']
        elif file_type == 'voice':
            file_info = message['voice']
            file_id = file_info['file_id']
        elif file_type == 'video':
            file_info = message['video']
            file_id = file_info['file_id']

        if file_id:
            # Get file info from Telegram
            file_data = get_file(file_id)
            if file_data:
                file_path = file_data['file_path']
                # Create save path
                save_dir = f"downloads/{file_type}s"
                filename = os.path.basename(file_path)
                save_path = os.path.join(save_dir, filename)

                # Download the file
                downloaded_path = download_file(file_path, save_path)
                if downloaded_path:
                    log(f"File saved: {downloaded_path}")
                    return downloaded_path

    except Exception as e:
        log(f"Error saving {file_type} file: {e}")

    return None

def process_referral(chat_id):
    """Process pending referral if exists"""
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
        except Exception as e:
            log(f"Error processing referral: {e}")

def callback(text, result):
    """Handle callback queries"""
    if text.startswith("gender:"):
        try:
            gender = text.split(":", 1)[1]
            chat_id = result["from"]["id"]
            first_name = result["from"].get("first_name", "")
            last_name = result["from"].get("last_name", "")
            username = result["from"].get("username", "")

            # Store gender temporarily in user context
            context = {
                "chat_id": str(chat_id),
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "gender": gender
            }

            # Create temporary context file
            context_file = f"temp_context_{chat_id}.txt"
            with open(context_file, 'w') as f:
                f.write(json.dumps(context))

            # Ask for email
            send_message(chat_id=chat_id,
                         text="Please enter your email address for verification\nPrefer entering your College/Company email id for getting matched within your College/Comany:")

            log(f"Gender selected, waiting for email: {chat_id}, {gender}")

        except Exception as e:
            log(f"Error handling gender callback for {result.get('from', {}).get('id', 'Unknown')}: {e}")

    elif text.startswith("email_verify:"):
        try:
            chat_id = result["from"]["id"]
            otp = text.split(":", 1)[1]

            # Verify OTP
            if email_verification.verify_otp(chat_id, otp):
                # Get verified email
                email = email_verification.get_verified_email(chat_id)

                # Load context
                context_file = f"temp_context_{chat_id}.txt"
                if os.path.exists(context_file):
                    with open(context_file, 'r') as f:
                        context = json.loads(f.read())

                    # Extract context data
                    gender = context.get("gender")
                    first_name = context.get("first_name", "")
                    last_name = context.get("last_name", "")
                    username = context.get("username", "")

                    # Add user with email
                    user_json.add_user(
                        chat_id=str(chat_id),
                        first_name=first_name,
                        last_name=last_name,
                        username=username,
                        gender=gender,
                        email=email,
                        match_org=False
                    )

                    # Extract domain for organization matching
                    domain = email.split('@')[1] if '@' in email else None

                    # Offer organization matching if domain exists
                    if domain and not domain.startswith('gmail') and not domain.startswith('outlook') and not domain.startswith('yahoo'):
                        org_buttons = {
                            "inline_keyboard": [
                                [{"text": f"Match with people from @{domain}", "callback_data": f"org:yes"}],
                                [{"text": "Match in Open Category", "callback_data": "org:no"}]
                            ]
                        }
                        send_message(chat_id=chat_id,
                                     text="Select your matching preference:",
                                     reply_markup=org_buttons)
                    else:
                        send_message(chat_id=chat_id,
                                    text=f"Gender '{gender}' selected and email verified. You can now use /connect to find a chat partner!")

                        # Process pending referral if exists
                        process_referral(chat_id)

                    # Clean up
                    os.remove(context_file)
                    email_verification.clear_otp_data(chat_id)
                else:
                    send_message(chat_id=chat_id,
                                 text="Error: Your session has expired. Please use /start again.")
            else:
                send_message(chat_id=chat_id,
                             text="Invalid OTP. Please try again or use /start to restart.")
        except Exception as e:
            log(f"Error handling OTP verification for {result.get('from', {}).get('id', 'Unknown')}: {e}")

    elif text.startswith("org:"):
        try:
            match_org = text.split(":", 1)[1] == "yes"
            chat_id = result["from"]["id"]

            # Store matching preference
            user_data = user_json.user_read(str(chat_id))
            email = user_data.get("email", "")
            domain = email.split('@')[1] if '@' in email else "your organization"

            if match_org and not domain.startswith('gmail') and not domain.startswith('outlook') and not domain.startswith('yahoo'):
                user_json.changeOrgPrefer(chat_id=chat_id, OrgPrefer=True)
                send_message(chat_id=chat_id,
                            text=f"You've chosen to match with people from @{domain}.\nTo change your organisation match preference go to /settings\nUse /connect to find a chat partner!")
            else:
                user_json.changeOrgPrefer(chat_id=chat_id, OrgPrefer=False)
                send_message(chat_id=chat_id,
                            text=f"You've chosen to match in the open category.\nTo change your organisation match preference go to /settings\nUse /connect to find a chat partner!")

            # Process pending referral if exists
            process_referral(chat_id)

        except Exception as e:
            log(f"Error handling organization preference for {result.get('from', {}).get('id', 'Unknown')}: {e}")

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
                            status_text += f"Refer {remaining} more users to earn VIP membership!\nClick /refer to get your referal link"
                        else:
                            status_text += "Click /refer to get your referal link"

                    send_message(chat_id=chat_id, text=status_text)
                except:
                    send_message(chat_id=chat_id, text="Your current membership: Free User")

            elif setting_type == "MatchOrg":
                domain = user_json.user_read(str(chat_id))["email"].split("@")[1]
                org_buttons = {
                    "inline_keyboard": [
                        [{"text": f"Match with people from @{domain}", "callback_data": f"org:yes"}],
                        [{"text": "Match in Open Category", "callback_data": "org:no"}]
                    ]
                }
                send_message(chat_id=chat_id,
                             text="Select your matching preference:",
                             reply_markup=org_buttons)

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
    """Handle bot commands"""
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
🤖 Welcome to GhostChat - An Anonymous Chat Bot!

Connect with random people and have anonymous conversations!

📱 Supported media types:
• Text messages
• Photos and images
• Documents and files  
• Voice messages
• Videos and GIFs
• Stickers and emojis
• Location sharing

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

            # If there's a valid referrer, store temporarily for processing after gender selection
            if referrer_id:
                temp_referral_file = f"temp_referral_{chat_id}.txt"
                with open(temp_referral_file, 'w') as f:
                    f.write(str(referrer_id))
        else:
            # User already exists, add to lobby
            send_message(text="Looking for a new partner for you\nPlease wait patiently... 🔍\nUse /disconnect to stop search", chat_id=chat_id)
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

            bot_username = "TextGhost_bot"  # Replace with your actual bot username
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

📱 Supported Media:
• Photos, Documents, Voice messages
• Videos, Stickers, Location sharing

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

📱 Supported Media Types:
• Text messages and emojis
• Photos and images (JPG, PNG)
• Documents and files (PDF, DOC, etc.)
• Voice messages and audio
• Videos and GIFs
• Stickers
• Location sharing

🔗 Referral System:
• Share your referral link with friends
• Earn VIP membership by referring 5 users
• VIP users get higher match priority

✏️ Message Editing:
• Edit your messages in Telegram
• Your partner will see edited messages
• Works for text messages

How to use:
1. Use /connect to find a chat partner
2. Start chatting with any media type
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
                text='Write your issue after "/issue" command.\n\nFor example: "/issue voice messages not working"',
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

            user_data = user_json.user_read(str(chat_id))
            send_message(text="Looking for a new partner for you\nPlease wait patiently... 🔍\nUse /disconnect to stop search", chat_id=chat_id)
            add_to_lobby(str(chat_id), user_data.get("match_org", False))
        except Exception as e:
            log(f"Error in connect command: {e}")
            send_message(text="Error connecting. Please try again later.", chat_id=chat_id)

    elif text.startswith("/disconnect"):
        reply_markup = json.dumps({
            "inline_keyboard": [[
                {
                    "text": "Fill Feedback Form",
                    "url": "https://forms.gle/yyQ9BFdEJKxNfJhA9"
                }
            ]]
        })
        try:
            if match.check_matched(chat_id):
                partner_id = match.check_matched(chat_id)
                match.unmatch(chat_id)
                send_message(
                    text="Chat ended.\nUse /connect to find a new partner!",
                    chat_id=chat_id,
                    reply_markup=reply_markup
                )
                if partner_id:
                    send_message(text="Your partner has left the chat.\nUse /connect to find a new partner!",
                                 chat_id=partner_id, reply_markup=reply_markup)

            elif lobby.is_in_lobby(chat_id=chat_id):
                lobby.remove_from_lobby(chat_id=chat_id)
                send_message(text="You have been removed from lobby.\nUse /connect to find a new partner!", chat_id=chat_id)

            else:
                send_message(text="You're not currently in a chat.\nUse /connect to find a partner!", chat_id=chat_id)
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
                    [{"text": "View your Membership Status", "callback_data": "settings:Status"}],
                    [{"text": "Change Organisation Match Preference", "callback_data": "settings:MatchOrg"}]
                ]
            }
            send_message(chat_id=chat_id, text="⚙️ Settings - Please select an option:", reply_markup=settings_buttons)
        except Exception as e:
            log(f"Error in settings: {e}")
            send_message(text="Error loading settings. Please try again.", chat_id=chat_id)