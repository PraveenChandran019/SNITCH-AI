# Snitch AI — Group Accountability & Task Intelligence System

## Problem Statement

Have you ever struggled with poor team coordination or unresponsive teammates during a group project? In many academic and professional settings, it becomes difficult to track who is actually contributing and who is not. This leads to unfair evaluation, missed deadlines, and reduced overall productivity.

Snitch AI addresses this problem by monitoring group conversations, extracting actionable tasks, tracking progress, and generating detailed reports about each member’s contribution. It enables professors or managers to gain transparent insights into team performance without manually reviewing chat history.



## Overview

Snitch AI is a Slack-integrated AI system that automatically analyzes team communication, extracts tasks using LLMs, stores structured data, and generates periodic reports. It combines FastAPI, LangChain, RAG (Retrieval-Augmented Generation), and a SQL database to create a smart accountability layer on top of group chats.



## Key Features

### 1. Task Extraction

* Converts natural language messages into structured tasks
* Extracts deadlines and intent
* Ignores irrelevant messages

### 2. Task Tracking

* Stores tasks in a SQLite database
* Tracks status (pending / completed)
* Prevents duplicate entries

### 3. User Contribution Tracking

* Maps Slack user IDs to real names
* Tracks activity and task ownership
* Maintains last active timestamps

### 4. Automatic Reporting

* Sends periodic reports (every 3 minutes)
* Delivered directly to Admin (Professor / Manager)
* Displays:

  * Who is working
  * Pending tasks
  * Completed tasks

### 5. RAG-Based Memory

* Stores chat history using embeddings
* Retrieves contextual past messages
* Improves task extraction accuracy

### 6. Slack Integration

* Real-time interaction via Slack events API
* Supports:

  * Message parsing
  * Automated replies
  * Direct messaging

---

## Tech Stack

| Component    | Technology           |
| ------------ | -------------------- |
| Backend      | FastAPI              |
| LLM          | Groq (LLaMA 3.3)     |
| Framework    | LangChain            |
| Database     | SQLite               |
| Vector Store | Chroma               |
| Embeddings   | HuggingFace (MiniLM) |
| Integration  | Slack API            |
| Tunneling    | ngrok                |

---

## System Architecture

Slack → FastAPI → Agent Layer → LLM + RAG
↓
SQLite Database
↓
Report Engine (Thread)
↓
Admin (DM)

<img width="1536" height="1024" alt="ChatGPT Image Apr 19, 2026, 01_02_19 AM" src="https://github.com/user-attachments/assets/f200fe9a-5b45-4116-9d88-5219984edb74" />

<img width="1237" height="866" alt="image" src="https://github.com/user-attachments/assets/cf49b507-cf2f-4219-af33-1c5bba9abe82" />

---

## Project Structure

```
snitch-ai/
│
├── main.py               # FastAPI entry point
├── agent.py              # Core logic and orchestration
├── llm.py                # LLM chains and prompts
├── rag.py                # Vector DB and context retrieval
├── database.py           # SQLite operations
├── slack_handler.py      # Slack API interactions
├── report_engine.py      # Auto-report thread
├── .env                  # API keys
└── tasks.db              # Database file
```


---

## Setup Instructions

### 1. Clone Repository

```
git clone <repo-url>
cd snitch-ai
```

### 2. Install Dependencies

```
pip install fastapi uvicorn python-dotenv requests
pip install langchain langchain-core langchain-groq
pip install langchain-community chromadb sentence-transformers
```

### 3. Environment Variables

Create a `.env` file:

```
GROQ_API_KEY=your_groq_api_key
SLACK_BOT_TOKEN=xoxb-your-token
```

---

### 4. Run the Backend

```
uvicorn main:app --reload
```

---

### 5. Connect Slack (via ngrok)

```
ngrok http 8000
```

Use the generated URL in Slack Event Subscriptions:

```
https://<ngrok-url>/slack/events
```

---

## Usage

### Add Task

```
i will complete backend by tomorrow
```

### Mark Complete

```
i already done backend
```

### Get Report

```
report
```

---

## Example Output

### Task Added

```
Task added:
- backend
Deadline: tomorrow
```

### Report

```
Praveen C → backend → pending
John → frontend → done
```

---

## Future Enhancements

* Free-rider detection (low contribution users)
* Intelligent delay prediction
* Performance scoring system
* Alert system for inactivity
* Dashboard for professors/managers
* Multi-platform integration (Teams, Discord)

---

## Use Cases

* Academic group projects
* Startup team monitoring
* Remote team accountability
* Hackathon team tracking

---

## Conclusion

Snitch AI transforms unstructured team communication into actionable insights. By combining LLMs, RAG, and automation, it ensures accountability, improves productivity, and provides transparency in collaborative environments.

---
