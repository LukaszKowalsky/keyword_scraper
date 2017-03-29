import operator

from keyword_scraper.web_scraping import KeywordScraper


class KeywordScraperService(object):
    def __init__(self, keyword_scraper=KeywordScraper()):
        self._keyword_scraper = keyword_scraper

    def get_keywords_frequency(self, url):
        self._keyword_scraper.load_web_page(url)
        keyword_frequency_map = dict()
        keywords = self._keyword_scraper.get_keywords()
        if keywords:
            for k in keywords:
                frequency = self._keyword_scraper.get_keyword_frequency(k)
                keyword_frequency_map[k] = frequency
            return sorted(keyword_frequency_map.items(), key=operator.itemgetter(1), reverse=True)
