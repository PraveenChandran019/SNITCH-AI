import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("SLACK_BOT_TOKEN")


# ------------------------
# SEND MESSAGE (CHANNEL)
# ------------------------
def send_message(channel, text):
    url = "https://slack.com/api/chat.postMessage"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "channel": channel,
        "text": text
    }

    res = requests.post(url, headers=headers, json=data).json()

    if not res.get("ok"):
        print("❌ Send message error:", res)


# ------------------------
# GET USER NAME
# ------------------------
def get_user_name(user_id):
    url = "https://slack.com/api/users.info"

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    params = {"user": user_id}

    res = requests.get(url, headers=headers, params=params).json()

    if res.get("ok"):
        return res["user"]["real_name"]

    print("❌ Get user name error:", res)
    return user_id


# ------------------------
# GET USER ID BY NAME
# ------------------------
def get_user_id_by_name(target_name):
    url = "https://slack.com/api/users.list"

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    res = requests.get(url, headers=headers).json()

    if not res.get("ok"):
        print("❌ User list error:", res)
        return None

    for user in res["members"]:
        if not user.get("deleted") and user.get("real_name") == target_name:
            return user["id"]

    print("❌ Admin not found:", target_name)
    return None


# ------------------------
# SEND DM
# ------------------------
def send_dm(user_id, text):
    # Open DM channel
    url = "https://slack.com/api/conversations.open"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    data = {"users": user_id}

    res = requests.post(url, headers=headers, json=data).json()

    if not res.get("ok"):
        print("❌ DM open error:", res)
        return

    channel_id = res["channel"]["id"]

    # Send message
    url = "https://slack.com/api/chat.postMessage"

    data = {
        "channel": channel_id,
        "text": text
    }

    res = requests.post(url, headers=headers, json=data).json()

    if not res.get("ok"):
        print("❌ DM send error:", res)