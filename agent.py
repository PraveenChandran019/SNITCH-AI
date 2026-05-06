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


class MonitoringAgent:
    def process_event(self, user_id: str, message: str):
        return {
            "user_id": user_id,
            "message": message.strip()
        }


class RetrievalAgent:
    def retrieve(self, message: str):
        context = retrieve_context(message)

        if isinstance(context, list):
            return "\n".join(
                [doc.page_content for doc in context]
            )

        return context


class TaskExtractionAgent:
    SYSTEM_PROMPT = """
You are an expert project task extraction agent.

Your responsibilities:
- Identify actionable project tasks
- Identify contribution activity
- Detect completion status
- Detect deadlines if mentioned
- Ignore greetings and casual conversation
- Return ONLY valid JSON

Rules:
- Extract only meaningful technical/project tasks
- Ignore messages like 'hi', 'lol', 'okay', 'thanks'
- Detect whether task is completed, pending, or in-progress
- If no task exists, return is_task=false

Output Schema:
{
  "is_task": boolean,
  "task": "string",
  "status": "pending | in_progress | completed",
  "deadline": "string or null",
  "category": "frontend/backend/debugging/deployment/documentation/general",
  "confidence": float
}
"""

    def extract(self, user_name: str, message: str, context: str):
        prompt = f"""
Conversation Context:
{context}

Slack Message:
{message}

Contributor:
{user_name}

Think step-by-step:
1. Understand the conversational meaning
2. Identify whether a project task exists
3. Detect ownership and contribution type
4. Infer task status
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

            return json.loads(content)

        except Exception:
            return {
                "is_task": False,
                "task": None,
                "status": "unknown",
                "deadline": None,
                "category": "general",
                "confidence": 0.0
            }


class ValidationAgent:
    def validate(self, extracted_data: dict):
        if not extracted_data.get("is_task"):
            return False

        task = extracted_data.get("task")

        if not task:
            return False

        if len(task.strip()) < 3:
            return False

        confidence = extracted_data.get("confidence", 0)

        if confidence < 0.5:
            return False

        return True


class ContributionAnalysisAgent:
    def analyze(self, extracted_data: dict):
        contribution_score = 0

        status = extracted_data.get("status")
        category = extracted_data.get("category")

        if status == "completed":
            contribution_score += 5

        elif status == "in_progress":
            contribution_score += 3

        else:
            contribution_score += 1

        if category in [
            "backend",
            "deployment",
            "debugging"
        ]:
            contribution_score += 2

        return {
            "contribution_score": contribution_score
        }


class DatabaseAgent:
    def store(self, user_name: str, extracted_data: dict):
        task = extracted_data.get("task")
        deadline = extracted_data.get("deadline")
        status = extracted_data.get("status")

        add_task(user_name, task, deadline)

        if status == "completed":
            complete_task(user_name)


class ReportingAgent:
    def generate_report(self):
        tasks = get_tasks()

        if not tasks:
            return "No contributions recorded yet."

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

        report = ["📊 Weekly Contribution Report\n"]

        for user, stats in user_stats.items():
            report.append(
                f"{user}\n"
                f"Completed Tasks: {stats['completed']}\n"
                f"Pending Tasks: {stats['pending']}\n"
            )

        return "\n".join(report)


class OrchestratorAgent:
    def __init__(self):
        self.monitoring_agent = MonitoringAgent()
        self.retrieval_agent = RetrievalAgent()
        self.extraction_agent = TaskExtractionAgent()
        self.validation_agent = ValidationAgent()
        self.analysis_agent = ContributionAnalysisAgent()
        self.database_agent = DatabaseAgent()
        self.reporting_agent = ReportingAgent()

    def run(self, user_id: str, message: str):
        monitored = self.monitoring_agent.process_event(
            user_id,
            message
        )

        message = monitored["message"]

        store_message(message)

        user_name = get_user_name(user_id)

        add_user(user_name)

        if "report" in message.lower():
            return self.reporting_agent.generate_report()

        context = self.retrieval_agent.retrieve(message)

        extracted_data = self.extraction_agent.extract(
            user_name=user_name,
            message=message,
            context=context
        )

        is_valid = self.validation_agent.validate(
            extracted_data
        )

        if not is_valid:
            return (
                "Message processed. "
                "No actionable task detected."
            )

        analysis = self.analysis_agent.analyze(
            extracted_data
        )

        self.database_agent.store(
            user_name,
            extracted_data
        )

        return (
            f"Task recorded for {user_name}.\n"
            f"Task: {extracted_data['task']}\n"
            f"Status: {extracted_data['status']}\n"
            f"Category: {extracted_data['category']}\n"
            f"Confidence: {extracted_data['confidence']}\n"
            f"Contribution Score: "
            f"{analysis['contribution_score']}"
        )


orchestrator = OrchestratorAgent()


def run_agent(user_id: str, message: str):
    return orchestrator.run(user_id, message)
