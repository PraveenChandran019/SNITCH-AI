from fastapi import FastAPI, Request
from slack_handler import send_message
from agent import run_agent
from database import init_db
from report_engine import start as start_report

processed_events = set()
MAX_EVENTS = 1000  # prevent memory leak

app = FastAPI()


# ---------------- STARTUP ----------------
@app.on_event("startup")
async def startup():
    init_db()
    print("✅ Database initialized")

    # start report engine only once
    if not hasattr(app, "report_started"):
        start_report()
        app.report_started = True
        print("🚀 Auto report engine started (every 3 mins)")


# ---------------- SLACK EVENTS ----------------
@app.post("/slack/events")
async def slack_events(req: Request):

    body = await req.json()

    # Slack URL verification
    if "challenge" in body:
        return {"challenge": body["challenge"]}

    event = body.get("event", {})

    # ignore bot messages
    if event.get("bot_id") or event.get("subtype") == "bot_message":
        return {"ok": True}

    event_id = body.get("event_id")

    # prevent duplicate events
    if event_id:
        if event_id in processed_events:
            return {"ok": True}

        processed_events.add(event_id)

        # prevent memory overflow
        if len(processed_events) > MAX_EVENTS:
            processed_events.clear()

    text = event.get("text")
    user = event.get("user")
    channel = event.get("channel")

    if not text or not user or not channel:
        return {"ok": True}

    print("\n========================")
    print("USER:", user)
    print("TEXT:", text)

    try:
        response = run_agent(user, text)

        if not response:
            response = "🤖 No response generated."

    except Exception as e:
        print("❌ ERROR:", e)
        response = "⚠️ Something went wrong."

    print("AGENT RESPONSE:", response)

    send_message(channel, response)

    return {"ok": True}