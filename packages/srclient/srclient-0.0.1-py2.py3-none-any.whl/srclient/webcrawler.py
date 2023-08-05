from requests import get as http_get
from bs4 import BeautifulSoup


def get_soup(url):
    page = http_get(url)
    return BeautifulSoup(page.text, 'html.parser')

def get_domain(url):
    return url.split("//")[0] + '//' + url.split("//")[1].split('/')[0]

def find_links(url, params=None, domain=False):
    soup = get_soup(url)
    result = []
    for item in soup.findAll('a', params):
        href = item.get('href','')
        if href == '': continue
        if href[0:4] != 'http' and domain:
            href = get_domain(url) + href

        if href[0:4] == 'http': result.append(href)
    return result




def hacker_news():
    ycombinator = [
        'https://news.ycombinator.com',
        'https://news.ycombinator.com/newest',
        'https://news.ycombinator.com/active',
    ]
    result = []
    for url in ycombinator:
        result.extend(find_links(url, {"class": "storylink"}, True))
    return result

def hacker_news_archive():
    result = []
    for i in range(2,7):
        url = 'https://news.ycombinator.com/active?p='+str(i)
        result.extend(find_links(url, {"class": "storylink"}, True))
    return result

def heise_security():
    url = 'https://www.heise.de/security'
    return find_links(url, {"class": "akwa-article-teaser__link"}, True)

def fefe():
    url = 'https://blog.fefe.de'
    return find_links(url)

def shz_ticker():
    url = 'https://www.shz.de/regionales/newsticker-nord/'
    return find_links(url, {"class": "headline"}, True)

def golem_ticker():
    soup = get_soup('https://www.golem.de/ticker/')
    result = []
    for item in soup.findAll('ol', {"class": "list-tickers"}):
        for l in item.findAll('a'):
            href = l.get('href','')
            if href != '':
                result.append(href)
    return result
