import json
import re
import os
from datetime import datetime

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

    # Save the cleaned JSON in the same folder, replacing the old file
    output_path = file_path.replace(".json", "_cleaned.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    # Delete the original file
    os.remove(file_path)

    print(f"Processed: {file_path} → {output_path}")

def process_all_json_files(data_folder):
    """Find and process all JSON files in the given folder."""
    for filename in os.listdir(data_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(data_folder, filename)
            standardize_json(file_path)

# Automatically process all JSON files in the "data" folder
data_folder = r"C:/Users/Siddhant/Frosthack-25/backend/data"
process_all_json_files(data_folder)
