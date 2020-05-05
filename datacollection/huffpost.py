import requests

def build_url(category):
    """Build the resource URL given the news category (good or bad).

    Arguments:
        category {str} -- news category by which to filter results

    Raises:
        Exception: thrown when category is invalid

    Returns:
        str -- resource URL to query
    """
    allowed_categories = ['good', 'bad']
    if category.lower() in allowed_categories:
        url = f'https://www.huffpost.com/api/topic/{category}-news/cards'
    else:
        raise Exception(f'Invalid category name {category}. Excpected category in {allowed_categories}')
    return url

def query(url, max_results = 100):
    """Query Huffpost at the given URL and return back the article JSON information.

    Arguments:
        url {str} -- the resource URL to query, given by build_url()

    Keyword Arguments:
        max_results {int} -- the maximum number of results to return (default: {100})

    Returns:
        list -- a list of JSON objects for each result article
    """
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
    }
    response = requests.get(url, params = {
        'page': 1,
        'limit': max_results
    }, headers = headers)
    article_cards = response.json()['cards']
    return article_cards

def extract_data(article_cards, category):
    """Extract desired data from list of article JSON objects.

    Arguments:
        article_cards {list} -- list of Huffpost article JSON data

    Returns:
        list -- list of dictionaries containing the desired information about each article
    """
    articles = []
    for card in article_cards:
        try:
            article = {
                'headline': card['headlines'][0]['text'],
                'url': card['headlines'][0]['url'],
                'description': card['description'],
                'category': category
            }
            articles.append(article)
        except KeyError:
            # Ignore any strange sponsored messages without descriptions.
            pass
    return articles

def scrape_articles(category, max_results):
    """Scrape Huffpost for articles in a given category.

    Arguments:
        category {str} -- category of articles to query (good or bad)
        max_results {int} -- maximum number of desired results

    Returns:
        list -- list of dictionaries containing information about each article
    """
    huffpost_url = build_url(category)
    json = query(huffpost_url, max_results = max_results)
    articles = extract_data(json, category)
    return articles
