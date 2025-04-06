import time
from typing import Any, Dict
from uagents import Agent, Context, Model
import os
import json
import re
import pdfplumber
from datetime import datetime

# ------------------- UAgents Setup -------------------
class Request(Model):
    text: str

class Response(Model):
    timestamp: int
    text: str
    agent_address: str

class EmptyMessage(Model):
    pass

agent = Agent(
    name="Rest API",
    seed="fetch",
    port=8000,
    endpoint=["http://localhost:8000/submit"],
    mailbox=True
)

# ------------------- PDF Processing Logic -------------------

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
    name = name.lower().strip()
    for standard_name, variations in COLUMN_MAPPINGS.items():
        if any(variant in name for variant in variations):
            return standard_name
    return name

def extract_table_from_pdf(pdf_path, output_json_path):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                headers = [map_column_name(col) for col in table[0]]
                for row in table[1:]:
                    row_data = {headers[i]: row[i] for i in range(len(headers)) if row[i]}
                    if 'amount' in row_data and 'type' in row_data:
                        if row_data['type'].strip().upper() == 'CR':
                            row_data['credit'] = row_data.pop('amount', '0')
                            row_data['debit'] = '0'
                        elif row_data['type'].strip().upper() == 'DR':
                            row_data['debit'] = row_data.pop('amount', '0')
                            row_data['credit'] = '0'
                    row_data.setdefault('debit', '0')
                    row_data.setdefault('credit', '0')
                    data.append(row_data)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def parse_date(date_str):
    date_formats = ["%d-%m-%y", "%d %b %Y", "%d %b\n%Y", "%d\n%b %Y", "%d/%m/%Y", "%d/%m/%y"]
    date_str = date_str.replace("\n", " ")
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%d-%b-%Y")
        except ValueError:
            continue
    return date_str

def standardize_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for entry in data:
        date_keys = [key for key in entry.keys() if "date" in key.lower()]
        for key in date_keys:
            if entry[key]:
                entry["Date"] = parse_date(entry[key])
                del entry[key]
    output_path = file_path.replace(".json", "_cleaned.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.remove(file_path)
    return output_path

def extract_transactions(json_file, output_text_path):
    with open(json_file, "r", encoding="utf-8") as f:
        transactions = json.load(f)
    with open(output_text_path, "w", encoding="utf-8") as out_f:
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

def process_pdf_pipeline(pdf_filename):
    input_path = os.path.join("input", pdf_filename)
    json_path = os.path.join("data", pdf_filename.replace(".pdf", ".json"))
    text_path = os.path.join("output", pdf_filename.replace(".pdf", ".txt"))

    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    extract_table_from_pdf(input_path, json_path)
    cleaned_json = standardize_json(json_path)
    extract_transactions(cleaned_json, text_path)
    return text_path

# ------------------- API Endpoint -------------------

@agent.on_rest_post("/rest/process_pdf", Request, Response)
async def process_pdf(ctx: Context, req: Request) -> Response:
    ctx.logger.info(f"Received request to process PDF: {req.text}")
    try:
        output_file = process_pdf_pipeline(req.text)
        return Response(
            text=f"Successfully processed PDF to {output_file}",
            agent_address=ctx.agent.address,
            timestamp=int(time.time()),
        )
    except Exception as e:
        ctx.logger.error(f"Error processing PDF: {e}")
        return Response(
            text=f"Failed to process {req.text}: {e}",
            agent_address=ctx.agent.address,
            timestamp=int(time.time()),
        )

# ------------------- Run Agent -------------------
if __name__ == "__main__":
    agent.run()
