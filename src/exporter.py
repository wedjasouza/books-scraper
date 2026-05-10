#!/usr/bin/env python3

"""
This module contains the function to export the books list into the specified
file format.
"""

import logging
import json
from pathlib import Path
import pandas as pd


def export(books: list[dict], output_format: str, output_file: str) -> None:
    """
    This function will export the books into the chosen output format into
    a file with the specified filename.
    :param books: A list of dictionaries.
    :param output_format: A string indicating the desired output format.
    :param output_file: A string indicating the desired output file.
    :return None:
    """

    logging.info("Saving to file...")
    if output_format == "csv":
        if not output_file.endswith(".csv"):
            output_file = output_file + ".csv"
        target_path = Path("../outputs") / output_file
        df = pd.DataFrame(books)
        df.to_csv(target_path, index=False)
    elif output_format == "json":
        if not output_file.endswith(".json"):
            output_file = output_file + ".json"
        target_path = Path("../outputs") / output_file
        with target_path.open( "w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=4)
    else:
        logging.error("Invalid format")
