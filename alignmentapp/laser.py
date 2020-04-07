#!/bin/python
import codecs

import requests


class Laser:

    def __init__(self):
        pass

    def get_vect(self, query_in, lang, address='127.0.0.1:8050'):
        url = "http://" + address + "/vectorize"
        params = {"q": query_in, "lang": lang}
        resp = requests.get(url=url, params=params).json()
        return resp["embedding"]