from uagents import Agent, Context, Model
import time
import traceback
from db import pdf_collection, json_collection, txt_collection, embedding_collection

class DeleteRequest(Model):
    pass

class DeleteResponse(Model):
    timestamp: int
    agent_address: str
    status: str
    message: str

delete_agent = Agent(name="Delete Agent", seed="delete", port=8005, endpoint=["http://localhost:8005/submit"])

@delete_agent.on_rest_post("/rest/clear_all_data", DeleteRequest, DeleteResponse)
async def clear_all_data(ctx: Context, _: DeleteRequest) -> DeleteResponse:
    try:
        pdf_result = pdf_collection.delete_many({})
        json_result = json_collection.delete_many({})
        txt_result = txt_collection.delete_many({})
        embedding_result = embedding_collection.delete_many({})

        ctx.logger.info(f"✅ Cleared collections — PDFs: {pdf_result.deleted_count}, JSONs: {json_result.deleted_count}, TXTs: {txt_result.deleted_count}, Embeddings: {embedding_result.deleted_count}")

        return DeleteResponse(
            timestamp=int(time.time()),
            agent_address=ctx.agent.address,
            status="success",
            message="All documents and embeddings have been cleared from the database."
        )
    except Exception as e:
        err_msg = traceback.format_exc()
        ctx.logger.error(f"❌ Exception during deletion:\n{err_msg}")
        return DeleteResponse(
            timestamp=int(time.time()),
            agent_address=ctx.agent.address,
            status="error",
            message=str(e) or "Unknown error occurred"
        )

if __name__ == "__main__":
    delete_agent.run()
