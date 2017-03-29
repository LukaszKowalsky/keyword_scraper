import lxml.html
import requests
import requests.exceptions
from lxml import html

from keyword_scraper import error_messages

DEFAULT_TIMEOUT = 5


class WebPageContentGrabber(object):
    def get_web_page_content_type(self, url, timeout=DEFAULT_TIMEOUT):
        content_type = None
        content_type_header = 'Content-Type'
        http_headers = self._get_http_headers(url, timeout)

        if content_type_header in http_headers:
            content_type = http_headers[content_type_header].lower()
            separator_index = content_type.find(';')
            if separator_index > 1:
                content_type = content_type[0:separator_index]
        return content_type

    def get_web_page_content(self, url, timeout=DEFAULT_TIMEOUT):
        response = self._send_http_request(url, 'get', timeout)
        content = response.text
        return content

    def _get_http_headers(self, url, timeout):
        response = self._send_http_request(url, 'head', timeout)
        headers = response.headers
        return headers

    @staticmethod
    def _send_http_request(url, method, timeout):
        try:
            response = requests.request(method, url, timeout=timeout, verify=False)
            response.raise_for_status()

        except requests.HTTPError as e:
            raise HTTPError(error_messages.HTTP_ERROR) from e

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(error_messages.CONNECTION_ERROR) from e

        except requests.Timeout as e:
            raise Timeout(error_messages.TIMEOUT) from e

        except (requests.exceptions.MissingSchema,
                requests.exceptions.InvalidSchema,
                requests.exceptions.InvalidURL) as e:
            raise InvalidURLError(error_messages.INVALID_URL) from e

        except Exception as e:
            raise WebScrapingError(error_messages.UNEXPECTED_EXCEPTION) from e
        return response


class KeywordScraper(object):
    def __init__(self, content_grabber=WebPageContentGrabber()):
        self._content_grabber = content_grabber

    SUPPORTED_CONTENT_TYPE = 'text/html'

    _html = None
    _is_page_loaded = False
    _body_content_lower_case = None

    def get_keywords(self):
        if not self._is_page_loaded:
            raise WebPageNotLoadedError()
        meta_keywords_content = self._html.xpath('//html/head/meta[@name="keywords"]/@content')
        if meta_keywords_content:
            keywords = meta_keywords_content[0].split(',')
            keywords = list(filter(None, keywords))
            keywords = [k.strip() for k in keywords]
            keywords = sorted(set(keywords))
            return keywords
        else:
            raise MetaKeywordsTagNotFoundError(error_messages.META_KEYWORDS_TAG_NOT_FOUND)

    def get_keyword_frequency(self, keyword):
        if not self._is_page_loaded:
            raise WebPageNotLoadedError()
        frequency = self._body_content_lower_case.count(keyword.lower())
        return frequency

    def load_web_page(self, url, timeout=DEFAULT_TIMEOUT):
        content_type = self._content_grabber.get_web_page_content_type(url, timeout)
        if content_type == self.SUPPORTED_CONTENT_TYPE:
            content = self._content_grabber.get_web_page_content(url, timeout)
            self._html = lxml.html.fromstring(content)
            body_content = self._get_body_content()
            self._body_content_lower_case = body_content.lower()
        else:
            raise InvalidContentTypeError(error_messages.INVALID_CONTENT_TYPE)
        self._is_page_loaded = True

    def _get_body_content(self):
        body_content = None
        body_node = self._html.xpath('//body')[0]
        if body_node is not None:
            body_content = self._get_node_inner_html(body_node)
        return body_content

    @staticmethod
    def _get_node_inner_html(node):
        node.attrib.clear()
        opening_tag = len(node.tag) + 2
        closing_tag = -(len(node.tag) + 3)
        body_content = html.tostring(node, encoding='utf-8').decode()
        body_content = body_content.strip()[opening_tag:closing_tag]
        return body_content


class WebScrapingError(Exception):
    def __init__(self, message):
        self.message = message


class ConnectionError(WebScrapingError):
    pass


class HTTPError(WebScrapingError):
    pass


class Timeout(WebScrapingError):
    pass


class InvalidContentTypeError(WebScrapingError):
    pass


class InvalidURLError(WebScrapingError):
    pass


class MetaKeywordsTagNotFoundError(WebScrapingError):
    pass


class WebPageNotLoadedError(Exception):
    pass
