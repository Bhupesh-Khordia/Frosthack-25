import pdfplumber
import json
import re
import os
from datetime import datetime

# --------------------------- Step 1: Extract Tables from PDFs ---------------------------

COLUMN_MAPPINGS = {
    "balance": ["balance", "closing balance", "final balance"],
    "debit": ["debit", "withdrawal", "amount debited"],
    "credit": ["credit", "deposit", "amount credited"],
    "date": ["date", "transaction date", "posted date"],
    "amount": ["amount", "transaction amount"],
    "type": ["type", "transaction type"],
    "description": ["description", "remarks", "narration", "details", "reference"]
}

def map_column_name(name):
    """Map extracted column names to standard names."""
    name = name.lower().strip()
    for standard_name, variations in COLUMN_MAPPINGS.items():
        if any(variant in name for variant in variations):
            return standard_name
    return name  # Return original if no match found

def extract_table_from_pdf(pdf_path, output_json_path):
    """Extract tables from a PDF and save as JSON with dynamic column mapping."""
    data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                headers = [map_column_name(col) for col in table[0]]  # Map column names
                for row in table[1:]:
                    row_data = {headers[i]: row[i] for i in range(len(headers)) if row[i]}
                    
                    # Handle cases where 'Amount' and 'Type' columns are used
                    if 'amount' in row_data and 'type' in row_data:
                        if row_data['type'].strip().upper() == 'CR':
                            row_data['credit'] = row_data.pop('amount', '0')
                            row_data['debit'] = '0'
                        elif row_data['type'].strip().upper() == 'DR':
                            row_data['debit'] = row_data.pop('amount', '0')
                            row_data['credit'] = '0'
                    
                    # Ensure debit and credit exist in each row
                    row_data.setdefault('debit', '0')
                    row_data.setdefault('credit', '0')
                    
                    data.append(row_data)

    # Save extracted data to JSON
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
    print(f"Extracted: {pdf_path} → {output_json_path}")

# --------------------------- Step 2: Standardize JSON Date Fields ---------------------------

def parse_date(date_str):
    """Convert various date formats to 'DD-MMM-YYYY'."""
    date_formats = ["%d-%m-%y", "%d %b %Y", "%d %b\n%Y", "%d\n%b %Y", "%d/%m/%Y", "%d/%m/%y"]
    date_str = date_str.replace("\n", " ")  # Remove newlines

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%d-%b-%Y")
        except ValueError:
            continue
    return date_str  # Return as-is if no format matches

def standardize_json(file_path):
    """Standardize date fields in JSON files and ensure correct column mappings."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for entry in data:
        # Normalize date fields
        date_keys = [key for key in entry.keys() if "date" in key.lower()]
        for key in date_keys:
            if entry[key]:
                entry["Date"] = parse_date(entry[key])
                del entry[key]  # Remove original key

    output_path = file_path.replace(".json", "_cleaned.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.remove(file_path)
    print(f"Processed: {file_path} → {output_path}")

# --------------------------- Step 3: Convert JSON Files to Text Files ---------------------------

def extract_transactions(json_folder, output_text_folder):
    """Extract structured transaction summaries from JSON and save as text files."""
    os.makedirs(output_text_folder, exist_ok=True)

    for json_file in os.listdir(json_folder):
        if not json_file.endswith(".json"):
            continue

        json_path = os.path.join(json_folder, json_file)
        with open(json_path, "r", encoding="utf-8") as f:
            transactions = json.load(f)

        output_file = os.path.join(output_text_folder, json_file.replace(".json", ".txt"))

        with open(output_file, "w", encoding="utf-8") as out_f:
            transaction_texts = []
            for entry in transactions:
                date = entry.get("Date", "Unknown Date")
                debit = str(entry.get("debit", "0") or "0").replace("-", "0")
                credit = str(entry.get("credit", "0") or "0").replace("-", "0")
                balance = str(entry.get("balance", "Unknown Balance"))
                description = entry.get("description", "No description available")
                
                transaction_text = (
                    f"On {date}, a transaction took place where Debit: {debit} Rs and Credit: {credit} Rs. "
                    f"Description: {description}. The balance after this transaction was {balance} Rs. "
                )
                transaction_texts.append(transaction_text)
            
            full_text = " ".join(transaction_texts)
            if transactions:
                final_balance = transactions[-1].get("balance", "Unknown Balance")
                full_text += f" The final balance at the end of the transactions is {final_balance} Rs."
            
            out_f.write(full_text)
        print(f"Processed: {json_file} → {output_file}")

# --------------------------- Step 4: Run the Full Pipeline ---------------------------

def batch_process_pdfs_and_json(pdf_folder, json_folder, output_text_folder):
    """Convert PDFs to JSON, clean JSON files, and extract transactions to text files."""
    os.makedirs(json_folder, exist_ok=True)
    os.makedirs(output_text_folder, exist_ok=True)

    # Step 1: Convert PDFs to JSON
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            json_path = os.path.join(json_folder, f"{os.path.splitext(pdf_file)[0]}.json")
            extract_table_from_pdf(pdf_path, json_path)

    # Step 2: Process and clean JSON files
    for json_file in os.listdir(json_folder):
        if json_file.endswith('.json'):
            json_path = os.path.join(json_folder, json_file)
            standardize_json(json_path)

    # Step 3: Convert JSON to Text
    extract_transactions(json_folder, output_text_folder)

if __name__ == "__main__":
    batch_process_pdfs_and_json("input", "data", "output")
