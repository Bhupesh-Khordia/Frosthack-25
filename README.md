# FrostHack - Finance Tracker

## � Team: [KamandNET2.0]

## 📌 Overview
Welcome to our **Finance Tracker** project for FrostHack! This project is designed to help users manage and query financial data effectively. We utilize **Pathway RAG** to store vector embeddings of financial data extracted from PDFs and retrieve the most relevant document based on user queries. The next steps involve integrating **Fetch.AI** to answer specific queries from these PDFs and developing a **Streamlit web app** for user interaction.

## 🚀 Current Progress
We have successfully implemented the **Pathway RAG** system using **LangChain**, which allows us to store financial document embeddings and retrieve the most similar PDF based on a given query.

### 🔜 Next Steps:
1. Integrate **Fetch.AI** to extract answers from retrieved PDFs.
2. Develop a **Streamlit web app** to provide a user-friendly interface.

---

## 🛠 Running the Project Locally

### ✅ Prerequisites
Make sure you have the following installed:
- Python (>=3.8)
- pip

### 📥 Installation Steps
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Bhupesh-Khordia/Frosthack-25.git
   cd Frosthack-25
   cd backend
   ```
2. **Install Dependencies:**
   ```bash
   pip install langchain langchain_community pathway[xpack-llm-docs] pdfplumber
   pip install -qU langchain_huggingface
   ```

3. **Adjust paths**
   Adjust folder path in `pdf.py`

4. **Run the Pathway RAG Implementation:**
   ```bash
   First, load the bank data that you want to test in input folder. Then run the following:
   python pdf.py
   python main.py
   ```