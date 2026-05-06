from llm import llm
            contribution_score += 3

        else:
            contribution_score += 1

        if category in ["backend", "deployment", "debugging"]:
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

        report_lines = ["📊 Contribution Report\n"]

        for task in tasks:
            report_lines.append(
                f"User: {task['user']} | "
                f"Task: {task['task']} | "
                f"Status: {task['status']}"
            )

        return "\n".join(report_lines)


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
        monitored = self.monitoring_agent.process_event(user_id, message)

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

        is_valid = self.validation_agent.validate(extracted_data)

        if not is_valid:
            return "Message processed. No actionable task detected."

        analysis = self.analysis_agent.analyze(extracted_data)

        self.database_agent.store(user_name, extracted_data)

        return (
            f"Task recorded for {user_name}.\n"
            f"Task: {extracted_data['task']}\n"
            f"Status: {extracted_data['status']}\n"
            f"Category: {extracted_data['category']}\n"
            f"Contribution Score: {analysis['contribution_score']}"
        )


orchestrator = OrchestratorAgent()


def run_agent(user_id: str, message: str):
    return orchestrator.run(user_id, message)
