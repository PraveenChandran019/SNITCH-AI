import json
from database import (
    add_task, get_tasks, task_exists,
    complete_task, add_user, update_user_activity,
    get_user_name_from_db
)
from slack_handler import get_user_name
from rag import store_message, retrieve_context
from llm import extract_task_llm


def clean_task(text):
    text = text.lower()

    if "will" in text:
        text = text.split("will")[-1]

    for word in ["before", "by", "tomorrow", "today", "pm", "am"]:
        text = text.replace(word, "")

    return text.strip()


def run_agent(user, message):

    print("\n===== AGENT START =====")
    print("USER:", user)
    print("MESSAGE:", message)

    # ---------------- STORE MEMORY ----------------
    store_message(message)

    # ---------------- USER TRACKING ----------------
    name = get_user_name(user)
    add_user(user, name)
    update_user_activity(user)

    message_lower = message.lower()

    # ---------------- COMPLETE TASK ----------------
    if "done" in message_lower or "completed" in message_lower:
        complete_task(user)
        return "🎉 Task marked as completed!"

    # ---------------- REPORT ----------------
    if "report" in message_lower:
        tasks = get_tasks()

        if not tasks:
            return "📭 No tasks available."

        formatted = "\n".join(
            [f"{get_user_name_from_db(t[0])} → {t[1]} → {t[3]}" for t in tasks]
        )

        return f"📊 *Report*\n\n{formatted}"

    # ---------------- TASK EXTRACTION (FIXED) ----------------
    context = retrieve_context(message)

    data = extract_task_llm(message, context)

    print("EXTRACTED:", data)

    if data.get("is_task"):
        task = clean_task(data.get("task", message))
        deadline = data.get("deadline", "Not specified")

        if task_exists(user, task):
            return "⚠️ Task already exists"

        add_task(user, task, deadline)

        return f"✅ Task added:\n• {task}\n📅 {deadline}"

    return "🤖 Got it! No task detected."