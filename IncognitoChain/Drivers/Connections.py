import json

import requests
from websocket import create_connection

from IncognitoChain.Drivers.Response import Response
from libs.AutoLog import DEBUG

rpc_test_net = "http://test-node.incognito.org:9334"
rpc_main_net = "http://main-node.incognito.org:9334"
rpc_dev_net = "http://dev-node.incognito.org:9334"

ws_test_net = ""
ws_dev_net = ""
ws_main_net = ""


class RpcConnection:

    def __init__(self, url, headers=None, id_num=None, json_rpc=None):
        if headers is None:
            self.headers = {'Content-Type': 'application/json'}
        else:
            self.headers = headers

        if id_num is None:
            self.id = 1
        else:
            self.id = id_num

        if json_rpc is None:
            self.json_rpc = "1.0"
        else:
            self.json_rpc = json_rpc

        self.base_url = url
        self.params = None
        self.method = None

    def with_id(self, new_id):
        self.id = new_id
        return self

    def with_jsonrpc(self, json_rpc):
        self.json_rpc = json_rpc
        return self

    def with_url(self, url):
        self.base_url = url
        return self

    def with_test_net(self):
        return self.with_url(rpc_test_net)

    def with_dev_net(self):
        self.with_url(rpc_dev_net)

    def with_main_net(self):
        self.with_url(rpc_main_net)

    def with_params(self, params):
        self.params = params
        return self

    def with_method(self, method):
        self.method = method
        return self

    def execute(self):
        data = {"jsonrpc": self.json_rpc,
                "id": self.id,
                "method": self.method,
                "params": self.params}
        print(f'!!! exec RCP {data} !!!')
        response = requests.post(self.base_url, data=json.dumps(data), headers=self.headers)
        return Response(json.loads(response.text))


class WebSocket(RpcConnection):
    def __init__(self, url, id_num=None, subscription=None, ws_type=None, timeout=None):
        super(WebSocket, self).__init__(url, None, id_num)

        if subscription is None:
            self.subscription = "11"
        else:
            self.subscription = subscription

        if ws_type is None:
            self.type = 0
        else:
            self.type = ws_type

        if timeout is None:
            timeout = 180
        self.url = url
        self.ws_conn = create_connection(self.url, timeout)

    def with_time_out(self, time: int):
        self.ws_conn.settimeout(time)

    def close(self):
        self.ws_conn.close()
        from libs.AutoLog import DEBUG
        DEBUG(self.url + " connection closed")

    def execute(self):
        data = {"request": {"jsonrpc": self.json_rpc, "method": self.method, "params": [self.params], "id": self.id},
                "subcription": self.subscription, "type": self.type}
        DEBUG(f'!!! Sending {self.method}')
        self.ws_conn.send(json.dumps(data))
        DEBUG(f'Receiving response')
        result = self.ws_conn.recv()
        return Response(json.loads(result))
