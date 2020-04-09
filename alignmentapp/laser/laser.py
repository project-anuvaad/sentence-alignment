#!/bin/python
import codecs
import os

import requests
import numpy as np

laser_url = os.environ.get('LASER_PATH', 'http://127.0.0.1:8050/vectorize')

class Laser:

    def __init__(self):
        pass

    def get_vect(self, query_in, lang):
        params = {"q": query_in, "lang": lang}
        resp = requests.get(url=laser_url, params=params).json()
        return resp["embedding"]