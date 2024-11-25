from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import os
from urllib.parse import urlparse
from extract_sheet1_data import extractSheet1Data
from extract_sheet2_data import extractSheet2Data
import time


def clean_url(url):
    """
    Clean a URL by removing the protocol, pathnames, and trailing slashes, leaving only the domain.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    if not domain:
        domain = url.split('/')[0]

    domain = domain.replace("www.", "")

    return domain


def initialize_browser():
    """
    Initialize and return a Selenium WebDriver instance with log suppression.
    """
    chrome_options = Options()
    # Uncomment to run in headless mode
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")  # Suppress logs
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-logging"])
    service = Service()  # Replace with your chromedriver path
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def google_search_selenium(driver, query, num_results=5):
    """
    Perform a Google search using Selenium and return a list of result links.
    """
    # Navigate to Google
    driver.get(f"https://www.google.com/search?q={query}&num={num_results}")

    # Wait for the page to load
    time.sleep(5)

    # Extract links using the same logic as with BeautifulSoup
    links = []
    try:
        result_elements = driver.find_elements(By.XPATH, "//a[@href]")
        for element in result_elements:
            href = element.get_attribute("href")
            if href and "https://" in href and not "#" in href and not "google" in href:
                links.append(href)
    except Exception as e:
        print(f"Error extracting links: {e}")

    return links[:num_results]  # Limit the number of links


def extract_text_from_url(driver, url):
    """
    Visit a URL using Selenium, extract all the visible text, and return it.
    """
    try:
        driver.get(url)
        time.sleep(2)  # Wait for the page to load
        # Extract the visible text
        text = driver.find_element(By.TAG_NAME, "body").text
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from {url}: {e}")
        return ""


def save_results_incrementally(carrier, article, output_file="results.json"):
    """
    Save the results incrementally to a JSON file after each link is processed.
    """
    if os.path.exists(output_file):
        # Load existing data
        with open(output_file, "r") as f:
            results = json.load(f)
    else:
        results = []

    # Check if carrier already exists
    carrier_found = False
    for result in results:
        if result["carrier"] == carrier:
            # Append only unique articles
            existing_urls = {article["url"] for article in result["articles"]}
            if article["url"] not in existing_urls:
                result["articles"].append(article)
            carrier_found = True
            break

    # If carrier doesn't exist, add a new entry
    if not carrier_found:
        results.append({
            "carrier": carrier,
            "articles": [article]
        })

    # Save back to the file
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)


def carrier_already_processed(carrier, output_file="results.json"):
    """
    Check if a carrier has already been processed by looking into the JSON file.
    """
    if not os.path.exists(output_file):
        return False

    with open(output_file, "r") as f:
        results = json.load(f)

    for result in results:
        if result["carrier"] == carrier and len(result["articles"]) == 10:
            return True

    return False


def process_carriers(carriers, num_results=5, output_file="results.json", start_index=0):
    """
    Process each carrier, extract text from articles, and save results incrementally.
    """
    # Initialize the browser once
    driver = initialize_browser()

    total_carriers = len(carriers)  # Total number of carriers

    try:
        for idx, carrier_url in enumerate(carriers[start_index:], start=start_index):
            carrier = clean_url(carrier_url)

            # Skip carriers already processed
            if carrier_already_processed(carrier, output_file):
                print(f"Skipping already processed carrier: {
                      carrier} ({idx + 1}/{total_carriers})")
                continue

            query = f'("optimizing shipping rates" OR "reduce shipping costs" OR "logistics efficiency") AND ("{carrier}" OR {
                carrier}) site:.com -filetype:pdf -filetype:doc -filetype:ppt -site:youtube.com -site:wikipedia.org'
            links = google_search_selenium(driver, query, num_results)

            total_links = len(links)
            for link_idx, link in enumerate(links, start=1):
                # Extract text from the link
                text = extract_text_from_url(driver, link)
                if text:  # Only save non-empty text
                    article = {"url": link, "text": text}
                    save_results_incrementally(carrier, article, output_file)
                    print(f"Saved article for carrier: {carrier} ({
                          idx + 1}/{total_carriers}), Link: {link_idx}/{total_links}")
    finally:
        driver.quit()


# List of carrier URLs
carriers = extractSheet1Data() + extractSheet2Data()

# Process carriers and save results incrementally
process_carriers(carriers, num_results=10,
                 output_file="carriers-rate-negotiation.json", start_index=0)
