import json
from extract_sheet1_data import extractSheet1Data
from extract_sheet2_data import extractSheet2Data

json_data = []

with open("api_docs_data.json", 'r', encoding="utf8") as f:
    json_data = json.load(f)


carrier_urls = extractSheet1Data() + extractSheet2Data()


def clean_url(url):
    url = url.replace("http://", "").replace("https://",
                                             "").replace("www.", "")
    if url.endswith("/"):
        url = url[:-1]
    return url


def find_carrier_api_docs(carrier_url):
    docs = []
    for doc in json_data:
        if carrier_url in doc["url"]:
            docs.append(doc)
    return docs


carrier_urls = [clean_url(url) for url in carrier_urls]

final_json = []

for url in carrier_urls:
    docs = find_carrier_api_docs(url)
    if len(docs) > 0:
        final_json.append({
            "carrier_url": url,
            "api_docs": docs
        })
        
with open("api_docs_data_final.json", 'w', encoding="utf8") as f:
    json.dump(final_json, f, indent=4)