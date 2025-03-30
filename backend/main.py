import os
import pathway as pw
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import PathwayVectorClient
from pathway.xpacks.llm.vector_store import VectorStoreServer
from langchain.text_splitter import CharacterTextSplitter

os.environ["HF_TOKEN"] = "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"

data = pw.io.fs.read(
    "/backend/data",
    format="binary",
    with_metadata=True,
)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
# embeddings.embed_query("Hello, world!")

splitter = CharacterTextSplitter()

host = "127.0.0.1"
port = 8666

server = VectorStoreServer.from_langchain_components(
    data, embedder=embeddings, splitter=splitter
)
server.run_server(host, port=port, with_cache=True, cache_backend=pw.persistence.Backend.filesystem("./Cache"), threaded=True)

client = PathwayVectorClient(host=host, port=port)

query = "How much money did i spend on 8-02-25?"
docs = client.similarity_search(query)
print(docs)
