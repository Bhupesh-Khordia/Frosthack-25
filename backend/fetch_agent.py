import time
from typing import Any, Dict
 
from uagents import Agent, Context, Model
 
class Request(Model):
    text: str

class Query(Model):
    query: str
 
class Response(Model):
    timestamp: int
    text: str
    agent_address: str

class QueryResponse(Model):
    timestamp: int
    text: str
    agent_address: str
    response: str
 
class EmptyMessage(Model):
    pass
 
agent = Agent(name="Rest API", seed="fetch", port=8000, endpoint=["http://localhost:8000/submit"])

import subprocess

@agent.on_rest_post("/rest/process_pdf", Request, Response)
async def process_pdf(ctx: Context, req: Request) -> Response:
    ctx.logger.info(f"Processing PDF: {req.text}")
    try:
        # Call pdf.py with the uploaded file path
        subprocess.run(["python", "pdf.py", req.text], check=True)
        return Response(
            text=f"Successfully processed {req.text}",
            agent_address=ctx.agent.address,
            timestamp=int(time.time()),
        )
    except Exception as e:
        ctx.logger.error(f"Error processing PDF: {e}")
        return Response(
            text=f"Failed to process {req.text}: {e}",
            agent_address=ctx.agent.address,
            timestamp=int(time.time()),
        )
    
@agent.on_rest_post("/rest/process_query", Query, Response)
async def process_query(ctx: Context, req: Query) -> Response:
    ctx.logger.info(f"Processing Query: {req.query}")
    try:
        # Call pdf.py with the uploaded file path
        result = subprocess.run(["python", "process_query.py", req.query], capture_output=True, text=True)
        ctx.logger.info(result)
        return Response(
            text=f"Successfully processed Query",
            # response=result.stdout.strip(),
            agent_address=ctx.agent.address,
            timestamp=int(time.time()),
        )
    except Exception as e:
        ctx.logger.error(f"Error processing Query: {e}")
        return Response(
            text=f"Failed to process query: {e}",
            agent_address=ctx.agent.address,
            timestamp=int(time.time()),
        )
 
@agent.on_rest_get("/rest/get", Response)
async def handle_get(ctx: Context) -> Dict[str, Any]:
    ctx.logger.info("Received GET request")
    return {
        "timestamp": int(time.time()),
        "text": "Hello from the GET handler!",
        "agent_address": ctx.agent.address,
    }
 
@agent.on_rest_post("/rest/post", Request, Response)
async def handle_post(ctx: Context, req: Request) -> Response:
    ctx.logger.info("Received POST request")
    return Response(
        text=f"Received: {req.text}",
        agent_address=ctx.agent.address,
        timestamp=int(time.time()),
    )
 
if __name__ == "__main__":
    agent.run()