import json
import os
import re
import subprocess
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Union, Dict

from APIs.Bridge import BridgeRpc
from APIs.DEX import DexRpc
from APIs.Explore import ExploreRpc
from APIs.Portal import PortalRpc
from APIs.Subscription import SubscriptionWs
from APIs.System import SystemRpc
from APIs.Transaction import TransactionRpc
from APIs.Utils import UtilsRpc
from APIs.pDEX_V3 import DEXv3RPC, ResponseGetEstimatedLPValue
from Configs.Configs import ChainConfig
from Configs.Constants import PRV_ID
from Drivers.Connections import SshSession
from Helpers import TestHelper
from Helpers.Logging import config_logger
from Helpers.TestHelper import l6, ChainHelper
from Helpers.Time import WAIT
from Objects.BeaconObject import BeaconBestStateDetailInfo, BeaconBlock, BeaconBestStateInfo
from Objects.BlockChainObjects import BlockChainCore
from Objects.CoinObject import BridgeTokenResponse, InChainTokenResponse
from Objects.CommitteeState import CommitteeState
from Objects.PdeObjects import PDEStateInfo
from Objects.PdexV3Objects import PdeV3State
from Objects.PortalObjects import PortalStateInfo
from Objects.ShardBlock import ShardBlock
from Objects.ShardState import ShardBestStateDetailInfo, ShardBestStateInfo
from Objects.ViewDetailBlock import AllViewDetail

logger = config_logger(__name__)


def action_over_ssh(func):
    def deco(self):
        from Objects.TestBedObject import TestBed
        try:
            if not self._ssh_session.isalive():
                TestBed.ssh_to(self)
        except AttributeError:
            TestBed.ssh_to(self)
        return func(self)

    return deco


