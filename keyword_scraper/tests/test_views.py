import unittest
from unittest.mock import patch

import flask

from keyword_scraper import web_scraping, error_messages, app
from keyword_scraper.tests import test_web_scraping

test_app = flask.Flask(__name__)


class ViewsTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    @patch("keyword_scraper.services.KeywordScraperService.get_keywords_frequency")
    def test_get_keywords_displays_keywords(self, mock_get_keywords_frequency):
        mock_get_keywords_frequency.return_value = test_web_scraping.KEYWORD_FREQUENCY_MAP_SORTED
        response = self.app.post('/', data=dict(url=test_web_scraping.URL))
        for k in test_web_scraping.KEYWORDS:
            assert k.encode() in response.data

    @patch("keyword_scraper.services.KeywordScraperService.get_keywords_frequency")
    def test_get_keywords_displays_error(self, mock_get_keywords_frequency):
        error_message_map = [(web_scraping.ConnectionError, error_messages.CONNECTION_ERROR),
                             (web_scraping.HTTPError, error_messages.HTTP_ERROR),
                             (web_scraping.Timeout, error_messages.TIMEOUT),
                             (web_scraping.InvalidContentTypeError, error_messages.INVALID_CONTENT_TYPE),
                             (web_scraping.InvalidURLError, error_messages.INVALID_URL),
                             (web_scraping.WebScrapingError, error_messages.UNEXPECTED_EXCEPTION)]

        for error, message in error_message_map:
            mock_get_keywords_frequency.side_effect = error(message)
            response = self.app.post('/', data=dict(url=test_web_scraping.URL))
            assert message.encode() in response.data
