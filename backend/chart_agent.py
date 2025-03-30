import time
from typing import Any, Dict
 
from uagents import Agent, Context, Model

class Query(Model):
    query: str
    path: str

class QueryResponse(Model):
    timestamp: int
    text: str
    agent_address: str
    answer: str
 
class EmptyMessage(Model):
    pass
 
agent = Agent(name="Rest API", seed="query", port=8003, endpoint=["http://localhost:8003/submit"])

import subprocess
    
@agent.on_rest_post("/rest/plot_chart", Query, QueryResponse)
async def plot_chart(ctx: Context, req: Query) -> QueryResponse:
    ctx.logger.info(f"Processing Query: {req.query}")
    try:
        result = subprocess.run(["python", "plot_chart.py", req.query, req.path], capture_output=True, text=True)
        ctx.logger.info(result.stdout.strip())
        return QueryResponse(
            text=f"Successfully plotted chart",
            agent_address=ctx.agent.address,
            answer=result.stdout.strip(),
            timestamp=int(time.time()),
        )
    except Exception as e:
        ctx.logger.error(f"Error ploting chart: {e}")
        return QueryResponse(
            text=f"Failed to plot a chart: {e}",
            agent_address=ctx.agent.address,
            answer=None,
            timestamp=int(time.time()),
        )
 
if __name__ == "__main__":
    agent.run()