from extract_sheet1_data import extractSheet1Data
from extract_sheet2_data import extractSheet2Data
from llama_index.readers.web import BeautifulSoupWebReader
import json
import os
import re

loader = BeautifulSoupWebReader()

# Combine URLs from both sheets

originalUrls = []

with open("data/audit_companies.json", "r") as f:
    data = json.load(f)
    for company in data:
        originalUrls.append(company["website"])


pagesUrls = []

commonPages = ["/services", "/pricing", "/about",
               "/blog", "/contact", "/home", "/faq",
               "/company", "/about-us", "/summary"]


for url in originalUrls:
    url = url.strip('/')
    pagesUrls.append(url)
    for page in commonPages:
        pagesUrls.append(url + page)


print("Total URLs to fetch:", len(pagesUrls))

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
# json_file = 'all_pages_data.json'
json_file = 'json/audit_companies_data.json'

# Iterate over each URL and fetch the content individually
for idx, url in enumerate(pagesUrls):
    print(f"Fetching {idx + 1} of {len(pagesUrls)} pages")

    url = re.sub(r'(?<!:)/{2,}', '/', url)

    try:
        # Fetch the data from the URL
        documents = loader.load_data(urls=[url])

        if str(documents[0].text).find("404") != -1 or str(documents[0].text).find("403") != -1 or str(documents[0].text).lower().find("not found") != -1:
            print(f"Error occurred while fetching {url}: 404")
            continue

        # Read the existing data from data.json
        existing_data = read_existing_data(json_file)

        # Append the newly fetched document(s) to the existing data
        for doc in documents:
            cleaned_text = "\n".join(
                line.strip() for line in re.sub(r'\n+', '\n', doc.text).splitlines() if line.strip()
            )
            document_data = {
                'text': cleaned_text,
                'url': url
            }
            existing_data.append(document_data)

        # Write the updated data back to the file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

        print(f"Fetched and saved {url}")

    except (json.JSONDecodeError, OSError) as e:
        # Print error message and continue to the next URL
        print(f"Error occurred while fetching {url}: {e}")
        continue
    except Exception as e:  # Catch all other exceptions
        print(f"An unexpected error occurred while fetching {url}: {e}")
        continue
    # finally:
    #     continue

print("Documents saved to ", json_file)
