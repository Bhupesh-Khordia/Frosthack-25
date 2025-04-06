import streamlit as st
import requests
import os
import re
import plotly.express as px
import datetime

def upload_page():
    st.subheader("📥 Upload PDF Files")
    uploaded_files = st.file_uploader("Choose one or more PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
        for uploaded_file in uploaded_files:
            with st.expander(f"📑 {uploaded_file.name}"):
                st.write(f"- *File Type:* {uploaded_file.type}")
                st.write(f"- *File Size:* {uploaded_file.size / 1024:.2f} KB")

                # Save the file
                file_path = f"../backend/input/{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())
                    st.write(f"✅ *{uploaded_file.name}* saved successfully!")

                # Process with the AI Agent
                st.write("🔎 Processing file...")
                response = requests.post(
                    "http://localhost:8000/rest/process_pdf",
                    json={"text": uploaded_file.name},  # ✅ FIXED!
                )
                if response.status_code == 200:
                    st.success(f"🤖 Agent Response: {response.json().get('text')}")
                else:
                    st.error(f"❗ Failed to process {uploaded_file.name}. Error: {response.text}")
    # Delete Uploads Button
    st.markdown("---")
    if st.button("🗑️ Delete Uploads"):
        import glob

        folders_to_clear = ["../backend/data", "../backend/input", "../backend/output"]
        files_to_delete = []

        for folder in folders_to_clear:
            files_to_delete += glob.glob(f"{folder}/*")

        # Add .txt and .index files in backend folder
        files_to_delete += glob.glob("../backend/*.txt")
        files_to_delete += glob.glob("../backend/*.index")

        deleted_files = []
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
            except Exception as e:
                st.error(f"❌ Error deleting {file_path}: {e}")

        st.success(f"✅ Deleted {len(deleted_files)} files successfully!")

def assistant_page():
    st.subheader("💬 AI Assistant")
    uploaded_files = os.listdir("../backend/input")
    if uploaded_files:
        with st.form(key="query_form"):
            user_query = st.text_input("Ask a question about your expenses:")
            submit_button = st.form_submit_button("Submit")
        if submit_button and user_query:
            st.write(f"🗨 *You asked:* {user_query}")
            response = requests.post(
                "http://localhost:8002/rest/retrieve_closest",
                json={"query": user_query},
            )
            if response.status_code == 200:
                path = response.json().get('path')
                query_response = requests.post(
                    "http://localhost:8001/rest/process_query",
                    json={"query": user_query, "path": path},
                )
                if query_response.status_code == 200:
                    answer = query_response.json().get('answer')
                    st.success(f"🤖 AI Response: {answer}")
                else:
                    st.error(f"❗ Failed to process your query. Error: {query_response.text}")
            else:
                st.error(f"❗ Failed to process your query. Error: {response.text}")
                
    else:
        st.warning("⚠ Please upload at least one PDF before asking a question.")



# New Charts Page
def charts_page():
    st.subheader("📊 Generate Charts")
    uploaded_files = os.listdir("../backend/input")
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
                path = response.json().get('path')
                fetch_and_plot_chart(user_query, path, "📈 Generated Chart")
            else:
                st.error(f"❗ Failed to retrieve document path. Error: {response.text}")
    else:
        st.warning("⚠️ Please upload at least one PDF before trying to generate a chart.")



def fetch_and_plot_chart(prompt, path, title):
    query_response = requests.post(
        "http://localhost:8003/rest/plot_chart",
        json={"query": prompt, "path": path},
    )
    if query_response.status_code == 200:
        answer = query_response.json().get('answer')

        # 🔍 Show raw code
        st.code(answer, language="python")

        # 🧼 Remove markdown wrappers if any
        answer = re.sub(r"^```python\s*", "", answer)
        answer = re.sub(r"\s*```$", "", answer)

        # 🛠️ Ensure 'fig' is returned if not explicitly assigned
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


def track_page():
    st.subheader("📊 Track Insights")
    input_folder = "../backend/input"
    output_folder = "../backend/output"

    uploaded_files = os.listdir(input_folder)

    if uploaded_files:
        selected_file = st.selectbox("Select a file to view insights:", uploaded_files)
        base_name = os.path.splitext(selected_file)[0]
        file_path = f"{base_name}.txt"  # ✅ This matches what you save in output/
        full_output_path = os.path.join(output_folder, file_path)

        if os.path.exists(full_output_path):
            fetch_and_plot_chart("Generate a line plot showing trend of Balance.", file_path, "📈 Trend of Balance in Your Account")
            fetch_and_plot_chart("Generate a bar plot showing distribution of credit and debit.", file_path, "📊 Categorized Expenses")
            fetch_and_plot_chart("Generate a pie chart showing distribution of expenses and income.", file_path, "🥧 Expense Distribution")
        else:
            st.warning(f"⚠️ The file `{file_path}` does not exist in the output folder.\nPlease process the PDF first.")
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