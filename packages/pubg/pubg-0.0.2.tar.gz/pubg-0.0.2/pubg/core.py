from .constants import Endpoint
from .objects import Match, Status
import requests


class Battlegrounds:
    def __init__(self, api_key, region):
        self.api_key = api_key
        self.region = region
        self.session = Session(api_key)

    def matches(self):
        json = self.session.get(Endpoint.matches.format(region=self.region))
        return Match(json)

    def status(self):
        json = self.session.get(Endpoint.status)
        return Status(json)


class Session:
    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': api_key,
            'Accept': 'application/vnd.api+json'
        })

    def get(self, endpoint):
        response = self.session.get(f'{Endpoint.base}{endpoint}')
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
