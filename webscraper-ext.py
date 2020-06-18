from gensim.summarization import summarize
import pandas
import numpy as np
from bs4 import BeautifulSoup
import urllib.request

URL = "https://en.wikipedia.org/wiki/2019%E2%80%9320_coronavirus_pandemic"
WORD_COUNT = 100

# Scrape Websites

URL = urllib.request.urlopen(URL).read()
URL = BeautifulSoup(URL, features="lxml")

collection = ""

for text in URL.find_all("p"):
    if len(text) > 10:
        collection += text.get_text()

# Summarize using gensim

collection = summarize(collection, word_count=WORD_COUNT)

# extract keywords from all the different documents and see if any are more popular than others

print(collection.items())
