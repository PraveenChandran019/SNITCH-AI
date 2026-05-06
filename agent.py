from llm import llm
from rag import store_message, retrieve_context
from database import (
    add_task,
    complete_task,
    add_user,
    get_tasks,
)
from slack_handler import get_user_name
import json


class ContextAgent:
    def prepare(self, user_id: str, message: str):
        cleaned_message = message.strip()

        store_message(cleaned_message)

        user_name = get_user_name(user_id)

        add_user(user_name)

        context = retrieve_context(cleaned_message)

        if isinstance(context, list):
            context = "\n".join(
                [doc.page_content for doc in context]
            )

        return {
            "user_name": user_name,
            "message": cleaned_message,
            "context": context
        }


class TaskReasoningAgent:
    SYSTEM_PROMPT = """
You are an expert project contribution analysis agent.

Responsibilities:
- Detect meaningful project tasks
- Identify contribution activity
- Infer task completion state
- Ignore greetings and casual chatter
- Return ONLY valid JSON

Rules:
- Extract only actionable project work
- Ignore non-technical conversation
- Infer whether work is completed, pending, or in progress
- If no task exists, return is_task=false

Output Schema:
{
  "is_task": boolean,
  "task": "string",
  "status": "pending | in_progress | completed",
  "category": "frontend/backend/debugging/deployment/documentation/general",
  "confidence": float
}
"""

    def analyze(self, user_name: str, message: str, context: str):
        prompt = f"""
Conversation Context:
{context}

Slack Message:
{message}

Contributor:
{user_name}

Think step-by-step:
1. Understand the conversational meaning
2. Detect whether project work exists
3. Infer contribution type
4. Infer completion status
5. Return structured JSON
"""

        response = llm.invoke([
            ("system", self.SYSTEM_PROMPT),
            ("human", prompt)
        ])

        try:
            content = (
                response.content
                if hasattr(response, "content")
                else response
            )

            data = json.loads(content)

            if not data.get("is_task"):
                return None

            if data.get("confidence", 0) < 0.5:
                return None

            if not data.get("task"):
                return None

            return data

        except Exception:
            return None


class ReportingAgent:
    def generate_report(self):
        tasks = get_tasks()

        if not tasks:
            return "No contributions recorded yet."

        report = ["📊 Weekly Contribution Report\n"]

        user_stats = {}

        for task in tasks:
            user = task["user"]

            if user not in user_stats:
                user_stats[user] = {
                    "completed": 0,
                    "pending": 0
                }

            if task["status"] == "completed":
                user_stats[user]["completed"] += 1
            else:
                user_stats[user]["pending"] += 1

        for user, stats in user_stats.items():
            report.append(
                f"{user}\n"
                f"Completed Tasks: {stats['completed']}\n"
                f"Pending Tasks: {stats['pending']}\n"
            )

        return "\n".join(report)


class OrchestratorAgent:
    def __init__(self):
        self.context_agent = ContextAgent()
        self.reasoning_agent = TaskReasoningAgent()
        self.reporting_agent = ReportingAgent()

    def run(self, user_id: str, message: str):
        prepared = self.context_agent.prepare(
            user_id,
            message
        )

        user_name = prepared["user_name"]
        message = prepared["message"]
        context = prepared["context"]

        if "report" in message.lower():
            return self.reporting_agent.generate_report()

        result = self.reasoning_agent.analyze(
            user_name=user_name,
            message=message,
            context=context
        )

        if not result:
            return "Message processed. No actionable task detected."

        task = result["task"]
        status = result["status"]

        add_task(user_name, task, None)

        if status == "completed":
            complete_task(user_name)

        contribution_score = 1

        if status == "completed":
            contribution_score += 4

        if result["category"] in [
            "backend",
            "deployment",
            "debugging"
        ]:
            contribution_score += 2

        return (
            f"Task recorded for {user_name}.\n"
            f"Task: {task}\n"
            f"Status: {status}\n"
            f"Category: {result['category']}\n"
            f"Confidence: {result['confidence']}\n"
            f"Contribution Score: {contribution_score}"
        )


orchestrator = OrchestratorAgent()


def run_agent(user_id: str, message: str):
    return orchestrator.run(user_id, message)
