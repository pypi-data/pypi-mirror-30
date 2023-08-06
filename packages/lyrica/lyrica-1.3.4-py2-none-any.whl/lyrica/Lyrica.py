from lyrica.GeniusSession import GeniusSession
from lyrica.AZLyricsSession import AZLyricsSession
import os
from os.path import expanduser


class Lyrica(object):

    def __init__(self):
        self.directory = expanduser("~") + '/.lyrica'
        self.sessions = [
            GeniusSession(),
            AZLyricsSession()
        ]

    def get_cache_filename(self, artist, song):
        return (artist + '_' + song).replace(' ', '-') + '.txt'

    def save_lyrics(self, artist, song, lyrics):
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)

        fname = self.directory + '/' + self.get_cache_filename(artist, song)

        if not os.path.exists(fname):
            with open(fname, 'w+') as _file:
                _file.write(lyrics)
            _file.close()

    def get_cached_lyrics(self, artist, song):
        fname = self.directory + '/' + self.get_cache_filename(artist, song)

        if os.path.isfile(fname):
            contents = ''

            with open(fname) as _file:
                contents = _file.read()
            _file.close()

            return contents

    def get_lyrics(self, artist, song):
        for session in self.sessions:
            cached_lyrics = self.get_cached_lyrics(artist, song)
            lyrics = session.get_lyrics(artist, song) if not cached_lyrics\
                else cached_lyrics

            if lyrics and not cached_lyrics:
                self.save_lyrics(artist, song, lyrics)

            return lyrics
