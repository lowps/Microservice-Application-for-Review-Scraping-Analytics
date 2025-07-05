import sys
import os
import traceback
from contextlib import contextmanager
import time
from bs4 import BeautifulSoup
from typing import Iterable, Tuple, List
from datetime import datetime, timedelta
import re

# ----
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from b_utils.helper import get_directory_name
from b_utils.logger import Logger

abs_path = get_directory_name(
    "/Users/ericklopez/Desktop/django_gun/empirical/a_sourceCode"
)
inspector_gadget = Logger(abs_path)


def verify_url(driver, url: str, expected_url: str) -> str:
    """Verify current URL matches expected pattern.

    Args:
        driver: Pre-initialized WebDriver
        url: URL to load
        verify_url: Expected URL pattern

    Returns:
        Verified URL

    Raises:
        AssertionError: If URL verification fails
    """
    driver.get(url)
    current_url = driver.current_url.lower()

    patterns = [
        f"https://www.{expected_url.lower()}",
        f"http://www.{expected_url.lower()}",
        f"https://{expected_url.lower()}",
        f"http://{expected_url.lower()}",
    ]

    if not any(current_url.startswith(p) for p in patterns):
        raise AssertionError(
            f"URL verification failed. Expected start: {expected_url}\n"
            f"Actual URL: {current_url}"
        )
    return current_url


def get_address(driver, url: str, expected_url: str) -> str:
    """Get address from Google Maps page."""
    verify_url(driver, url, expected_url)

    # ==========Click Overview Button==========
    try:
        overview_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[aria-label^="Overview"]')
            )
        )
        overview_button.click()
        print("location data found!")
    except Exception as e:
        print(f"Overview button not found, error: {e}")
        inspector_gadget.get_log().warning(f"Overview button not found, error: {e}")

    # ==========Get Address==========
    try:
        address_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'button[aria-label^="Address:"] div.Io6YTe')
            )
        )

        address = address_element.text
        inspector_gadget.get_log().info(f"Address recorded: {address}")
        print(f"Address: {address}")
    except Exception as e:
        print(f"Address Not Found, error: {e}")

    return address


def snap_to_top_of_page(driver):
    """Returns to Top of Page"""
    # Snap to top
    scrollable_div = driver.find_element(
        By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf"
    )
    driver.execute_script("arguments[0].scrollTop = 0", scrollable_div)
    time.sleep(2)
    print("Snaped to Top of Page Complete.")


def expand_all_reviews(driver, url: str, expected_url: str, max_attempts=30):
    """Automatically scrolls through and expands all Google Maps reviews.

    Continuously scrolls to the bottom of the reviews container, clicking all
    "See more" buttons to reveal full review text.

    Args:
        driver (webdriver): Selenium WebDriver instance
        max_attempts (int): Maximum scroll attempts before stopping (default: 30)

    Raises:
        TimeoutException: If critical elements aren't found within wait time
        WebDriverException: For general Selenium-related errors

    Notes:
        - Requires being on a Google Maps location page with reviews loaded
        - Designed to work with Google Maps' dynamic review loading system
        - Includes automatic loading spinner detection
    """

    verify_url(driver, url, expected_url)

    # ==========Click Reviews Button==========
    try:
        overview_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[aria-label^="Reviews"]')
            )
        )
        overview_button.click()
        time.sleep(3)
        print("Reviews button clicked!")
    except Exception as e:
        print(f"Could not click Reviews button, error: {e}")

    # ==========Scroll Logic==========

    scrollable_div = driver.find_element(
        By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf"
    )
    last_height = driver.execute_script(
        "return arguments[0].scrollHeight", scrollable_div
    )
    loading_circle_selector = 'div[aria-label="Loading..."]'
    consecutive_no_loads = 0
    max_consecutive_no_loads = 3  # Adjust based on network speed

    while True:
        # Scroll to bottom
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div
        )
        time.sleep(2)

        # Check for loading indicator
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, loading_circle_selector)
                )
            )
            print("Loading detected, waiting...")
            time.sleep(3)  # Extra wait for loading to complete
            consecutive_no_loads = 0
        except:
            consecutive_no_loads += 1
            print(
                f"No loading detected ({consecutive_no_loads}/{max_consecutive_no_loads})"
            )

        # Click all "See more" buttons
        more_buttons = driver.find_elements(
            By.CSS_SELECTOR, 'button[aria-label^="See more"]'
        )

        for btn in more_buttons:
            try:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", btn
                )
                ActionChains(driver).move_to_element(btn).pause(0.5).click().perform()
                print("Expanded review text")
                time.sleep(0.3)

            except Exception as e:
                print(f"Couldn't click button: {str(e)}")
                continue

        # Check if we've reached the end
        new_height = driver.execute_script(
            "return arguments[0].scrollHeight", scrollable_div
        )
        if new_height == last_height:
            if consecutive_no_loads >= max_consecutive_no_loads:
                print("No new content loaded - ending scroll")
                break
        else:
            last_height = new_height
            consecutive_no_loads = 0

        # Safety check
        max_attempts -= 1
        if max_attempts <= 0:
            print("Reached maximum scroll attempts")
            break

    print("Finished scrolling through all available reviews")
    return snap_to_top_of_page(driver)


