import time
from typing import Any, Dict
 
from uagents import Agent, Context, Model

class Query(Model):
    query: str

class PathResponse(Model):
    timestamp: int
    text: str
    agent_address: str
    path: str
 
class EmptyMessage(Model):
    pass
 
agent = Agent(name="Rest API", seed="embed", port=8002, endpoint=["http://localhost:8002/submit"])

import subprocess
    
@agent.on_rest_post("/rest/retrieve_closest", Query, PathResponse)
async def retrieve_closest(ctx: Context, req: Query) -> PathResponse:
    ctx.logger.info(f"Retrieving closest statement for the query: {req.query}")
    try:
        result = subprocess.run(["python", "main.py", req.query], capture_output=True, text=True)
        ctx.logger.info(result.stdout.strip())
        if(result.stdout.strip() == ""):
            return PathResponse(
                text=f"Query not found in the documents",
                agent_address=ctx.agent.address,
                path=None,
                timestamp=int(time.time()),
            )
        return PathResponse(
            text=f"Retrieved closest statement successfully",
            agent_address=ctx.agent.address,
            path=result.stdout.strip(),
            timestamp=int(time.time()),
        )
    except Exception as e:
        ctx.logger.error(f"Error retrieving closest statement: {e}")
        return PathResponse(
            text=f"An error occured: {e}",
            agent_address=ctx.agent.address,
            path=None,
            timestamp=int(time.time()),
        )
 
if __name__ == "__main__":
    agent.run()
