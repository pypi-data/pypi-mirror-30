from bs4 import BeautifulSoup as Soup
from muse.util import HeadlessChrome

import time

SITE_URL = 'http://www.melon.com'
REAL_TIME_CHART = '{0}/chart/index.htm'.format(SITE_URL)

"""
    Module for melon music chart API

    Attribute:
        SITE_URL: Path for melon web site
        REAL_TIME_CHART: Path for melon real time chart page
"""


def get_real_time_chart_songs():
    """
        Get top 100 songs
        from melon real time chart

        Return:
            list: top 100 songs from melon real time chart
    """

    songs = []

    with HeadlessChrome() as chrome:
        chrome.get(REAL_TIME_CHART)

        # Delay 5 seconds and load document to prevent request latency
        time.sleep(5)
        soup = Soup(chrome.page_source, 'html.parser')

        for row in soup.select('tr.lst50, tr.lst100'):
            song = {
                'rank': row.select('span.rank')[0].get_text().strip(),
                'title': row.select('div.rank01')[0].get_text().strip(),
                'artist': row.select('div.rank02 > span.checkEllipsis')[0].get_text().strip(),
                'album': row.select('div.rank03')[0].get_text().strip()
            }

            songs.append(song)

    return songs


