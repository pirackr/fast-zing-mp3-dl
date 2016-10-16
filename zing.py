import requests
import bs4
import json
from optparse import OptionParser
import sys


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
    data_xml_link = _fetch_data_xml(link)
    pass


song_name, link = get_mp3(sys.argv[1])
save_as(song_name, link)
