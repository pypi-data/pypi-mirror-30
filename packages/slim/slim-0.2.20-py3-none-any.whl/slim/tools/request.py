# >= python3.6 only
import json
import requests


'''
config = {
    'remote': {
        'API_SERVER': 'http://localhost:9999',
        'WS_SERVER': 'ws://localhost:9999/ws',
        'authMode': 'access_token'  # access_token / access_token_in_params / cookie
    },
    'access_token': None
}
'''


class UnexpectedResponseException(Exception):
    pass


def do_request(config, method, url, params=None, data=None, role=None):
    headers = {}
    if params is None: params = {}
    auth_mode = config['remote']['authMode']

    if auth_mode in ('access_token', 'access_token_in_params'):
        token = config.get('access_token', None)
        if auth_mode == 'access_token':
            headers['AccessToken'] = token
        else:
            params['AccessToken'] = token

    if role:
        headers['Role'] = role

    if method == 'GET':
        resp = requests.get(url, params=params, headers=headers)
    elif method == 'POST':
        resp = requests.post(url, params=params, data=data)
    else:
        resp = None

    if resp:
        if resp.status_code != 200:
            raise UnexpectedResponseException("status: %d text: %r" % (resp.status_code, resp.content))
        try:
            resp.json()
        except json.JSONDecodeError:
            raise UnexpectedResponseException("status: %d text: %r" % (resp.status_code, resp.content))


class SlimViewRequest:
    def __init__(self, config, path):
        self.config = config
        self.path = path
        self.urlPrefix = f"{self.config['remote']['API_SERVER']}/api/{path}"

    def get(self, params=None, role=None):
        if params and 'loadfk' in params:
            params['loadfk'] = json.loads(params['loadfk'])
        return do_request(self.config, 'GET', f'{self.urlPrefix}/get', params, role=role)

    def list(self, params=None, page=1, size=None, role=None):
        if params and 'loadfk' in params:
            params['loadfk'] = json.loads(params['loadfk'])
        url = f'{self.urlPrefix}/list/{page}'
        if size: url += f'/{size}'
        return do_request(self.config, 'GET', url, params, role=role)

    def set(self, params, data, role=None):
        return do_request(self.config, 'POST', f'{self.urlPrefix}/get', params, data, role)

    def new(self, data, role=None):
        return do_request(self.config, 'POST', f'{self.urlPrefix}/new', {}, data, role)

    def delete(self, params, role=None):
        return do_request(self.config, 'POST', f'{self.urlPrefix}/new', params, {}, role)
