import os
import time
import re
import json
import requests
import asyncio
from typing import Any, Dict
from dotenv import load_dotenv
from uagents import Agent, Context, Model

# Load API keys
load_dotenv()
api_key = os.getenv("ASI_API_KEY")

# === Agent Models ===
class Query(Model):
    query: str
    path: str

class QueryResponse(Model):
    timestamp: int
    text: str
    agent_address: str
    answer: str

# === Define Agent ===
agent = Agent(name="Rest API", seed="query", port=8003, endpoint=["http://localhost:8003/submit"])

# === Utility Functions ===
def read_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def query_asi(ctx, context, query):
    try:
        url = "https://api.asi1.ai/v1/chat/completions"
        prompt = f"""
        Context: {context}

        Question: {query}

        Instructions: Generate code in python using the library plotly.express as px and the final plot should be stored in variable named fig. Only write the code and nothing else. Give python code only in plain text (not in any other format) with proper indentation that can be run from any other device without any modification. Do not create functions. The last line should be fig = ... and no other line. Always trim arrays to the shortest length before plotting.
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
            'Authorization': 'Bearer ' + api_key,
        }

        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            raise Exception(f"ASI API failed with status {response.status_code}: {response.text}")

    except Exception as e:
        raise Exception(f"Error during ASI API call: {e}")

def extract_python_code(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()

# === REST Handler ===
@agent.on_rest_post("/rest/plot_chart", Query, QueryResponse)
async def plot_chart(ctx: Context, req: Query) -> QueryResponse:
    ctx.logger.info(f"📊 Plotting chart for query: {req.query} on file {req.path}")
    
    try:
        output_folder = os.path.abspath("../backend/output")
        txt_file = os.path.join(output_folder, req.path)

        if not os.path.exists(txt_file):
            raise FileNotFoundError(f"{txt_file} does not exist.")

        context_data = read_txt_file(txt_file)

        # ✅ Use asyncio's executor pattern instead of ctx.run_in_executor
        loop = asyncio.get_running_loop()
        raw_answer = await loop.run_in_executor(None, query_asi, ctx, context_data, req.query)

        answer_code = extract_python_code(raw_answer)

        ctx.logger.info("✅ Chart code generated successfully")

        return QueryResponse(
            text="Successfully generated chart code.",
            agent_address=ctx.agent.address,
            answer=answer_code,
            timestamp=int(time.time()),
        )

    except Exception as e:
        ctx.logger.error(f"❌ Failed to generate chart: {e}")
        return QueryResponse(
            text=f"Failed to generate chart: {e}",
            agent_address=ctx.agent.address,
            answer="",
            timestamp=int(time.time()),
        )


# === Run the Agent ===
if __name__ == "__main__":
    agent.run()
