import sys
from gensim.summarization import summarize
import pandas
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import regex


def get_links_from_google_search(query):
    """
    Performs some regex manipulations on the received HTML to clean up the links.

    - Positive Lookbehind: 

        ?<=   

    - This searches for '/url?q=' BEHIND (http:// | https:// | any variant thereof):

        (?<=/url\?q=)(htt.*://.*)   

    - link["href"] returns the 'href' element in the link object

    - re.compile()  Compile a regular expression pattern into a regular expression object, 
    which can be used for matching using its match() and search() methods, described below.

    - The sequence

        prog = re.compile(pattern)
        result = prog.match(string)

    is equivalent to

        result = re.match(pattern, string)

    - Find all "a" tags where the contents of the "href" element contain 
    the pattern in re.compile():

        find_all("a",href=re.compile("(?<=/url\?q=)(htt.*://.*)"))

    - Look AHEAD assertion:

        :(?=http)     a colon FOLLOWED BY 'http'

    """
    page = requests.get("https://www.google.co.uk/search?q="+query)
    soup = BeautifulSoup(page.content, features="html.parser")
    links = []

    for link in soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)")):
        links.append(link["href"].replace("/url?q=", ""))

    return links


def find_site_from_url(links):
    sites = dict()
    for link in links:
        res = regex.search('(?<=((\/{2}\.)|(w{3}\.)|(\w+)\.))\w+', link)
        sites[res.group(0)] = link
    return sites


def main(argv):
    links = get_links_from_google_search(argv)
    sites = find_site_from_url(links)

    print(sites)


if __name__ == "__main__":

    main(sys.argv[1])
