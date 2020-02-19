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


def print_list_of_sites(sites):
    print("---")
    print("Your options to choose from are:")
    print()
    options = dict()
    for i, site in enumerate(sites.keys()):
        options[i] = site
        print(f'  {i:<3}- {site}')
    print()
    user_num = int(input("Please enter a number to investivate a site further: "))
    while(user_num < 0 or user_num > len(sites)): 
        user_num = input("Please select a number from the list above: ")
    return options[user_num]


def main(searchterm):
    print("---")
    print("Retreiving Google results for: '"+searchterm+"'")
    links = get_links_from_google_search(searchterm)
    sites = find_site_from_url(links)
    user_selection = print_list_of_sites(sites)
    print("---")
    print("Selection: " + user_selection)


if __name__ == "__main__":
    if(len(sys.argv) > 2):
        # Too many arguments
        print("Please enter only one keyword to search.")
        searchterm=input("Search term: ")
        while(' ' in searchterm or searchterm == ''):
            print("Please enter only one keyword to search.")
            searchterm=input("Search term: ")
        main(searchterm)
    elif(len(sys.argv) == 2 and sys.argv[1] != ''):
        main(sys.argv[1])
    else:
        print("Please enter only one keyword to search.")
        searchterm=input("Search term: ")
        while(' ' in searchterm or searchterm == ''):
            print("Please enter only one keyword to search.")
            searchterm=input("Search term: ")
        main(searchterm)