class Node:
    default_user = "thach"
    default_password = '123123Az'
    default_address = "localhost"
    default_rpc_port = 9334
    default_ws_port = 19334
    default_ssh_pub_key = f"{os.getenv('HOME')}/.ssh/id_rsa"

    def __init__(self, address=default_address, username=default_user, password=default_password,
                 rpc_port=default_rpc_port, ws_port=default_ws_port, account=None, sshkey=default_ssh_pub_key,
                 url=None, node_name=None):
        self._address = address
        self._username = username
        self._password = password
        self._ssh_key = sshkey
        self._rpc_port = rpc_port
        self._ws_port = ws_port
        self._node_name = node_name
        self.account = account
        self.url = url
        if url is not None:
            self.parse_url(url)
        self._ssh_session = SshSession(self._address, self._username, self._password, self._ssh_key)
        self._cache = {"rpc": {}}

    def __str__(self):
        return f"{self._get_rpc_url()} ws:{self._ws_port}"

    def parse_url(self, url):
        import re
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if re.match(regex, url) is None:
            raise SyntaxError(f'Url {url} is not in correct format')

        self._address = url.split(':')[1].lstrip('//')
        try:
            self._rpc_port = int(url.split(':')[2].split('/')[0])
        except IndexError:
            self._rpc_port = 80

        return self

    def set_web_socket_port(self, port):
        self._ws_port = port
        return self

    def _get_rpc_url(self):
        if self.url is not None:
            return self.url
        self.url = f'http://{self._address}:{self._rpc_port}'
        return self.url

    def _get_ws_url(self):
        return f'ws://{self._address}:{self._ws_port}'

    def transaction(self) -> TransactionRpc:
        """
        Transaction APIs by RPC
        @return: TransactionRpc object
        """
        return TransactionRpc(self._get_rpc_url())

    def system_rpc(self) -> SystemRpc:
        return SystemRpc(self._get_rpc_url())

    def dex(self) -> DexRpc:
        """
        Decentralize Exchange APIs by RPC
        @return: DexRpc Object
        """
        return DexRpc(self._get_rpc_url())

    def dex_v3(self) -> DEXv3RPC:
        return DEXv3RPC(self._get_rpc_url())

    def bridge(self) -> BridgeRpc:
        """
        Bridge APIs by RPC
        @return: BridgeRpc object
        """
        return BridgeRpc(self._get_rpc_url())

    def portal(self) -> PortalRpc:
        return PortalRpc(self._get_rpc_url())

    def subscription(self) -> SubscriptionWs:
        """
        Subscription APIs on web socket
        @return: SubscriptionWs object
        """
        return SubscriptionWs(self._get_ws_url())

    def explore_rpc(self) -> ExploreRpc:
        return ExploreRpc(self._get_rpc_url())

    def util_rpc(self) -> UtilsRpc:
        return UtilsRpc(self._get_rpc_url())

    def get_tx_by_hash(self, tx_hash, interval=10, time_out=120):
        """
        @param tx_hash:
        @param interval:
        @param time_out: set = 0 to ignore interval, won't retry if got error in Response or block height = 0
        @return: TransactionDetail, use TransactionDetail.is_none() to check if it's an empty object
        """
        if tx_hash is None:
            raise ValueError("Tx id must not be none")
        logger.info(f"Getting transaction hash: {tx_hash}")
        while True:
            tx_detail = self.transaction().get_tx_by_hash(tx_hash)
            if tx_detail.get_error_msg():
                logger.info(tx_detail.get_error_msg())
                return tx_detail
            if tx_detail.is_confirmed():
                return tx_detail
            if time_out <= 0:
                break
            time_out -= interval
            WAIT(interval)
        logger.info("Time out, tx is not confirmed!")
        return tx_detail

    def get_latest_beacon_block(self, beacon_height=None):
        if beacon_height is None:
            beacon_height = self.help_get_beacon_height()
        logger.info(f'Get beacon block at height {beacon_height}')
        response = self.system_rpc().retrieve_beacon_block_by_height(beacon_height)
        return BeaconBlock(response.get_result()[0])

    def get_first_beacon_block_of_epoch(self, epoch=None):
        """
        @param epoch: epoch number
        @return: BeaconBlock obj of the first epoch of epoch.
        If epoch is specified, get first beacon block of that epoch
        If epoch is None,  get first beacon block of current epoch.
        If epoch = -1 then wait for the next epoch and get first beacon block of epoch
        """
        if epoch == -1:
            current_height = self.get_block_chain_info().get_beacon_block().get_height()
            current_epoch = ChainHelper.cal_epoch_from_height(current_height)
            if not ChainConfig.is_first_height_of_epoch(current_height):
                next_first_height = ChainHelper.cal_first_height_of_epoch(current_epoch + 1)
                wait_height = next_first_height + 1 - current_height
                time_till_next_epoch_first_block = ChainConfig.BLOCK_TIME * wait_height
                logger.info(f'Current epoch {current_epoch} Current height {current_height}, '
                            f'wait for {wait_height} height till height {current_height + wait_height}')
                # +1 just to make sure that the first block of epoch is already confirmed
                WAIT(time_till_next_epoch_first_block)
            else:
                logger.info(f'Current epoch {current_epoch} Current height {current_height}, no need to wait')
            epoch = current_epoch + 1
        elif epoch is None:
            epoch = self.help_get_current_epoch()
        else:
            pass

        beacon_height = TestHelper.ChainHelper.cal_first_height_of_epoch(epoch)
        return self.get_latest_beacon_block(beacon_height)

    def get_beacon_best_state_detail_info(self):
        return self.system_rpc().get_beacon_best_state_detail()

    def get_latest_pde_state_info(self, beacon_height=None):
        beacon_height = self.help_get_beacon_height() if not beacon_height else beacon_height
        pde_state = self.dex().get_pde_state(beacon_height)
        return PDEStateInfo(pde_state.get_result())

    def pde3_get_state(self, beacon_height=None, key_filter="All", id_filter="1", verbose=1):
        beacon_height = self.help_get_beacon_height() if not beacon_height else beacon_height
        logger.info(f'Get PDE3 state at beacon height: {beacon_height}, filter: {key_filter}')
        return self.dex_v3().get_pdev3_state(beacon_height, key_filter, id_filter, verbose)

    def pde3_make_trade_tx(self, private_key, token_sell, token_buy, sell_amount, min_acceptable, trade_path,
                           trading_fee, use_prv_fee=True):
        """
        @param private_key:
        @param token_sell:
        @param token_buy:
        @param sell_amount:
        @param min_acceptable:
        @param trade_path: list of pair id
        @param trading_fee:
        @param use_prv_fee:
        @return: tuple(tx hash, raw tx)
        """
        _path = f'{os.getcwd()}/bin'
        _exe_name = 'pde3-make-trade-tx'
        _binary = {'darwin': f'{_path}/{_exe_name}-mac',
                   'linux': f'{_path}/{_exe_name}-linux',
                   '*': f'{_path}/{_exe_name}-win'}
        exe = _binary.get(sys.platform, _binary["*"])
        logger.info(f"Making trade tx: private k: {private_key[-6:]}, sell-buy {token_sell[-6:]}-{token_buy[-6:]}, "
                    f"amount: {sell_amount}, path len: {len(trade_path)}")
        command = [exe, f'-url={self._get_rpc_url()}', f'-pk={private_key}', f'-s={token_sell}', f'-b={token_buy}',
                   f'-sa={sell_amount}', f'-ea={min_acceptable}', f'-tf={trading_fee}', f'-tp={",".join(trade_path)}',
                   f'-prvFee={use_prv_fee}']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                   universal_newlines=True)
        stdout, stderr = process.communicate()
        if "Error" in stdout:
            raise RuntimeError(stdout)
        output = json.loads(stdout)
        return output['Hash'], output['Transaction']

    def pde3_get_lp_value(self, pool_id, nft, beacon_height=0, extract_value=None) \
            -> Union[ResponseGetEstimatedLPValue, Dict[str, Union[int, ResponseGetEstimatedLPValue]]]:
        """
        get estimate LP value of NFT of pool id
        @param extract_value: TradingFee or PoolValue
        @param pool_id:
        @param nft:
        @param beacon_height:
        @return: {token id : int} or {token id : ResponseGetEstimatedLPValue} or {nft: {token: int} or
        {nft: {token: ResponseGetEstimatedLPValue}}
        """
        if isinstance(nft, str):
            lp_value = self.dex_v3().get_estimated_lp_value(pool_id, nft, beacon_height)
            return lp_value if not extract_value else lp_value.get_result(extract_value)
        with ThreadPoolExecutor() as tpe:
            threads = {nft: tpe.submit(self.dex_v3().get_estimated_lp_value, pool_id, nft, beacon_height) for nft in
                       nft}
        return {nft: future.result() for nft, future in threads.items()} if not extract_value else \
            {nft: future.result().get_result(extract_value) for nft, future in threads.items()}

    def pde3_get_lp_values_of_pools(self, pool_ids, pde_state=None, extract_value=None):
        """
        get estimate LP value of all provider of multiple pool
        @param pool_ids:
        @param pde_state:
        @param extract_value: TradingFee or PoolValue
        @return:
        """
        pde_state = pde_state if isinstance(pde_state, PdeV3State) else self.pde3_get_state()
        beacon_height = pde_state.rpc_params().get_beacon_height()
        providers_per_pool = {}
        for pool_id in pool_ids:
            providers = pde_state.get_pool_pair(id=pool_id).get_providers()
            providers_per_pool[pool_id] = self.pde3_get_lp_value(pool_id, providers, beacon_height, extract_value)
        return providers_per_pool

    def get_block_chain_info(self):
        return BlockChainCore(self.system_rpc().get_block_chain_info())

    def get_all_view_detail(self, chain_id):
        return AllViewDetail(self.system_rpc().get_all_view_detail(chain_id).get_result())

    def get_slashing_committee_detail(self, epoch):
        raw_data = self.system_rpc().get_slashing_committee_detail(epoch).get_result()
        dict_obj = {}
        for shard_id, committees in raw_data.items():
            committees_obj = []
            for committee in committees:
                committees_obj.append(BeaconBestStateDetailInfo().Committee(committee))
            dict_obj[shard_id] = committees_obj
        return

    def get_slashing_committee(self, epoch):
        return self.system_rpc().get_slashing_committee(epoch).get_result()

    def create_fork(self, block_fork_list, chain_id=1, num_of_branch=2, branch_tobe_continue=1):
        return self.system_rpc().create_fork(block_fork_list, chain_id, num_of_branch, branch_tobe_continue)

    def help_get_beacon_height(self):
        latest_height = self.get_block_chain_info().get_beacon_block().get_height()
        logger.info(f"Latest beacon height = {latest_height}")
        return latest_height

    def help_get_beacon_height_in_best_state_detail(self):
        beacon_height = self.get_beacon_best_state_info().get_beacon_height()
        logger.info(f"Current beacon height = {beacon_height}")
        return beacon_height

    def help_clear_mem_pool(self, tx=None):
        if tx == "all":
            mem_pool_res = self.system_rpc().get_mem_pool()
            list_tx = mem_pool_res.get_result('ListTxs')
            mem_pool_size = mem_pool_res.get_result("Size")
            logger.info(f"There are {mem_pool_size} tx(s) in mem pool. Cleaning now...")
            with ThreadPoolExecutor() as executor:
                for tx in list_tx:
                    executor.submit(self.system_rpc().remove_tx_in_mem_pool, tx['TxID'])
        self.system_rpc().remove_tx_in_mem_pool(tx)

    def help_get_current_epoch(self):
        """
        @return:
        """
        logger.debug(f'Get current epoch number')
        beacon_best_state = self.get_beacon_best_state_info()
        epoch = beacon_best_state.get_epoch()
        logger.debug(f"Current epoch = {epoch}")
        return epoch

    def help_watch_block_chain_info(self):
        """
        for manual debug only, this will print short block chain info every block height until KeyboardInterrupt happens
        @return:
        """
        try:
            while True:
                print(self.get_block_chain_info())
                WAIT(ChainConfig.BLOCK_TIME)
        except KeyboardInterrupt:
            pass

    def help_watch_pde_state(self):
        height = self.help_get_beacon_height()
        try:
            while True:
                logger.info(height)
                pde = self.get_latest_pde_state_info(height)
                waiting_str = "Waiting contributions:\n"
                for obj in pde.get_waiting_contributions():
                    waiting_str += f'\t\t{obj}\n'
                logger.info(waiting_str)
                pool_str = 'Pool:\n'
                for obj in pde.get_pde_pool_pairs():
                    pool_str += f'\t\t{obj}\n'
                logger.info(pool_str)
                share_str = 'PDE Shares:\n'
                for obj in pde._get_pde_share_objects():
                    share_str += f'\t\t{obj}\n'
                logger.info(share_str)
                fee_str = 'Fee:\n'
                for obj in pde._get_contributor_reward_objects():
                    fee_str += f'\t\t{obj}\n'
                logger.info(fee_str)
                WAIT(ChainConfig.BLOCK_TIME)
                height += 1
        except KeyboardInterrupt:
            pass

    def get_latest_portal_state_info(self, beacon_height=None):
        if beacon_height is None:
            beacon_height = self.help_get_beacon_height()
            logger.info(f'Get LATEST portal state at beacon height: {beacon_height}')
        else:
            logger.info(f'Get portal state at beacon height: {beacon_height}')

        portal_state_raw = self.portal().get_portal_state(beacon_height).expect_no_error()
        return PortalStateInfo(portal_state_raw.get_result())

    def cal_transaction_reward_from_beacon_block_info(self, epoch=None, token=None, shard_txs_fee_list=None, dcz=False):
        """
        Calculate reward of an epoch
        @param shard_txs_fee_list:
        @param token:
        @param epoch: if None, get latest epoch -1
        @return: dict { "DAO" : DAO_reward_amount
                        "beacon" : total_beacon_reward_amount
                        "0" : shard0_reward_amount
                        "1" : shard1_reward_amount
                        .....
                        }
        @param dcz: True: calculate follow reward formula of dynamic committee size, False: normal
        """

        num_of_active_shard = self.get_block_chain_info().get_num_of_shard()
        shard_txs_fee_list = [0] * num_of_active_shard if shard_txs_fee_list is None else shard_txs_fee_list
        shard_range = range(0, num_of_active_shard)
        RESULT = {}

        if epoch is None:
            latest_beacon_block = self.get_latest_beacon_block()
            epoch = latest_beacon_block.get_epoch() - 1
            # can not calculate reward on latest epoch, because the instruction for splitting reward is only exist on
            # the first beacon block of next future epoch

        token = PRV_ID if token is None else token
        # todo: not yet handle custom token

        first_height_of_epoch = TestHelper.ChainHelper.cal_first_height_of_epoch(epoch)
        last_height_of_epoch = TestHelper.ChainHelper.cal_last_height_of_epoch(epoch)

        logger.info(
            f'GET reward info, epoch {epoch}, token {l6(token)}, first block of epoch = {first_height_of_epoch}, '
            f'last block of epoch = {last_height_of_epoch}')

        list_num_of_shard_block = []
        beacon_blocks_in_epoch = [self.get_latest_beacon_block(height) for height in
                                  range(first_height_of_epoch, last_height_of_epoch + 1)]
        for shard_id in shard_range:
            smallest_shard_height = int(1e30)
            biggest_shard_height = -1
            for bb in beacon_blocks_in_epoch:
                shard_state = bb.get_shard_states(shard_id)
                if shard_state:
                    big, small = shard_state.get_biggest_block_height(), shard_state.get_smallest_block_height()
                    if big > biggest_shard_height:
                        biggest_shard_height = big
                    if small < smallest_shard_height:
                        smallest_shard_height = small
            num_of_block = biggest_shard_height - smallest_shard_height + 1
            logger.info(f'shard{shard_id} {biggest_shard_height} - {smallest_shard_height} = {num_of_block}')
            list_num_of_shard_block.append(num_of_block)

        list_beacon_reward_from_shard = []
        list_DAO_reward_from_shard = []
        committee_state = self.get_committee_state(first_height_of_epoch)
        for shard_id in shard_range:  # now calculate each shard reward
            ChainConfig.DAO_REWARD_PERCENT = ChainConfig.DAO_REWARD_PERCENT
            basic_reward = ChainConfig.BASIC_REWARD_PER_BLOCK
            num_of_shard_block = list_num_of_shard_block[shard_id]
            shard_fee_total = shard_txs_fee_list[shard_id]
            if token == PRV_ID:
                total_reward_from_shard = num_of_shard_block * basic_reward + shard_fee_total
            else:
                total_reward_from_shard = shard_fee_total
            DAO_reward_from_shard = ChainConfig.DAO_REWARD_PERCENT * total_reward_from_shard
            list_DAO_reward_from_shard.append(max(0, DAO_reward_from_shard))
            if dcz:  # calculate reward for dynamic committee size
                shard_comm_size = committee_state.get_shard_committee_size(shard_id)
                beacon_committee_size = committee_state.get_beacon_committee_size()
                remain_reward_for_beacon_n_shard = total_reward_from_shard - DAO_reward_from_shard
                num_o_portion = shard_comm_size + (beacon_committee_size * 2 / num_of_active_shard)
                each_validator_reward = remain_reward_for_beacon_n_shard / num_o_portion
                shard_reward = each_validator_reward * shard_comm_size
                beacon_reward_from_shard = remain_reward_for_beacon_n_shard - shard_reward
            else:  # calculate reward for fixed committee size
                beacon_reward_from_shard = \
                    (1 - ChainConfig.DAO_REWARD_PERCENT) * 2 * total_reward_from_shard / (num_of_active_shard + 2)
                shard_reward = (1 - ChainConfig.DAO_REWARD_PERCENT) * total_reward_from_shard - beacon_reward_from_shard

            if shard_reward >= 0:
                RESULT[str(shard_id)] = int(shard_reward)
            list_beacon_reward_from_shard.append(max(0, beacon_reward_from_shard))

        # now calculate total beacon reward and DAO reward
        RESULT['beacon'] = int(sum(list_beacon_reward_from_shard))
        RESULT['DAO'] = int(sum(list_DAO_reward_from_shard))
        # NOTE, the RESULT must in order of Shard reward -> beacon -> DAO, "DO NOT CHANGE IT"
        # to unify with the return result of method get reward in instruction
        # thus it will be easier to compare them to each other
        return RESULT

    def get_committee_state(self, beacon_height=None):
        """
        @param beacon_height: beacon height number, default = None will get latest height automatically
        @return: committee state of beacon_height
        """
        beacon_height = self.get_block_chain_info().get_beacon_block().get_height() if beacon_height is None else \
            beacon_height
        return CommitteeState(self.system_rpc().get_committee_state(beacon_height).get_result())

    def help_get_shard_height(self, shard_num=None):
        """
        Function to get shard height
        @param shard_num:
        @return:
        """
        if shard_num is None:
            dict_shard_height = {}
            num_shards_info = self.get_block_chain_info().get_num_of_shard()
            for shard_id in range(0, num_shards_info):
                shard_height = self.get_block_chain_info().get_shard_block(shard_id).get_height()
                dict_shard_height.update({str(shard_id): shard_height})
            return dict_shard_height
        else:
            return self.get_block_chain_info().get_shard_block(shard_num).get_height()

    def get_shard_best_state_detail_info(self, shard_num):
        shard_state_detail_raw = self.system_rpc().get_shard_best_state_detail(shard_num).get_result()
        shard_state_detail_obj = ShardBestStateDetailInfo(shard_state_detail_raw)
        return shard_state_detail_obj

    def get_beacon_best_state_info(self):
        return BeaconBestStateInfo(self.system_rpc().get_beacon_best_state())

    def get_shard_best_state_info(self, shard_num=None):
        shard_state_raw = self.system_rpc().get_shard_best_state(shard_num).get_result()
        shard_state_obj = ShardBestStateInfo(shard_state_raw)
        return shard_state_obj

    def is_local_host(self):
        return self._address == Node.default_address

    def send_proof(self, proof, tx_type='prv'):
        # logger.info('Sending proof')
        if tx_type in ["prv", PRV_ID]:
            return self.transaction().send_prv_tx(proof)
        else:
            return self.transaction().send_token_tx(proof)

    def get_mem_pool_txs(self):
        response = self.system_rpc().get_mem_pool()
        return response.get_mem_pool_transactions_id_list()

    def get_shard_block_by_height(self, shard_id, height):
        response = self.system_rpc().retrieve_block_by_height(height, shard_id)
        return ShardBlock(response.get_result()[0])

    def get_all_token_in_chain_list(self):
        return InChainTokenResponse(self.explore_rpc().list_privacy_custom_token())

    def get_bridge_token_list(self):
        return BridgeTokenResponse(self.bridge().get_bridge_token_list())

    def does_chain_have_this_token(self, token_id):
        return token_id in self.get_all_token_in_chain_list().get_tokens_info()

    def wait_till_beacon_height(self, beacon_height, interval=None, timeout=120):
        """
        Wait until a specific beacon height
        @param interval:
        @param timeout:
        @param beacon_height:
        @return:
        """
        logger.info(f'Waiting till beacon height {beacon_height}')
        current_beacon_h = self.help_get_beacon_height()
        if beacon_height <= current_beacon_h:
            logger.info(f'Beacon height {beacon_height} is passed already')
            return current_beacon_h

        while beacon_height > current_beacon_h:
            if timeout <= 0:
                logger.info(f'Time out and current beacon height is {current_beacon_h}')
                return current_beacon_h
            if interval is None:
                block_remain = beacon_height - current_beacon_h
                interval = block_remain * ChainConfig.BLOCK_TIME
            WAIT(interval)
            timeout -= interval
            current_beacon_h = self.help_get_beacon_height()

        logger.info(f'Beacon height {beacon_height} is passed already')
        return current_beacon_h

    def wait_till_next_beacon_height(self, num_of_beacon_height_to_wait=1, wait=None, timeout=120):
        """
        wait for an amount of beacon height to pass
        @param timeout:
        @param wait:
        @param num_of_beacon_height_to_wait:
        @return:
        """
        current_beacon_h = self.help_get_beacon_height()
        return self.wait_till_beacon_height(current_beacon_h + num_of_beacon_height_to_wait, wait, timeout)

    def wait_till_next_shard_height(self, shard_id, num_of_shard_height_to_wait=1, wait=None, timeout=120):
        """
        Function to wait for an amount of shard height to pass
        @param shard_id:
        @param num_of_shard_height_to_wait:
        @param wait:
        @param timeout:
        @return:
        """
        wait = ChainConfig.BLOCK_TIME if wait is None else wait
        current_shard_h = self.help_get_shard_height(shard_id)
        shard_height = current_shard_h + num_of_shard_height_to_wait
        logger.info(f'Waiting till shard {shard_id} height {shard_height}')

        if shard_height <= current_shard_h:
            logger.info(f'Shard {shard_id} height {shard_height} is passed already')
            return current_shard_h

        while shard_height > current_shard_h:
            WAIT(wait)
            timeout -= wait
            current_shard_h = self.help_get_shard_height(shard_id)
            if timeout <= 0:
                logger.info(f'Time out and current shard {shard_id} height is {current_shard_h}')
                return current_shard_h

        logger.info(f'Time out and current shard {shard_id} height is {current_shard_h}')
        return current_shard_h

    def get_beacon_best_state(self, number_of_beacon_height_to_get=100, wait=5, timeout=50):
        """
        Function to get beacon best state
        @param number_of_beacon_height_to_get: number of beacon height to get
        @param wait:
        @param timeout:
        @return: a list beacon best state obj
        """
        list_beacon_best_state_objs = []
        for i in range(1, number_of_beacon_height_to_get + 1):
            list_beacon_best_state_objs.append(self.get_beacon_best_state_info())
            # Waiting till beacon height increase
            self.wait_till_next_beacon_height(num_of_beacon_height_to_wait=1, wait=wait, timeout=timeout)
            list_beacon_best_state_objs.append(self.get_beacon_best_state_info())
        return list_beacon_best_state_objs

    def wait_till_next_epoch(self, epoch_to_wait=1, block_of_epoch=1):
        f"""
        Wait till {epoch_to_wait} to come, if {epoch_to_wait} is None, just wait till next epoch
        @param epoch_to_wait: number of epoch to wait
        @param block_of_epoch: the n(th) block of epoch, default is the first block
        @return: current epoch number and beacon height
        """
        blk_chain_info = self.get_block_chain_info()
        current_epoch = blk_chain_info.get_beacon_block().get_epoch()
        current_height = blk_chain_info.get_beacon_block().get_height()
        first_blk_of_current_epoch = ChainHelper.cal_first_height_of_epoch(current_epoch)
        num_of_block_till_next_epoch = blk_chain_info.get_beacon_block().get_remaining_block_epoch()
        if epoch_to_wait == 0:
            block_to_wait = first_blk_of_current_epoch + block_of_epoch - current_height
        else:
            block_to_wait = num_of_block_till_next_epoch + block_of_epoch \
                            + (epoch_to_wait - 1) * ChainConfig.BLOCK_PER_EPOCH
        time_to_wait = ChainConfig.get_epoch_n_block_time(0, block_to_wait)
        logger.info(f'Current height = {current_height} @ epoch = {current_epoch}. '
                    f'Wait {time_to_wait}s until epoch {current_epoch + epoch_to_wait} and B height {block_of_epoch}')
        WAIT(time_to_wait)
        blk_chain_info = self.get_block_chain_info()
        return blk_chain_info.get_epoch_number(), blk_chain_info.get_beacon_block().get_height()

    def get_shard_best_state(self, shard_id, number_of_shard_height_to_get=100, wait=5, timeout=50):
        """
        Function to get shard best state
        @param shard_id: shard id
        @param number_of_shard_height_to_get: number of shard height to get
        @param wait:
        @param timeout:
        @return: a list shard best state obj
        """
        list_shard_best_state_objs = []
        for i in range(1, number_of_shard_height_to_get + 1):
            list_shard_best_state_objs.append(self.get_shard_best_state_info(shard_id))
            # Waiting till shard height increase
            self.wait_till_next_shard_height(shard_id=shard_id, num_of_shard_height_to_wait=1, wait=wait,
                                             timeout=timeout)
            list_shard_best_state_objs.append(self.get_shard_best_state_info(shard_id))
        return list_shard_best_state_objs

    def get_beacon_best_state_detail(self, number_of_beacon_height_to_get=100, wait=5, timeout=50):
        """
        Function to get beacon best state detail
        @param number_of_beacon_height_to_get: number of beacon height to get
        @param wait:
        @param timeout:
        @return: a list beacon best state detail obj
        """
        list_beacon_best_state_detail_objs = []
        for i in range(1, number_of_beacon_height_to_get + 1):
            list_beacon_best_state_detail_objs.append(self.get_beacon_best_state_detail_info())
            # Waiting till beacon height increase
            self.wait_till_next_beacon_height(num_of_beacon_height_to_wait=1, wait=wait, timeout=timeout)
            list_beacon_best_state_detail_objs.append(self.get_beacon_best_state_detail_info())
        return list_beacon_best_state_detail_objs

    def get_shard_best_state_detail(self, shard_id, number_of_shard_height_to_get=100, wait=5, timeout=50):
        """
        Function to get shard best state detail
        @param shard_id:
        @param number_of_shard_height_to_get: number of shard height to get
        @param wait:
        @param timeout:
        @return: a list shard detail obj
        """
        list_shard_best_state_detail_objs = []
        for i in range(1, number_of_shard_height_to_get + 1):
            list_shard_best_state_detail_objs.append(self.get_shard_best_state_detail_info(shard_id))
            # Waiting till shard height increase
            self.wait_till_next_shard_height(shard_id=shard_id, num_of_shard_height_to_wait=1, wait=wait,
                                             timeout=timeout)
            list_shard_best_state_detail_objs.append(self.get_shard_best_state_detail_info(shard_id))
        return list_shard_best_state_detail_objs

    def ssh_attach(self, ssh_session):
        """
        @return:
        """
        self._ssh_session = ssh_session
        return self

    def __pgrep_incognito(self):
        cmd = 'pgrep incognito -a'
        pgrep_data = self._ssh_session.send_cmd(cmd)
        return pgrep_data

    def __find_cmd_full_line(self):

        try:
            return self._cache['cmd']
        except KeyError:
            pass

        regex = re.compile(
            r'--rpclisten (localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):'
            f'{self._rpc_port}', re.IGNORECASE)
        for line in self.__pgrep_incognito():
            if re.findall(regex, line):
                self._cache['cmd'] = line.split()
                return line.split()
        logger.info(f'Not found any Incognito process running with rpc port {self._rpc_port}')

    def __find_run_command(self):
        """
        @return: string
        """
        try:
            return ' '.join(self._cache['cmd'][1:])
        except KeyError:
            return ' '.join(self.__find_cmd_full_line()[1:])

    def __get_working_dir(self):
        """
        @return: Absolute path to working dir
        """
        try:
            return self._cache['dir']
        except KeyError:
            raise ValueError('Not found working directory in cache, must run find_pid_by_rpc_port first')

    def __get_data_dir(self):
        """
        @return: data dir, relative to working dir
        """
        full_cmd = self.__find_run_command()
        pattern = re.compile(r"--datadir \w+/(\w+)")
        return re.findall(pattern, full_cmd)[0]

    @action_over_ssh
    def get_mining_key(self):
        command = self.__find_run_command()
        pattern = re.compile(r"--miningkeys \"*(\w+)\"*")
        try:
            return re.findall(pattern, command)[0]
        except IndexError:
            return None

    def __goto_working_dir(self):
        return self._ssh_session.goto_folder(self.__get_working_dir())

    def __goto_data_dir(self):
        return self._ssh_session.goto_folder(f'{self.__get_working_dir()}/{self.__get_data_dir()}')

    @action_over_ssh
    def find_pid(self):
        """
        get process id base on rpc port of the node
        @return:
        """
        try:
            pid = self._cache['cmd'][0]
        except KeyError:
            pid = self.__find_cmd_full_line()[0]

        # find working dir if not yet found
        try:
            self._cache['dir']
        except KeyError:
            cmd = f'pwdx {pid}'
            result = self._ssh_session.send_cmd(cmd)
            if result[1] != 'No such process':
                self._cache['dir'] = result[1].split()[1]

        return pid

    @action_over_ssh
    def start_node(self):
        cmd = self.__find_run_command()
        folder = self.__get_working_dir()
        self._ssh_session.send_cmd(f'cd {folder}')
        return self._ssh_session.send_cmd(f'{cmd} >> logs/{self.get_log_file()} 2> logs/{self.get_error_log_file()} &')

    @action_over_ssh
    def kill_node(self):
        return self._ssh_session.send_cmd(f'kill {self.find_pid()}')

    @action_over_ssh
    def is_node_alive(self):
        cmd = f'[ -d "/proc/{self.find_pid()}" ] && echo 1 || echo 0'
        return bool(int(self._ssh_session.send_cmd(cmd)[1][0]))

    @action_over_ssh
    def clear_data(self):
        if self.is_node_alive():
            raise IOError(f'Cannot clear data when process is running')
        self.__goto_data_dir()
        return self._ssh_session.send_cmd(f'rm -Rf *')

    @action_over_ssh
    def get_log_folder(self):
        return f"{self.__get_working_dir()}/logs"

    @action_over_ssh
    def get_log_file(self):
        # when build chain, the log file name must be the same as data dir name
        # if encounter problem here, check your build config again
        data_path = self.__get_data_dir()
        data_dir_name = data_path.split('/')[-1]
        return f"{data_dir_name}.log"

    @action_over_ssh
    def get_error_log_file(self):
        # when build chain, the log file name must be the same as data dir name
        # if encounter problem here, check your build config again
        data_path = self.__get_data_dir()
        data_dir_name = data_path.split('/')[-1]
        return f"{data_dir_name}_error.log"

    @action_over_ssh
    def log_tail_grep(self, grep_pattern, tail_option=''):
        """
        @param grep_pattern:
        @param tail_option: careful with this, -f might cause serious problem when not handling correctly afterward
        @return: output of tail command
        """
        tail_cmd = f'tail {tail_option} {self.get_log_file()} | grep {grep_pattern}'
        return self._ssh_session.send_cmd(tail_cmd)

    @action_over_ssh
    def log_cat_grep(self, grep_pattern):
        """

        @param grep_pattern:
        @return: output of cat command
        """
        cat_cmd = f'cat {self.get_log_file()} | grep {grep_pattern}'
        return self._ssh_session.send_cmd(cat_cmd)

    @action_over_ssh
    def shell(self):
        return self._ssh_session
