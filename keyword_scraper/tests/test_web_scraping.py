import unittest.mock
from unittest.mock import patch, Mock

import requests

from keyword_scraper import web_scraping
from keyword_scraper.web_scraping import KeywordScraper, WebPageContentGrabber

PAGE_CONTENT_WITHOUT_KEYWORDS = '''
    <html>
        <body>
            <h1>test1</h1>
            test2
            <div id="test3"></div>
        </body>
    <html>'''

PAGE_CONTENT_WITH_KEYWORDS = '''
    <html>
        <head>
            <meta name="keywords" content="test1, test2,test3,, test4,test3," />
        </head>
        <body>
            <h1>test1</h1>
            test2 test2
            <div id="test3">test3 test3</div>
        </body>
    <html>'''

KEYWORD_1 = 'test1'
KEYWORD_2 = 'test2'
KEYWORD_3 = 'test3'
KEYWORD_4 = 'test4'

KEYWORDS = [KEYWORD_1, KEYWORD_2, KEYWORD_3, KEYWORD_4]
KEYWORD_FREQUENCY_MAP = {KEYWORD_1: 1, KEYWORD_2: 2, KEYWORD_3: 3, KEYWORD_4: 0}
KEYWORD_FREQUENCY_MAP_SORTED = [(KEYWORD_3, 3), (KEYWORD_2, 2), (KEYWORD_1, 1), (KEYWORD_4, 0)]

URL = "http://domain.com"
TIMEOUT = 5
CONTENT_TYPE_JPEG = 'image/jpeg'
CONTENT_TYPE_HTML = 'text/html'
CONTENT_TYPE_HTML_WITH_CHARSET = 'text/html; charset=utf-8'


class WebPageContentGrabberTests(unittest.TestCase):
    def setUp(self):
        self._content_grabber = WebPageContentGrabber()

    @patch("requests.request")
    def test_get_web_page_content_handles_connection_error(self, mock_request):
        mock_request.side_effect = requests.ConnectionError
        with self.assertRaises(web_scraping.ConnectionError):
            self._content_grabber.get_web_page_content(URL)

    @patch("requests.request")
    def test_get_web_page_content_handles_invalid_url_error(self, mock_request):
        exceptions = [requests.exceptions.MissingSchema,
                      requests.exceptions.InvalidSchema,
                      requests.exceptions.InvalidURL]
        for e in exceptions:
            mock_request.side_effect = e
            with self.assertRaises(web_scraping.InvalidURLError):
                self._content_grabber.get_web_page_content(URL)

    @patch("requests.request")
    def test_get_web_page_content_handles_timeout_error(self, mock_request):
        mock_request.side_effect = requests.Timeout()
        with self.assertRaises(web_scraping.Timeout):
            self._content_grabber.get_web_page_content_type(URL)

    @patch("requests.request")
    def test_get_web_page_content_handles_http_error(self, mock_request):
        mock_request.side_effect = requests.HTTPError()
        with self.assertRaises(web_scraping.HTTPError):
            self._content_grabber.get_web_page_content_type(URL)

    @patch("requests.request")
    def test_get_web_page_content_calls_request(self, mock_request):
        self._content_grabber.get_web_page_content(URL, TIMEOUT)
        mock_request.assert_called_with('get', URL, timeout=TIMEOUT, verify=False)

    @patch("requests.request")
    def test_get_web_page_content_handles_unexpected_exception(self, mock_request):
        mock_request.side_effect = Exception()
        with self.assertRaises(web_scraping.WebScrapingError):
            self._content_grabber.get_web_page_content(URL)

    @patch("requests.request")
    def test_get_web_page_content_returns_page_content(self, mock_request):
        mock_request.return_value.text = PAGE_CONTENT_WITH_KEYWORDS
        content = self._content_grabber.get_web_page_content(URL, TIMEOUT)
        self.assertEqual(content, PAGE_CONTENT_WITH_KEYWORDS)

    @patch("requests.request")
    def test_get_web_page_content_type_handles_connection_error(self, mock_request):
        mock_request.side_effect = requests.ConnectionError()
        with self.assertRaises(web_scraping.ConnectionError):
            self._content_grabber.get_web_page_content_type(URL)

    @patch("requests.request")
    def test_get_web_page_content_type_handles_invalid_url_error(self, mock_request):
        exceptions = [requests.exceptions.MissingSchema,
                      requests.exceptions.InvalidSchema,
                      requests.exceptions.InvalidURL]
        for e in exceptions:
            mock_request.side_effect = e
            with self.assertRaises(web_scraping.InvalidURLError):
                self._content_grabber.get_web_page_content_type(URL)

    @patch("requests.request")
    def test_get_web_page_content_type_handles_timeout_error(self, mock_request):
        mock_request.side_effect = requests.Timeout()
        with self.assertRaises(web_scraping.Timeout):
            self._content_grabber.get_web_page_content_type(URL)

    @patch("requests.request")
    def test_get_web_page_content_type_handles_unexpected_exception(self, mock_request):
        mock_request.side_effect = Exception()
        with self.assertRaises(web_scraping.WebScrapingError):
            self._content_grabber.get_web_page_content_type(URL)

    @patch("requests.request")
    def test_get_web_page_content_type_handles_http_error(self, mock_request):
        mock_request.side_effect = requests.HTTPError()
        with self.assertRaises(web_scraping.HTTPError):
            self._content_grabber.get_web_page_content_type(URL)

    @patch("requests.request")
    def test_get_web_page_content_type_calls_request(self, mock_request):
        self._content_grabber.get_web_page_content(URL, TIMEOUT)
        mock_request.assert_called_with('get', URL, timeout=TIMEOUT, verify=False)

    @patch("requests.request")
    def test_get_web_page_content_type_returns_page_content_type(self, mock_request):
        content_types = (CONTENT_TYPE_HTML, CONTENT_TYPE_HTML_WITH_CHARSET)
        for ct in content_types:
            headers = {'Content-Type': ct}
            mock_request.return_value.headers = headers
            content_type = self._content_grabber.get_web_page_content_type(URL, TIMEOUT)
            self.assertEqual(content_type, CONTENT_TYPE_HTML)


