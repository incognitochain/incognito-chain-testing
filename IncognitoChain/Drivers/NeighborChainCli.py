import base64
import hashlib
import json
import os
import subprocess
import sys
import typing

from IncognitoChain.Configs.Constants import PBNB_ID, PBTC_ID
from IncognitoChain.Drivers.Connections import RpcConnection
from IncognitoChain.Helpers.Logging import INFO, DEBUG
from IncognitoChain.Helpers.TestHelper import l6, json_extract
from IncognitoChain.Helpers.Time import WAIT


class NeighborChainCli:
    @staticmethod
    def new(token_id):
        if token_id == PBNB_ID:
            return BnbCli()
        elif token_id == PBTC_ID:
            return BtcGo()


class BnbCli:
    _bnb_host = 'data-seed-pre-0-s1.binance.org'
    _bnb_rpc_port = 443
    _bnb_rpc_protocol = 'https'
    _path = f'{os.getcwd()}/IncognitoChain/bin'
    if sys.platform == 'darwin':
        tbnbcli = f'{_path}/tbnbcli-mac'
    elif sys.platform == 'linux':
        tbnbcli = f'{_path}/tbnbcli-linux'
    else:
        tbnbcli = f'{_path}/tbnbcli-win'

    def __init__(self, cmd=tbnbcli, chain_id="Binance-Chain-Ganges", node=None):
        if node is None:
            self.node = f'tcp://{BnbCli._bnb_host}:80'
        self.cmd = cmd
        self.chain_id = chain_id
        self.trust = '--trust-node'
        self.stdout = subprocess.PIPE
        self.stderr = subprocess.PIPE

    def get_default_conn(self):
        return ['--chain-id', self.chain_id, '--node', self.node, self.trust]

    def get_balance(self, key):
        INFO()
        INFO(f'Bnbcli | get balance of {l6(key)}')
        process = subprocess.Popen([self.cmd, 'account', key] + self.get_default_conn(), stdout=self.stdout,
                                   stderr=self.stderr, universal_newlines=True)
        stdout, stderr = process.communicate()
        out = json_extract(stdout)
        print(f"out: {stdout.strip()}\n"
              f"err: {stderr.strip()}")
        return int(BnbCli.BnbResponse(out).get_balance())

    def send_to(self, sender, receiver, amount, password, memo):
        memo_encoded = BnbCli.encode_memo(memo)
        INFO(f'Bnbcli | send {amount} from {l6(sender)} to {l6(receiver)} | memo: {memo_encoded}')
        command = [self.cmd, 'send', '--from', sender, '--to', receiver, '--amount', f'{amount}:BNB', '--json',
                   '--memo', memo_encoded] + self.get_default_conn()
        return self._exe_bnb_cli(command, password)

    def send_to_multi(self, sender, receiver_amount_dict: dict, password, *memo):
        """
        :param sender: sender addr or account name
        :param receiver_amount_dict: dict { receiver_addr : amount to send, ...}
        :param password:
        :param memo:
        :return:
        """
        memo_encoded = BnbCli.encode_memo(memo)
        INFO(f'Bnbcli | send from {l6(sender)} to {json.dumps(receiver_amount_dict, indent=3)} | memo: {memo_encoded}')
        bnb_output = '['
        for key, value in receiver_amount_dict.items():
            bnb_output += "{\"to\":\"%s\",\"amount\":\"%s:BNB\"}," % (key, value)
        bnb_output = bnb_output[:-1] + ']'

        command = [self.cmd, 'token', 'multi-send', '--from', sender, '--transfers',
                   bnb_output, '--json', '--memo', memo_encoded]
        return self._exe_bnb_cli(command, password)

    def _exe_bnb_cli(self, command, more_input):
        command += self.get_default_conn()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                   universal_newlines=True)
        WAIT(7)
        stdout, stderr = process.communicate(f'{more_input}\n')
        INFO(f"\n"
             f"+++ command: {' '.join(command)}\n\n"
             f"+++ out: {stdout}\n\n"
             f"+++ err: {stderr}")
        out = json_extract(stdout)
        err = json_extract(stderr)
        if out is not None:
            return BnbCli.BnbResponse(out)
        else:
            return BnbCli.BnbResponse(err)

    @staticmethod
    def get_bnb_rpc_url():
        return f'{BnbCli._bnb_rpc_protocol}://{BnbCli._bnb_host}:{BnbCli._bnb_rpc_port}'

    @staticmethod
    def encode_memo(info):
        if len(info) == 1:
            return BnbCli.encode_porting_memo(info[0])
        elif len(info) == 2:
            return BnbCli.encode_redeem_memo(info[0], info[1])
        raise Exception('Expect 1 or 2 parameters only')

    @staticmethod
    def encode_porting_memo(porting_id):
        INFO(f"""Encoding porting memo
                    Porting id: {porting_id}""")
        memo_struct = '{"PortingID":"%s"}' % porting_id
        byte_ascii = memo_struct.encode('ascii')
        b64_encode = base64.b64encode(byte_ascii)
        encode_memo_str_output = b64_encode.decode('utf-8')
        return encode_memo_str_output

    @staticmethod
    def encode_redeem_memo(redeem_id, custodian_incognito_addr):
        INFO(f"""Encoding redeem memo
                    Redeem id: {redeem_id}
                    Incognito addr: {custodian_incognito_addr}""")

        memo_struct = '{"RedeemID":"%s","CustodianIncognitoAddress":"%s"}' % (redeem_id, custodian_incognito_addr)
        byte_ascii = memo_struct.encode('ascii')
        sha3_256 = hashlib.sha3_256(byte_ascii)
        b64_encode = base64.b64encode(sha3_256.digest())
        encode_memo_str_output = b64_encode.decode('utf-8')
        return encode_memo_str_output

    class BnbResponse:
        def __init__(self, stdout):
            self.data = stdout

        def get_coins(self):
            try:
                return self.data['value']['base']['coins']
            except TypeError:
                return 0

        def get_amount(self, denom):
            coins = self.get_coins()
            for coin in coins:
                if coin['denom'] == denom:
                    return coin['amount']

        def get_balance(self):
            return self.get_amount('BNB')

        def get_tx_hash(self):
            return self.data['hash']

        def build_proof(self):
            INFO()
            INFO(f'Portal | Building proof | tx {self.get_tx_hash()}')
            bnb_get_block_url = f"{BnbCli.get_bnb_rpc_url()}/tx?hash=0x{self.get_tx_hash()}&prove=true"
            block_response = RpcConnection(bnb_get_block_url, id_num='', json_rpc='2.0'). \
                with_params([]).with_method('').execute()
            block_height = int(block_response.data()['result']['height'])
            proof = {"Proof": block_response.data()['result']['proof'],
                     "BlockHeight": block_height}

            proof['Proof']['Proof']['total'] = int(proof['Proof']['Proof']['total'])  # convert to int
            proof['Proof']['Proof']['index'] = int(proof['Proof']['Proof']['index'])  # convert to int
            proof_string = json.dumps(proof, separators=(',', ':'))  # separators=(',', ':') to remove all spaces
            proof_ascii = proof_string.encode('ascii')  # convert to byte
            string_base64 = base64.b64encode(proof_ascii)  # encode
            string_base64_utf8 = string_base64.decode('utf-8')  # convert to string
            DEBUG(f""" Proof: =================  \n{proof}""")
            return string_base64_utf8


