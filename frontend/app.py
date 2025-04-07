import streamlit as st
import requests
import os
import re
import plotly.express as px
import datetime
import base64

def upload_page():
    st.subheader("📥 Upload PDF Files to Agent")

    uploaded_files = st.file_uploader("Choose one or more PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) ready for processing!")
        
        for uploaded_file in uploaded_files:
            with st.expander(f"📑 {uploaded_file.name}"):
                st.write(f"- *File Type:* {uploaded_file.type}")
                st.write(f"- *File Size:* {uploaded_file.size / 1024:.2f} KB")

                # Convert PDF to base64
                file_bytes = uploaded_file.read()
                encoded_pdf = base64.b64encode(file_bytes).decode("utf-8")

                # Inform user
                st.write("🔄 Sending to backend agent...")

                try:
                    response = requests.post(
                        "http://localhost:8000/rest/process_pdf",
                        json={"text": encoded_pdf, "filename": uploaded_file.name},
                        timeout=60
                    )
                    if response.status_code == 200:
                        st.success(f"✅ Agent Response: {response.json().get('text')}")
                    else:
                        st.error(f"❌ Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"🚨 Failed to contact agent: {e}")


    st.markdown("---")
    st.subheader("🗑️ Reset Project Data")

    st.info("To maintain clean and efficient operations, we only support **batch uploads** at a time.\n\n"
            "If you'd like to upload a new set of files, please reset the system to remove the existing files and embeddings.")

    # Confirm Reset Action
    confirm = st.text_input("Type `RESET` to confirm deletion of all uploads and embeddings")

    if confirm.strip().upper() == "RESET":
        if st.button("🔄 Delete All Uploads and Embeddings from Database"):
            with st.spinner("Deleting data from MongoDB..."):
                try:
                    response = requests.post("http://localhost:8005/rest/clear_all_data", json={}, timeout=30)
                    data = response.json()
                    st.write("🔍 Full Response:", data)
                    if response.status_code == 200 and data["status"] == "success":
                        st.success("✅ All documents and embeddings deleted successfully!")
                    else:
                        st.error(f"❌ Failed to delete data: {data.get('message')}")
                except Exception as e:
                    st.error(f"🚨 Error decoding response: {e}")
                    st.write("⚠️ Raw Response Text:", response.text)

def assistant_page():
    st.subheader("💬 AI Assistant")

    # Directly show the query form without checking local files
    with st.form(key="query_form"):
        user_query = st.text_input("Ask a question about your expenses:")
        submit_button = st.form_submit_button("Submit")

    if submit_button and user_query:
        st.write(f"🗨 *You asked:* {user_query}")

        # Step 1: Ask embedding agent to retrieve the closest document
        response = requests.post(
            "http://localhost:8002/rest/retrieve_closest",
            json={"query": user_query},
        )

        if response.status_code == 200:
            path = response.json().get('path')
            if not path:
                st.warning("⚠ No relevant document found.")
                return

            # Step 2: Ask query agent to extract answer from the retrieved document
            query_response = requests.post(
                "http://localhost:8001/rest/process_query",
                json={"query": user_query, "path": path},
            )

            if query_response.status_code == 200:
                answer = query_response.json().get('answer')
                st.success(f"🤖 AI Response: {answer}")
            else:
                st.error(f"❗ Failed to process your query.\nError: {query_response.text}")
        else:
            st.error(f"❗ Failed to retrieve document.\nError: {response.text}")


# === Helper to Get List of Files from MongoDB ===
def get_uploaded_files():
    try:
        response = requests.post("http://localhost:8002/rest/list_files", json={})
        if response.status_code == 200:
            return response.json().get("files", [])
        else:
            st.error(f"Failed to fetch uploaded files. Status: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return []
    

# === Charts Page ===
def charts_page():
    st.subheader("📊 Generate Charts")
    uploaded_files = get_uploaded_files()

    if uploaded_files:
        with st.form(key="chart_query_form"):
            user_query = st.text_input("Enter the prompt for the chart you want to generate:")
            submit_button = st.form_submit_button("Submit")

        if submit_button and user_query:
            st.write(f"🗨️ *You asked:* {user_query}")
            st.write("🔎 Generating chart...")

            response = requests.post(
                "http://localhost:8002/rest/retrieve_closest",
                json={"query": user_query},
            )

            if response.status_code == 200:
                path = response.json().get('path')  # e.g., 'abcd.txt'
                fetch_and_plot_chart(user_query, path, "📈 Generated Chart")
            else:
                st.error(f"❗ Failed to retrieve document path. Error: {response.text}")
    else:
        st.warning("⚠️ Please upload at least one PDF before trying to generate a chart.")


# === Chart Generator ===
def fetch_and_plot_chart(prompt, path, title):
    query_response = requests.post(
        "http://localhost:8003/rest/plot_chart",
        json={"query": prompt, "path": path},
    )
    if query_response.status_code == 200:
        answer = query_response.json().get('answer')

        # 🔍 Show raw code
        st.code(answer, language="python")

        # 🧼 Clean code
        answer = re.sub(r"^```python\s*", "", answer)
        answer = re.sub(r"\s*```$", "", answer)

        if "fig" not in answer:
            answer += "\nfig"

        local_vars = {}
        try:
            exec(answer, {"datetime": datetime, "px": px}, local_vars)
            fig = local_vars.get("fig")
            if fig:
                st.title(title)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("⚠️ No figure was found in the executed code.")
        except Exception as e:
            st.error(f"🚨 Failed to execute chart code: {e}")
    else:
        st.error(f"❗ Failed to plot the chart. Error: {query_response.text}")

# === Track Insights Page ===
def track_page():
    st.subheader("📊 Track Insights")
    uploaded_files = get_uploaded_files()

    if uploaded_files:
        selected_file = st.selectbox("Select a file to view insights:", uploaded_files)

        fetch_and_plot_chart("Generate a line plot showing trend of Balance.", selected_file, "📈 Trend of Balance in Your Account")
        fetch_and_plot_chart("Generate a bar plot showing distribution of credit and debit.", selected_file, "📊 Categorized Expenses")
        fetch_and_plot_chart("Generate a pie chart showing distribution of expenses and income.", selected_file, "🥧 Expense Distribution")
    else:
        st.warning("⚠️ Please upload at least one PDF before trying to track insights.")




def main():
    # Page Title and Styling
    st.set_page_config(page_title="Bank Statement Assistant", layout="wide")
    st.title("📄 Track Your Personal Finance Using the power of AI")

    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .sidebar .block-container {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.write("Upload your bank statements and ask questions about your expenses!")

    os.makedirs("../backend/input", exist_ok=True)

    # Sidebar Section with Cool Design
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", caption="Bank Assistant")
        st.markdown("## 🌟 Features")
        page = st.radio("🚀 Navigate to:", ["📥 Upload Bank Statements", "💬 Ask AI Questions", "📈 Generate Charts", "📊 Track Insights"])
        st.markdown("---")
        st.write("💡 Tip: Try asking questions like 'How much did I spend last month?'")

    # Navigation Logic
    if page == "📥 Upload Bank Statements":
        upload_page()
    elif page == "💬 Ask AI Questions":
        assistant_page()
    elif page == "📈 Generate Charts":
        charts_page()
    elif page == "📊 Track Insights":
        track_page()

if __name__ == "__main__":
    main()