def create_fake_content_grabber(content_type, content):
    content_grabber = Mock()
    content_grabber.get_web_page_content.return_value = content
    content_grabber.get_web_page_content_type.return_value = content_type
    return content_grabber


class KeywordScraperTests(unittest.TestCase):
    def setUp(self):
        self._fake_content_grabber = create_fake_content_grabber(CONTENT_TYPE_HTML, PAGE_CONTENT_WITH_KEYWORDS)
        self._keyword_scraper = KeywordScraper(self._fake_content_grabber)

    def test_get_keywords_when_page_not_loaded_raises_exception(self):
        with self.assertRaises(web_scraping.WebPageNotLoadedError):
            self._keyword_scraper.get_keywords()

    def test_get_keywords_when_meta_keywords_tag_exist_returns_keyword_list(self):
        self._keyword_scraper.load_web_page(URL, TIMEOUT)
        keywords = self._keyword_scraper.get_keywords()
        self.assertEqual(keywords, KEYWORDS)

    def test_get_keywords_when_meta_keywords_tag_not_exist_raises_exception(self):
        fake_content_grabber = create_fake_content_grabber(CONTENT_TYPE_HTML, PAGE_CONTENT_WITHOUT_KEYWORDS)
        keyword_scraper = KeywordScraper(fake_content_grabber)
        keyword_scraper.load_web_page(URL, TIMEOUT)
        with self.assertRaises(web_scraping.MetaKeywordsTagNotFoundError):
            keyword_scraper.get_keywords()

    def test_get_keyword_frequency_returns_keyword_frequency(self):
        self._keyword_scraper.load_web_page(URL, TIMEOUT)
        for k, f in KEYWORD_FREQUENCY_MAP.items():
            frequency = self._keyword_scraper.get_keyword_frequency(k)
            self.assertEqual(f, frequency)

    def test_get_keyword_frequency_when_page_not_loaded_raises_exception(self):
        with self.assertRaises(web_scraping.WebPageNotLoadedError):
            self._keyword_scraper.get_keyword_frequency(KEYWORD_1)

    def test_load_web_page_calls_get_web_page_content_type(self):
        self._keyword_scraper.load_web_page(URL, TIMEOUT)
        self._fake_content_grabber.get_web_page_content_type.assert_called_with(URL, TIMEOUT)

    def test_load_web_page_calls_get_web_page_content(self):
        self._keyword_scraper.load_web_page(URL)
        self._fake_content_grabber.get_web_page_content.assert_called_with(URL, TIMEOUT)

    def test_load_web_page_when_unsupported_content_type_raises_exception(self):
        fake_content_grabber = create_fake_content_grabber(CONTENT_TYPE_JPEG, None)
        keyword_scraper = KeywordScraper(fake_content_grabber)
        with self.assertRaises(web_scraping.InvalidContentTypeError):
            keyword_scraper.load_web_page(URL, TIMEOUT)
