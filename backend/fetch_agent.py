import time
import base64
import io
import pdfplumber
import json
from datetime import datetime, timezone  # Use timezone-aware datetime
from uagents import Agent, Context, Model
from bson.binary import Binary
from db import pdf_collection, json_collection, txt_collection

# ------------------- UAgents Setup -------------------

class Request(Model):
    text: str  # base64 encoded PDF
    filename: str  # original filename from frontend

class Response(Model):
    timestamp: int
    text: str
    agent_address: str

agent = Agent(
    name="Unified PDF Processor",
    seed="fetch",
    port=8000,
    endpoint=["http://localhost:8000/submit"],
    mailbox=True
)

# ------------------- Helpers -------------------

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

def parse_date(date_str):
    formats = ["%d-%m-%y", "%d %b %Y", "%d %b\n%Y", "%d\n%b %Y", "%d/%m/%Y", "%d/%m/%y"]
    date_str = date_str.replace("\n", " ")
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%d-%b-%Y")
        except ValueError:
            continue
    return date_str

def extract_table_from_pdf(pdf_bytes: bytes):
    data = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
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
    return data

def standardize_json(data):
    for entry in data:
        date_keys = [key for key in entry if "date" in key.lower()]
        for key in date_keys:
            if entry[key]:
                entry["Date"] = parse_date(entry[key])
                del entry[key]
    return data

def extract_transactions_text(transactions):
    transaction_texts = []
    for entry in transactions:
        date = entry.get("Date", "Unknown Date")
        debit = str(entry.get("debit", "0")).replace("-", "0")
        credit = str(entry.get("credit", "0")).replace("-", "0")
        balance = str(entry.get("balance", "Unknown Balance"))
        description = entry.get("description", "No description available")
        transaction_texts.append(
            f"On {date}, a transaction took place where Debit: {debit} Rs and Credit: {credit} Rs. "
            f"Description: {description}. The balance after this transaction was {balance} Rs."
        )
    full_text = " ".join(transaction_texts)
    if transactions:
        final_balance = transactions[-1].get("balance", "Unknown Balance")
        full_text += f" The final balance at the end of the transactions is {final_balance} Rs."
    return full_text

# ------------------- Main Pipeline -------------------

def full_pipeline(base64_pdf: str, filename: str) -> str:
    pdf_bytes = base64.b64decode(base64_pdf)
    base_filename = filename.rsplit(".", 1)[0]
    now_utc = datetime.now(timezone.utc)

    # Step 1: Store PDF
    pdf_collection.replace_one(
        {"filename": f"{base_filename}.pdf"},
        {
            "filename": f"{base_filename}.pdf",
            "content": Binary(pdf_bytes),
            "content_type": "application/pdf",
            "upload_time": now_utc
        },
        upsert=True
    )

    # Step 2: Convert to JSON
    raw_data = extract_table_from_pdf(pdf_bytes)
    json_data = standardize_json(raw_data)
    json_collection.replace_one(
        {"filename": f"{base_filename}.json"},
        {
            "filename": f"{base_filename}.json",
            "content": json_data,
            "content_type": "application/json",
            "upload_time": now_utc
        },
        upsert=True
    )

    # Step 3: Convert to Narration Text
    narration = extract_transactions_text(json_data)
    txt_collection.replace_one(
        {"filename": f"{base_filename}.txt"},
        {
            "filename": f"{base_filename}.txt",
            "content": narration,
            "content_type": "text/plain",
            "upload_time": now_utc
        },
        upsert=True
    )

    return f"✅ Successfully processed and stored {base_filename}.pdf → .json → .txt"

# ------------------- REST Endpoint -------------------

@agent.on_rest_post("/rest/process_pdf", Request, Response)
async def handle_pdf(ctx: Context, req: Request) -> Response:
    try:
        
        original_filename = req.filename  # already provided by frontend
        msg = full_pipeline(req.text, original_filename)
                
        return Response(
            timestamp=int(time.time()),
            text=msg,
            agent_address=ctx.agent.address
        )
    except Exception as e:
        ctx.logger.error(f"Error: {e}")
        return Response(
            timestamp=int(time.time()),
            text=f"❌ Failed to process: {e}",
            agent_address=ctx.agent.address
        )

# ------------------- Run Agent -------------------
if __name__ == "__main__":
    agent.run()
