from extract_sheet1_data import extractSheet1Data
from extract_sheet2_data import extractSheet2Data
from bs4 import BeautifulSoup
import requests
import json
import os


# Combine URLs from both sheets
originalUrls = extractSheet1Data() + extractSheet2Data()

baseUrl = "https://www.trustpilot.com/review/"

pagesUrls = []


for url in originalUrls:
    url = url.strip('/').replace("https://", "").replace("http://", "")
    pagesUrls.append(baseUrl+url)
    pagesUrls.append(baseUrl+url+"?page=2")
    pagesUrls.append(baseUrl+url+"?page=3")


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
json_file = 'json/structured_reviews_scraped_data.json'

# Iterate over each URL and fetch the content individually
for idx, url in enumerate(pagesUrls):
    
    print(f"Fetching {idx + 1} of {len(pagesUrls)} pages")

    try:
        # Fetch the data from the URL
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        reviews_data = []
        review_cards = soup.find_all(
            'article', class_='styles_reviewCard__hcAvl')

        for review in review_cards:
            # Extract reviewer name
            reviewer_name_tag = review.find(
                'span', {'data-consumer-name-typography': 'true'})
            reviewer_name = reviewer_name_tag.text.strip() if reviewer_name_tag else "Unknown"

            # Extract reviewer country
            country_tag = review.find(
                'span', {'data-consumer-country-typography': 'true'})
            reviewer_country = country_tag.text.strip() if country_tag else "Unknown"

            # Extract review rating
            rating_tag = review.find(
                'div', {'data-service-review-rating': True})
            rating = rating_tag['data-service-review-rating'] if rating_tag else "Not rated"

            # Extract review date
            date_tag = review.find(
                'time', {'data-service-review-date-time-ago': 'true'})
            review_date = date_tag['datetime'] if date_tag else "Unknown"

            # Extract review title
            title_tag = review.find(
                'h2', {'data-service-review-title-typography': 'true'})
            review_title = title_tag.text.strip() if title_tag else "No title"

            # Extract review content
            content_tag = review.find(
                'p', {'data-service-review-text-typography': 'true'})
            review_content = content_tag.text.strip() if content_tag else "No content"

            # Extract date of experience (if available)
            experience_date_tag = review.find(
                'p', {'data-service-review-date-of-experience-typography': 'true'})
            experience_date = experience_date_tag.text.split(
                ":")[-1].strip() if experience_date_tag else "Not specified"

            # Extract review link
            link_tag = review.find(
                'a', {'data-review-title-typography': 'true'})
            review_link = "https://www.trustpilot.com" + \
                link_tag['href'] if link_tag else "No link"

            # Append extracted data to reviews_data list
            reviews_data.append({
                "carrier": url.replace(baseUrl, "").split("?")[0],
                "reviewer_name": reviewer_name,
                "reviewer_country": reviewer_country,
                "rating": rating,
                "review_date": review_date,
                "review_title": review_title,
                "review_content": review_content,
                "experience_date": experience_date,
                "review_link": review_link
            })

        existing_data = read_existing_data(json_file)
        existing_data.extend(reviews_data)

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=4)

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

print("Documents saved to json/structured_reviews_scraped_data.json")
