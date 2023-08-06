import sys
from json.decoder import JSONDecodeError

import requests


class ApiError(Exception):
    def __init__(self, response, *args) -> None:
        super().__init__(*args)
        self.response = response

    def format_console_error(self):
        print(self.response.json())


class GeniusClient(object):
    def __init__(self, api_url, token) -> None:
        super().__init__()

        self.api_url = api_url
        self.token = token

    def _get(self, service):
        headers = {'Authorization': f'Token {self.token}'}
        response = requests.get(f'{self.api_url}{service}', headers=headers)
        self.handle_error(service, response)
        return response.json()

    def _post(self, service, data):
        headers = {'Authorization': f'Token {self.token}'}
        response = requests.post(f'{self.api_url}{service}', headers=headers, json=data)
        self.handle_error(service, response)
        return response.json()

    def handle_error(self, service, response):
        if response.status_code >= 400:
            try:
                error = response.json()
                print(f'Error happened at /{service}:')
                if 'detail' in error:
                    print(error['detail'])
                else:
                    print(error)
            except JSONDecodeError:
                print(f'Unexpected error happened on Genius server when working with /{service}.')
                print(response.content)

            sys.exit()

    def list_requests(self):
        return self._get('genius/request/')

    def generate(self, files, name=None, collections=None):
        return self._post('genius/request/', {
            'name': name,
            'collections': ','.join(collections),
            'files': [{
                'name': name,
                'body': body
            } for name, body in files.items()]
        })
