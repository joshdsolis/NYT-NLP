#!/usr/bin/env python

import requests, bs4, os, errno, time, datetime, re

def download_page(url):
    try:
        page = requests.get(url, timeout=10.0)
    except requests.exceptions.Timeout:
        print('Timeout\n')
        return None
    except requests.exceptions.ConnectionError:
        print('ConnectionError\n')
        time.sleep(120)
        return None
    except requests.exceptions.HTTPError:
        print('HTTPError\n')
        return None
    except requests.exceptions.TooManyRedirects:
        print('TooManyRedirects\n')
        return None
    else:
        return page


max_attempts = 10

r_unwanted = re.compile('[\n\t\r]')

urls_to_articles = []

if not os.path.exists('articles/'):
    try:
        os.makedirs('articles/')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

# STEP 1. BUILD THE LIST OF URLS TO ARTICLES
if True:
#not os.path.exists('urls_to_articles.txt'):
    links_to_parts = []

    for year in range(2019, datetime.datetime.now().year + 1):

        catalog_page_by_years = 'http://spiderbites.nytimes.com/%s/' % (year)

        attempts = 0

        print('Year: ', year)

        with open('logfile.log', 'w') as f:
            f.write('STEP 1. Year: ' + str(year) + '\n')

        catalog_page = download_page(catalog_page_by_years)

        while not (catalog_page or attempts > max_attempts):
            catalog_page = download_page(catalog_page_by_years)
            attempts += 1
            
        if catalog_page:
            catalog_page = bs4.BeautifulSoup(catalog_page.text, "lxml")
            if year > 1995:
                links_to_parts.append(['http://spiderbites.nytimes.com%s' % (el.get('href')) for el in catalog_page.select('body > div > div > div > div > div > div > ul > li > a')])
            else:
                links_to_parts.append(['http://spiderbites.nytimes.com/free_%s/%s' % (year, el.get('href')) for el in catalog_page.select('body > div > div > div > div > div > div > ul > li > a')])

    links_to_parts = [item for sublist in links_to_parts for item in sublist]
    
    for link_to_parts in links_to_parts:

        attempts = 0

        parts_page = download_page(link_to_parts)

        while not (parts_page or attempts > max_attempts):
            parts_page = download_page(link_to_parts)
            attempts += 1

        if parts_page:
            parts_page = bs4.BeautifulSoup(parts_page.text, "lxml")
            urls_to_articles.append([el.get('href') for el in parts_page.select('body > div > div > div > div > ul > li > a')])

urls_to_articles = [item for sublist in urls_to_articles for item in sublist]

# Backing up the list of URLs
with open('urls_to_articles.txt', 'w') as output:
    for u in urls_to_articles:
        output.write('%s\n' % (u.strip()))

# Part where I find the content in the articles and put it in a list
articles = []
for url in urls_to_articles:
    article_page = download_page(url)
    article_page = bs4.BeautifulSoup(article_page.text, "lxml")
    body = article_page.find_all(class_="meteredContent")
    if body:
        articles.append(body[0].text)


