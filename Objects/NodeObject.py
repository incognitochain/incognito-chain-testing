import os
import re
from concurrent.futures.thread import ThreadPoolExecutor

from APIs.Bridge import BridgeRpc
from APIs.DEX import DexRpc
from APIs.Explore import ExploreRpc
from APIs.Portal import PortalRpc
from APIs.Subscription import SubscriptionWs
from APIs.System import SystemRpc
from APIs.Transaction import TransactionRpc
from Configs.Constants import ChainConfig, PRV_ID
from Drivers.Connections import WebSocket, RpcConnection, SshSession
from Helpers import TestHelper
from Helpers.Logging import INFO, DEBUG, INFO_HEADLINE
from Helpers.TestHelper import l6, ChainHelper
from Helpers.Time import WAIT
from Objects.BeaconObject import BeaconBestStateDetailInfo, BeaconBlock, BeaconBestStateInfo
from Objects.BlockChainObjects import BlockChainCore
from Objects.CommitteeState import CommitteeState
from Objects.PdeObjects import PDEStateInfo
from Objects.PortalObjects import PortalStateInfo
from Objects.ShardBlock import ShardBlock
from Objects.ShardState import ShardBestStateDetailInfo, ShardBestStateInfo
from Objects.ViewDetailBlock import AllViewDetail


