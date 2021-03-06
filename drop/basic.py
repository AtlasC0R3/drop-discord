import random

import duckduckpy
import requests
import lyricsgenius

import drop.ext as ext

genius = None


def owofy(string: str):
    for old, new in ext.OwofyData.owofy_letters.items():
        string = string.replace(old, new)
    while '!' in string:
        string = string.replace('!', random.choice(ext.OwofyData.owofy_exclamations), 1)
    return string


def search(to_search: str):
    response = duckduckpy.query(to_search, user_agent=u'duckduckpy 0.2', no_redirect=False, no_html=True,
                                skip_disambig=True, container='dict')
    if response['abstract']:
        if response.get('infobox'):
            infobox = response['infobox']['content']
            is_infobox = True
        else:
            infobox = []
            is_infobox = False
        image = None
        if response['image']:
            if response['image'].startswith('/'):
                image = 'https://duckduckgo.com' + response['image']
            else:
                image = response['image']
        result = {
            "title": response['heading'],
            "description": ext.format_html(response.get('abstract_text')),
            "url": response['abstract_url'],
            "source": response['abstract_source'],
            "image": image,
            "fields": [],
            "infobox": is_infobox
        }
        for info in infobox:
            if info['data_type'] == 'string':
                if len(info['value']) >= 256:
                    value = ''.join(list(info['value'])[:253]) + '...'
                else:
                    value = info['value']
                result["fields"].append({
                    "name": info['label'],
                    "value": value
                })
        return result
    elif response['related_topics']:
        description = response.get('abstract_text')
        result = {
            "title": response['heading'],
            "description": description,
            "url": response.get('abstract_url'),
            "source": response['abstract_source'],
            "fields": [],
            "image": None,
            "infobox": False
        }
        for topic in response['related_topics'][:5]:
            if topic.get('topics'):
                pass  # not really what we're looking for
            else:
                name = topic.get('text')
                if len(name) >= 256:
                    name = ''.join(list(name)[:253]) + '...'
                if ' - ' in name:
                    things = name.split(' - ')
                    name = things[0]
                    description = ' - '.join(things[1:]) + '\n' + f"({topic.get('first_url')})"
                else:
                    description = topic.get('first_url')
                result["fields"].append({
                    "name": name,
                    "value": description
                })
        return result
    else:
        return None


def init_genius(token):
    global genius
    try:
        genius = lyricsgenius.Genius(token, verbose=False, remove_section_headers=True,
                                     skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])
    except TypeError:
        # Invalid token
        print("FIXME: Genius token invalid")
        genius = None


# noinspection PyUnresolvedReferences
def get_lyrics(artist, title):
    if genius:
        try:
            song = genius.search_song(title=title, artist=artist)
            # Fun fact: that's how I discovered that GHOST by Camellia (the song every beat saber player hates the most)
            # has lyrics, and that they lead to youtu.be/DkrzV5GIQXQ! how the actual fuck did i get here
            # I am now in shock and terrified. If anyone's into ARGs and reading this, well here you go.
            # It appears to be in Japanese though. Anyway, enough 3 minutes wasted.
        except requests.exceptions.HTTPError:
            song = None
            print("FIXME: Genius API token probably not working")
        if song:
            return song
    # no genius, woopsies
    return None


# noinspection PyUnresolvedReferences
def get_artist(artist):
    if genius:
        try:
            songs = genius.search_artist(artist, max_songs=5, sort='popularity').songs
        except requests.exceptions.HTTPError:
            songs = None
            print("FIXME: Genius API token probably not working")
        if songs:
            lyrics = []
            for song in songs:
                lyric = song.lyrics.split('\n')
                lyrics.append([song.title, lyric[:5], song.url])
            artist_name = songs[0].artist
            return ['Genius', [artist_name, lyrics]]
    return ['nothing', []]
