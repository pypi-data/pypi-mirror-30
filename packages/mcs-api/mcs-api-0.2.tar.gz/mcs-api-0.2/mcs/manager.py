from requests import Session
import json
import os

class Manager(object):

    def __init__(self, token=None, version=None, url=None):

        self.token = token
        self.url = url
        self.version = version

        # Check the environment, and set some sensible default
        if not token:
            self.token = os.environ.get('MCS_JWT_TOKEN', '')

        if not url:
            self.url = os.environ.get('MCS_ENDPOINT', "https://api.macquariecloudservices.com")

        if not version:
            self.version = os.environ.get('MCS_VERSION', "1.0")

        # Setup session
        self.session = Session()
        self.session.headers.update({
            'Api-Version': self.version,
            'Authorization': 'Bearer {}'.format(self.token)
        })

    def get(self, path, params={}, headers={}):
        url = "{}/{}".format(self.url, path)
        return self.session.get(url, params=params, headers=headers).json()

    def post(self, path, params={}, data={}, headers={}):
        url = "{}/{}".format(self.url, path)
        headers['content-type'] = 'application/json'
        return self.session.post(url, params=params, data=data, headers=headers).json()

    def put(self, path, params={}, data={}, headers={}):
        url = "{}/{}".format(self.url, path)
        headers['content-type'] = 'application/json'
        return self.session.put(url, params=params, data=data, headers=headers).json()

    def delete(self, path, params={}, data={}, headers={}):
        url = "{}/{}".format(self.url, path)
        headers['content-type'] = 'application/json'
        return self.session.delete(url, params=params, data=data, headers=headers).json()