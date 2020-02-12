import sys
from gensim.summarization import summarize
import pandas
import numpy as np
from bs4 import BeautifulSoup
import requests
import re


def get_links_from_google_search(query):
    page = requests.get("https://www.google.co.uk/search?q="+query)
    soup = BeautifulSoup(page.content, features="html.parser")
    links = []
    
    for link in soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)")):
        links.append(link["href"].replace("/url?q=",""))

    return links


def main(argv):
    l = get_links_from_google_search(argv)

    print(l)



if __name__ == "__main__":

    main(sys.argv[1])
