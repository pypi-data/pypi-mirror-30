#!/usr/bin/python3.6
"""Part of bot wars."""


from requests_html import HTMLSession


def list_events():
    """Get events of summoners wars."""
    s = HTMLSession()
    r = s.get(
        'https://forum.com2us.com/forum/main-forum/summoner-s-war/events-ab')
    s.close()
    return "\n".join([
        x.text for x in r.html.find("a.topic-title")[:5]])
