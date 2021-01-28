import copy

import pytest

from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS
from IncognitoChain.TestCases.Transactions import test_TRX007_multi_output_x_shard as TRX007


list_acc_x_shard = {}
for i in range(8):
    try:
        acc = ACCOUNTS.get_accounts_in_shard(i)[0]
        list_acc_x_shard[i] = acc
    except TypeError:
        INFO(f'Not found account in shard {i}')


@pytest.mark.parametrize('shard_sender', [0, 1, 2, 3, 4, 5, 6, 7])
def test_send_prv_multi_output_privacy_no_auto_fee(shard_sender):
    INFO()
    INFO(f"""
        Verify send PRV ( privacy - noAuto fee ) FROM SHARD {shard_sender} to another address x Shard successfully
         """)
    INFO()
    try:
        sender_account = list_acc_x_shard[shard_sender]
        TRX007.sender_account = sender_account
    except KeyError:
        pytest.skip(f'Test Data not exist account in shard {shard_sender}')
    TRX007.is_sent = False
    INFO()
    receiver_account_list_before = copy.deepcopy(list_acc_x_shard)
    receiver_account_list_before.pop(shard_sender)
    receiver_account_list_before = receiver_account_list_before.values()
    TRX007.receiver_account_list_before = receiver_account_list_before
    TRX007.receiver_account_dict_to_send = {}
    TRX007.total_sent_amount = 0
    INFO('SET UP FUNCTION')
    TRX007.setup_function()
    INFO()
    try:
        TRX007.test_send_prv_multi_output_privacy_x_shard_no_auto_fee()
        result = True
    except:
        result = False
    INFO()
    INFO('TEARDOWN FUNCTION')
    TRX007.teardown_function()
    assert result and INFO('Pass'), 'Fail'
    INFO()

