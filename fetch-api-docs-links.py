import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from googlesearch import search
import json
import os
import time
import re
from extract_sheet1_data import extractSheet1Data
from extract_sheet2_data import extractSheet2Data

# Input: List of company URLs
company_urls = []
for company_url in extractSheet2Data():
    company_urls.append(company_url.replace("https://", "").replace("http://", "").replace("www.", ""))
    
# Output JSON file for links
LINKS_FILE = "api_docs_links_sheet_2.json"

# Settings
MAX_DEPTH = 2  # Limit the depth of inner link crawling
# Headers to avoid being blocked
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
visited = set()  # Track visited URLs

# Load existing links if resuming
if os.path.exists(LINKS_FILE):
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        all_links = json.load(f)
        visited = set(link for company_links in all_links.values()
                      for link in company_links)
        print(f"Resuming with {len(visited)} already found links.")
else:
    all_links = {company: [] for company in company_urls}


def find_api_docs_links(company_url):
    """Find potential API documentation links using Google Search."""
    query = f"API documentation site:{company_url}"
    api_links = []
    try:
        for result in search(query, num_results=5):
            if result not in visited:
                api_links.append(result)
    except Exception as e:
        print(f"Error searching for {company_url}: {e}")
    return api_links


def get_inner_links(url, domain, depth=MAX_DEPTH, lang="en-us"):
    """Recursively find inner links on the given page, limited by depth and language."""
    if depth == 0:
        return []

    # Normalize the URL (remove fragments)
    parsed_main_url = urlparse(url)
    normalized_url = parsed_main_url._replace(fragment="", query="").geturl()

    if normalized_url in visited:
        return []

    visited.add(normalized_url)  # Add the normalized URL to visited
    inner_links = []

    # Normalize the domain for consistent comparison
    normalized_domain = domain.replace("www.", "")  # Remove 'www.' for consistency

    try:
        response = requests.get(normalized_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(normalized_url, href)  # Resolve relative URLs
            parsed_url = urlparse(full_url)

            # Normalize each link by removing its fragment
            normalized_full_url = parsed_url._replace(fragment="", query="").geturl()

            # Detect if the URL contains a language system
            has_lang = re.search(r"/[a-z]{2}-[a-z]{2}/", normalized_full_url, re.IGNORECASE)

            # Language filtering logic
            if has_lang:
                # Only include URLs with the desired language
                if f"/{lang}/" not in normalized_full_url:
                    continue
            elif normalized_domain not in parsed_url.netloc:  # Exclude other domains
                continue

            # Add the link if not visited
            if normalized_full_url not in visited:
                inner_links.append(normalized_full_url)
                inner_links.extend(get_inner_links(normalized_full_url, domain, depth - 1, lang))

    except Exception as e:
        print(f"Error crawling {url}: {e}")

    return list(set(inner_links))  # Deduplicate links



def save_links_to_json(links, output_file):
    """Save links to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=4)
    print(f"Progress saved to {output_file}")


def main():
    """Main function to fetch and save API documentation links."""
    for company in company_urls:
        if company not in all_links:
            all_links[company] = []

        print(f"Searching for API docs links for {company}...")
        domain = urlparse(f"https://{company}").netloc

        # Step 1: Get initial links from Google Search
        initial_links = find_api_docs_links(company)
        for link in initial_links:
            if link not in all_links[company]:
                all_links[company].append(link)
        save_links_to_json(all_links, LINKS_FILE)

        # Step 2: Crawl each link to find inner links
        for link in all_links[company]:
            print(f"Finding inner links for: {link}")
            inner_links = get_inner_links(link, domain, MAX_DEPTH)
            for inner_link in inner_links:
                if inner_link not in all_links[company]:
                    all_links[company].append(inner_link)
            save_links_to_json(all_links, LINKS_FILE)

    print("All links collected and saved.")


if __name__ == "__main__":
    main()
