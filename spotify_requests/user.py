# -*- coding: utf-8 -*-
import sys
import requests
import json

class UserGrabber():
    """
    Class to make requests to retrieve data on user
    """
    def __init__(self, header):
        self.token = header
        self.headers = {'content-type': 'application/json', 'authorization': '%s' % self.token}
        self.url = 'https://api.spotify.com/v1/me'

    def get_user(self):
        r = requests.get(self.url, verify=True, headers=self.headers)
        if r.status_code // 100 == 2:
            user = self.handle_response(r)
        else:
            print(str(r))
            user = None
            exit()
        return user

    def handle_response(self, r):
        tracks = []
        r = json.loads(r.text)
        # choose what data to get from users
        user = {
            'id':r['id'],
            'uri':r['uri'],
            'email':r['email'],
            'country':r['country']
        }
        return user
