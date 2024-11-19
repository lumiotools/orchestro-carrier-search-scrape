import json
import re
import os

def read_existing_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)  # Read and return existing JSON data
            except json.JSONDecodeError:
                return []  # Return an empty list if the file is empty or invalid
    return []


existing_data = read_existing_data("json/reviews_scraped_data2.json")

existing_data = [item for item in existing_data if item.get("text")]

existing_data = [item for item in existing_data if not "not found" in item.get("text").lower()]

existing_data = [item for item in existing_data if not "be the first to review" in item.get("text").lower()]

for data in existing_data:
    cleaned_text = "\n".join(
        line.strip() for line in re.sub(r'\n+', '\n', data['text']).splitlines() if line.strip()
    )
    data['text'] = cleaned_text
    
with open("json/cleaned_reviews_data2.json", 'w', encoding='utf-8') as f:
    json.dump(existing_data, f, ensure_ascii=False, indent=4)
print("Data cleaned and saved to json/cleaned_reviews_data2.json")