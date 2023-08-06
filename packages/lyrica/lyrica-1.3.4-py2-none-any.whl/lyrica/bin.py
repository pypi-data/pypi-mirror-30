import argparse
from lyrica.Lyrica import Lyrica


parser = argparse.ArgumentParser()
parser.add_argument("artist")
parser.add_argument("song")
args = parser.parse_args()


def run():
    lyrica = Lyrica()

    lyrics = lyrica.get_lyrics(args.artist, args.song)

    print lyrics if lyrics else 'No lyrics was found'
