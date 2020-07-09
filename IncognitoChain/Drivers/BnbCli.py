import base64
import hashlib
import json
import subprocess
from json.decoder import JSONDecodeError

from IncognitoChain.Drivers.Connections import RpcConnection
from IncognitoChain.Helpers.Logging import INFO, DEBUG
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Helpers.Time import WAIT

_bnb_host = 'data-seed-pre-0-s1.binance.org'
_bnb_rpc_port = 443
_bnb_rpc_protocol = 'https'


class BnbCli:
    def __init__(self,
                 cmd='tbnbcli',
                 chain_id="Binance-Chain-Nile",
                 node=None):
        if node is None:
            self.node = f'tcp://{_bnb_host}:80'
        self.cmd = cmd
        self.chan_id = chain_id
        self.trust = '--trust-node'
        self.stdout = subprocess.PIPE
        self.stderr = subprocess.PIPE

    def get_default_conn(self):
        return ['--chain-id', self.chan_id, '--node', self.node, self.trust]

    def get_balance(self, key):
        INFO()
        INFO(f'Bnbcli | get balance of {l6(key)}')
        process = subprocess.Popen([self.cmd, 'account', key] + self.get_default_conn(), stdout=self.stdout,
                                   stderr=self.stderr, universal_newlines=True)
        stdout, stderr = process.communicate()
        out = _json_extract(stdout)
        print(f"out: {stdout.strip()}\n"
              f"err: {stderr.strip()}")
        return int(BnbResponse(out).get_balance())

    def send_to(self, sender, receiver, amount, password, *memo):
        memo_encoded = encode_memo(memo)
        INFO(f"Memo: {memo}")
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
        memo_encoded = encode_memo(memo)
        INFO(f"Memo: {memo}")
        INFO(f'Bnbcli | send from {l6(sender)} to {json.dumps(receiver_amount_dict, indent=3)} | memo: {memo_encoded}')
        bnb_output = '['
        for key, value in receiver_amount_dict.items():
            bnb_output += "{\"to\":\"%s\",\"amount\":\"%s:BNB\"}," % (key, value)
        bnb_output = bnb_output[:-1] + ']'

        command = [self.cmd, 'token', 'multi-send', '--from', sender, '--transfers',
                   bnb_output, '--json', '--memo', memo_encoded]
        return self._exe_bnb_cli(command, password)

    @staticmethod
    def build_proof(tx_hash):
        INFO()
        INFO(f'Portal | Building proof | tx {tx_hash}')
        bnb_get_block_url = f"{_get_bnb_rpc_url()}/tx?hash=0x{tx_hash}&prove=true"
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

    def _exe_bnb_cli(self, command, more_input):
        command += self.get_default_conn()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                   universal_newlines=True)
        WAIT(7)
        stdout, stderr = process.communicate(f'{more_input}\n')
        INFO(f"\n"
             f"command: {command}\n"
             f"out: {stdout}\n"
             f"err: {stderr}")
        out = _json_extract(stdout)
        err = _json_extract(stderr)
        if out is not None:
            return BnbResponse(out)
        else:
            return BnbResponse(err)


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


def _get_bnb_rpc_url():
    return f'{_bnb_rpc_protocol}://{_bnb_host}:{_bnb_rpc_port}'


def _json_extract(string):
    """
    strip all none json part of bnbcli command's result
    :param string:
    :return: dictionary
    """
    try:
        string = '{' + string.split('{', 1)[-1]  # remove all non-sense before the first {
        string = string.split(', error', 1)[0]  # remove all non-sense from ', error'
        return json.loads(string)
    except JSONDecodeError:
        return None


def encode_memo(*info):
    if len(info) == 1:
        return _encode_porting_memo(info)
    elif len(info) == 2:
        return _encode_redeem_memo(info[0], info[1])
    raise Exception('Expect 1 or 2 parameters only')


def _encode_porting_memo(porting_id):
    memo_struct = '{"PortingID":"%s"}' % porting_id
    byte_ascii = memo_struct.encode('ascii')
    b64_encode = base64.b64encode(byte_ascii)
    encode_memo_str_output = b64_encode.decode('utf-8')
    return encode_memo_str_output


def _encode_redeem_memo(redeem_id, custodian_incognito_addr):
    memo_struct = '{"RedeemID":"%s","CustodianIncognitoAddress":"%s"}' % (redeem_id, custodian_incognito_addr)
    byte_ascii = memo_struct.encode('ascii')
    sha3_256 = hashlib.sha3_256(byte_ascii)
    b64_encode = base64.b64encode(sha3_256.digest())
    encode_memo_str_output = b64_encode.decode('utf-8')
    return encode_memo_str_output


def build_bnb_proof(tx_hash):
    INFO()
    INFO(f'Portal | Building proof | tx {tx_hash}')
    bnb_get_block_url = f"{_get_bnb_rpc_url()}/tx?hash=0x{tx_hash}&prove=true"
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
