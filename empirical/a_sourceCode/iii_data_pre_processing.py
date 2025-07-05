import os
import sys
import pandas as pd
import numpy as np
import re


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from b_utils.logger import Logger
from b_utils.helper import get_directory_name

absolute_path = "django_gun/empirical/a_sourceCode"
inspector_gadget = get_directory_name(absolute_path)
inspector_gadget = Logger(inspector_gadget)


def csv_to_df(abs_path: str) -> pd.DataFrame:

    if not abs_path.lower().endswith("csv"):
        inspector_gadget.get_log().warning(
            f"csv_to_df() unsuccessful. The file at {absolute_path} is not a .csv file."
        )
        return None

    try:
        df = pd.read_csv(abs_path)
        return df
    except Exception as e:
        inspector_gadget.get_log().error(f"Failed to read CSV file at {abs_path}: {e}")
        return None


def remove_alphabetic_chars(df: pd.DataFrame, *target_cols: str) -> pd.DataFrame:

    try:
        for col in target_cols:
            df[col] = df[col].str.replace("[a-zA-Z]", "", regex=True).astype(int)
        return df
    except Exception as e:
        inspector_gadget.get_log().warning(
            f"remove_alphabetic_chars() failed for columns:{target_cols}; {e}"
        )
        return None


def remove_pattern_from_columns(
    df: pd.DataFrame, pattern: str, *target_cols: str
) -> pd.DataFrame:
    try:
        for col in target_cols:
            if col in df.columns:
                df[col] = df[col].str.replace(pattern, "", regex=True)
            else:
                inspector_gadget.get_log().warning(
                    f"{col} not found in DataFrame {df} columns."
                )
        return df
    except Exception as e:
        inspector_gadget.get_log().error(f"remove_pattern_from_columns() failed; {e}")
        return None


def remove_emojis(df: pd.DataFrame, *target_cols: str) -> pd.DataFrame:
    """
    Removes ALL Unicode emojis from specified columns in a DataFrame.

    Args:
        df: Input DataFrame
        *target_cols: Column names to process (default: all string columns)

    Returns:
        pd.DataFrame: Copy of DataFrame with emojis removed
    """
    # Get all known emoji Unicode codes
    all_emoji_regex = _get_complete_emoji_regex()

    # Default to all string columns if none specified
    cols_to_clean = (
        target_cols
        if target_cols
        else [col for col in df.columns if pd.api.types.is_string_dtype(df[col])]
    )

    df_clean = df.copy()
    for col in cols_to_clean:
        df_clean[col] = (
            df_clean[col].astype(str).apply(lambda x: all_emoji_regex.sub("", x))
        )

    return df_clean


def _get_complete_emoji_regex():
    """Builds a regex pattern matching all known emojis"""
    # Base emoji ranges (covers most standard emojis)
    base_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # Emoticons
        "\U0001f300-\U0001f5ff"  # Symbols & pictographs
        "\U0001f680-\U0001f6ff"  # Transport & map symbols
        "\U0001f700-\U0001f77f"  # Alchemical symbols
        "\U0001f780-\U0001f7ff"  # Geometric Shapes Extended
        "\U0001f800-\U0001f8ff"  # Supplemental Arrows-C
        "\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
        "\U0001fa00-\U0001fa6f"  # Chess Symbols
        "\U0001fa70-\U0001faff"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027b0"  # Dingbats
        "\U000024c2-\U0001f251"  # Enclosed characters
        "\U0001f004-\U0001f0cf"  # Additional symbols
        "\U0001f170-\U0001f251"  # Enclosed alphanumeric supplement
        "]",
        re.UNICODE,
    )

    # Zero-width joiner sequences (e.g., skin tone modifiers)
    zwj_pattern = re.compile(
        r"\u200d[\U0001F3FB-\U0001F3FF]|"  # Skin tones
        r"[\U0001F3FB-\U0001F3FF]"  # Standalone skin tones
    )

    # Combined pattern
    return re.compile(f"({base_pattern.pattern}|{zwj_pattern.pattern})", re.UNICODE)


def df_to_list_dict_values(df: pd.DataFrame) -> list[dict]:

    if not isinstance(
        pd.DataFrame
    ):  # Use isinstance() for type checking instead of type() because type() checks for exact types and does not handle inheritance well. And isinstance() checks if object is an instance of a specified class or a subclass.
        inspector_gadget.get_log().warning(
            f"You must provide a DataFrame for df_to_list_dict_value() function."
        )
        return None
    else:
        df = df.to_dict(orient="records")
        return df


def main():
    path = "/Users/ericklopez/Desktop/django_gun/empirical/f_data/raw/starbucks_location_coveRd.csv"
    df = csv_to_df(path)
    df = remove_emojis(df, "review_content")
    processed_file_path = "/Users/ericklopez/Desktop/django_gun/empirical/f_data/processed/starbucks_location_coveRd.csv"
    df.to_csv(path_or_buf=processed_file_path)


if __name__ == "__main__":
    main()
