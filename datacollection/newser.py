import grequests
import requests
from bs4 import BeautifulSoup

def article_request(num_rows, start_row):
    """Return a grequests GET request object from newser given the start row and the number of rows. 
    The controlpage.aspx endpoint returns a grid of articles, with three per row. The first row is 
    'start_row' and the request returns 'num_rows' rows.

    Arguments:
        num_rows {int} -- the number of rows of articles to GET per request.
        start_row {int} -- the index of the start row. if iterating, pass in iteration number * interval.

    Returns:
        AsyncRequest -- asynchronous GET request object that should then be passed to grequests.map()
    """
    url = 'https://www.newser.com/controlpage.aspx'
    r = grequests.get(url, params = {
        'control': 'storysquarecontainer',
        'sectionid': 117,
        'gridrownum': int(start_row),
        'numgridrows': int(num_rows),
        'categoryid': 19
    })
    return r

def article_responses(num_requests, rows_per_request):
    """Return a list of 'num_requests' responses from newser's depressing news page.
    Each response contains the HTML page with 3 * 'rows_per_request' articles.

    Arguments:
        num_requests {int} -- the number of requests to make
        rows_per_request {int} -- the number of article rows to return per request

    Returns:
        list -- list of Response objects to the requests.
    """
    article_requests = (
        article_request(num_rows = rows_per_request, start_row = i * rows_per_request) 
        for i in range(num_requests)
    )
    article_responses = grequests.map(article_requests, size = 10)
    return article_responses

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
        else:
            soup = BeautifulSoup(response.content, 'lxml')
            cards = soup.find_all('a', class_='aGridSquareLink')
            article_cards += cards
    return article_cards

def parse_article_cards(article_cards):
    """Parse a list of HTML article cards and return a list of dictionaries containing the headline and URL of each article.

    Arguments:
        article_cards {list} -- list of article cards, returned by get_article_cards

    Returns:
        list -- list of dictionaries containing information about each article.
    """
    articles = []
    for card in article_cards:
        article = {
            'headline': card.img['alt'],
            'url': 'https://www.newser.com'+ card['href'],
            'category': 'good'
        }
        articles.append(article)
    return articles

def fetch_articles(num_requests, articles_per_request):
    """Fetch depressing articles from newser.com. The number of articles returned is 'num_requests' * 'articles_per_request.'

    Arguments:
        num_requests {int} -- the number of requests to make to newser.com
        articles_per_request {int} -- the number of articles to return per request

    Returns:
        list -- list of dictionaries containing article information (title and URL)
    """
    if articles_per_request % 3 != 0:
        # returns articles per request 'rounded up' to the nearest 3
        adjusted_num_articles = articles_per_request + 3 - (articles_per_request % 3)
        output = (f'\nExpected articles_per_request to be a multiple of 3, since articles are returned by '
        f'newser.com in groups of three. Fetching {adjusted_num_articles} articles instead.\n')
        print(output)
        rows_per_request = adjusted_num_articles / 3
    else:
        rows_per_request = articles_per_request / 3
    r = article_responses(num_requests, rows_per_request)
    cards = article_cards(r)
    articles = parse_article_cards(cards)
    return articles

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

def add_descriptions(articles, description_responses):
    """Add the description for each article into the list of articles.

    Arguments:
        articles {list} -- list of article dictionaries
        responses {list} -- list of Response objects, returned by description_responses()
    """
    for article, response in zip(articles, description_responses):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            url = article['url']
            print(f'HTTPError: Request for article with URL "{url}" returned status {response.status_code}.')
        else:
            soup = BeautifulSoup(response.content, 'lxml')
            description = soup.find('div', id='divDeck')
            article['description'] = description.text

def fetch_descriptions(articles):
    """Fetch the descriptions for the given articles, add the description for each into the dict, and return the dict.

    Arguments:
        articles {list} -- list of the articles

    Returns:
        list -- list of the articles, but with descriptions!
    """
    responses = description_responses(articles)
    add_descriptions(articles, responses)
    return articles

def scrape(num_requests, articles_per_request):
    """Scrape newser.com for depressing articles and return the articles with headline, description, and URL.

    Arguments:
        num_requests {int} -- the number of requests to newser.com to make
        articles_per_request {int} -- the number of articles to return per request

    Returns:
        list -- list of articles, where each article is a dict with keys 'headline,' 'description,' and 'url.'
    """
    a_without_descriptions = fetch_articles(num_requests, articles_per_request)
    articles = fetch_descriptions(a_without_descriptions)
    return articles