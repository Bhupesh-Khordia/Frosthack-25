import streamlit as st


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

    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
        for uploaded_file in uploaded_files:
            st.write("File Details:")
            st.write(f"Filename: {uploaded_file.name}")
            st.write(f"File Type: {uploaded_file.type}")
            st.write(f"File Size: {uploaded_file.size / 1024:.2f} KB")

            # Save file to local directory
            with open(f"input/{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.read())
                st.write(f"{uploaded_file.name} saved!")

        # AI Assistant Section
        st.write("### AI Assistant")
        user_query = st.text_input("Ask a question about your expenses:")
        if user_query:
            st.write(f"You asked: {user_query}")
            st.write("AI Response: (Coming Soon)")


if __name__ == "__main__":
    main()
