import copy

import pytest

from Helpers.Logging import *
from Objects.AccountObject import Account
from Objects.IncognitoTestCase import ACCOUNTS
from TestCases.ChainTestBusiness.Transactions import test_TRX004_cross_shard_not_0_balance_with_fee_n_privacy as TRX004

receiver = sender = Account()
send_amount = 1000
list_acc_x_shard = {}
for i in range(8):
    try:
        acc = ACCOUNTS.get_accounts_in_shard(i)[0]
        list_acc_x_shard[i] = acc
    except IndexError:
        INFO(f'Not found account in shard {i}')


@pytest.mark.parametrize('shard_sender,fee,privacy', [
    (0, -1, 1),
    (0, -1, 0),
    (0, 2, 1),
    (0, 2, 0),
    (1, -1, 1),
    (1, -1, 0),
    (1, 2, 1),
    (1, 2, 0),
    (2, -1, 1),
    (2, -1, 0),
    (2, 2, 1),
    (2, 2, 0),
    (3, -1, 1),
    (3, -1, 0),
    (3, 2, 1),
    (3, 2, 0),
    (4, -1, 1),
    (4, -1, 0),
    (4, 2, 1),
    (4, 2, 0),
    (5, -1, 1),
    (5, -1, 0),
    (5, 2, 1),
    (5, 2, 0),
    (6, -1, 1),
    (6, -1, 0),
    (6, 2, 1),
    (6, 2, 0),
    (7, -1, 1),
    (7, -1, 0),
    (7, 2, 1),
    (7, 2, 0)
])
def test_send_prv_with_fee_privacy(shard_sender, fee, privacy):
    INFO(f'Test transaction cross shard FROM SHARD {shard_sender} TO ------>')
    try:
        sender = list_acc_x_shard[shard_sender]
        TRX004.sender = sender
    except KeyError:
        pytest.skip(f'Test Data not exist account in shard {shard_sender}')
    receiver_account_list_before = copy.deepcopy(list_acc_x_shard)
    receiver_account_list_before.pop(shard_sender)
    result = True
    for shard, receiver in receiver_account_list_before.items():
        INFO()
        INFO(f'------> TO SHARD {shard}')
        INFO()
        TRX004.receiver = receiver
        TRX004.send_amount = send_amount
        try:
            TRX004.test_send_prv_cross_shard_with_fee_privacy(fee, privacy)
            result = result and True
            INFO(f'Shard sender, Shard receiver, Fee, Privacy: {shard_sender} - {shard} - {fee} - {privacy}: Pass')
        except:
            result = result and False
            INFO(f'Shard sender, Shard receiver, Fee, Privacy: {shard_sender} - {shard} - {fee} - {privacy}: Fail')
    assert result