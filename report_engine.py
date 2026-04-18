import time
import threading

from database import get_tasks, get_user_name_from_db
from slack_handler import send_dm

# 🔥 PUT YOUR REAL SLACK USER ID HERE
ADMIN_ID = "U0ATLRLBZPV"


def start():
    print("🚀 Auto report started (every 3 mins)")

    thread = threading.Thread(target=loop)
    thread.daemon = True
    thread.start()


def loop():
    while True:
        try:
            print("⏳ Running report cycle...")

            tasks = get_tasks()

            if tasks:
                formatted = "\n".join(
                    [f"{get_user_name_from_db(t[0])} → {t[1]} → {t[3]}" for t in tasks]
                )

                report = f"""
📊 *Auto Report (Every 3 mins)*

{formatted}
"""

                print("📤 Sending DM...")

                send_dm(ADMIN_ID, report)

        except Exception as e:
            print("❌ Report error:", e)

        time.sleep(180)  # 3 minutes