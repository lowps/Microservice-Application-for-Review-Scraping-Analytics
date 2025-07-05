import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import re

BASE_DIR = Path().resolve().parent.parent


def extract_first_last(name: str) -> tuple[str, str]:
    parts = name.strip().split()
    if len(parts) >= 2:
        first_name = parts[0].title()
        last_name = parts[-1].title()
        return first_name, last_name
    elif len(parts) == 1:
        return parts[0].title(), None
    else:
        return None, None


def parse_subcategory_ratings(s):
    if not isinstance(s, str):
        return pd.Series(
            [None, None, None],
            index=["food_rating", "service_rating", "atmosphere_rating"],
        )

    food = re.search(r"Food:(\d+)", s)
    service = re.search(r"Service:(\d+)", s)
    atmosphere = re.search(r"Atmosphere:(\d+)", s)

    return pd.Series(
        [
            int(food.group(1)) if food else None,
            int(service.group(1)) if service else None,
            int(atmosphere.group(1)) if atmosphere else None,
        ],
        index=["food_rating", "service_rating", "atmosphere_rating"],
    )


def extract_address_parts(address: str) -> pd.Series:
    pattern = r"^(.*),\s*(.*),\s*([A-Z]{2})\s*(\d{5})$"
    match = re.match(pattern, address.strip()) if isinstance(address, str) else None
    if match:
        street, city, state, zip_code = match.groups()
        return pd.Series(
            {
                "street": street.strip().upper(),
                "city": city.strip().upper(),
                "state": state.strip().upper(),
                "zip": zip_code.strip(),
            }
        )
    else:
        return pd.Series({"street": None, "city": None, "state": None, "zip": None})


def main():
    BASE_DIR = Path().resolve().parent.parent
    path = "/Users/ericklopez/desktop/django_gun/empirical/f_data/processed/starbucks_location_coveRd.csv"
    df = pd.read_csv(path)
    df[["first_name", "last_name"]] = (
        df["review_author"].apply(extract_first_last).apply(pd.Series)
    )
    ratings = df["category_ratings"].apply(parse_subcategory_ratings)
    df[["food_rating", "service_rating", "atmosphere_rating"]] = ratings.astype("Int64")
    df[["street", "city", "state", "zip"]] = df["business_address"].apply(
        extract_address_parts
    )
    df.drop(
        columns=["review_author", "business_address", "category_ratings"], inplace=True
    )
    processed_file_path = "/Users/ericklopez/Desktop/django_gun/empirical/f_data/final/starbucks_location_coveRd.csv"
    df.to_csv(path_or_buf=processed_file_path)


if __name__ == "__main__":
    main()
