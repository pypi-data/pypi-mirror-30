import xmltodict
import requests
from copy import deepcopy
from lxml import etree

class Intuition(object):
    def __init__(self, url: str, app_token: str=""):
        self.base_url = url + '/db/'
        self.app_token = app_token
        self.ticket: str = None

        self.base_payload = etree.Element('qdbapi')

        if self.app_token:
            apptoken = etree.SubElement(self.base_payload, 'apptoken')
            apptoken.text = self.app_token
    
    def _make_xml_payload(self, payload: dict):
        _payload = deepcopy(self.base_payload)

        for k, v in payload.items():
            if k == 'fields':
                for l, j in payload[k].items():
                    node = etree.SubElement(_payload, 'field', name=l)
                    node.text = str(j)
            else:
                node = etree.SubElement(_payload, k)
                node.text = str(v)
        
        return _payload

    def _request(self, endpoint: str, action: str, payload: dict = None) -> dict:
        """
        Generic QuickBase request method. 

        Arguments:  
        endpoint -- almost always 'main' or a tableid  
        payload -- dictionary containing the URL parameters for the QuickBase API

        Returns: dictionary containing the API response
        """
        if not payload:
            payload = {}
        payload['ticket'] = self.ticket
        payload['apptoken'] = self.app_token
        payload = self._make_xml_payload(payload)
        endpoint = self.base_url + endpoint
        headers = {'Content-Type': 'application/xml', 'QUICKBASE-ACTION': action}
        response = requests.post(endpoint, data=etree.tostring(payload), headers=headers)
        response_dict = xmltodict.parse(response.text)['qdbapi']
        return response_dict

    def authenticate(self, username: str, password: str, hours: int=24) -> str:
        payload = {
            'username': username,
            'password': password,
            'hours': str(hours)
        }
        response = self._request('main', 'API_Authenticate', payload)
        self.ticket = response['ticket']
        return self.ticket

    def do_query(self, tableid: str, query: str) -> dict:
        payload = {
            'query': query
        }
        response = self._request(tableid, 'API_DoQuery', payload)
        return response

    def add_record(self, tableid: str, record: dict) -> dict:
        response = self._request(tableid, 'API_AddRecord', record)
        return response

    def delete_record(self, tableid: str, rid: str) -> dict:
        payload = {
            'rid': rid
        }
        response = self._request(tableid, 'API_DeleteRecord', payload)
        return response

    def update_record(self, tableid: str, record: dict) -> dict:
        payload = {
            'rid': record['rid']
        }
        payload.update(record)
        response = self._request(tableid, 'API_EditRecord', payload)
        return response

    def get_schema(self, tableid: str) -> dict:
        response = self._request(tableid, 'API_GetSchema')
        return response
