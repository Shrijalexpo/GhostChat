
import requests
import os
import root_json
from log import log

BASE_URL = root_json.root_read("BASE_URL")

def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    """Send message to user"""
    url = f"{BASE_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = reply_markup
    if parse_mode:
        data["parse_mode"] = parse_mode

    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            log(f"Error sending message to {chat_id}: {response.text}")
        return response
    except Exception as e:
        log(f"Exception sending message to {chat_id}: {e}")
        return None

def send_photo(chat_id, photo, caption=None, reply_markup=None):
    """Send photo to user"""
    url = f"{BASE_URL}/sendPhoto"

    # Check if photo is a file path or file_id
    if os.path.isfile(str(photo)):
        # Upload file
        with open(photo, 'rb') as f:
            files = {'photo': f}
            data = {'chat_id': chat_id}
            if caption:
                data['caption'] = caption
            if reply_markup:
                data['reply_markup'] = reply_markup

            try:
                response = requests.post(url, data=data, files=files)
                if response.status_code != 200:
                    log(f"Error sending photo to {chat_id}: {response.text}")
                return response
            except Exception as e:
                log(f"Exception sending photo to {chat_id}: {e}")
                return None
    else:
        # Use file_id or URL
        data = {
            "chat_id": chat_id,
            "photo": photo
        }
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = reply_markup

        try:
            response = requests.post(url, json=data)
            if response.status_code != 200:
                log(f"Error sending photo to {chat_id}: {response.text}")
            return response
        except Exception as e:
            log(f"Exception sending photo to {chat_id}: {e}")
            return None

def send_document(chat_id, document, caption=None, reply_markup=None):
    """Send document to user"""
    url = f"{BASE_URL}/sendDocument"

    # Check if document is a file path or file_id
    if os.path.isfile(str(document)):
        # Upload file
        with open(document, 'rb') as f:
            files = {'document': f}
            data = {'chat_id': chat_id}
            if caption:
                data['caption'] = caption
            if reply_markup:
                data['reply_markup'] = reply_markup

            try:
                response = requests.post(url, data=data, files=files)
                if response.status_code != 200:
                    log(f"Error sending document to {chat_id}: {response.text}")
                return response
            except Exception as e:
                log(f"Exception sending document to {chat_id}: {e}")
                return None
    else:
        # Use file_id or URL
        data = {
            "chat_id": chat_id,
            "document": document
        }
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = reply_markup

        try:
            response = requests.post(url, json=data)
            if response.status_code != 200:
                log(f"Error sending document to {chat_id}: {response.text}")
            return response
        except Exception as e:
            log(f"Exception sending document to {chat_id}: {e}")
            return None

def send_voice(chat_id, voice, caption=None, duration=None, reply_markup=None):
    """Send voice message to user"""
    url = f"{BASE_URL}/sendVoice"

    # Check if voice is a file path or file_id
    if os.path.isfile(str(voice)):
        # Upload file
        with open(voice, 'rb') as f:
            files = {'voice': f}
            data = {'chat_id': chat_id}
            if caption:
                data['caption'] = caption
            if duration:
                data['duration'] = duration
            if reply_markup:
                data['reply_markup'] = reply_markup

            try:
                response = requests.post(url, data=data, files=files)
                if response.status_code != 200:
                    log(f"Error sending voice to {chat_id}: {response.text}")
                return response
            except Exception as e:
                log(f"Exception sending voice to {chat_id}: {e}")
                return None
    else:
        # Use file_id or URL
        data = {
            "chat_id": chat_id,
            "voice": voice
        }
        if caption:
            data["caption"] = caption
        if duration:
            data["duration"] = duration
        if reply_markup:
            data["reply_markup"] = reply_markup

        try:
            response = requests.post(url, json=data)
            if response.status_code != 200:
                log(f"Error sending voice to {chat_id}: {response.text}")
            return response
        except Exception as e:
            log(f"Exception sending voice to {chat_id}: {e}")
            return None

def get_file(file_id):
    """Get file information from Telegram"""
    url = f"{BASE_URL}/getFile"
    data = {"file_id": file_id}

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            if result['ok']:
                return result['result']
        log(f"Error getting file info for {file_id}: {response.text}")
        return None
    except Exception as e:
        log(f"Exception getting file info for {file_id}: {e}")
        return None

def download_file(file_path, save_path):
    """Download file from Telegram servers"""
    # Extract bot token from BASE_URL
    bot_token = BASE_URL.split('/bot')[1]
    download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"

    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as f:
                f.write(response.content)
            log(f"File downloaded successfully: {save_path}")
            return save_path
        else:
            log(f"Error downloading file: {response.status_code}")
            return None
    except Exception as e:
        log(f"Exception downloading file: {e}")
        return None

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode=None):
    """Edit existing message"""
    url = f"{BASE_URL}/editMessageText"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = reply_markup
    if parse_mode:
        data["parse_mode"] = parse_mode

    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            log(f"Error editing message for {chat_id}: {response.text}")
        return response
    except Exception as e:
        log(f"Exception editing message for {chat_id}: {e}")
        return None

def edit_message_caption(chat_id, message_id, caption, reply_markup=None, parse_mode=None):
    """Edit message caption for media messages"""
    url = f"{BASE_URL}/editMessageCaption"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "caption": caption
    }

    if reply_markup:
        data["reply_markup"] = reply_markup
    if parse_mode:
        data["parse_mode"] = parse_mode

    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            log(f"Error editing message caption for {chat_id}: {response.text}")
        return response
    except Exception as e:
        log(f"Exception editing message caption for {chat_id}: {e}")
        return None

def answer_callback_query(callback_query_id, text=None, show_alert=False):
    """Answer callback query"""
    url = f"{BASE_URL}/answerCallbackQuery"
    data = {
        "callback_query_id": callback_query_id,
        "show_alert": show_alert
    }

    if text:
        data["text"] = text

    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            log(f"Error answering callback query: {response.text}")
        return response
    except Exception as e:
        log(f"Exception answering callback query: {e}")
        return None

def forward_message(chat_id, from_chat_id, message_id):
    """Forward message to another chat"""
    url = f"{BASE_URL}/forwardMessage"
    data = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            log(f"Error forwarding message: {response.text}")
        return response
    except Exception as e:
        log(f"Exception forwarding message: {e}")
        return None

def copy_message(chat_id, from_chat_id, message_id, caption=None):
    """Copy message to another chat (without forward header)"""
    url = f"{BASE_URL}/copyMessage"
    data = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    }

    if caption:
        data["caption"] = caption

    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            log(f"Error copying message: {response.text}")
        return response
    except Exception as e:
        log(f"Exception copying message: {e}")
        return None