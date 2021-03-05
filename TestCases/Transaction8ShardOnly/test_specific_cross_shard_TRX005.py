import copy

import pytest

from Helpers.Logging import *
from Objects.AccountObject import Account
from Objects.IncognitoTestCase import ACCOUNTS
from TestCases.Transactions import test_TRX005_cross_shard_insufficient_fund as TRX005

sender = receiver = Account()
list_acc_x_shard = {}
for i in range(8):
    try:
        acc = ACCOUNTS.get_accounts_in_shard(i)[0]
        list_acc_x_shard[i] = acc
    except IndexError:
        INFO(f'Not found account in shard {i}')


@pytest.mark.parametrize('shard_sender,privacy', [
    (0, 1),
    (1, 1),
    (2, 1),
    (3, 1),
    (4, 1),
    (5, 1),
    (6, 1),
    (7, 1),
    (0, 0),
    (1, 0),
    (2, 0),
    (3, 0),
    (4, 0),
    (5, 0),
    (6, 0),
    (7, 0)
])
def test_send_prv_privacy_insufficient_fund(shard_sender, privacy):
    INFO()
    INFO(f"""Verify send PRV FROM SHARD {shard_sender} to another Shard:
        - Not enough coin (insufficient fund)
        - Wrong input transaction
        """)
    INFO()
    try:
        sender = list_acc_x_shard[shard_sender]
        TRX005.sender = sender
    except KeyError:
        pytest.skip(f'Test Data not exist account in Shard {shard_sender}')
    receiver_account_list_before = copy.deepcopy(list_acc_x_shard)
    receiver_account_list_before.pop(shard_sender)
    result = True
    for shard, receiver in receiver_account_list_before.items():
        INFO()
        INFO(f'-------> TO Shard {shard}')
        INFO()
        TRX005.receiver = receiver
        TRX005.setup_function()
        try:
            TRX005.test_send_prv_privacy_x_shard_insufficient_fund(privacy)
            result = result and True
            INFO(f'Shard sender, Privacy, Shard receiver: {shard_sender} - {privacy} - {shard}: Pass')
        except:
            INFO(f'Shard sender, Privacy, Shard receiver: {shard_sender} - {privacy} - {shard}: Fail')
            result = result and False
    assert result