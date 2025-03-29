import pdfplumber
import json

def extract_table_from_pdf(pdf_path, output_json_path):
    data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                headers = table[0]  # Assuming the first row is the header
                for row in table[1:]:
                    row_data = {headers[i]: row[i] for i in range(len(headers))}
                    data.append(row_data)

    # Save to JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    print("Table extracted and saved to JSON:", output_json_path)

# Example Usage
import os

def batch_convert_pdfs_to_json(pdf_folder, output_folder):
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # List all PDF files in the folder
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    
    # Convert each PDF to JSON
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        json_path = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}.json")
        extract_table_from_pdf(pdf_path, json_path)
        print(f"Converted: {pdf_file} -> {json_path}")

# Example Usage
batch_convert_pdfs_to_json('D:\Important Documents\Placement\Projects\pathway-classifier\input', 'D:\Important Documents\Placement\Projects\pathway-classifier\data')

import os
os.environ["HF_TOKEN"] = "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"

from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
# embeddings.embed_query("Hello, world!")

splitter = CharacterTextSplitter()

host = "127.0.0.1"
port = 8666

server = VectorStoreServer.from_langchain_components(
    data, embedder=embeddings, splitter=splitter
)
server.run_server(host, port=port, with_cache=True, cache_backend=pw.persistence.Backend.filesystem("./Cache"), threaded=True)

from langchain_community.vectorstores import PathwayVectorClient

client = PathwayVectorClient(host=host, port=port)

query = "How much money did i spend on 8-02-25?"
docs = client.similarity_search(query)
print(docs)
