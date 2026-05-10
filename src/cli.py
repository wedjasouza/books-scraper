#!/usr/bin/env python3

"""
This module contains the logic to process command line arguments. It orchestrates
the logic from the other modules.
"""


import argparse
import sys
import logging
from scraper import scraper
from exporter import export


# create parser
parser = argparse.ArgumentParser(description = "Scrape books pages")

# add arguments to parser
parser.add_argument("--output-file", dest="output_file", type = str, required=True,
                    help = "The output file")
parser.add_argument("-v", "--verbose", action = "store_true", help = "Enable verbose output")
parser.add_argument("--categories", nargs="*", default = None,
                    help = "The category to scrape from (enclose multiword categories"
                           " in double quotes)")
parser.add_argument("--format", dest="output_format", type = str, default = "csv",
                    help = "The output format (csv [default], json)")
parser.add_argument("--limit", type = int, default = 1000,
                    help = "The number of books to scrape per category if categories"
                           " provided otherwise will be total number of books to scrape")

args = parser.parse_args()

# enable verbose output
if args.verbose:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def main():
    """
    This is the main function. It takes the command line arguments and calls the required
    functions accordingly.
    :return None:
    """
    output_file = args.output_file
    output_format = args.output_format
    categories = args.categories
    limit = args.limit
    if not output_format in ["csv", "json"]:
        logging.error("Invalid format. Please choose from: csv, json")
        sys.exit(1)
    books = scraper(limit, categories)
    export(books, output_format, output_file)


if __name__ == "__main__":
    main()
