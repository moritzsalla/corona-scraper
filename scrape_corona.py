from gensim.summarization import summarize
import pandas
import numpy as np
import bs4
import requests


def get_link_response(url:str) -> requests.Response:
    """
    get_link_response gets a URL and scrapes it, returning the object.
    """
    return requests.get(url)


def choose_next_link(next_link_candidates: list) ->list:
    """
    choose_next_link

    Given a list of URLs strings from the website scraped, it chooses which link to go to next.
    """
    url_keywords = ["breitbart", "foxnews", "thehill", "dailymail", "wallstreet", "drudgereport", "hannity", "trump"]
    next_links = []
    for link in urls:
        for rightist_link in url_keywords:
            if rightist_link in link:
                next_links.append(link)

    return next_links


# def parse_html(html:str) -> :
    # """


    # :param html:
    # :return: next_link_candidates
    # """



if __name__ == "__main__":
    print("Scraping stuff for corona. Limes!")

    url_to_search = "https://drudgereport.com"

    # while True:
        # response = get_link_response(url_to_search)

    print(get_link_response(url_to_search))
