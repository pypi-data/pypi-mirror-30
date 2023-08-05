#!/usr/bin/python3.6
"""Part of bot-wars"""


import re
import requests
from bot_wars.get_mobs import list_mobs
from bs4 import BeautifulSoup as bs
from collections import defaultdict


def get_info(mob):
    """Get info of mob."""
    mobs = list_mobs()
    dict_mob = defaultdict(lambda: False)
    get_info = bs(requests.get(mobs[mob]['link']).text, 'lxml')
    dict_mob[mob] = defaultdict(lambda: False)
    dict_mob[mob]['skills'] = defaultdict(lambda: False)
    for i in get_info.find_all('div', {'class': 'skill-info'}):
        skill_name = i.find('h5', {'class': 'skill-title'}).text
        dict_mob[mob]['skills'][skill_name] = defaultdict(lambda: False)
        description = i.find('div', {'class': 'description'}).text
        dict_mob[mob]['skills'][skill_name]['description'] = description
        if i.find('div', {'class': 'multiplier'}):
            multiplier = i.find('div', {'class': 'multiplier'}).text
            dict_mob[mob]['skills'][skill_name]['multiplier'] = multiplier
        if i.find('div', {'class': 'level-data'}):
            skill_up = "\n".join(re.findall(
                r"Lv.*%", i.find('div', {'class': 'level-data'}).text))
            dict_mob[mob]['skills'][skill_name]['skill_up'] = skill_up
    get_stats = get_info.find_all('table', {'class': 'major-stats'})
    list_stats = list(filter(
        None, re.sub(r'<[^>]+>', '|',
                     str(get_stats[-1].encode())).split('|')))[1:-1]
    list_stats_max = [x for x in list_stats if 'Min' not in x]
    dict_mob[mob]['stats'] = defaultdict(lambda: False)
    for x in zip(list_stats_max[:5], list_stats_max[-5:]):
        dict_mob[mob]['stats'][x[0]] = x[1]

    return dict_mob
