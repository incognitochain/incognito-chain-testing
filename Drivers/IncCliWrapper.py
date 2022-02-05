import json
import subprocess
import sys

from Helpers import Logging

logger = Logging.config_logger(__name__)


class IncCliWrapper:
    _binary = {'darwin': 'bin/incognito-cli-mac',
               'linux': 'bin/incognito-cli-linux'}. \
        get(sys.platform, 'bin/incognito-cli-win')

    def __init__(self, **settings):
        self.setting = ["--network", settings.get('network', 'local'),
                        "--host", settings.get('host', 'http://localhost:8334'),
                        "--utxoCache", str(settings.get('utxoCache', 0)),
                        "--debug", str(settings.get('debug', 0))]

    def run(self, *args):
        cmd = [IncCliWrapper._binary] + self.setting + list(args)
        logger.debug(" ".join(cmd))
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate()
        logger.debug(stdout)
        if stderr:
            raise RuntimeError(stderr)
        return stdout

    def get_balance(self, private_k):
        output = self.run('account', 'balance', '-p', private_k)
        return int(output.split('\n')[1].strip())

    def key_info(self, private_k):
        output = self.run('account', "keyinfo", "-p", private_k)
        return json.loads(output)

    def gen_account(self, num_of_acc) -> (str, dict):
        output = self.run("account", "gen", "--numAccounts", str(num_of_acc))
        mnemonic, acc = output.split("\n", 1)
        mnemonic = mnemonic.split(" ", 1)[1]
        return mnemonic, json.loads(acc)

    def import_account(self, mnemonic, num_of_acc) -> dict:
        output = self.run("account", "import", "--mnemonic", mnemonic, "--numAccounts", str(num_of_acc))
        _, acc = output.split("\n", 1)
        return json.loads(acc)

    def send(self, private_key, to_addr, token, amount, fee):
        output = self.run('send', "-p", private_key, '--addr', to_addr, "--amt", amount, '----tokenID', token, "--fee",
                          fee)
