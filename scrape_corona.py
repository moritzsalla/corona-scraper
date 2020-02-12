from gensim.summarization import summarize
import pandas
import numpy as np
from bs4 import BeautifulSoup
import requests
import datetime


def get_link_response(url: str) -> requests.Response:
    """
    get_link_response gets a URL and scrapes it, returning the object.
    """
    return requests.get(url)


def choose_next_link(next_link_candidates: list) -> list:
    """
    choose_next_link
    Given a list of URLs strings from the website scraped, it chooses which link to go to next.
    We're using only the MOST TRUSTWORTHY not Fake News papers.
    Clearly we'll get non-sensational and useful content.
    """
    url_keywords = ["breitbart", "foxnews", "thehill", "dailymail", "drudgereport", "hannity", "onion", "chinadaily",
                    "rt.com"]
    next_links = []
    for link in next_link_candidates:
        for rightist_url_keyword in url_keywords:
            if rightist_url_keyword in link:
                next_links.append(link)
    return next_links


def parse_page(webpage: requests.Response) -> tuple:
    """
    This function breaks apart an HTML document and returns the next links.
    It also summarizes and prints
    :param webpage: Response object for parsing
    :return: summary for inclusion in data row, next_link_candidates_cleaned for the next round of scraping
    """
    soup = BeautifulSoup(webpage.text, 'html.parser')
    next_link_candidates = [a.get('href') for a in soup.find_all('a')]
    next_link_candidates_cleaned = []
    if len(next_link_candidates) > 0:
        for link in next_link_candidates:
            if link[0] == "/":
                next_link_candidates_cleaned.append(webpage.url + link)

            if "mailto:" not in link:
                next_link_candidates_cleaned.append(link)

    paragraphs = soup.find_all('p')
    if len(paragraphs) > 0:
        paragraphs_joined = " ".join(paragraphs)
        summary = summarize(paragraphs_joined, word_count=140)  # make a twitter summary!
        print(f"{webpage.url} summarizes down to {summary}")
    else:
        summary = ""

    return summary, next_link_candidates_cleaned


def scrape_page(links: list) -> tuple:
    """
    Scrape_page coordinates the collection of pages from their links.
    Summarizes them.
    And stores them into a Pandas Dataframe which will be saved later.
    :param dataframe: Dataframe to insert data into
    :param links: Page links to process this round.
    :return: next_links: links to process in the next round
    """

    # First we use Requests to get the Response objects for every page in the links list
    responses = [get_link_response(link) for link in links]
    scraped_data_dict_list = []
    filtered_candidates = []
    # Then we iterate through them
    for response in responses:
        # create the summary and get all possible link candidates
        summary, next_link_candidates = parse_page(response)
        # Then we choose the next links from the candidates
        related_links = choose_next_link(next_link_candidates)
        filtered_candidates.extend(related_links)
        # Then we have what we need. We add it to the dict we'll use to write the dataframe
        data_dict = {
            "url": response.url,
            "summary": summary,
            "related_links": related_links
        }
        scraped_data_dict_list.append(data_dict)

    return scraped_data_dict_list, filtered_candidates


if __name__ == "__main__":
    # TODO: argparse subject to scrape
    starting_time = datetime.datetime.now()
    print(f"Scraping the news for corona. Limes! Starting at {starting_time}.")


    next_links = ["https://drudgereport.com"]
    depth = 5  # specify how many layers links we're going to follow.
    current_depth = 0
    save_csv_path = "corona.csv"
    total_scraped_pages = 0

    # Here we try to load a CSV file, if we're saving additional data to it.
    # If it's not found, we just create a blank one to use.
    try:
        # converter since the list is loaded as a str by default from CSV.
        # See:https://stackoverflow.com/questions/23111990/pandas-dataframe-stored-list-as-string-how-to-convert-back-to-list
        # https://stackoverflow.com/questions/36519086/how-to-get-rid-of-unnamed-0-column-in-a-pandas-dataframe
        beginning_df = pandas.read_csv(save_csv_path, converters={'related_links': eval}, index_col=0)
        new_file = False

    except FileNotFoundError as e:
        print("File not found, we'll make one later")
        new_file = True

    # Prepare a new empty list of dicts to write into the pandas doc at the end.
    dict_list_to_write = []

    # Run the scraping methods until we reach the desired number of iterations
    while current_depth < depth:
        print(f"Scraping at depth {current_depth}. Total scraping: {len(next_links)} links")
        current_depth += 1
        current_amt_links = len(next_links)

        # Get the list of data dicts and links for this depth. Add them to the list of dicts to convert to a table.
        # Each dict object gets converted into a row in the table
        data_dict_list, next_links = scrape_page(next_links)
        dict_list_to_write.extend(data_dict_list)

        # Now that the scraped round is complete (prior 2 methods are quite time-consuming), increment the completed count.
        total_scraped_pages += current_amt_links
        print(f"Scraping depth {current_depth} complete. Next up: {len(next_links)} links")

    # turn list of dicts into a dataframe. Each dict is a row.
    df_additions = pandas.DataFrame(dict_list_to_write, columns=["url", "summary", "related_links"])

    # Finally, (re)save the CSV
    if not new_file:
        df_to_save = pandas.concat([beginning_df, df_additions])
        df_to_save.to_csv(save_csv_path, sep=",")
    else:
        df_additions.to_csv(save_csv_path, sep=",")

    # Print out to console just how much time has elapsed
    end_time = datetime.datetime.now()
    duration = (end_time-starting_time).seconds
    print(f"Scraped a total of {total_scraped_pages} pages in {duration}")

    exit(code=1)
