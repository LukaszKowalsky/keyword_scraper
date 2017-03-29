from flask import flash
from flask import render_template, request

from keyword_scraper import app
from keyword_scraper.services import KeywordScraperService
from keyword_scraper.web_scraping import WebScrapingError


@app.route('/', methods=['GET', 'POST'])
def get_keywords_frequency():
    url = None
    keyword_frequency_map = []

    if request.method == 'POST':
        url = request.form['url']
        if url:
            try:
                service = KeywordScraperService()
                keyword_frequency_map = service.get_keywords_frequency(url)
            except WebScrapingError as e:
                flash(e.message, 'error')

    return render_template('index.html', url=url, keyword_frequency_map=keyword_frequency_map)
