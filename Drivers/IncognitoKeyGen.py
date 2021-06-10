import os
import re
import subprocess
import sys

if sys.platform == 'darwin':
    get_key = {1: f'{os.getcwd()}/bin/getKey-mac',
               2: f''}
elif sys.platform == 'linux':
    get_key = {1: f'{os.getcwd()}/bin/getKey-linux',
               2: f'{os.getcwd()}/bin/getKeyV2-linux'}
else:
    get_key = {1: f'{os.getcwd()}/bin/getKey-win',
               2: f''}


def get_key_set_from_private_k(private_k, version):
    """
    @param version: 1 or 2, for privacy v1/2
    @param private_k:
    @type private_k:
    @return:   (private_k,
                payment_k,
                public_k,
                read_only_k,
                validator_k,
                bls_public_k,
                bridge_public_k,
                mining_public_k,
                committee_public_k,
                view_k,
                ota_k,
                shard_id)
    """
    try:
        process = subprocess.Popen([get_key[version], '-privatekey', private_k],
                                   stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True)
    except KeyError:
        raise ValueError(f'Version {version} not found. Acceptable version: {list(get_key.keys())}')

    stdout, stderr = process.communicate()
    if 'error' in stdout:
        raise ValueError(f"Invalid private key: {stdout}")
    # print(f'Generating keys from private key {l6(private_k)}')
    # print(stdout)
    return (
        __get_key_from_output(stdout, 'Private Key'),
        __get_key_from_output(stdout, 'Payment Address'),
        __get_key_from_output(stdout, 'Public Key'),
        __get_key_from_output(stdout, 'ReadOnlykey'),
        __get_key_from_output(stdout, 'Validatorkey'),
        __get_key_from_output(stdout, 'BLS public key'),
        __get_key_from_output(stdout, 'Bridge public key'),
        __get_key_from_output(stdout, 'Mining Public Key'),
        __get_key_from_output(stdout, 'Committee Public Key'),
        __get_key_from_output(stdout, 'View Key'),
        __get_key_from_output(stdout, 'OTA Key'),
        int(__get_key_from_output(stdout, 'ShardID')),
    )


def get_random_k_from_word(word, num_of_key=1):
    """
    @todo Random a new private key from word
    @param word:
    @param num_of_key:
    @return:
    """
    pass


def __get_key_from_output(output, k_name):
    for line in output.splitlines():
        match = re.match(f".*{k_name}.*:\\s+(.*)", line)
        if match is not None:
            key = match.group(1)
            # print(f"\t{k_name}: {key}")
            return key
