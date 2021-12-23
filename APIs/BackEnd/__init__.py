import json
import platform

import requests

from Drivers import ResponseBase
from Helpers.Logging import config_logger

logger = config_logger(__name__)


class BackEndApiBase:
    HEADER = {'accept-encoding': 'gzip',
              'content-type': 'application/json'}

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def post(self, path, data, headers=None):
        """
        @param headers: dict
        @param path:
        @param data:
        @return:
        """
        url = f"{self.endpoint}/{path}"
        headers = {**BackEndApiBase.HEADER, **headers} if isinstance(headers, dict) else BackEndApiBase.HEADER
        logger.debug(f'exec RCP: {url} \n{json.dumps(data, indent=3)}')
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return ResponseBase(response)

    def get(self, path, headers=None, **params):
        """
        @param headers:
        @param path:
        @param params:
        @return:
        """
        url = f"{self.endpoint}/{path}?"
        headers = {**BackEndApiBase.HEADER, **headers} if isinstance(headers, dict) else BackEndApiBase.HEADER
        for key, value in params.items():
            url += f'{key}={value}&'
        url = url.strip('&').strip('?')
        response = requests.get(url, headers=headers)
        return ResponseBase(response)


class BackEndApiWithAuth(BackEndApiBase):
    AUTH_TOKEN = ""

    def __init__(self, endpoint):
        super().__init__(endpoint)
        if not BackEndApiWithAuth.AUTH_TOKEN:
            self.get_auth_token()

    def get_auth_token(self, device_id=None, device_token=None):
        device_id = device_id if device_id else platform.node()
        device_token = device_token if device_token else platform.machine()
        post_DATA = {"DeviceID": device_id, "DeviceToken": device_token}
        BackEndApiWithAuth.AUTH_TOKEN = self.post("auth/new-token", post_DATA).get_result("Token")
        return BackEndApiWithAuth.AUTH_TOKEN

    def post(self, path, data, headers=None):
        return super(BackEndApiWithAuth, self). \
            post(path, data, {"Authorization": f"Bearer {BackEndApiWithAuth.AUTH_TOKEN}"})

    def get(self, path, headers=None, **params):
        return super(BackEndApiWithAuth, self). \
            get(path, {"Authorization": f"Bearer {BackEndApiWithAuth.AUTH_TOKEN}"}, **params)
