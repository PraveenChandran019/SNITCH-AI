import os
import json
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

parser = StrOutputParser()

# ---------------- EXTRACTION ----------------

extract_prompt = ChatPromptTemplate.from_template("""
You are a strict task extractor.

Message: {message}

Context:
{context}

Rules:
- Extract only actionable tasks
- Ignore greetings
- Extract deadline if present

Return ONLY JSON:
{{"task": "...", "deadline": "...", "is_task": true/false}}
""")

extract_chain = extract_prompt | llm | parser


def extract_task_llm(message, context):
    output = extract_chain.invoke({
        "message": message,
        "context": context
    })

    print("RAW LLM OUTPUT:", output)

    try:
        return json.loads(output)
    except:
        return {"is_task": False}