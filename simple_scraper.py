import sys
from gensim.summarization import summarize, keywords
import pandas
import numpy as np
import urllib.request
import certifi
from bs4 import BeautifulSoup
import requests
import re
import regex
import ssl


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
        # Left align i with 3 character spaces
        print(f'  {i:<3}- {site}')
    print()
    user_num = int(
        input("Please enter a number to investivate a site further: "))
    while(user_num < 0 or user_num > len(sites)):
        user_num = input("Please select a number from the list above: ")
    return options[user_num]


def check_url(url):
    print("---")
    print("Checking URL...")
    print(f"URL: {0}", url)
    try:
        # I think this is necessary otherwise you get bad permission HTTP responses.
        ssl._create_default_https_context=ssl._create_unverified_context
        html = urllib.request.urlopen(url).read()
        return html
    except:
        print("Error retreiving HTML content with 'urllib'.")
        try:
            print("Trying with 'requests'...")
            html = requests.get(url)
            if not html:
                raise Exception
            else:
                return html
        except:
            print("Error retreiving HTML content with 'requests'.")
            print("See 'failed_urls.txt'.")
            with open("failed_urls.txt", "a") as file:
                file.write(url + '\n')
            return None



def get_html_content(user_selection, url):
    print("---")
    print("Retreiving text for: " + user_selection)
    # print(url)
    text = []
    html = urllib.request.urlopen(url).read()

    soup = BeautifulSoup(html, features="html.parser")
    ps = soup.body.find_all('p')
    # Check if is empty
    if not ps:
        print("Found no 'p' tags")
    for p in ps:
        line = p.get_text()
        # Removes any blank strings:
        if line and not regex.search("^\s*$", line):
            text.append(line)

    return text


def get_summary(text):
    print("---")
    print("Summarizing text...")
    # word_count=150 seems to be the minimum...
    summary = summarize(text, word_count=150)
    return summary


def get_key_words(text):
    print("---")
    print("Finding keywords...")
    keywords = keywords(text).split('\n')
    return keywords


def main(searchterm):
    print("---")
    print("Retreiving Google results for: '"+searchterm+"'")
    links=get_links_from_google_search(searchterm)
    sites=find_site_from_url(links)
    user_selection=print_list_of_sites(sites)
    # .split("&sa")[0] removes some extra Google junk on the url
    url_to_search=sites[user_selection].split("&sa")[0]

    while(not check_url(url_to_search)):
        print("---")
        print("! Error retrieving data, please try again.")
        user_selection=print_list_of_sites(sites)

    text_list=get_html_content(user_selection, url_to_search)
    text_block="".join(text_list)
    summary=get_summary(text_block)

    print()
    print(summary)


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
    #  else:
        #  print("Please enter only one keyword to search.")
        #  searchterm = input("Search term: ")
        #  while(' ' in searchterm or searchterm == ''):
            #  print("Please enter only one keyword to search.")
            #  searchterm = input("Search term: ")
        #  main(searchterm)
