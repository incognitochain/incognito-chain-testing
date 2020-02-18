from pexpect import pxssh

import IncognitoChain.Helpers.Logging as Log
from IncognitoChain.APIs.Bridge import BridgeRpc
from IncognitoChain.APIs.DEX import DexRpc
from IncognitoChain.APIs.Subscription import SubscriptionWs
from IncognitoChain.APIs.Transaction import TransactionRpc
from IncognitoChain.Drivers.Connections import WebSocket, RpcConnection
from IncognitoChain.Drivers.Response import Response
from IncognitoChain.Objects.AccountObject import Account


class Node:
    default_user = "root"
    default_password = 'xxx'
    default_address = "localhost"
    default_rpc_port = 9334
    default_ws_port = 19334

    def __init__(self, address=default_address, username=default_user, password=default_password,
                 rpc_port=default_rpc_port, ws_port=default_ws_port, sshkey=None, node_name=None):
        self._address = address
        self._username = username
        self._password = password
        self._sshkey = sshkey
        self._rpc_port = rpc_port
        self._ws_port = ws_port
        self._node_name = node_name
        self._spawn = pxssh.pxssh()
        self._web_socket = None
        self._rpc_connection = RpcConnection(self._get_rpc_url())

    def ssh_connect(self):
        if self._password is not None:
            Log.INFO(f'SSH logging in with password. User: {self._username}')
            self._spawn.login(self._address, self._username, password=self._password)
            return self
        if self._sshkey is not None:
            Log.INFO(f'SSH logging in with ssh key. User: {self._username}')
            self._spawn.login(self._username, ssh_key=self._sshkey)
            return self

    def logout(self):
        self._spawn.logout()
        Log.INFO(f'SSH logout of: {self._address}')

    def send_cmd(self, command):
        if not self._spawn.isalive():
            self.ssh_connect()

        self._spawn.sendline(command)
        self._spawn.prompt()

    def _get_rpc_url(self):
        return f'http://{self._address}:{self._rpc_port}'

    def _get_ws_url(self):
        return f'ws://{self._address}:{self._ws_port}'

    def rpc_connection(self) -> RpcConnection:
        """
        get RPC connection to send custom command
        :return:
        """
        return self._rpc_connection

    def web_socket_connection(self) -> WebSocket:
        """
        get web socket to send your custom command
        :return: RpcConnection object
        """
        return self._web_socket

    def transaction(self) -> TransactionRpc:
        """
        Transaction APIs by RPC
        :return: TransactionRpc object
        """
        return TransactionRpc(self._get_rpc_url())

    def dex(self) -> DexRpc:
        """
        Decentralize Exchange APIs by RPC
        :return: DexRpc Object
        """
        return DexRpc(self._get_rpc_url())

    def bridge(self) -> BridgeRpc:
        """
        Bridge APIs by RPC
        :return: BridgeRpc object
        """
        return BridgeRpc(self._get_rpc_url())

    def subscription(self) -> SubscriptionWs:
        """
        Subscription APIs on web socket
        :return: SubscriptionWs object
        """
        if self._web_socket is None:
            self._web_socket = WebSocket(self._get_ws_url())
        return SubscriptionWs(self._web_socket)

    def get_latest_rate_between(self, token_id_1, token_id_2):
        """
        find latest rate between input tokens, return None if cannot find rate

        :param token_id_1:
        :param token_id_2:
        :return: List of [token 1 contributed amount, token 2 contributed amount]
        """
        best_state = self.dex().get_beacon_best_state()
        beacon_height = best_state.get_beacon_height()

        pde_state = self.dex().get_pde_state(beacon_height)

        try:
            pool_pair = f"pdepool-{beacon_height}-{token_id_1}-{token_id_2}"
            pool = pde_state.get_pde_pool_pairs()[pool_pair]
            rate = [pool["Token1PoolValue"], pool["Token2PoolValue"]]
            return rate
        except KeyError:
            try:
                pool_pair = f"pdepool-{beacon_height}-{token_id_2}-{token_id_1}"
                pool = pde_state.get_pde_pool_pairs()[pool_pair]
                rate = [pool["Token2PoolValue"], pool["Token1PoolValue"]]
                return rate
            except KeyError:
                return None
        return None

    ##########
    # BRIDGE
    ##########

    def issue_centralize_token(self, account: Account, token_id, token_name, amount) -> Response:
        """
        initialize a new centralize token

        :return: Response Object

        """
        return self.bridge().issue_centralized_bridge_token(account.payment_key, token_id, token_name, amount)

    def withdraw_centralize_token(self, account: Account, token_id, amount) -> Response:
        """
        withdrawal a centralize token

        :return: Response Object

        """
        return self.bridge().withdraw_centralized_bridge_token(account.private_key, token_id, amount)
