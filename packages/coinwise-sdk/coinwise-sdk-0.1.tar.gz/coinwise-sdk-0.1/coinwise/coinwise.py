import requests
import urllib.parse
import status

from coinwise import coinwise_confs
from coinwise.exceptions import CoinWiseInvalidUserException, CoinWiseException


class CoinWise(object):
    def __init__(self, username, password, client_id, instance_id, http_client=requests, staging_mode=True):
        self.instance_id = instance_id
        self.client_id = client_id
        self.conf = coinwise_confs
        self.password = password
        self.username = username
        self.http_client = http_client
        self.base_url = self.conf.STAGING_URL if staging_mode else self.conf.PRODUCTION_URL

    def login(self):
        path = 'login'
        return self.__get(path=path)

    def create_invoice(self, value, extra_msg, label, hex_dark, hex_light):
        params = {
            'value': value, 'extra': extra_msg, 'label': label, 'dark': hex_dark, 'light': hex_light
        }
        return self.__get(params=params)

    def check_invoice(self, invoice_id, waitting_method=False):
        path = '{invoice_id}'.format(invoice_id=invoice_id)
        params = {}
        if waitting_method:
            params = {'transition': 'new­incoming'}
        return self.__get(path=path, params=params)

    def invoce_history(self, number_invoices=100):
        path = 'history'
        params = {"last": number_invoices}
        return self.__get(path=path, params=params)


    def __get(self, path=None, params={}):
        url = self.__url_join(path)
        print(url)
        print(params)
        response = requests.get(url, params=params, headers=self.__headers(), auth=(self.username, self.password))
        return response

    def __url_join(self, path):
        if path:
            url = urllib.parse.urljoin(self.base_url, path)
        else:
            url = self.base_url[:-1]
        return url.format(client_id=self.client_id, instance_id=self.instance_id)

    def __headers(self):
        return {
            'Content-Type': 'application/json'
        }