def get_reviews(driver) -> List[dict]:

    # Snap back to top
    scrollable_div = driver.find_element(
        By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf"
    )
    driver.execute_script("arguments[0].scrollTop = 0", scrollable_div)
    time.sleep(2)  # Allow UI to settle

    # Get all review elements
    reviews = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.jftiEf"))
    )
    print(f"Found {len(reviews)} reviews")

    # Extract data from each review
    all_reviews_data = []
    for review in reviews:

        # Scroll each review into view to ensure full rendering
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", review)
        time.sleep(0.3)

        # Parse
        soup = BeautifulSoup(review.get_attribute("outerHTML"), "html.parser")

        review_data = {
            "author": (
                soup.select_one("div.d4r55").text
                if soup.select_one("div.d4r55")
                else None
            ),
            "overall_stars": len(
                soup.select('span[aria-hidden="true"].hCCjke.elGi1d')
            ),  # Count filled stars
            "date": (
                parse_relative_date(soup.select_one("span.rsqaWe").text)
                if soup.select_one("span.rsqaWe")
                else None
            ),
            "content": (
                soup.select_one("span.wiI7pd").text
                if soup.select_one("span.wiI7pd")
                else None
            ),
            "category_ratings": [],
        }

        # Extract category ratings if they exist
        rating_divs = soup.select("div.PBK6be")
        for div in rating_divs:
            rating_text = div.get_text(strip=True)
            if ":" in rating_text:  # Basic validation for category:rating format
                review_data["category_ratings"].append(rating_text)
        all_reviews_data.append(review_data)

    return all_reviews_data


def parse_relative_date(relative_date: str) -> str:
    """Convert Google Maps relative dates to YYYY-MM-DD format.

    Args:
        relative_date: String like "3 months ago", "a year ago", etc.

    Returns:
        Date string in YYYY-MM-DD format (or original string if conversion fails)
    """
    today = datetime.now()

    try:
        # Handle "a month ago" -> "1 month ago"
        normalized = relative_date.lower().replace("a ", "1 ")

        # Extract number and unit
        match = re.search(r"(\d+)\s+(year|month|day|week)s?", normalized)
        if not match:
            return relative_date  # Return original if pattern doesn't match

        num, unit = int(match.group(1)), match.group(2)

        # Calculate timedelta
        if unit == "day":
            delta = timedelta(days=num)
        elif unit == "week":
            delta = timedelta(weeks=num)
        elif unit == "month":
            delta = timedelta(days=num * 30)  # Approximate
        elif unit == "year":
            delta = timedelta(days=num * 365)  # Approximate

        actual_date = today - delta
        return actual_date.strftime("%Y-%m-%d")

    except Exception:
        return relative_date  # Fallback to original string


def parse_data_to_list(
    target: Iterable[str], **kwargs: str
) -> Tuple[List[str], List[str]]:
    # Default value
    start_tag = kwargs.get("start_tag", '<span class="wiI7pd">')
    # Default value
    end_tag = kwargs.get("end_tag", "</span>")

    start_tag_2 = kwargs.get("ratings_start_tag_2", 'class="DU9Pgb"><span aria-label="')
    end_tag_2 = kwargs.get("ratings_end_tag_2", '"')

    # Initialize an empty list to hold the extracted texts
    list_holding_parsed_data_1 = []
    list_holding_parsed_data_2 = []
    # Start position for the search
    current_position = 0

    try:
        while True:
            start_index = target.find(start_tag, current_position)
            if start_index == -1:  # If no more spans are found, break
                break

            # Adjust start_index to the start of the text after the start_tag
            start_index += len(start_tag)

            end_index = target.find(end_tag, start_index)
            if end_index == -1:  # If no end_tag is found, break
                break

            # Extract the text and add it to the list
            review_text = target[start_index:end_index].strip()

            list_holding_parsed_data_1.append(review_text)

            # Extract data to 2nd empty list starts here:
            start_index_2 = target.find(start_tag_2, current_position)
            if start_index_2 == -1:
                list_holding_parsed_data_2.append(None)
            else:
                start_index_2 += len(start_tag_2)
                end_index_2 = target.find(end_tag_2, start_index_2)
                star_int = target[start_index_2:end_index_2].strip()
                list_holding_parsed_data_2.append(star_int)

            # Update current_position to search for the next span
            current_position = end_index + len(end_tag)

    except Exception as e:
        print(f"input variable is not a str object; {e}")

    total = len(list_holding_parsed_data_1)
    print(f"Total comments parsed {total}")
    return list_holding_parsed_data_1, list_holding_parsed_data_2


def main():
    pass


if __name__ == "__main__":
    main()
