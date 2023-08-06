from lyrica.GeniusSession import GeniusSession
from lyrica.AZLyricsSession import AZLyricsSession


class Lyrica(object):

    def __init__(self):
        self.sessions = [
            GeniusSession(),
            AZLyricsSession()
        ]

    def get_lyrics(self, artist, song):
        for session in self.sessions:
            lyrics = session.get_lyrics(artist, song)

            if lyrics:
                return lyrics
