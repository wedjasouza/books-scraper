#!/usr/bin/env python3

"""
This module provides utility functions for scraping the books.toscrape.com website.

Available functions:
- get_soup: Gets a BeautifulSoup object from the provided URL.
- get_book_page: Gets a BeautifulSoup object from the individual book URL.
- get_next: Gets the link to the next page if one exists.
- get_full_page: Gets a list of dictionaries containing the book details.
- scraper: Adds dictionaries from get_full_page together into a final output.

"""


import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
from bs4 import BeautifulSoup
from parser import get_category_urls, get_book, get_book_urls_per_page

# specify home page url

URL_HOME = "https://books.toscrape.com/"

# create retry logic

session = requests.Session()

retries = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

session.mount("https://", HTTPAdapter(max_retries=retries))


def get_soup(url: str) -> BeautifulSoup | None:
    """
    This function takes the url provided and returns a BeautifulSoup object.

    :param url:
    :return soup: A BeautifulSoup object.
    :raises: requests.exceptions.HTTPError if the request fails.
    :raises: requests.exceptions.SSLError if a secure connection cannot be established.
    """

    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        return soup
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error occurred: {err}")
    except requests.exceptions.SSLError as err:
        print(f"SSL Error occurred: {err}")


def get_book_page(book_url: str) -> BeautifulSoup:
    """
    This function takes the url from an individual book and returns a BeautifulSoup object
    of the book page.
    :param book_url:
    :return soup: A BeautifulSoup object.
    """

    time.sleep(0.5)
    soup = get_soup(book_url)
    return soup


def get_next(soup: BeautifulSoup | None) -> str | None:
    """
    This helper function takes the soup provided and returns the url extension connected
    to the next button if there is one, and None otherwise.
    :param soup:
    :return url_text:
    """
    pager = soup.find("ul", {"class": "pager"})
    if not pager:
        return None

    next_link = pager.find("li", {"class": "next"})
    if next_link:
        url_text = next_link.find("a").get("href")
        return url_text

    return None


def get_full_page(soup: BeautifulSoup, previous_len: int, limit: int =1000):
    """
    This function takes a BeautifulSoup object containing the current page and returns
    a list of dictionaries containing the book details for that page.
    :param soup: A BeautifulSoup object.
    :param previous_len: An integer indicating the number of books previously scraped.
    :param limit: An integer indicating the limit of the number of books to scrape.
    :return list: A list of dictionaries containing the book details.
    """

    links = get_book_urls_per_page(soup)
    book_list = []
    for link in links:
        # make sure the link extension is properly formatted
        if "catalogue" not in link:
            link = "catalogue/" + link
        if (len(book_list) + previous_len) == limit:
            break
        link = URL_HOME + link
        logging.info("Scraping: %s", link)
        book_page = get_book_page(link)
        book = get_book(book_page)
        book_list.append(book)
    return book_list


def scraper(limit: int = 1000, categories: list[str] = None) -> list[dict]:
    """
    This function takes optional parameters limit and categories from the command
    line and returns a final list of dictionaries containing the book details.

    :param limit: An int indicating the number of books to scrape (per category if
    categories provided).
    :param categories: A list of strings indicating the categories to scrape.
    :return list[dict]: A list of dictionaries containing the book details.
    """
    logging.info("Starting scraping...")
    main_page = get_soup(URL_HOME)

    previous_len = 0

    if categories:
        category_urls = get_category_urls(categories, main_page)
        # if categories provided had no matches
        if len(category_urls) == 0:
            logging.error("No available category urls")
            return
        full_list = []
        for category_url in category_urls:
            # reset previous_len for each category
            previous_len = 0
            logging.info("Scraping: %s", category_url)
            soup = get_soup(category_url)
            book_list = get_full_page(soup, previous_len, limit)
            previous_len += len(book_list)
            next_page = get_next(soup)
            while next_page:
                if previous_len >= limit:
                    break
                url = category_url.replace("index.html", "")
                url = url + next_page
                logging.info("Scraping: %s", url)
                soup = get_soup(url)
                book_page = get_full_page(soup, previous_len, limit)
                previous_len += len(book_page)
                book_list.extend(book_page)
                next_page = get_next(soup)
            full_list.extend(book_list)
        return full_list

    next_page = get_next(main_page)
    logging.info("Scraping: %s", URL_HOME)
    book_list = get_full_page(main_page, previous_len, limit)
    previous_len += len(book_list)
    while next_page:
        if previous_len >= limit:
            break
        if "catalogue" not in next_page:
            next_page = "catalogue/" + next_page
        url = URL_HOME + next_page
        logging.info("Scraping: %s", url)
        soup = get_soup(url)
        book_page = get_full_page(soup, previous_len, limit)
        previous_len += len(book_page)
        book_list.extend(book_page)
        next_page = get_next(soup)
    return book_list
