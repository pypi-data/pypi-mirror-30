import xmltodict
import requests

class Intuition(object):
    def __init__(self, url: str, app_token: str=""):
        self.base_url = url + '/db/'
        self.app_token = app_token
        self.ticket: str = None

    def _request(self, endpoint: str, payload: dict) -> dict:
        """
        Generic QuickBase request method. 

        Arguments:  
        endpoint -- almost always 'main' or a tableid  
        payload -- dictionary containing the URL parameters for the QuickBase API

        Returns: dictionary containing the API response
        """
        payload['ticket'] = self.ticket
        payload['apptoken'] = self.app_token
        endpoint = self.base_url + endpoint
        response = requests.get(endpoint, params=payload)
        response_dict = xmltodict.parse(response.text)['qdbapi']
        return response_dict

    def authenticate(self, username: str, password: str, hours: int=24) -> str:
        payload = {
            'a': 'API_Authenticate',
            'username': username,
            'password': password,
            'hours': str(hours)
        }
        response = self._request('main', payload)
        self.ticket = response['ticket']
        return self.ticket

    def do_query(self, tableid: str, query: str) -> dict:
        payload = {
            'a': 'API_DoQuery',
            'query': query
        }
        response = self._request(tableid, payload)
        return response
