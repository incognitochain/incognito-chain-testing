import os
import re
import subprocess

get_key = f'{os.getcwd()}/IncognitoChain/bin/getKey'


def get_key_set_from_private_k(private_k):
    """

    :param private_k:
    :type private_k:
    :return:   (private_k,
                payment_k,
                public_k,
                read_only_k,
                validator_k,
                bls_public_k,
                bridge_public_k,
                mining_public_k,
                committee_public_k,
                shard_id)
    :rtype:
    """
    process = subprocess.Popen([get_key, '-privatekey', private_k], stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                               universal_newlines=True)
    stdout, stderr = process.communicate()
    # print(stdout)
    # print(f'Generating keys from private key {l6(private_k)}')
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
        __get_key_from_output(stdout, 'ShardID')
    )


def __get_key_from_output(output, k_name):
    for line in output.splitlines():
        match = re.match(f".*{k_name}.*:\\s+(.*)", line)
        if match is not None:
            key = match.group(1)
            # print(f"\t{k_name}: {key}")
            return key


def test_():
    from IncognitoChain.Drivers.IncognitoKeyGen import get_key_set_from_private_k
    pk = '112t8rnXVMJJZzfF1naXvfE9nkTKwUwFWFeh8cfEyViG1vpA8A9khJk3mhyB1hDuJ4RbreDTsZpgJK4YcSxdEpXJKMEd8Vmp5UqKWwBcYzxv'
    get_key_set_from_private_k(pk)