# ============= BTC ===================


class BtcGo:
    if sys.platform == 'darwin':
        btc_go_path = f'{os.getcwd()}/IncognitoChain/bin/btcGo/mac/'
    elif sys.platform == 'linux':
        btc_go_path = f'{os.getcwd()}/IncognitoChain/bin/btcGo/linux/'
    else:
        btc_go_path = f'{os.getcwd()}/IncognitoChain/bin/btcGo/win/'

    btc_build_proof_cli = btc_go_path + 'buildProof'
    btc_get_tx_cli = btc_go_path + 'getTxBTC'
    btc_send_porting_cli = btc_go_path + 'txportingBTC'
    btc_send_redeem_cli = btc_go_path + 'txRedeemBTC'

    if sys.platform == 'windows':
        btc_build_proof_cli += '.exe'
        btc_get_tx_cli += '.exe'
        btc_send_porting_cli += '.exe'
        btc_send_redeem_cli += '.exe'

    def __init__(self):
        pass

    @staticmethod
    def get_balance(addr):
        pass

    @staticmethod
    def send_to(sender, receiver, amount, password, memo):
        """

        :param sender: dummy, just add here to match with bnbcli signature.
            sender is hardcoded = miERaVjAsBriPmAEHSkfymRUo3xjaEoM2r in btcGo command
        :param receiver:
        :param amount:
        :param password: dummy, just add here to match with bnbcli signature
        :param memo:
        :return:
        """
        if type(memo) is typing.Tuple:  # send redeem tx
            send_cli = BtcGo.btc_send_redeem_cli
            redeem_id = memo[0]
            custodian_addr = memo[1]
            command = [send_cli, '-amt', f"{amount}", '-userAdd', f"{receiver}", '-redeemId', f"{redeem_id}",
                       '-custIncAdd', f"{custodian_addr}"]
        else:  # send porting tx
            send_cli = BtcGo.btc_send_porting_cli
            porting_id = memo
            command = [send_cli, '-amtAdd1', f'{amount}', '-outAdd1', f'{receiver}', '-portingId', f'{porting_id}']
        return BtcGo._exe_command(command)

    @staticmethod
    def send_to_multi(sender, receiver_amount_dict: dict, password, *memo):
        """

                :param receiver_amount_dict:
                :param sender: dummy, just add here to match with bnbcli signature.
                    sender is hardcoded = miERaVjAsBriPmAEHSkfymRUo3xjaEoM2r in btcGo command
                :param password: dummy, just add here to match with bnbcli signature
                :param memo:
                :return:
                """

        command = [BtcGo.btc_send_porting_cli]
        i = 1
        for receiver, amount in receiver_amount_dict.items():
            command.append(f'-amtAdd{i}')
            command.append(f'{amount}')
            command.append(f'-outAdd{i}')
            command.append(f'{receiver}')
            i += 1

        command.append('-portingId')
        command.append(f'{memo[0]}')
        return BtcGo._exe_command(command)

    @staticmethod
    def get_tx_by_hash(tx_hash):
        command = [BtcGo.btc_get_tx_cli, '-txhash', tx_hash]
        return BtcGo._exe_command(command)

    @staticmethod
    def _exe_command(command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                   universal_newlines=True)
        stdout, stderr = process.communicate()

        INFO(f"\n"
             f"+++ command: {' '.join(command)}\n\n"
             f"+++ out: {stdout}\n\n"
             f"+++ err: {stderr}")

        dict_response = json_extract(stdout)
        return BtcGo.BtcResponse(dict_response)

    class BtcResponse:
        def __init__(self, data):
            self.data = data

        def get_tx_hash(self):
            try:
                return self.data['tx']['hash']
            except KeyError:
                return self.data['hash']

        def get_block_height(self):
            try:
                return self.data['tx']["block_height"]
            except KeyError:
                return self.data["block_height"]

        def build_proof(self):
            INFO()
            INFO(f'Portal | Building proof | tx {self.get_tx_hash()}')
            tx_by_hash = BtcGo.get_tx_by_hash(self.get_tx_hash())
            height = tx_by_hash.get_block_height()
            timeout = 2 * 60 * 60  # 2hours
            interval = 120
            while timeout > 0:
                if height != -1:
                    break

                WAIT(interval)
                tx_by_hash = BtcGo.get_tx_by_hash(self.get_tx_hash())
                height = tx_by_hash.get_block_height()

                timeout -= interval

            WAIT(30)

            command = [BtcGo.btc_build_proof_cli, '-blockHeight', f'{height}', '-txhash', f'{self.get_tx_hash()}']
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                       universal_newlines=True)
            stdout, stderr = process.communicate()
            INFO(f"\n"
                 f"+++ command: {' '.join(command)}\n\n"
                 f"+++ out: {stdout}\n\n"
                 f"+++ err: {stderr}")
            proof = stdout.split()[1]
            DEBUG(f""" Proof: =================  \n{proof}""")

            return proof
