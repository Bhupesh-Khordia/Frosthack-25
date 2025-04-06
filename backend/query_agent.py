import time
from typing import Optional

from uagents import Agent, Context, Model

import os
import google.generativeai as genai
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ASI_API_KEY = os.getenv("ASI_API_KEY")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Folder containing text files
OUTPUT_FOLDER = r"C:\Users\Siddhant\Desktop\Frosthack-25\backend\output"

# Agent definitions
class Query(Model):
    query: str
    path: str

class QueryResponse(Model):
    timestamp: int
    text: str
    agent_address: str
    answer: Optional[str]

agent = Agent(name="Rest API", seed="query", port=8001, endpoint=["http://localhost:8001/submit"])

def read_txt_file(file_path):
    """Read the content of a text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def query_asi(context: str, query: str) -> Optional[str]:
    try:
        url = "https://api.asi1.ai/v1/chat/completions"
        prompt = f"""
        Context: {context}

        Question: {query}
        """
        payload = json.dumps({
            "model": "asi1-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "stream": False,
            "max_tokens": 8000
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + ASI_API_KEY,
        }

        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
        return f"Error from ASI API: Status Code {response.status_code}"
    except Exception as e:
        return f"Exception during ASI API call: {str(e)}"

@agent.on_rest_post("/rest/process_query", Query, QueryResponse)
async def process_query(ctx: Context, req: Query) -> QueryResponse:
    ctx.logger.info(f"Processing Query: {req.query} on file: {req.path}")
    file_path = os.path.join(OUTPUT_FOLDER, req.path)

    if not os.path.exists(file_path):
        error_msg = f"File '{req.path}' does not exist."
        ctx.logger.error(error_msg)
        return QueryResponse(
            text="File not found",
            agent_address=ctx.agent.address,
            answer=error_msg,
            timestamp=int(time.time())
        )

    context = read_txt_file(file_path)
    answer = query_asi(context, req.query)

    return QueryResponse(
        text="Query processed successfully",
        agent_address=ctx.agent.address,
        answer=answer,
        timestamp=int(time.time())
    )

if __name__ == "__main__":
    agent.run()
