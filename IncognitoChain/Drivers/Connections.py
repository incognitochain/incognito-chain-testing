import json

import requests
from urllib3.exceptions import NewConnectionError
from websocket import create_connection

import IncognitoChain.Helpers.Logging as Log
from IncognitoChain.Drivers.Response import Response
from IncognitoChain.Helpers.Logging import DEBUG, ERROR

rpc_test_net = "http://test-node.incognito.org:9334"
rpc_main_net = "http://main-node.incognito.org:9334"
rpc_dev_net = "http://dev-node.incognito.org:9334"

ws_test_net = ""
ws_dev_net = ""
ws_main_net = ""


class RpcConnection:

    def __init__(self, url, headers=None, id_num=None, json_rpc=None):
        if headers is None:
            self._headers = {'Content-Type': 'application/json'}
        else:
            self._headers = headers

        if id_num is None:
            self._id = 1
        else:
            self._id = id_num

        if json_rpc is None:
            self._json_rpc = "1.0"
        else:
            self._json_rpc = json_rpc

        self._base_url = url
        self._params = None
        self._method = None

    def with_id(self, new_id):
        self._id = new_id
        return self

    def with_jsonrpc(self, json_rpc):
        self._json_rpc = json_rpc
        return self

    def with_url(self, url):
        self._base_url = url
        return self

    def with_test_net(self):
        return self.with_url(rpc_test_net)

    def with_dev_net(self):
        self.with_url(rpc_dev_net)

    def with_main_net(self):
        self.with_url(rpc_main_net)

    def with_params(self, params):
        self._params = params
        return self

    def with_method(self, method):
        self._method = method
        return self

    def execute(self):
        data = {"jsonrpc": self._json_rpc,
                "id": self._id,
                "method": self._method}
        if self._params is not None:
            data["params"] = self._params
        Log.DEBUG(f'exec RCP: {self._base_url} \n{json.dumps(data, indent=3)}')
        try:
            response = requests.post(self._base_url, data=json.dumps(data), headers=self._headers)
        except NewConnectionError:
            ERROR('Connection refused')
        return Response(response, f'From: {self._base_url}')


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
            self._ws_conn = create_connection(self._url, self.__timeout)
            DEBUG('Open web socket')
            return
        if not self.is_alive():
            self._ws_conn = create_connection(self._url, self.__timeout)

    def close(self):
        self._ws_conn.close()
        Log.DEBUG(self._url + " Connection closed")

    def is_alive(self):
        DEBUG(f"Is web socket connection alive?{self._ws_conn.connected}")
        return self._ws_conn.connected

    def with_time_out(self, time: int):
        DEBUG(f'Setting timeout = {time} seconds')
        self.open()
        self._ws_conn.settimeout(time)
        return self

    def execute(self, close_when_done=True):
        data = {"request": {"jsonrpc": self._json_rpc, "method": self._method, "params": self._params,
                            "id": self._id},
                "subcription": self.__subscription, "type": self.__type}
        self.open()
        Log.DEBUG(f'exec WS: {self._base_url} \n{json.dumps(data, indent=3)}')
        self._ws_conn.send(json.dumps(data))
        Log.DEBUG(f'Receiving response')
        result = self._ws_conn.recv()
        if close_when_done:
            self.close()
        return Response(json.loads(result))
