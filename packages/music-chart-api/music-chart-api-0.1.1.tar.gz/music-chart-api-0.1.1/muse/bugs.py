from bs4 import BeautifulSoup as Soup
from muse.util import HeadlessChrome

import time

"""
    Module for bugs music chart API
    
    Attribute:
        SITE_URL: Path for bugs web site
        REAL_TIME_CHART: Path for bugs real time chart page
"""

SITE_URL = "https://music.bugs.co.kr"
REAL_TIME_CHART = "{0}/chart".format(SITE_URL)


def get_real_time_chart_songs():
    """
        Get top 100 songs from
        melon real time chart

        Return:
            list: Top 100 songs from real time chart
    """

    songs = []

    with HeadlessChrome() as chrome:
        # move into real time chart page
        chrome.get(REAL_TIME_CHART)

        # Delay 5 seconds and load document to prevent request latency
        time.sleep(5)
        soup = Soup(chrome.page_source, 'html.parser')

        # parse table rows contains information of track
        for row in soup.select('tr[rowtype=track]'):
            song = {
                'rank': row.select('div.ranking > strong')[0].get_text().strip(),
                'title': row.select('p.title')[0].get_text().strip(),
                'artist': row.select('p.artist')[0].get_text().strip(),
                'album': row.select('a.album')[0].get_text().strip()
            }

            songs.append(song)

    return songs
