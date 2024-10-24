from llama_index.core import VectorStoreIndex, Document
import json
from dotenv import load_dotenv

load_dotenv()

data = []

with open('landingPagesData.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

documents = []
for entry in data:
    # Create a Document with 'text' as content, and 'extra_info' like URL
    document = Document(text=entry['text'],
                        extra_info={"url": entry['url']})
    documents.append(document)

# Create the index using from_documents with a proper list of Document objects
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

while True:
    query = input("\n\nEnter your query: ")
    if (query == 'exit'):
        break
    response = query_engine.query(query)
    sources = []
    for node in response.source_nodes:
        sources.append({"url": node.metadata["url"], "score": node.score})

    print("\nResponse: "+str(response))
    print("\nSources: " + str(sources))
