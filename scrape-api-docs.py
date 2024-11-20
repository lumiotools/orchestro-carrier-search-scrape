from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import os
import time

# Input and Output JSON files
LINKS_FILE = "api_docs_links_sheet_1.json"
OUTPUT_FILE = "api_docs_data_sheet_1.json"

options = Options()
options.add_argument("--headless")  # Run in headless mode for faster execution
driver_service = Service()
driver = webdriver.Chrome(service=driver_service, options=options)

# Initialize data storage
visited = set()  # Track visited URLs
scraped_data = []  # Store scraped data

# Load previously scraped data if resuming
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        scraped_data = json.load(f)
        visited = set(entry["url"] for entry in scraped_data)
        print(f"Resuming from {len(visited)} already scraped URLs.")


def save_to_json(data, output_file):
    """Save data to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {output_file}")


def scrape_page(url):
    """Scrape the content of a page using Selenium and store it."""
    try:
        driver.get(url)
        time.sleep(2)  # Allow time for the page to load
        soup = BeautifulSoup(driver.page_source, "html.parser")
        content = soup.get_text()

        # Append the scraped data to the list
        scraped_data.append({"url": url, "text": content.strip()})
        save_to_json(scraped_data, OUTPUT_FILE)  # Save after each page
        print(f"Scraped and saved: {url}")

    except Exception as e:
        print(f"Error scraping {url}: {e}")


def main():
    """Main function to scrape all pages."""
    if not os.path.exists(LINKS_FILE):
        print(f"Links file '{LINKS_FILE}' not found. Run 'fetch_links.py' first.")
        return

    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        links_to_scrape = json.load(f)

    final_links = []
    for company, links in links_to_scrape.items():
        final_links.extend(links)

    print(f"Total links to scrape: {len(final_links)}")

    for index, link in enumerate(final_links):
        if link in visited:
            print(f"Skipping link {index+1}/{len(final_links)}: {link}")
            continue
        if index < 0 and index >1000:
            continue
        print(f"Scraping link {index+1}/{len(final_links)}: {link}")
        if link not in visited:
            scrape_page(link)

    driver.quit()
    print("Scraping completed.")


if __name__ == "__main__":
    main()
