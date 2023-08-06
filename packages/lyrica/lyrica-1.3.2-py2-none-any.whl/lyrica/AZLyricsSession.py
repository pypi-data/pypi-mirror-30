from lyrica.SiteSession import SiteSession
from bs4 import BeautifulSoup
from lyrica.utils import clean_lyrics


class AZLyricsSession(SiteSession):

    def __init__(self):
        SiteSession.__init__(self)
        self.base_url = 'https://www.azlyrics.com/lyrics'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3)\
            AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/65.0.3325.181 Safari/537.36'
        }

    def get_lyrics(self, artist, song):
        url = self.base_url + '/{}/{}.html'.format(
            artist.replace(' ', ''),
            song.replace(' ', '')
        )

        resp = self.session.get(url, headers=self.headers)

        soup = BeautifulSoup(resp.text, 'html.parser')
        element = soup.select_one('''
            body > div.container.main-page >
            div > div.col-xs-12.col-lg-8.text-center >
            div:nth-of-type(5)
        ''')

        return clean_lyrics(element.text) if element else None
