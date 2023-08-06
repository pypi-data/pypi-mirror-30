from lyrica.SiteSession import SiteSession
from bs4 import BeautifulSoup
from lyrica.utils import clean_lyrics


class GeniusSession(SiteSession):

    def __init__(self):
        SiteSession.__init__(self)
        self.base_url = 'https://genius.com/'

    def get_lyrics(self, artist, song):
        url = (self.base_url + artist + '-' + song + '-lyrics')\
            .replace(' ', '-')

        resp = self.session.get(url)

        soup = BeautifulSoup(resp.text, 'html.parser')
        lyrics_element = soup.find('div', {'class': 'lyrics'})

        return clean_lyrics(lyrics_element.text) if lyrics_element else None
