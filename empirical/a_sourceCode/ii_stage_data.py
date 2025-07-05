import csv
import os
import sys
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from b_utils.helper import get_directory_name
from b_utils.logger import Logger
from a_sourceCode.i_web_scraper import *

abs_path = get_directory_name(
    "/Users/ericklopez/Desktop/django_gun/empirical/a_sourceCode"
)
inspector_gadget = Logger(abs_path)

import csv
from datetime import datetime
import os


def save_to_csv(
    business_address: str,
    reviews_data: list[dict],
    file_path: str = None,
    filename: str = None,
) -> str:
    """
    Saves scraped Google Maps data to CSV with one row per review.

    Args:
        business_address: String from get_address() (e.g., "123 Main St")
        reviews_data: List of review dictionaries from get_reviews()
        file_path: Full path to directory where file should be saved
        filename: Custom filename (optional, will auto-generate if None)

    Returns:
        str: Full path to the created CSV file

    """
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"google_maps_{timestamp}.csv"

    # Handle file path
    if file_path:
        os.makedirs(file_path, exist_ok=True)
        full_path = os.path.join(file_path, filename)
    else:
        os.makedirs("scraped_data", exist_ok=True)
        full_path = os.path.join("scraped_data", filename)

    # CSV writing
    fieldnames = [
        "business_address",
        "review_author",
        "review_date",
        "review_rating",
        "review_content",
        "category_ratings",
    ]

    with open(full_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for review in reviews_data:
            writer.writerow(
                {
                    "business_address": business_address,
                    "review_author": review.get("author", ""),
                    "review_date": parse_relative_date(review.get("date", "")),
                    "review_rating": review.get("overall_stars", ""),
                    "review_content": review.get("content", ""),
                    "category_ratings": " | ".join(review.get("category_ratings", [])),
                }
            )

    print(f"Saved {len(reviews_data)} reviews to {full_path}")
    return full_path


def main():
    # from selenium.webdriver.chrome.options import Options

    # options = Options()
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")

    # Usage (CONTEXT MANAGER)
    with webdriver.Chrome() as driver:  # Context manager for auto-cleanup
        url = "https://www.google.com/maps/place/Starbucks/@27.1323611,-80.2087961,17z/data=!3m1!4b1!4m6!3m5!1s0x88dedc112a70bb53:0x9413abc42aa43981!8m2!3d27.1323563!4d-80.2062265!16s%2Fg%2F1wt3p70p?entry=ttu&g_ep=EgoyMDI1MDYyMi4wIKXMDSoASAFQAw%3D%3D"
        expected_url = "google.com/maps/place/Starbucks"
        verify_url(driver, url, expected_url)
        address = get_address(driver, url, expected_url)
        expand_all_reviews(driver, url, expected_url)
        data = get_reviews(driver)
        save_to_csv(
            address,
            data,
            file_path="/Users/ericklopez/desktop/django_gun/empirical/f_data/raw",
            filename="starbucks_location_coveRd.csv",
        )


if __name__ == "__main__":
    main()
