import copy
import random

import pytest

from Configs.Constants import coin
from Helpers.Logging import *
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import ACCOUNTS
from TestCases.Transactions import test_TRX008_init_contribute_send_custom_token as TRX008

account_init = ACCOUNTS.get_accounts_in_shard(5)[0]
TRX008.account_init = account_init

custom_token_id = None
token_fee = 1400000
list_acc_x_shard = {}
for i in range(8):
    try:
        acc = ACCOUNTS.get_accounts_in_shard(i)[0]
        list_acc_x_shard[i] = acc
    except IndexError:
        INFO(f'Not found account in shard {i}')

COIN_MASTER.top_up_if_lower_than(list(list_acc_x_shard.values()), coin(50000), coin(100000))


@pytest.mark.dependency()
def test_init_ptoken():
    global custom_token_id
    TRX008.test_init_ptoken()
    custom_token_id = TRX008.custom_token_id


@pytest.mark.parametrize('shard_sender,fee,fee_type,privacy,privacy_type', [
    # shard 0
    pytest.param(0, -1, 'token', 1, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(0, -1, 'token', 0, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(0, token_fee, 'token', 1, 'prv'),
    pytest.param(0, token_fee, 'token', 0, 'prv'),
    pytest.param(0, -1, 'prv', 1, 'prv'),
    pytest.param(0, -1, 'prv', 0, 'prv'),
    pytest.param(0, 1, 'prv', 1, 'prv'),
    pytest.param(0, 1, 'prv', 0, 'prv'),
    pytest.param(0, token_fee, 'token', 1, 'token'),
    pytest.param(0, token_fee, 'token', 0, 'token'),
    pytest.param(0, -1, 'prv', 1, 'token'),
    pytest.param(0, -1, 'prv', 0, 'token'),
    pytest.param(0, 1, 'prv', 1, 'token'),
    pytest.param(0, 1, 'prv', 0, 'token'),
    # shard 1
    pytest.param(1, -1, 'token', 1, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(1, -1, 'token', 0, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(1, token_fee, 'token', 1, 'prv'),
    pytest.param(1, token_fee, 'token', 0, 'prv'),
    pytest.param(1, -1, 'prv', 1, 'prv'),
    pytest.param(1, -1, 'prv', 0, 'prv'),
    pytest.param(1, 1, 'prv', 1, 'prv'),
    pytest.param(1, 1, 'prv', 0, 'prv'),
    pytest.param(1, token_fee, 'token', 1, 'token'),
    pytest.param(1, token_fee, 'token', 0, 'token'),
    pytest.param(1, -1, 'prv', 1, 'token'),
    pytest.param(1, -1, 'prv', 0, 'token'),
    pytest.param(1, 1, 'prv', 1, 'token'),
    pytest.param(1, 1, 'prv', 0, 'token'),
    # shard 2
    pytest.param(2, -1, 'token', 1, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(2, -1, 'token', 0, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(2, token_fee, 'token', 1, 'prv'),
    pytest.param(2, token_fee, 'token', 0, 'prv'),
    pytest.param(2, -1, 'prv', 1, 'prv'),
    pytest.param(2, -1, 'prv', 0, 'prv'),
    pytest.param(2, 1, 'prv', 1, 'prv'),
    pytest.param(2, 1, 'prv', 0, 'prv'),
    pytest.param(2, token_fee, 'token', 1, 'token'),
    pytest.param(2, token_fee, 'token', 0, 'token'),
    pytest.param(2, -1, 'prv', 1, 'token'),
    pytest.param(2, -1, 'prv', 0, 'token'),
    pytest.param(2, 1, 'prv', 1, 'token'),
    pytest.param(2, 1, 'prv', 0, 'token'),
    # shard 3
    pytest.param(3, -1, 'token', 1, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(3, -1, 'token', 0, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(3, token_fee, 'token', 1, 'prv'),
    pytest.param(3, token_fee, 'token', 0, 'prv'),
    pytest.param(3, -1, 'prv', 1, 'prv'),
    pytest.param(3, -1, 'prv', 0, 'prv'),
    pytest.param(3, 1, 'prv', 1, 'prv'),
    pytest.param(3, 1, 'prv', 0, 'prv'),
    pytest.param(3, token_fee, 'token', 1, 'token'),
    pytest.param(3, token_fee, 'token', 0, 'token'),
    pytest.param(3, -1, 'prv', 1, 'token'),
    pytest.param(3, -1, 'prv', 0, 'token'),
    pytest.param(3, 1, 'prv', 1, 'token'),
    pytest.param(3, 1, 'prv', 0, 'token'),
    # shard 4
    pytest.param(4, -1, 'token', 1, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(4, -1, 'token', 0, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(4, token_fee, 'token', 1, 'prv'),
    pytest.param(4, token_fee, 'token', 0, 'prv'),
    pytest.param(4, -1, 'prv', 1, 'prv'),
    pytest.param(4, -1, 'prv', 0, 'prv'),
    pytest.param(4, 1, 'prv', 1, 'prv'),
    pytest.param(4, 1, 'prv', 0, 'prv'),
    pytest.param(4, token_fee, 'token', 1, 'token'),
    pytest.param(4, token_fee, 'token', 0, 'token'),
    pytest.param(4, -1, 'prv', 1, 'token'),
    pytest.param(4, -1, 'prv', 0, 'token'),
    pytest.param(4, 1, 'prv', 1, 'token'),
    pytest.param(4, 1, 'prv', 0, 'token'),
    # shard 5
    pytest.param(5, -1, 'token', 1, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(5, -1, 'token', 0, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(5, token_fee, 'token', 1, 'prv'),
    pytest.param(5, token_fee, 'token', 0, 'prv'),
    pytest.param(5, -1, 'prv', 1, 'prv'),
    pytest.param(5, -1, 'prv', 0, 'prv'),
    pytest.param(5, 1, 'prv', 1, 'prv'),
    pytest.param(5, 1, 'prv', 0, 'prv'),
    pytest.param(5, token_fee, 'token', 1, 'token'),
    pytest.param(5, token_fee, 'token', 0, 'token'),
    pytest.param(5, -1, 'prv', 1, 'token'),
    pytest.param(5, -1, 'prv', 0, 'token'),
    pytest.param(5, 1, 'prv', 1, 'token'),
    pytest.param(5, 1, 'prv', 0, 'token'),
    # shard 6
    pytest.param(6, -1, 'token', 1, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(6, -1, 'token', 0, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(6, token_fee, 'token', 1, 'prv'),
    pytest.param(6, token_fee, 'token', 0, 'prv'),
    pytest.param(6, -1, 'prv', 1, 'prv'),
    pytest.param(6, -1, 'prv', 0, 'prv'),
    pytest.param(6, 1, 'prv', 1, 'prv'),
    pytest.param(6, 1, 'prv', 0, 'prv'),
    pytest.param(6, token_fee, 'token', 1, 'token'),
    pytest.param(6, token_fee, 'token', 0, 'token'),
    pytest.param(6, -1, 'prv', 1, 'token'),
    pytest.param(6, -1, 'prv', 0, 'token'),
    pytest.param(6, 1, 'prv', 1, 'token'),
    pytest.param(6, 1, 'prv', 0, 'token'),
    # shard 7
    pytest.param(7, -1, 'token', 1, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(7, -1, 'token', 0, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(7, token_fee, 'token', 1, 'prv'),
    pytest.param(7, token_fee, 'token', 0, 'prv'),
    pytest.param(7, -1, 'prv', 1, 'prv'),
    pytest.param(7, -1, 'prv', 0, 'prv'),
    pytest.param(7, 1, 'prv', 1, 'prv'),
    pytest.param(7, 1, 'prv', 0, 'prv'),
    pytest.param(7, token_fee, 'token', 1, 'token'),
    pytest.param(7, token_fee, 'token', 0, 'token'),
    pytest.param(7, -1, 'prv', 1, 'token'),
    pytest.param(7, -1, 'prv', 0, 'token'),
    pytest.param(7, 1, 'prv', 1, 'token'),
    pytest.param(7, 1, 'prv', 0, 'token'),

])
@pytest.mark.dependency(depends=["test_init_ptoken"])
def test_send_token(shard_sender, fee, fee_type, privacy, privacy_type):
    INFO(f''' Send from SHARD {shard_sender}''')
    try:
        sender = list_acc_x_shard[shard_sender]
        if sender != account_init:
            account_init.top_up_if_lower_than(sender, coin(2), coin(5), custom_token_id)
    except KeyError:
        pytest.skip(f'Test Data not exist account in shard {shard_sender}')
    receiver_account_list_before = copy.deepcopy(list_acc_x_shard)
    receiver_account_list_before.pop(shard_sender)
    result = True
    for shard, receiver in receiver_account_list_before.items():
        TRX008.custom_token_id = custom_token_id
        try:
            TRX008.test_send_token(sender, receiver, fee, fee_type, privacy, privacy_type)
            result = result and True
            INFO(f'Shard sender, Shard receiver, fee, fee_type, privacy, privacy_type: \
                {shard_sender} - {shard} - {fee} - {fee_type} - {privacy} - {privacy_type}: Pass')
        except:
            result = result and False
            INFO(f'Shard sender, Shard receiver, fee, fee_type, privacy, privacy_type: \
                {shard_sender} - {shard} - {fee} - {fee_type} - {privacy} - {privacy_type}: Fail')
    assert result


@pytest.mark.dependency(depends=["test_init_ptoken"])
@pytest.mark.parametrize('shard_sender', [0, 1, 2, 3, 4, 5, 6, 7])
def test_send_token_insufficient_fund(shard_sender):
    INFO(f''' Send from SHARD {shard_sender}''')
    try:
        sender = list_acc_x_shard[shard_sender]
        if sender != account_init:
            account_init.top_up_if_lower_than(sender, coin(2), coin(5), custom_token_id)
    except KeyError:
        pytest.skip(f'Test Data not exist account in shard {shard_sender}')
    receiver_account_list_before = copy.deepcopy(list_acc_x_shard)
    receiver_account_list_before.pop(shard_sender)
    result = True
    for shard, receiver in receiver_account_list_before.items():
        INFO(f'to SHARD {shard}')
        TRX008.sender_account = sender
        TRX008.token_fee = token_fee
        TRX008.custom_token_id = custom_token_id
        try:
            TRX008.test_send_token_insufficient_fund(sender, receiver)
            result = result and True
            INFO(f'Shard sender, Shard receiver: {shard_sender} - {shard}: Pass')
        except:
            result = result and False
            INFO(f'Shard sender, Shard receiver: {shard_sender} - {shard}: Fail')
    assert result


@pytest.mark.dependency(depends=["test_init_ptoken"])
@pytest.mark.parametrize('shard_sender', [0, 1, 2, 3, 4, 5, 6, 7])
def test_send_token_and_prv_x_shard_token_and_prv_fee_multi_output(shard_sender):
    INFO(f''' Send from SHARD {shard_sender}''')
    try:
        sender = list_acc_x_shard[shard_sender]
        if sender != account_init:
            account_init.top_up_if_lower_than(sender, coin(2), coin(5), custom_token_id)
    except KeyError:
        pytest.skip(f'Test Data not exist account in shard {shard_sender}')
    receiver_amount_dict = {}
    receiver_account_list_before = copy.deepcopy(list_acc_x_shard)
    receiver_account_list_before.pop(shard_sender)
    for receiver in receiver_account_list_before.values():  # create a {receiver: receive amount} dictionary
        receiver_amount_dict[receiver] = random.randint(1000, 2000)
    TRX008.receiver_amount_dict = receiver_amount_dict
    TRX008.sender_account = sender
    TRX008.custom_token_id = custom_token_id
    TRX008.test_send_token_and_prv_x_shard_token_and_prv_fee_multi_output()


@pytest.mark.dependency(depends=["test_init_ptoken"], reason="#761")
@pytest.mark.parametrize('shard_sender', [0, 1, 2, 3, 4, 5, 6, 7])
def est_crash_fullnode_when_token_receiver_null(shard_sender):
    INFO(f''' Send from SHARD {shard_sender}''')
    try:
        sender = list_acc_x_shard[shard_sender]
        if sender != account_init:
            account_init.top_up_if_lower_than(sender, coin(2), coin(5), custom_token_id)
    except KeyError:
        pytest.skip(f'Test Data not exist account in shard {shard_sender}')
    TRX008.sender_account = sender
    TRX008.custom_token_id = custom_token_id
    TRX008.est_crash_fullnode_when_token_receiver_null()
