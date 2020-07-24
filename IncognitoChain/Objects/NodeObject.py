import time

from pexpect import pxssh

import IncognitoChain.Helpers.Logging as Log
from IncognitoChain.APIs.Bridge import BridgeRpc
from IncognitoChain.APIs.DEX import DexRpc
from IncognitoChain.APIs.Explore import ExploreRpc
from IncognitoChain.APIs.Portal import PortalRpc
from IncognitoChain.APIs.Subscription import SubscriptionWs
from IncognitoChain.APIs.System import SystemRpc
from IncognitoChain.APIs.Transaction import TransactionRpc
from IncognitoChain.Drivers.Connections import WebSocket, RpcConnection
from IncognitoChain.Drivers.Response import Response
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.AccountObject import Account
from IncognitoChain.Objects.BlockChainObjects import BlockChainCore
from IncognitoChain.Objects.PdeObjects import PDEStateInfo
from IncognitoChain.Objects.PortalObjects import PortalStateInfo


class Node:
    default_user = "root"
    default_password = 'xxx'
    default_address = "localhost"
    default_rpc_port = 9334
    default_ws_port = 19334

    def __init__(self, address=default_address, username=default_user, password=default_password,
                 rpc_port=default_rpc_port, ws_port=default_ws_port, validator: Account = None, sshkey=None,
                 node_name=None):
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
        self.validator: Account = validator

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
        :return: RpcConnection object
        """
        return self._rpc_connection

    def web_socket_connection(self) -> WebSocket:
        """
        get web socket to send your custom command
        :return: WebSocket object
        """
        return self._web_socket

    def transaction(self) -> TransactionRpc:
        """
        Transaction APIs by RPC
        :return: TransactionRpc object
        """
        return TransactionRpc(self._get_rpc_url())

    def system_rpc(self) -> SystemRpc:
        return SystemRpc(self._get_rpc_url())

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

    def portal(self) -> PortalRpc:
        return PortalRpc(self._get_rpc_url())

    def subscription(self) -> SubscriptionWs:
        """
        Subscription APIs on web socket
        :return: SubscriptionWs object
        """
        if self._web_socket is None:
            self._web_socket = WebSocket(self._get_ws_url())
        return SubscriptionWs(self._web_socket)

    def explore_rpc(self) -> ExploreRpc:
        return ExploreRpc(self._get_rpc_url())

    def get_latest_pde_state_info(self, beacon_height=None):
        if beacon_height is None:
            beacon_height = self.help_get_beacon_height()
        pde_state = self.dex().get_pde_state(beacon_height)
        return PDEStateInfo(pde_state.get_result())

    def get_latest_rate_between(self, token_id_1, token_id_2):
        """
        find latest rate between input tokens, return None if cannot find rate

        :param token_id_1:
        :param token_id_2:
        :return: List of [token 1 contributed amount, token 2 contributed amount]
        """
        beacon_height = self.help_get_beacon_height()

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

    def help_get_current_pde_status(self):
        current_beacon_height = self.help_get_beacon_height()
        return self.dex().get_pde_state(current_beacon_height)

    def help_get_pde_share_list(self, token_id_1, token_id_2):
        """

        :param token_id_1: token id to get share part
        :param token_id_2:
        :return: list of token 1 share
        """
        INFO(f"Get sum PDE share of {l6(token_id_1)}-{l6(token_id_2)}")
        pde_status = self.help_get_current_pde_status()
        beacon_height = pde_status.params().get_beacon_height()
        INFO(f"Checking pdeshare {l6(token_id_2)}-{l6(token_id_1)} or {l6(token_id_1)}-{l6(token_id_2)}")
        share_key_1_2 = f'pdeshare-{beacon_height}-{token_id_2}-{token_id_1}'
        share_key_2_1 = f'pdeshare-{beacon_height}-{token_id_1}-{token_id_2}'
        share_response = pde_status.get_pde_share()

        pde_share_list = [value for key, value in share_response.items() if share_key_1_2 in key.lower()]
        if pde_share_list:
            INFO(f'Found pdeshare-{beacon_height}-{l6(token_id_2)}-{l6(token_id_1)}')
            return pde_share_list

        pde_share_list = [value for key, value in share_response.items() if share_key_2_1 in key.lower()]
        INFO(f'Found pdeshare-{beacon_height}-{l6(token_id_1)}-{l6(token_id_2)}')
        if pde_share_list:
            INFO(f'Found pdeshare-{beacon_height}-{l6(token_id_1)}-{l6(token_id_2)}')
            return pde_share_list

        INFO(f'{share_key_1_2} or {share_key_2_1} not found')
        return None

    def help_get_beacon_height(self):
        chain_info = BlockChainCore(self.system_rpc().get_block_chain_info().get_result())
        return chain_info.get_beacon_block().get_height()

    def help_get_beacon_height_in_best_state_detail(self, refresh_cache=True):
        beacon_height = self.system_rpc().get_beacon_best_state_detail(refresh_cache).get_beacon_height()
        INFO(f"Current beacon height = {beacon_height}")
        return beacon_height

    def help_clear_mem_pool(self):
        list_tx = self.system_rpc().get_mem_pool().get_result('ListTxs')
        for tx in list_tx:
            self.system_rpc().remove_tx_in_mem_pool(tx['TxID'])

    def help_count_shard_committee(self, refresh_cache=False):
        best = self.system_rpc().get_beacon_best_state_detail(refresh_cache)
        shard_committee_list = best.get_result()['ShardCommittee']
        return len(shard_committee_list)

    def help_count_committee_in_shard(self, shard_id, refresh_cache=False):
        best = self.system_rpc().get_beacon_best_state_detail(refresh_cache)
        shard_committee_list = best.get_result()['ShardCommittee']
        shard_committee = shard_committee_list[f'{shard_id}']
        return len(shard_committee)

    def help_get_current_epoch(self, refresh_cache=True):
        INFO(f'Get current epoch number')
        beacon_best_state = self.system_rpc().get_beacon_best_state_detail(refresh_cache)
        epoch = beacon_best_state.get_result('Epoch')
        INFO(f"Current epoch = {epoch}")
        return epoch

    def help_wait_till_epoch(self, epoch_number, pool_time=30, timeout=180):
        INFO(f'Wait until epoch {epoch_number}, check every {pool_time}s, timeout {timeout}s')
        epoch = self.help_get_current_epoch()
        if epoch >= epoch_number:
            return epoch
        time_start = time.perf_counter()
        while epoch < epoch_number:
            WAIT(pool_time)
            epoch = self.help_get_current_epoch()
            if epoch == epoch_number:
                INFO(f"Now epoch = {epoch}")
                return epoch
            time_current = time.perf_counter()
            if time_current - time_start > timeout:
                INFO('Timeout')
                return None

    def help_wait_till_next_epoch(self):
        current_epoch = self.help_get_current_epoch()
        return self.help_wait_till_epoch(current_epoch + 1)

    def get_latest_portal_state(self, beacon_height=None):
        INFO(f'Get latest portal state')
        if beacon_height is None:
            beacon_height = self.help_get_beacon_height()
        return self.portal().get_portal_state(beacon_height)

    def get_latest_portal_state_info(self, beacon_height=None):
        return PortalStateInfo(self.get_latest_portal_state(beacon_height).get_result())

    ##########
    # BRIDGE
    ##########

    # ISSUE centralize token is performed from a node

    def issue_centralize_token(self, account: Account, token_id, token_name, amount) -> Response:
        """
        initialize a new centralize token

        :return: Response Object

        """
        return self.bridge().issue_centralized_bridge_token(account.payment_key, token_id, token_name, amount)

        # WITHDRAW centralize token is performed from Account
        # def withdraw_centralize_token(self, account: Account, token_id, amount) -> Response:
