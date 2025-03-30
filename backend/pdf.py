import pdfplumber
import json
import re
import os
from datetime import datetime

# --------------------------- Step 1: Extract Tables from PDFs ---------------------------

def extract_table_from_pdf(pdf_path, output_json_path):
    """Extract tables from a PDF and save as JSON."""
    data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                headers = table[0]  # Assuming the first row is the header
                for row in table[1:]:
                    row_data = {headers[i]: row[i] for i in range(len(headers))}
                    data.append(row_data)

    # Save extracted data to JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    print(f"Extracted: {pdf_path} → {output_json_path}")

# --------------------------- Step 2: Standardize JSON Date Fields ---------------------------

def parse_date(date_str):
    """Convert various date formats to 'DD-MMM-YYYY'."""
    date_formats = ["%d-%m-%y", "%d %b %Y", "%d %b\n%Y", "%d\n%b %Y", "%d/%m/%Y", "%d/%m/%y"]
    date_str = date_str.replace("\n", " ")  # Remove newlines in date strings

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%d-%b-%Y")
        except ValueError:
            continue
    return date_str  # Return as-is if no format matches

def standardize_json(file_path):
    """Standardize date fields in JSON files by detecting any key with 'date' in it."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data:
        date_keys = [key for key in entry.keys() if re.search(r"date", key, re.IGNORECASE)]  # Find all date-related keys

        new_date = None
        for key in date_keys:
            if entry.get(key):  # If the date field has a value
                new_date = parse_date(entry[key])  # Convert and standardize
                break  # Stop after finding the first valid date field

        # Remove the original date keys *after* setting the new date
        for key in date_keys:
            entry.pop(key, None)

        # Ensure 'Date' is added back if found
        if new_date:
            entry["Date"] = new_date

    # Save the cleaned JSON
    output_path = file_path.replace(".json", "_cleaned.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    # Delete the original file
    os.remove(file_path)

    print(f"Processed: {file_path} → {output_path}")

# --------------------------- Step 3: Convert JSON Files to Text Files ---------------------------

def extract_transactions(json_folder, output_text_folder):
    """Extract structured transaction summaries from JSON and save as text files in paragraph form."""
    os.makedirs(output_text_folder, exist_ok=True)

    for json_file in os.listdir(json_folder):
        if not json_file.endswith(".json"):
            continue

        json_path = os.path.join(json_folder, json_file)
        with open(json_path, "r", encoding="utf-8") as f:
            transactions = json.load(f)

        output_file = os.path.join(output_text_folder, json_file.replace(".json", ".txt"))

        with open(output_file, "w", encoding="utf-8") as out_f:
            transaction_texts = []  # Store all transactions in a list

            for entry in transactions:
                date = entry.get("Date", "Unknown Date")
                debit = str(entry.get("Debit", "0") or "0").replace("-", "0")  # Handle null values
                credit = str(entry.get("Credit", "0") or "0").replace("-", "0")
                balance = str(entry.get("Balance", "Unknown Balance"))

                transaction_text = f"On {date}, a transaction took place where Debit: {debit} Rs and Credit: {credit} Rs. The balance after this transaction was {balance} Rs."
                transaction_texts.append(transaction_text)  # Append to list

            # Join all transactions into a single paragraph
            full_text = " ".join(transaction_texts)

            # Add a final summary if transactions exist
            if transactions:
                final_balance = transactions[-1].get("Balance", "Unknown Balance")
                full_text += f" The final balance at the end of the transactions is {final_balance} Rs."

            out_f.write(full_text)  # Write the entire paragraph

        print(f"Processed: {json_file} → {output_file}")

# --------------------------- Step 4: Run the Full Pipeline ---------------------------

def batch_process_pdfs_and_json(pdf_folder, json_folder, output_text_folder):
    """Convert PDFs to JSON, clean JSON files, and extract transactions to text files."""
    
    # Ensure output folders exist
    os.makedirs(json_folder, exist_ok=True)
    os.makedirs(output_text_folder, exist_ok=True)

    # Step 1: Convert PDFs to JSON
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        json_path = os.path.join(json_folder, f"{os.path.splitext(pdf_file)[0]}.json")
        extract_table_from_pdf(pdf_path, json_path)
    
    # Step 2: Process and clean JSON files
    json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
    for json_file in json_files:
        json_path = os.path.join(json_folder, json_file)
        standardize_json(json_path)

    # Step 3: Convert JSON to Text
    extract_transactions(json_folder, output_text_folder)

# --------------------------- Export This Function ---------------------------

if __name__ == "__main__":
    pdf_folder = r"C:\Users\Siddhant\Frosthack-25\backend\input"
    json_folder = r"C:\Users\Siddhant\Frosthack-25\backend\data"
    output_text_folder = r"C:\Users\Siddhant\Frosthack-25\backend\output"

    batch_process_pdfs_and_json(pdf_folder, json_folder, output_text_folder)
