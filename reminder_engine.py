import threading
import time
from database import get_tasks
from slack_handler import send_message

CH = None

def loop():
    while True:
        tasks = get_tasks()

        for row in tasks:
            user = row[0]
            task = row[1]
            status = row[3]

            if status == "pending":
                send_message(CH, f"⏰ {user} pending → {task}")

        time.sleep(300)  # every 5 mins (reduced spam)


def start(channel):
    global CH
    CH = channel
    threading.Thread(target=loop, daemon=True).start()