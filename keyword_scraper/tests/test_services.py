import unittest
from unittest.mock import Mock

from keyword_scraper.services import KeywordScraperService
from keyword_scraper.tests import test_web_scraping


class KeywordScraperServiceTest(unittest.TestCase):
    def setUp(self):
        mock_keyword_frequency_counter = Mock()
        self.service = KeywordScraperService(mock_keyword_frequency_counter)
        mock_keyword_frequency_counter.get_keyword_frequency.side_effect = self._get_keyword_frequency
        mock_keyword_frequency_counter.get_keywords.return_value = test_web_scraping.KEYWORDS

    def test_get_keywords_frequency_returns_sorted_keyword_frequency_map(self):
        keyword_frequency_map = self.service.get_keywords_frequency(test_web_scraping.URL)
        self.assertEqual(keyword_frequency_map, test_web_scraping.KEYWORD_FREQUENCY_MAP_SORTED)

    @staticmethod
    def _get_keyword_frequency(keyword):
        return test_web_scraping.KEYWORD_FREQUENCY_MAP[keyword]
