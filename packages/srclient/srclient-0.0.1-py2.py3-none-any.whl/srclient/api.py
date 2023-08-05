import os
import coreapi
import logging

SCHEMA_URL = 'http://www.short-report.de/api/docs/'

class Api:
    '''The Short-Report Client
    This is a small client for the Short-Report API. You can use it for
    uploading your url to Short-Report.
    '''

    def __init__(self):
        self.error = False
        self.token = ''

        self.client = coreapi.Client()
        self.load_schema(SCHEMA_URL)
        self._load_token()

    def _get_token_file(self):
        '''Return the token file'''
        homeDir = os.path.expanduser('~')
        return os.path.join(homeDir, '.rs_client.token')

    def _save_token(self):
        with open(self._get_token_file(), 'w') as f:
            f.write(self.token)

    def _load_token(self):
        if os.path.isfile(self._get_token_file()):
            with open(self._get_token_file(), 'r') as f:
                self.token = f.read()
        if self.token != '': self._use_token()

    def _use_token(self):
        auth = coreapi.auth.TokenAuthentication(scheme='JWT', token=self.token)
        self.client = coreapi.Client(auth=auth)

    def _update_token(self, token):
        self.token = token
        self._use_token()
        self._save_token()

    def _action(self, action, params=None):
        if not self.schema:
            self.error = True
            return {}
        try:
            if params:
                return self.client.action(self.schema, action, params=params)
            return self.client.action(self.schema, action)
        except Exception as e:
            self.errors = True
        return {}

    def load_schema(self, url):
        '''Load a alternative schema form a url. Maybe you will
        try your own server.
        '''
        try:
            self.schema = self.client.get(url)
        except:
            self.client = coreapi.Client()
            try:
                self.schema = self.client.get(url)
            except:
                self.schema = None

    def login(self, username, password):
        '''Use your username and password to create a token.'''
        self.client = coreapi.Client()
        self.error = False
        action = ['token', 'create']
        params = {
            'username': username,
            'password': password,
        }
        result = self._action(action, params)
        if not self.error:
            self._update_token(result['token'])
            return True
        return False


    def link_list(self):
        '''Return all the links.'''
        return self._action(['link', 'list'])

    def link_create(self, url):
        '''Create a new link. This function needs the url of your post.'''
        return self._action(['link', 'create'], {'url': url})
