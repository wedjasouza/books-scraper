#!/usr/bin/env python3

"""
This module provides parsing functions for book data processing.

Functions:
- get_category_url_list: Gets a full list of all available category URLs.
- convert_category: Formats category strings into a usable format.
- match_url: Ensures the category matches the corresponding URL.
- get_category_urls: Gets a list of category URLs matching the ones entered on the command line.
- get_book: Gets book details from the individual book page.
- get_book_urls_per_page: Gets a list of book URLs on the current page.
"""

import logging
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def get_category_url_list(main_page: BeautifulSoup) -> list[str]:
    """
    This function takes a BeautifulSoup object containing the main page and returns a url list.

    This function takes the argument of a BeautifulSoup object containing the main page and
    returns a list of urls containing the starting pages of each book category.

    :param main_page: A BeautifulSoup object.
    :param url: A url of the main page.
    :return list: A list of urls.
    """

    categories = main_page.find("div", {"class": "side_categories"})
    categories_list = categories.find_all("a")
    url_list = []
    for category_url in categories_list:
        url_extension = category_url.get("href")
        url_list.append("https://books.toscrape.com/" + url_extension)
    return url_list


def convert_category(category):
    """
    This function takes the category provided and formats it into the required url format.
    :param category:
    :return str:
    """

    if len(category.split(" ")) > 1:
        category = category.lower().split(" ")
        category_to_scrape = "-".join(category)
        return category_to_scrape

    return category.lower()


def match_url(category, url):
    """
    This function takes the category provided and ensures it is part of the url.
    :param category: The category provided.
    :param url: The url provided.
    :return bool:
    """

    parsed = urlparse(url)
    parsed_path = parsed.path
    url_match = parsed_path.replace("/catalogue/category/books/", "")
    url_match = url_match.replace("/index.html", "")

    url_match = re.sub(r"_\d+", "", url_match)

    if category == url_match:
        return True

    return False


def get_category_urls(categories, main_page):
    """
    This function takes the categories provided and searches the soup provided
    for the urls of the categories, returning a list of the urls.
    :param categories:
    :param main_page:
    :return list:
    """
    category_list = []
    scrape_list = []

    # convert categories to proper format
    for category in categories:
        category = convert_category(category)
        category_list.append(category)

    # get list of all category urls to match with
    urls = get_category_url_list(main_page)

    unavailable_categories = []

    for item in category_list:
        matches = [url for url in urls if item in url and match_url(item, url)]
        # if category is not available on the site, add it to unavailable_categories
        if not matches:
            unavailable_categories.append(item)
        scrape_list.extend(matches)

    # if any nonmatched categories were added
    if unavailable_categories:
        for unavailable in unavailable_categories:
            logging.warning("%s is not an available category", unavailable)

    # make sure list of returned urls is unique
    return list(set(scrape_list))


def get_book(book_page):
    """
    This function takes the book_page provided and returns a dictionary with the book details.

    This function takes the argument book_page and returns a dictionary with the following
    book details: upc, title, price, and category.

    :param book_page: A BeautifulSoup object of the book page.
    :return dict: A dictionary with the product details.
    """

    # get product category
    nav_list_container = book_page.find("ul", {"class": "breadcrumb"})
    nav_list = nav_list_container.find_all("li")
    category = nav_list[2].find("a").text

    # get upc
    book_details = book_page.find("table")
    rows = book_details.find_all("tr")
    upc = rows[0].find("td").text

    # get title
    title = nav_list[3].text

    # get price
    price = book_page.find("p", {"class": "price_color"}).text

    return {
        "upc": upc,
        "title": title,
        "price": price,
        "category": category
    }


def get_book_urls_per_page(page):
    """
    This function takes a BeautifulSoup object containing the current page and returns a url list
    for each book present on the page.
    :param page: A BeautifulSoup object.
    :return: A url list.
    """

    books = page.find("ol")
    extracted_list = books.find_all("li")
    link_list = []
    for book in extracted_list:
        # navigate to individual book link tag
        link_tag = book.find("a")
        link = link_tag.get("href")
        # clean up relative paths in link
        if "../../../" in link:
            link = link.replace("../../../", "")
        link_list.append(link)
    return link_list
