#!/usr/bin/python3.6
"""Part of bot wars."""


import requests
from bs4 import BeautifulSoup as bs
from collections import defaultdict


def list_mobs():
    """List all mobs from summonerswarskyarena.info."""
    get_list = bs(requests.get(
        'https://www.summonerswarskyarena.info/monster-list/').text, 'lxml')
    mobs = defaultdict(lambda: False)
    for i in get_list.find_all('tr', {'class': 'searchable'}):
        _name = i.attrs['data-search-text'].split()[0][1:-1].lower()
        mobs[_name] = defaultdict(lambda: False)
        mobs[_name]['name'] = _name.lower()
        mobs[_name]['link'] = i.find('a').attrs['href']
        mobs[_name]['element'] = i.attrs['data-element']
        mobs[_name]['class'] = i.find('h3').text
        mobs[_name]['early-runes'] = i.find(
            'td', {'class': 'early-runes'}).text
        mobs[_name]['late-runes'] = i.find(
            'td', {'class': 'late-runes'}).text

    return mobs
