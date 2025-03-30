import streamlit as st
import requests
import os

def main():
    st.title("Bank Statement Upload and AI Assistant")
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.write("Upload your bank statement PDFs below and ask questions about your expenses.")

    os.makedirs("input", exist_ok=True)

    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
        for uploaded_file in uploaded_files:
            st.write("File Details:")
            st.write(f"Filename: {uploaded_file.name}")
            st.write(f"File Type: {uploaded_file.type}")
            st.write(f"File Size: {uploaded_file.size / 1024:.2f} KB")

            # Save file to local directory
            with open(f"../backend/input/{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.read())
                st.write(f"{uploaded_file.name} saved!")
            
            st.write("Calling the agent to process the file...")
            response = requests.post(
                "http://localhost:8000/rest/process_pdf",
                json={"text": f"../backend/input/{uploaded_file.name}"},  # Adjusted to send the file path
            )
            if response.status_code == 200:
                st.success(f"Agent Response: {response.json().get('text')}")
            else:
                st.error(f"Failed to process {uploaded_file.name}. Agent Response: {response.text}")

        # AI Assistant Section
        st.write("### AI Assistant")
        user_query = st.text_input("Ask a question about your expenses:")
        if user_query:
            st.write(f"You asked: {user_query}")
            st.write("AI Response: (Coming Soon)")

if __name__ == "__main__":
    main()
