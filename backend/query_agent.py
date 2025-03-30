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
    answer: str
 
class EmptyMessage(Model):
    pass
 
agent = Agent(name="Rest API", seed="query", port=8001, endpoint=["http://localhost:8001/submit"])

import subprocess
    
@agent.on_rest_post("/rest/process_query", Query, QueryResponse)
async def process_query(ctx: Context, req: Query) -> QueryResponse:
    ctx.logger.info(f"Processing Query: {req.query}")
    try:
        result = subprocess.run(["python", "process_query.py", req.query], capture_output=True, text=True)
        ctx.logger.info(result.stdout.strip())
        return QueryResponse(
            text=f"Successfully processed Query",
            agent_address=ctx.agent.address,
            answer=result.stdout.strip(),
            timestamp=int(time.time()),
        )
    except Exception as e:
        ctx.logger.error(f"Error processing Query: {e}")
        return Response(
            text=f"Failed to process query: {e}",
            agent_address=ctx.agent.address,
            timestamp=int(time.time()),
        )
 
if __name__ == "__main__":
    agent.run()