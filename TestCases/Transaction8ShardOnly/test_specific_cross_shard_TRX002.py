import copy

import pytest

from Helpers.Logging import *
from Objects.AccountObject import Account
from Objects.IncognitoTestCase import ACCOUNTS
from TestCases.Transactions import test_TRX002_cross_shard_0_balance as TRX002

sender: Account
receiver: Account
sender_balance_init = None
receiver_balance = None

list_acc_x_shard = {}
for i in range(8):
    try:
        acc = ACCOUNTS.get_accounts_in_shard(i)[0]
        list_acc_x_shard[i] = acc
    except IndexError:
        INFO(f'Not found account in shard {i}')


@pytest.mark.parametrize('shard_sender,fee,privacy', [
    (0, -1, 0),
    (0, 2, 0),
    (0, -1, 1),
    (0, 2, 1),
    (1, -1, 0),
    (1, 2, 0),
    (1, -1, 1),
    (1, 2, 1),
    (2, -1, 0),
    (2, 2, 0),
    (2, -1, 1),
    (2, 2, 1),
    (3, -1, 0),
    (3, 2, 0),
    (3, -1, 1),
    (3, 2, 1),
    (4, -1, 0),
    (4, 2, 0),
    (4, -1, 1),
    (4, 2, 1),
    (5, -1, 0),
    (5, 2, 0),
    (5, -1, 1),
    (5, 2, 1),
    (6, -1, 0),
    (6, 2, 0),
    (6, -1, 1),
    (6, 2, 1),
    (7, -1, 0),
    (7, 2, 0),
    (7, -1, 1),
    (7, 2, 1)
])
def test_send_prv_balance_0_with_privacy_is(shard_sender, fee, privacy):
    INFO(f'TEST TRANSACTION CROSS SHARD FROM SHARD {shard_sender} TO --------->')
    try:
        sender = list_acc_x_shard[shard_sender]
        TRX002.sender = sender
    except KeyError:
        pytest.skip(f'Test Data not exist account in shard {shard_sender}')
    receiver_account_list_before = copy.deepcopy(list_acc_x_shard)
    receiver_account_list_before.pop(shard_sender)
    result = True
    for shard, receiver in receiver_account_list_before.items():
        INFO()
        INFO(f'--------->TO SHARD {shard}')
        INFO()
        sender_balance_init = sender.get_balance()
        TRX002.sender_balance_init = sender_balance_init
        INFO('SET UP FUNCTION')
        TRX002.receiver = receiver
        TRX002.setup_function()
        INFO()
        try:
            TRX002.test_send_prv_cross_shard_0_balance_with_privacy_is(fee, privacy)
            result = result and True
            INFO(f'Shard sender, Shard receiver, Fee, Privacy: {shard_sender} - {shard} - {fee} - {privacy}: Pass')
        except:
            result = result and False
            INFO(f'Shard sender, Shard receiver, Fee, Privacy: {shard_sender} - {shard} - {fee} - {privacy}: Failed')
        INFO()
        INFO('TEARDOWN FUNCTION')
        TRX002.teardown_function()
    assert result
