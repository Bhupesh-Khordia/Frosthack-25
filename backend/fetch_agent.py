import time
from typing import Any, Dict
 
from uagents import Agent, Context, Model
 
class Request(Model):
    text: str

class Response(Model):
    timestamp: int
    text: str
    agent_address: str

class EmptyMessage(Model):
    pass
 
agent = Agent(name="Rest API", seed="fetch", port=8000, endpoint=["http://localhost:8000/submit"], mailbox=True)

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
     
if __name__ == "__main__":
    agent.run()