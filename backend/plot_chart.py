import os
import google.generativeai as genai
from google.genai import types
import sys

api_key = "AIzaSyBcK1uJUBAWaBFEjz3kKkF_V4XCdEatn_A"

def read_txt_file(file_path):
    """Read the content of a text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def query_gemini(context, query):
    """
    Generates an answer based on a query and context using the Gemini API.

    Args:
        api_key: Your Gemini API key.
        query: The user's question or request.
        context: The relevant information to use for answering the query.

    Returns:
        The generated answer as a string, or None if an error occurred.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')  # or 'gemini-pro-vision' if you need image input
        prompt = f"""
        Context: {context}

        Question: {query}
        """

        response = model.generate_content(prompt, config=types.GenerateContentConfig(system_instruction="Generate code in python using the library plotly.express as px and the final plot should be stored in variable named fig. Only write the code and nothing else."))

        return response.text

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Error: No query provided.")
        return

    # Path to the output folder
    output_folder = r"C:\Users\Siddhant\Frosthack-25\backend\output"

    file_name = sys.argv[2]  # The name of the text file to read

    txt_file = os.path.join(output_folder, file_name)

    user_query = sys.argv[1] 

    # Read the text file
    if not os.path.exists(txt_file):
        print(f"Error: {txt_file} does not exist.")
        return

    context = read_txt_file(txt_file)

    # user_query = "How much money was debited on 3 May 2018?"

    # Query Gemini
    answer = query_gemini(context, user_query)

    # Print the answer
    print(answer)

if __name__ == "__main__":
    main()