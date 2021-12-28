import json

import requests
from pexpect import pxssh
from urllib3.exceptions import NewConnectionError
from websocket import create_connection

from Drivers.Response import Response
from Helpers.Logging import config_logger

logger = config_logger(__name__)


class RpcConnection:
    DEFAULT_JSON_RPC = "1.0"
    DEFAULT_HEADER = {'Content-Type': 'application/json'}
    DEFAULT_ID = 1
    DEFAULT_TIMEOUT = 320

    def __init__(self, url, headers=None, id_num=None, json_rpc=None):
        id_num = RpcConnection.DEFAULT_ID if id_num is None else id_num
        json_rpc = RpcConnection.DEFAULT_JSON_RPC if json_rpc is None else json_rpc

        self._headers = RpcConnection.DEFAULT_HEADER if headers is None else headers
        self._base_url = url
        self._payload = {"jsonrpc": json_rpc, "id": id_num}

    def with_id(self, new_id):
        self._payload['id'] = new_id
        return self

    def with_json_rpc(self, json_rpc):
        self._payload['jsonrpc'] = json_rpc
        return self

    def with_url(self, url):
        self._base_url = url
        return self

    def with_params(self, params):
        self._payload["params"] = params
        return self

    def with_method(self, method):
        self._payload["method"] = method
        return self

    def execute(self):
        try:
            logger.debug(f'exec RCP: {self._base_url} \n{json.dumps(self._payload, indent=3)}')
            response = requests.post(self._base_url, data=json.dumps(self._payload),
                                     headers=self._headers, timeout=RpcConnection.DEFAULT_TIMEOUT)
        except NewConnectionError:
            logger.error('Connection refused')
        return Response(response)

    def print_pay_load(self):
        print(f'RCP: {self._base_url} \n{json.dumps(self._payload, indent=3)}')
        return self

    def set_payload(self, payload):
        self._payload = payload
        return self


class WebSocket(RpcConnection):
    """
    must open connection before sending command on Web Socket
    """

    def __init__(self, url, id_num=None, subscription=None, ws_type=None, timeout=None):
        super(WebSocket, self).__init__(url, None, id_num)

        if subscription is None:
            self.__subscription = "11"
        else:
            self.__subscription = subscription

        if ws_type is None:
            self.__type = 0
        else:
            self.__type = ws_type

        if timeout is None:
            self.__timeout = 180
        self._url = url
        self._ws_conn = None

    def open(self):
        if self._ws_conn is None:
            logger.debug('Open new web socket connection')
            self._ws_conn = create_connection(self._url, self.__timeout)
            return
        if not self.is_alive():
            logger.debug('Current ws connection is dead, open new one')
            self._ws_conn = create_connection(self._url, self.__timeout)
            return
        logger.debug('WS connection is alive, use existing one')

    def close(self):
        self._ws_conn.close()
        logger.debug(self._url + " Connection closed")

    def is_alive(self):
        logger.debug(f"Is web socket connection alive?{self._ws_conn.connected}")
        return self._ws_conn.connected

    def with_time_out(self, time: int):
        logger.debug(f'Setting timeout = {time} seconds')
        self.open()
        self._ws_conn.settimeout(time)
        return self

    def execute(self, close_when_done=True):
        self.open()
        data = {"request": self._payload,
                "subcription": self.__subscription, "type": self.__type}
        logger.debug(f'exec WS: {self._base_url} \n{json.dumps(data, indent=3)}')
        self._ws_conn.send(json.dumps(data))
        result = self._ws_conn.recv()
        if close_when_done:
            self.close()
        return Response(result, self._url)


class SshSession(pxssh.pxssh):
    def __init__(self, address=None, username=None, password=None, sshkey=None):
        super().__init__()
        self._address = address
        self._username = username
        self._password = password
        self._sshkey = sshkey
        self._cache = {}

    def ssh_connect(self):
        # if self._password is not None and self._username is not None:
        #     Log.INFO(f'SSH logging in with password. User: {self._username}/{self._password}')
        #     self.login(self._address, self._username, password=self._password)
        #     return self
        if self._sshkey is not None:
            logger.info(f'SSH logging to {self._address} with ssh key. User: {self._username}')
            self.login(self._address, self._username, ssh_key=self._sshkey)
            return self

    def disconnect(self):
        self.logout()
        logger.info(f'SSH logout of: {self._address}')

    def send_cmd(self, command):
        """
        @param command:
        @return: command output as a list of strings, with each item of the list is a line of command output
        """
        logger.info(f'Send command via ssh: {command}')
        self.sendline(command)
        self.prompt()
        response = self.before.decode('utf-8')
        response_list = response.split('\n')
        logger.debug(response)
        if command[-1] == '&' and command[-2] != '&':
            pass
        else:
            return response_list

    def goto_folder(self, folder):
        return self.send_cmd(f'cd {folder}')
