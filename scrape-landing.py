from extract_sheet1_data import extractSheet1Data
from extract_sheet2_data import extractSheet2Data
from llama_index.readers.web import BeautifulSoupWebReader
import json
import os


loader = BeautifulSoupWebReader()

# Combine URLs from both sheets
websiteUrls = extractSheet1Data() + extractSheet2Data()

print("Total URLs to fetch:", len(websiteUrls))

# Function to read and load existing data from data.json, or return an empty list if the file doesn't exist
def read_existing_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)  # Read and return existing JSON data
            except json.JSONDecodeError:
                return []  # Return an empty list if the file is empty or invalid
    return []

# Path to the JSON file
json_file = 'landingPagesData.json'

# Iterate over each URL and fetch the content individually
for idx, url in enumerate(websiteUrls):
    print(f"Fetching {idx + 1} of {len(websiteUrls)} documents")

    try:
        # Fetch the data from the URL
        documents = loader.load_data(urls=[url])

        # Read the existing data from data.json
        existing_data = read_existing_data(json_file)

        # Append the newly fetched document(s) to the existing data
        for doc in documents:
            document_data = {
                'text': doc.text,
                'url': url
            }
            existing_data.append(document_data)

        # Write the updated data back to the file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

        print(f"Fetched and saved {url}")

    except Exception as e:
        # Print error message and continue to the next URL
        print(f"Error occurred while fetching {url}: {e}")
        continue

print("Documents saved to landingPagesData.json")
