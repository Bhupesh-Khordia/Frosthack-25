import streamlit as st
import requests
import os

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
                    json={"text": file_path},
                )
                if response.status_code == 200:
                    st.success(f"🤖 Agent Response: {response.json().get('text')}")
                else:
                    st.error(f"❗ Failed to process {uploaded_file.name}. Error: {response.text}")

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
                query_response = requests.post(
                    "http://localhost:8003/rest/plot_chart",
                    json={"query": user_query, "path": path},
                )
                if query_response.status_code == 200:
                    answer = query_response.json().get('answer')
                    answer = answer[9 : -3]
                    local_vars = {}
                    exec(answer, {}, local_vars)
    
                    # Get the figure from local_vars
                    fig = local_vars.get("fig")
    
                    # Display the plot if fig exists
                    if fig:
                        st.title("📈 Generated Chart")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("No figure found in the executed code.")
                else:
                    st.error(f"❗ Failed to plot the chart. Error: {query_response.text}")
            else:
                st.error(f"❗ Failed to plot the chart. Error: {response.text}")
    else:
        st.warning("⚠️ Please upload at least one PDF before trying to generate a chart.")




def fetch_and_plot_chart(prompt, path, title):
    query_response = requests.post(
        "http://localhost:8003/rest/plot_chart",
        json={"query": prompt, "path": path},
    )
    if query_response.status_code == 200:
        answer = query_response.json().get('answer')
        answer = answer[9 : -3]
        local_vars = {}
        exec(answer, {}, local_vars)

        fig = local_vars.get("fig")

        if fig:
            st.title(title)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No figure found in the executed code.")
    else:
        st.error(f"❗ Failed to plot the chart. Error: {query_response.text}")

def track_page():
    st.subheader("📊 Track Insights")
    uploaded_files = os.listdir("../backend/input")

    if uploaded_files:
        selected_file = st.selectbox("Select a file to view insights:", uploaded_files)
        file_path = selected_file[:-4] + "_cleaned.txt"

        fetch_and_plot_chart("Generate a line plot showing trend of Balance.", file_path, "📈 Trend of Balance in Your Account")
        fetch_and_plot_chart("Generate a bar plot showing distribution of credit and debit.", file_path, "📊 Categorized Expenses")
        fetch_and_plot_chart("Generate a pie chart showing distribution of expenses and income.", file_path, "🥧 Expense Distribution")

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