from gensim.summarization import summarize
import pandas
import numpy as np
from bs4 import BeautifulSoup
import requests


def get_link_response(url:str) -> requests.Response:
    """
    get_link_response gets a URL and scrapes it, returning the object.
    """
    return requests.get(url)


def choose_next_link(next_link_candidates: list) -> list:
    """
    choose_next_link

    Given a list of URLs strings from the website scraped, it chooses which link to go to next.
    """
    url_keywords = ["breitbart", "foxnews", "thehill", "dailymail", "wallstreet", "drudgereport", "hannity", "trump"]
    next_links = []
    for link in next_link_candidates:
        for rightist_link in url_keywords:
            if rightist_link in link:
                next_links.append(link)

    return next_links


def parse_html(webpage: requests.Response) -> tuple:
    """
    This function breaks apart an HTML document and returns the next links.
    It also summarizes and prints

    :param html:
    :return: summary, next_link_candidates
    """
    soup = BeautifulSoup(webpage.text, 'html.parser')
    next_link_candidates = [a.get('href') for a in soup.find_all('a')]
    next_link_candidates = [a for a in next_link_candidates if a[0] != "/"]

    if len(next_link_candidates) < 0:
        next_link_candidates = []

    paragraphs = soup.find_all('p')
    if len(paragraphs) > 0:
        paragraphs_joined = " ".join(paragraphs)
        summary = summarize(paragraphs_joined, word_count=140)  # make a twitter summary!
        print(f"{webpage.url} summarizes down to {summary}")
    else:
        summary = ""

    return summary, next_link_candidates


if __name__ == "__main__":
    print("Scraping stuff for corona. Limes!")

    next_links = ["https://drudgereport.com"]

    while True:
        responses = [get_link_response(link) for link in next_links]
        summaries, next_link_candidates = parse_html(responses[0])

        # next_links = choose_next_link(next_link_candidates)
