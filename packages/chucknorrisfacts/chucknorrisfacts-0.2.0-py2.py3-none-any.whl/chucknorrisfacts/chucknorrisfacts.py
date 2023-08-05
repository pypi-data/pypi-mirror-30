# -*- coding: utf-8 -*-

"""Main module"""
from __future__ import print_function
import json
from requests import get


def cnfacts():
    """Display a random Chuck Norris Jokes"""
    url = 'https://api.chucknorris.io/jokes/random'
    datafull = get(url).text
    info = json.loads(datafull)
    fact = info["value"]
    print("*** Chuck Norris Facts ***")
    print('\033[1;34m'+fact+'\033[0m')
    print("***")
    return None
