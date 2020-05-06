import requests
from bs4 import BeautifulSoup

def parsed_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    return soup

class Page:
    """A page on the Good News Network site."""
    def __init__(self, page_number, category = 'all'):
        self.page_number = page_number
        self.category = category

    def url(self):
        """Return the URL for this page."""
        url = 'https://www.goodnewsnetwork.org/category/news/'
        allowed_categories = ['usa', 'world', 'inspiring', 'animals', 'heroes']
        if self.category.lower() in allowed_categories:
            url = ''.join((url, self.category, '/'))
        elif self.category.lower() != 'all':
            raise Exception(f'Invalid category name {self.category}. Expected category in {allowed_categories}')

        if self.page_number > 1:
            url = ''.join((url, f'page/{self.page_number}/'))
        return url

    def article_description(self, article_url):
        """Get the description of an article from its URL.

        Arguments:
            url {str} -- URl of the article

        Returns:
            str -- description of the article
        """
        soup = parsed_html(article_url)
        description_div = soup.find('meta', attrs = {'property': 'og:description'})
        if not description_div:
            print(f'Could not find description for article at URL: {article_url}')
            return
        description = description_div['content']
        return description

    def articles(self):
        """Find the articles on a page and return title, url, and description for each.

        Returns:
            list -- list of article dictionaries, each of which contains title, category, and url
        """
        soup = parsed_html(self.url())
        article_cards = soup.find_all('div', class_ = 'td_module_3 td_module_wrap td-animation-stack')
        articles = []
        for card in article_cards:
            article = {
                'headline': card.h3.text,
                'url': card.h3.a['href'],
                'description': self.article_description(card.h3.a['href']),
                'category': 'good'
            }
            articles.append(article)
        return articles

def max_pages(category = 'all'):
    """Get the number of pages of articles in a given category."""
    category_page = Page(page_number = 1, category = category)
    soup = parsed_html(category_page.url())
    nav_div = soup.find('div', class_='page-nav td-pb-padding-side')
    max_pages = nav_div.find('a', class_='last', attrs = {'title': True}).text
    max_pages = max_pages.replace(',', '')
    return int(max_pages)

def scrape_pages(category = 'all', start = 0, stop = None):
    """Scrape Good News Network for articles in the given category, starting at page 'start' and ending at 'stop.'

    Keyword Arguments:
        category {str} -- the news category to return articles for (default: {'all'})
        start {int} -- the starting page (default: {0})
        stop {int} -- the ending page. if None, it returns results from every page. (default: {None})

    Returns:
        list -- list of dictionaries containing the article information.
    """
    if not stop:
        stop = max_pages(category)
    
    total_articles = []
    for i in range(stop):
        if i % 50 == 0:
            print(f'Scraping Good News Network page {i}/{stop}')
        page_number = i + start
        current_page = Page(page_number, category)
        total_articles += current_page.articles()
    
    return total_articles