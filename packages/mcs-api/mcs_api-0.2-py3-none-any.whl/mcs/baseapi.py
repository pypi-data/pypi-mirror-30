class BaseAPI(object):
    """ Class Providing Base API Functionality """

    def __init__(self, token, url, version):

        self.token = token
        self.url = url
        self.version = version

        # Check the environment, and set some sensible defaults
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

        self.subapis = []

    def set_token(self, token):
        """ Set the token for this and all sub API's """
        self.token = token
        self.session.headers.update({
            'Authorization': 'Bearer {}'.format(self.token)
        })

        for api in self.subapis:
            getattr(self, api).set_token(token)

    def set_version(self, version):
        """ Set the version for this and all sub API's """
        self.version = version
        self.session.headers.update({
            'Api-Version': self.version,
        })

        for api in self.subapis:
            getattr(self, api).set_version(version)

    def set_URL(self, url):
        """ Set the version for this and all sub API's """
        self.url = url

        for api in self.subapis:
            getattr(self, api).set_URL(url)

    def __get(self, path, params={}, headers={}):
        url = "{}/{}".format(self.url, path)
        return self.session.get(url, params=params, headers=headers)

    def __post(self, path, params={}, data={}, headers={}):
        url = "{}/{}".format(self.url, path)
        headers['content-type'] = 'application/json'
        return self.session.post(url, params=params, data=data, headers=headers)

    def __put(self, path, params={}, data={}, headers={}):
        url = "{}/{}".format(self.url, path)
        headers['content-type'] = 'application/json'
        return self.session.put(url, params=params, data=data, headers=headers)

    def __delete(self, path, params={}, data={}, headers={}):
        url = "{}/{}".format(self.url, path)
        headers['content-type'] = 'application/json'
        return self.session.delete(url, params=params, data=data, headers=headers)


