import copy

import pytest

from Helpers.Logging import *
from Objects.AccountObject import COIN_MASTER, Account
from Objects.IncognitoTestCase import ACCOUNTS
from TestCases.ChainTestBusiness.Transactions import test_TRX006_cross_shard_max_value as TRX006

sender: Account
receiver: Account
list_acc_x_shard = {}
for i in range(8):
    try:
        acc = ACCOUNTS.get_accounts_in_shard(i)[0]
        list_acc_x_shard[i] = acc
    except IndexError:
        INFO(f'Not found account in shard {i}')

send_amount = 10000
TRX006.send_amount = send_amount
max_fee = 900000000000000
TRX006.max_fee = max_fee
max_send_amount = 1000000000000000001
TRX006.max_send_amount = max_send_amount


@pytest.mark.parametrize('shard_sender', [0, 1, 2, 3, 4, 5, 6, 7])
def test_send_prv_privacy_max_value(shard_sender):
    INFO()
    INFO(f"""Verify send PRV FROM shard {shard_sender} TO another shard:
                 -  > 10 mil PRV unsuccess
                 - Tx fee = 100000000000 PRV success
                 """)
    INFO()
    try:
        sender = list_acc_x_shard[shard_sender]
        TRX006.sender = sender
    except KeyError:
        pytest.skip(f'Test Data not exist account in shard {shard_sender}')
    receiver_account_list_before = copy.deepcopy(list_acc_x_shard)
    receiver_account_list_before.pop(shard_sender)
    result = True
    for shard, receiver in receiver_account_list_before.items():
        INFO()
        INFO(f'----------> TO shard {shard}')
        INFO()
        TRX006.receiver = receiver
        sender_bal = sender.get_balance()
        if sender_bal < max_fee + send_amount:
            COIN_MASTER.send_prv_to(sender, max_fee + send_amount - sender_bal + 10, privacy=0).subscribe_transaction()
            if COIN_MASTER.shard != sender.shard:
                try:
                    sender.subscribe_cross_output_coin()
                except:
                    pass
        try:
            TRX006.test_send_prv_privacy_x_shard_max_value()
            result = result and True
            INFO(f'Shard sender, Shard receiver: {shard_sender} - {shard}: Pass')
        except:
            result = result and False
            INFO(f'Shard sender, Shard receiver: {shard_sender} - {shard}: Fail')
    assert result