import requests
import json
from APIs.CoinService.CoinServiceResponse import CoinServiceResponse
from Helpers.Logging import DEBUG


class CoinServiceApiBase:
    HEADER = {'accept-encoding': 'gzip',
              'content-type': 'application/json'}

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def post(self, path, data):
        """
        @param path:
        @param data:
        @return:
        """
        url = f"{self.endpoint}/{path}"
        DEBUG(f'exec RCP: {url} \n{json.dumps(data, indent=3)}')
        response = requests.post(url, data=json.dumps(data), headers=CoinServiceApiBase.HEADER)
        return CoinServiceResponse(response)

    def get(self, path, **params):
        """
        @param path:
        @param params:
        @return:
        """
        url = f"{self.endpoint}/{path}?"
        for key, value in params.items():
            url += f'{key}={value}&'
        url = url.strip('&')
        DEBUG(f'GET: {url}')
        response = requests.get(url, headers=CoinServiceApiBase.HEADER)
        return CoinServiceResponse(response)
