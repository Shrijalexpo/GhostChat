import requests
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


def edit_message(chat_id, message_id, text, reply_markup=None):
    """Edit existing message"""
    url = f"{BASE_URL}/editMessageText"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }

    if reply_markup:
        data["reply_markup"] = reply_markup

    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            log(f"Error editing message for {chat_id}: {response.text}")
        return response
    except Exception as e:
        log(f"Exception editing message for {chat_id}: {e}")
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