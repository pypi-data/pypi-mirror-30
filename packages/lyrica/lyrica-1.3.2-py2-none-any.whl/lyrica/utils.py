def clean_lyrics(lyrics):
    unwanted_chars = ['\r\n', '\n', ' ']
    pos = 0
    has_bad_chars = False

    for char in lyrics:
        if char in unwanted_chars:
            pos += 1
            has_bad_chars = True
            continue
        else:
            break

    if has_bad_chars:
        lyrics = lyrics[pos:]

    pos = len(lyrics)
    has_bad_chars = False

    for char in lyrics[::-1]:
        if char in unwanted_chars:
            pos -= 1
            has_bad_chars = True
            continue
        else:
            break

    if has_bad_chars:
        lyrics = lyrics[:pos]

    return lyrics
