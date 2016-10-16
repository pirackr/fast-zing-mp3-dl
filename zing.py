import os
import re
import sys
import json
from argparse import ArgumentParser


import requests

import bs4
from lxml import etree


def save_as(file_name, link):
    with open(file_name, 'wb') as f:
        response = requests.get(link, stream=True)

        if not response.ok:
            raise Exception('Can\'t fetched the link!')

        for block in response.iter_content(1024):
            f.write(block)


def _name(artist, name):
    return '{name}-{artist}.mp3'.format(name=name, artist=artist).\
        replace(' ', '_')


def _name_without_extension(artist, name):
    return '{name}-{artist}'.format(name=name, artist=artist).\
        replace(' ', '_')


def _fetch_data_xml(link):
    response = requests.get(link)
    html = bs4.BeautifulSoup(response.content, 'html.parser')
    data_xml_link = html.find(id='html5player').attrs['data-xml']
    return data_xml_link


def get_mp3(link):
    data_xml_link = _fetch_data_xml(link)
    data_xml = requests.get(data_xml_link)
    # hey, zing devs, why json when you name it xml T_T?
    data = json.loads(data_xml.content)['data'][0]

    song_name = _name(data['artist'], data['name'])
    mp3_link = data['source_list'][1]
    link = 'http://org2.%s' % mp3_link

    return song_name, link


def get_album(link):
    pattern = 'album\/((.)+)\/'
    album = re.compile(pattern).search(link).group(1)

    data_xml_link = _fetch_data_xml(link)
    content = requests.get(data_xml_link).content
    xml = etree.XML(content)
    songs = []

    for item in xml.cssselect('data item'):
        name = item.find('title').text
        artist = item.find('performer').text
        # directly pull from their server
        link = item.find('source').text.replace('http://', 'http://org2.')
        songs.append((_name_without_extension(artist, name), link))

    return album, songs


def save_album(album, songs):
    if not os.path.exists(album):
        os.makedirs(album)

    for song in songs:
        name, link = song
        file_name = '{album}/{song_name}.mp3'.format(album=album,
                                                     song_name=name)
        save_as(file_name, link)


def main():
    parser = ArgumentParser()
    parser.add_argument('link', metavar='link', type=str)
    parser.add_argument('--single', action='store_true', dest='is_single')
    parser.add_argument('--album', action='store_false', dest='is_single')

    args = parser.parse_args()
    is_single = args.is_single
    link = args.link

    if is_single:
        song_name, mp3_link = get_mp3(link)
        save_as(song_name, mp3_link)
    else:
        album, songs = get_album(link)
        save_album(album, songs)


if __name__ == '__main__':
    main()