def ssh_function(func):
    def deco(self):
        self: Node
        print(self)
        if not self._ssh_session.isalive():
            self._ssh_session.ssh_connect()
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
        self._web_socket = None
        self.account = account
        self.url = url
        if url is not None:
            self.parse_url(url)
        self._rpc_connection = RpcConnection(self._get_rpc_url())
        self._ssh_session = SshSession(self._address, self._username, self._password, self._ssh_key)
        self._cache = {}

    def __str__(self):
        return f"{self._get_rpc_url()} ws:{self._ws_port}"

    def parse_url(self, url):
        import re
        regex = re.compile(
            r'^(?:http|ftp)s?:\/\/'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:\/?|[\/?]\S+)$', re.IGNORECASE)
        if re.match(regex, url) is None:
            raise SyntaxError(f'Url {url} is not in correct format')

        self._address = url.split(':')[1].lstrip('//')
        self._rpc_port = int(url.split(':')[2].split('/')[0])
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

    def rpc_connection(self) -> RpcConnection:
        """
        get RPC connection to send custom command
        @return: RpcConnection object
        """
        return self._rpc_connection

    def web_socket_connection(self) -> WebSocket:
        """
        get web socket to send your custom command
        @return: WebSocket object
        """
        return self._web_socket

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
        if self._web_socket is None:
            self._web_socket = WebSocket(self._get_ws_url())
        return SubscriptionWs(self._web_socket)

    def explore_rpc(self) -> ExploreRpc:
        return ExploreRpc(self._get_rpc_url())

    def get_latest_beacon_block(self, beacon_height=None):
        if beacon_height is None:
            beacon_height = self.help_get_beacon_height()
        INFO(f'Get beacon block at height {beacon_height}')
        response = self.system_rpc().retrieve_beacon_block_by_height(beacon_height)
        return BeaconBlock(response.get_result()[0])

    def get_first_beacon_block_of_epoch(self, epoch=None):
        """

        @param epoch: epoch number
        @return: BeaconBlock obj of the first epoch of epoch.
        If epoch is specify, get first beacon block of that epoch
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
                INFO(f'Current epoch {current_epoch} Current height {current_height}, '
                     f'wait for {wait_height} height till height {current_height + wait_height}')
                # +1 just to make sure that the first block of epoch is already confirmed
                WAIT(time_till_next_epoch_first_block)
            else:
                INFO(f'Current epoch {current_epoch} Current height {current_height}, no need to wait')
            epoch = current_epoch + 1
        elif epoch is None:
            epoch = self.help_get_current_epoch()
        else:
            pass

        beacon_height = TestHelper.ChainHelper.cal_first_height_of_epoch(epoch)
        return self.get_latest_beacon_block(beacon_height)

    def get_beacon_best_state_detail_info(self):
        beacon_detail_raw = self.system_rpc().get_beacon_best_state_detail().get_result()
        beacon_state_obj = BeaconBestStateDetailInfo(beacon_detail_raw)
        return beacon_state_obj

    def get_latest_pde_state_info(self, beacon_height=None):
        if beacon_height is None:
            beacon_height = self.help_get_beacon_height()
            INFO(f'Get LATEST PDE state at beacon height: {beacon_height}')
        else:
            INFO(f'Get PDE state at beacon height: {beacon_height}')

        pde_state = self.dex().get_pde_state(beacon_height)
        return PDEStateInfo(pde_state.get_result())

    def get_block_chain_info(self):
        return BlockChainCore(self.system_rpc().get_block_chain_info().get_result())

    def get_all_view_detail(self, chain_id):
        return AllViewDetail(self.system_rpc().get_all_view_detail(chain_id).get_result())

    def create_fork(self, block_fork_list, chain_id=1, num_of_branch=2, branch_tobe_continue=1):
        return self.system_rpc().create_fork(block_fork_list, chain_id, num_of_branch, branch_tobe_continue)

    def help_get_beacon_height(self):
        chain_info = self.get_block_chain_info()
        return chain_info.get_beacon_block().get_height()

    def help_get_beacon_height_in_best_state_detail(self):
        beacon_height = self.get_beacon_best_state_info().get_beacon_height()
        INFO(f"Current beacon height = {beacon_height}")
        return beacon_height

    def help_clear_mem_pool(self):
        mem_pool_res = self.system_rpc().get_mem_pool()
        list_tx = mem_pool_res.get_result('ListTxs')
        mem_pool_size = mem_pool_res.get_result("Size")
        INFO(f"There're {mem_pool_size} tx(s) in mem pool. Cleaning now...")
        with ThreadPoolExecutor() as executor:
            for tx in list_tx:
                executor.submit(self.system_rpc().remove_tx_in_mem_pool, tx['TxID'])

    def help_get_current_epoch(self):
        """
        @return:
        """
        DEBUG(f'Get current epoch number')
        beacon_best_state = self.get_beacon_best_state_info()
        epoch = beacon_best_state.get_epoch()
        DEBUG(f"Current epoch = {epoch}")
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
                INFO_HEADLINE(height)
                pde = self.get_latest_pde_state_info(height)
                waiting_str = "Waiting contributions:\n"
                for obj in pde.get_waiting_contributions():
                    waiting_str += f'\t\t{obj}\n'
                INFO(waiting_str)
                pool_str = 'Pool:\n'
                for obj in pde.get_pde_pool_pairs():
                    pool_str += f'\t\t{obj}\n'
                INFO(pool_str)
                share_str = 'PDE Shares:\n'
                for obj in pde._get_pde_share_objects():
                    share_str += f'\t\t{obj}\n'
                INFO(share_str)
                fee_str = 'Fee:\n'
                for obj in pde._get_contributor_reward_objects():
                    fee_str += f'\t\t{obj}\n'
                INFO(fee_str)
                WAIT(ChainConfig.BLOCK_TIME)
                height += 1
        except KeyboardInterrupt:
            pass

    def get_latest_portal_state_info(self, beacon_height=None):
        if beacon_height is None:
            beacon_height = self.help_get_beacon_height()
            INFO(f'Get LATEST portal state at beacon height: {beacon_height}')
        else:
            INFO(f'Get portal state at beacon height: {beacon_height}')

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

        INFO(f'GET reward info, epoch {epoch}, token {l6(token)}, first block of epoch = {first_height_of_epoch}, '
             f'last block of epoch = {last_height_of_epoch}')

        list_num_of_shard_block = []
        beacon_blocks_in_epoch = {}
        for shard_id in shard_range:
            # get smallest and biggest height of shard block then we have num of block in epoch
            for height in range(first_height_of_epoch, last_height_of_epoch + 1):
                try:
                    bb = beacon_blocks_in_epoch[height]
                except KeyError:  # no height in beacon_blocks_in_epoch? get one
                    bb = self.get_latest_beacon_block(height)
                    beacon_blocks_in_epoch[height] = bb
                try:
                    smallest_shard_height = bb.get_shard_states(shard_id).get_smallest_block_height()
                    break
                except AttributeError:  # can't find shard state in beacon block? don't worry, behappy!!
                    pass
                smallest_shard_height = 0

            for height in range(last_height_of_epoch, first_height_of_epoch - 1, -1):
                try:
                    bb = beacon_blocks_in_epoch[height]
                except KeyError:  # no height in beacon_blocks_in_epoch? get one
                    bb = self.get_latest_beacon_block(height)
                    beacon_blocks_in_epoch[height] = bb
                try:
                    biggest_shard_height = bb.get_shard_states(shard_id).get_biggest_block_height()
                    break
                except AttributeError:  # can't find shard state in beacon block? don't worry, behappy!!
                    pass
                biggest_shard_height = -1

            num_of_block = biggest_shard_height - smallest_shard_height + 1
            INFO(f'shard{shard_id} {biggest_shard_height} - {smallest_shard_height} = {num_of_block}')
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
            # breakpoint()
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

            if shard_reward > 0:
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
        beacon_best_state_raw = self.system_rpc().get_beacon_best_state().get_result()
        beacon_best_state_obj = BeaconBestStateInfo(beacon_best_state_raw)
        return beacon_best_state_obj

    def get_shard_best_state_info(self, shard_num=None):
        shard_state_raw = self.system_rpc().get_shard_best_state(shard_num).get_result()
        shard_state_obj = ShardBestStateInfo(shard_state_raw)
        return shard_state_obj

    def is_local_host(self):
        return self._address == Node.default_address

    def send_proof(self, proof):
        INFO('Sending proof')
        return self.transaction().send_tx(proof)

    def get_mem_pool_txs(self):
        response = self.system_rpc().get_mem_pool()
        return response.get_mem_pool_transactions_id_list()

    def get_shard_block_by_height(self, shard_id, height):
        response = self.system_rpc().retrieve_block_by_height(height, shard_id)
        return ShardBlock(response.get_result()[0])

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
        INFO(f'Not found any Incognito process running with rpc port {self._rpc_port}')

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

    def get_mining_key(self):
        command = self.__find_run_command()
        pattern = re.compile(r"--miningkeys \"*(\w+)\"*")
        return re.findall(pattern, command)[0]

    def __goto_working_dir(self):
        return self._ssh_session.goto_folder(self.__get_working_dir())

    def __goto_data_dir(self):
        return self._ssh_session.goto_folder(f'{self.__get_working_dir()}/{self.__get_data_dir()}')

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

    def start_node(self):
        cmd = self.__find_run_command()
        folder = self.__get_working_dir()
        self._ssh_session.send_cmd(f'cd {folder}')
        return self._ssh_session.send_cmd(f'{cmd} >> logs/{self.get_log_file()} 2> logs/{self.get_error_log_file()} &')

    def kill_node(self):
        return self._ssh_session.send_cmd(f'kill {self.find_pid()}')

    @ssh_function
    def is_node_alive(self):
        cmd = f'[ -d "/proc/{self.find_pid()}" ] && echo 1 || echo 0'
        return bool(int(self._ssh_session.send_cmd(cmd)[1][0]))

    def clear_data(self):
        if self.is_node_alive():
            raise IOError(f'Cannot clear data when process is running')
        self.__goto_data_dir()
        return self._ssh_session.send_cmd(f'rm -Rf *')

    def get_log_folder(self):
        return f"{self.__get_working_dir()}/logs"

    def get_log_file(self):
        # when build chain, the log file name must be the same as data dir name
        # if encounter problem here, check your build config again
        data_path = self.__get_data_dir()
        data_dir_name = data_path.split('/')[-1]
        return f"{data_dir_name}.log"

    def get_error_log_file(self):
        # when build chain, the log file name must be the same as data dir name
        # if encounter problem here, check your build config again
        data_path = self.__get_data_dir()
        data_dir_name = data_path.split('/')[-1]
        return f"{data_dir_name}_error.log"

    def log_tail_grep(self, grep_pattern, tail_option=''):
        """
        @param grep_pattern:
        @param tail_option: careful with this, -f might cause serious problem when not handling correctly afterward
        @return: output of tail command
        """
        tail_cmd = f'tail {tail_option} {self.get_log_file()} | grep {grep_pattern}'
        return self._ssh_session.send_cmd(tail_cmd)

    def log_cat_grep(self, grep_pattern):
        """

        @param grep_pattern:
        @return: output of cat command
        """
        cat_cmd = f'cat {self.get_log_file()} | grep {grep_pattern}'
        return self._ssh_session.send_cmd(cat_cmd)
