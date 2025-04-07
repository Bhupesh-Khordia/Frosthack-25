# FrostHack 2025 - Real-time Personal Finance Tracker By Pathway & FetchAI

---

## 📌 Overview
Welcome to our **Real-time Personal Finance Tracker** project for FrostHack 2025! This project is designed to help users manage and query financial data effectively. The system processes bank statements in PDF format, extracts relevant financial data, and allows users to query this data using natural language. The architecture integrates multiple components to provide a seamless experience, including data extraction, embedding storage, query processing, and visualization.

---

## 📸 Screenshots

Here are some screenshots of the application in action:

### PDF Upload Page
![PDF Upload Page](screenshots/home_page.png)

### AI Chat
![AI Chat](screenshots/ai_chat.png)

### Generate Chart Using AI
![Generate Chart Using AI](screenshots/generate_chart_ai.png)

### Plots of Insights
![Plots of Insights](screenshots/plots.png)

---

## Live Agents on AgentVerse

- **PDF Upload + Narration Generator**  
  [View Agent](https://agentverse.ai/agents/details/agent1q0r7qpp84vv7n5m7hszp3uyy6vdnzx279s808he5vhf9un3k8zcpzpzp89k/profile)

- **Query Handler + Context Retriever**  
  [View Agent](https://agentverse.ai/agents/details/agent1q0z395082guwatyr5eul9quxmvd8q5v9fceeemlzvakkdzz0vkhs227q2qc/profile)

- **Chart Generator (Day-wise Breakdown)**  
  [View Agent](https://agentverse.ai/agents/details/agent1qtheaw4fsctn7mgjtt6lh5tv5zpvs97evj3539wagetdvm28vx48v4ltxgx/profile)

- **Finance Insights Engine**  
  [View Agent](https://agentverse.ai/agents/details/agent1qv9knjh8jpzhtc4llcm6qau4gzezu8038u24lfpr5lg2sgvy5pf0u3v2t0f/profile)

- **Delete Files From Database Agent**  
  [View Agent](https://agentverse.ai/agents/details/agent1qwgeaveflephkuu282sammqmf03yh4pmfwe6z58uf966gf5mzh54cctz6zy/profile)

---

### How It Works

1. **PDF Processing**  
   - Users upload their bank statements in PDF format via a **Streamlit web app**.  
   - A Fetch.ai agent receives the file, decodes the base64 content, and uses `pdfplumber` to extract tables and transaction details.  
   - The parsed content is converted into structured JSON and narrated text for downstream processing.

2. **Embedding and Storage**  
   - The narrated text is chunked and embedded using **HuggingFace sentence-transformers**.  
   - Embeddings, along with metadata, are stored in a **MongoDB Atlas** database.  
   - A **custom FAISS index** is used for efficient document similarity search.

3. **Query Processing**  
   - Users ask questions about their financial data directly through the web interface.  
   - The system performs:
     - **Retrieval**: Finds the most relevant document chunks using the FAISS index.  
     - **Answer Generation**: The retrieved content and query are sent to **Fetch.ai's ASI (Artificial Superintelligence Interface)**, which leverages powerful LLMs like Google Gemini to generate context-aware responses.

4. **Visualization**  
   - Users can request day-wise expense breakdowns and other financial visualizations.  
   - A separate agent sends prompts to **ASI**, which returns Python code to dynamically generate interactive **Plotly** charts.

---

### Tech Stack

- **Frontend**: Streamlit — for real-time file uploads, queries, and chart rendering.  
- **Backend**: Python — handles parsing, chunking, embeddings, vector search, and chart execution.  
- **Database**: MongoDB Atlas — used to store PDFs, parsed JSON, narrated TXT, and embeddings.  
- **AI Interface**: **Fetch.ai’s ASI** — routes prompts to advanced LLMs (e.g., Google Gemini) for query answering and code generation.  
- **Vector Search**: FAISS — for similarity-based retrieval of relevant document chunks.  
- **Agents & APIs**: Fetch.ai UAgents — for hosting modular RESTful agents on **AgentVerse**, each handling specific backend tasks like PDF parsing, querying, and chart generation.



## 🛠 Running the Project Locally

### ✅ Prerequisites
Make sure you have the following installed:
- Python (>=3.8)
- pip

### 📥 Installation Steps
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Bhupesh-Khordia/Frosthack-25.git
   ```
2. **Install Dependencies:**
   ```bash
   pip install langchain langchain_community pdfplumber faiss-cpu google.generativeai google.genai uagents streamlit plotly sentence-transformers pymongo
   pip install -qU langchain_huggingface
   ```
3. **Create a `.env` file:**
      Create a `.env` file in the root directory of the project and add your Gemini API Key to it:
      ```env
      # API keys
      ASI_API_KEY=your_asi_api_key

      #MONGODB
      MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.n2g4kia.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

      ```
      Replace `your_asi_api_key` with your actual asi key and `mongodb_uri` with your own mongodb_uri
4. **Run all agents in separate terminals:**
   ```bash
   cd backend
   python run fetch_agent.py
   python run embedding_agent.py
   python run query_agent.py
   python run chart_agent.py
   python run delete_agent.py
   ```
6. **Run your app:**
   ```bash
   cd ..
   cd frontend
   streamlit run app.py
   ```

## ✍️ Created By
This project was created by **Team KamandNET2.0** as part of the FrostHack 2025 hackathon. Our team is passionate about leveraging cutting-edge technologies to solve real-world problems. 
### Team Members:
- **Siddhant Shah**
- **Anshul Mendiratta**
- **Bhupesh Yadav**
