import requests
import grequests
from bs4 import BeautifulSoup

def parsed_html(url):
    """Return the parsed HTML for a given webpage from the URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    return soup

def description_responses(articles):
    """Query the URL of each articles and return the responses.

    Arguments:
        articles {list} -- list of article dictionaries containing key 'url' and linking to a newser article

    Returns:
        list -- list of Response objects
    """
    urls = (article['url'] for article in articles)
    reqs = (grequests.get(url) for url in urls)
    responses = grequests.map(reqs, size = 100)
    return responses

def add_descriptions(articles):
    """Add the description for each article into the list of articles.

    Arguments:
        articles {list} -- list of article dictionaries
    """
    responses = description_responses(articles)
    for article, response in zip(articles, responses):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            url = article['url']
            print(f'HTTPError: Request for article with URL "{url}" returned status {response.status_code}.')
        except:
            pass
        else:
            soup = BeautifulSoup(response.content, 'lxml')
            description_div = soup.find('meta', attrs = {'property': 'og:description'})
            article['description'] = description_div['content']

def max_pages():
    """Get the number of pages of articles in a given category."""
    url = build_url(1)
    soup = parsed_html(url)
    nav_div = soup.find('div', class_='page-nav td-pb-padding-side')
    max_pages = nav_div.find('a', class_='last', attrs = {'title': True}).text
    max_pages = max_pages.replace(',', '')
    return int(max_pages)

def build_url(page_number):
    """Return the URL for a given page."""
    url = f'https://www.goodnewsnetwork.org/category/news/page/{page_number}'
    return url

def article_responses(stop):
    """Get the responses to querying the HTML of Good News Network pages."""
    urls = (build_url(i) for i in range(stop))
    reqs = (grequests.get(url) for url in urls)
    responses = grequests.map(reqs, size = 10)
    return responses

def article_cards(responses):
    """Return a list of HTML elements that contain the title and URL of each article, or 'cards.'

    Arguments:
        responses {list} -- list of Response objects, returned by get_responses()

    Returns:
        list -- a list of article cards, which can be parsed by parse_article_cards()
    """
    article_cards = []
    for i, response in enumerate(responses):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print(f'HTTPError: Request {i} returned status {response.status_code}.')
        except:
            print(f"Encountered exception when handling response {i}")
        else:
            soup = BeautifulSoup(response.content, 'lxml')
            cards = soup.find_all('div', class_ = 'td_module_3 td_module_wrap td-animation-stack')
            article_cards += cards
    return article_cards

def parse_cards(article_cards):
    """Parse a list of HTML article cards and return a list of dictionaries containing the headline and URL of each article.

    Arguments:
        article_cards {list} -- list of article cards, returned by get_article_cards

    Returns:
        list -- list of dictionaries containing information about each article.
    """
    articles = []
    for card in article_cards:
        article = {
            'headline': card.h3.text,
            'url': card.h3.a['href'],
            'category': 'good'
        }
        articles.append(article)
    return articles

def scrape(stop = None):
    """Scrape Good News Network for articles, ending at page number 'stop.'

    Keyword Arguments:
        category {str} -- the news category to return articles for (default: {'all'})
        stop {int} -- the ending page. if None, it returns results from every page. (default: {None})

    Returns:
        list -- list of dictionaries containing the article information.
    """
    if not stop:
        stop = max_pages()
    
    responses = article_responses(stop)
    cards = article_cards(responses)
    articles = parse_cards(cards)

    print(f'Scraped {stop} pages from Good News Network, now adding descriptions.')
    add_descriptions(articles)

    return articles