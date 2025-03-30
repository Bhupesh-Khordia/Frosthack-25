import traceback
from uagents import Agent, Context, Protocol
import validators
from messages.requests import RagRequest
import os
# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import getpass
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import UnstructuredURLLoader
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
# from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
from ai_engine import UAgentResponse, UAgentResponseType
import nltk
from uagents.setup import fund_agent_if_low
 
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
 
 
LANGCHAIN_RAG_SEED = "SeedHaiBete"
 
agent = Agent(
    name="langchain_rag_agent",
    seed=LANGCHAIN_RAG_SEED,
    mailbox=True
)
 
fund_agent_if_low(agent.wallet.address())
 
docs_bot_protocol = Protocol("DocsBot")
 
 
PROMPT_TEMPLATE = """
Answer the question based only on the following context:
 
{context}
 
---
 
Answer the question based on the above context: {question}
"""
 
 
def create_retriever(
    ctx: Context, url: str, deep_read: bool
) -> ContextualCompressionRetriever:
    def scrape(site: str):
        if not validators.url(site):
            ctx.logger.info(f"Url {site} is not valid")
            return
 
        r = requests.get(site)
        soup = BeautifulSoup(r.text, "html.parser")
 
        parsed_url = urlparse(url)
        base_domain = parsed_url.scheme + "://" + parsed_url.netloc
 
        link_array = soup.find_all("a")
        for link in link_array:
            href: str = link.get("href", "")
            if len(href) == 0:
                continue
            current_site = f"{base_domain}{href}" if href.startswith("/") else href
            if (
                ".php" in current_site
                or "#" in current_site
                or not current_site.startswith(url)
                or current_site in urls
            ):
                continue
            urls.append(current_site)
            scrape(current_site)
 
    urls = [url]
    if deep_read:
        scrape(url)
        ctx.logger.info(f"After deep scraping - urls to parse: {urls}")
 
    try:
        if "COHERE_API_KEY" not in os.environ:
            os.environ["COHERE_API_KEY"] = getpass.getpass("Enter your Cohere API key: ")
        cohere_api_key = os.environ["COHERE_API_KEY"]

        loader = UnstructuredURLLoader(urls=urls)
        docs = loader.load_and_split()
        # db = FAISS.from_documents(docs, OpenAIEmbeddings())
        db = FAISS.from_documents(docs, HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"))
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=CohereRerank(cohere_api_key=cohere_api_key), 
            base_retriever=db.as_retriever()
        )
        return compression_retriever
    except Exception as exc:
        ctx.logger.error(f"Error happened: {exc}")
        traceback.format_exception(exc)
 
 
@docs_bot_protocol.on_message(model=RagRequest, replies={UAgentResponse})
async def answer_question(ctx: Context, sender: str, msg: RagRequest):
    ctx.logger.info(f"Received message from {sender}, session: {ctx.session}")
    ctx.logger.info(
        f"input url: {msg.url}, question: {msg.question}, is deep scraping: {msg.deep_read}"
    )
 
    parsed_url = urlparse(msg.url)
    if not parsed_url.scheme or not parsed_url.netloc:
        ctx.logger.error("invalid input url")
        await ctx.send(
            sender,
            UAgentResponse(
                message="Input url is not valid",
                type=UAgentResponseType.FINAL,
            ),
        )
        return
    base_domain = parsed_url.scheme + "://" + parsed_url.netloc
    ctx.logger.info(f"Base domain: {base_domain}")
 
    retriever = create_retriever(ctx, url=msg.url, deep_read=msg.deep_read == "yes")
 
    compressed_docs = retriever.get_relevant_documents(msg.question)
    context_text = "\n\n---\n\n".join([doc.page_content for doc in compressed_docs])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=msg.question)
 
    # model = ChatOpenAI(model="gpt-4o-mini")

    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    response = model.predict(prompt)
    ctx.logger.info(f"Response: {response}")
    await ctx.send(
        sender, UAgentResponse(message=response, type=UAgentResponseType.FINAL)
    )
 
 
agent.include(docs_bot_protocol, publish_manifest=True)
 
 
if __name__ == "__main__":
    agent.run()

