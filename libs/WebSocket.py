import json

from websocket import create_connection


class WebSocket():
    def __init__(self, url):
        self.url = url
        self.timeout = 60
        self.ws_conn = create_connection(self.url, self.timeout)

    def createConnection(self):
        if not self.ws_conn:
            print("####FAILED to establish ws connection: " + self.url)
            print("ERROR: " + str(self.ws_conn))
            return False
        print("\n####SUCCEED to establish ws connection: " + self.url + "\n")
        return True

    def subcribeNewShardBlock(self):
        data = {"request": {"jsonrpc": "1.0", "method": "subcribenewshardblock", "params": [0], "id": 1},
                "subcription": "11", "type": 0, }
        self.ws_conn.send(json.dumps(data))
        print("Sent subcribenewshardblock")
        print("Receiving...")
        result = self.ws_conn.recv()
        print("Received '%s'" % result)
        return True

    def subcribePendingTransaction(self, txid):
        data = {"request": {"jsonrpc": "1.0", "method": "subcribependingtransaction", "params": [txid], "id": 1},
                "subcription": "11", "type": 0, }
        self.ws_conn.send(json.dumps(data))
        print("Sent subcribependingtransaction: " + txid)
        print("Receiving...")
        result = self.ws_conn.recv()
        print("Received '%s'" % result)
        return True

    def subcribeCrossOutputCoinByPrivatekey(self, privatekey):
        data = {"request": {"jsonrpc": "1.0", "method": "subcribecrossoutputcoinbyprivatekey", "params": [privatekey],
                            "id": 1}, "subcription": "11", "type": 0, }
        self.ws_conn.send(json.dumps(data))
        print("Sent subcribecrossoutputcoinbyprivatekey: " + privatekey)
        print("Receiving...")
        result = self.ws_conn.recv()
        print("Received '%s'" % result)
        return True

    def closeConnection(self):
        self.ws_conn.close()
