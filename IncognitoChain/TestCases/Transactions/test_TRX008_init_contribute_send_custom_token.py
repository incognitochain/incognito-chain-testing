import copy
import random
import re

import pytest

from IncognitoChain.Configs import Constants
from IncognitoChain.Configs.Constants import ONE_COIN
from IncognitoChain.Drivers.Response import Response
from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Helpers.Time import get_current_date_time, WAIT
from IncognitoChain.Objects.AccountObject import get_accounts_in_shard
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER

amount_init_token = 1000000 * ONE_COIN
amount_contribute = 20000 * ONE_COIN  # contribute rate 1:1
account_init = get_accounts_in_shard(2)[0]

custom_token_symbol = get_current_date_time()
custom_token_id = None
contribute_success = False

token_amount_to_send = random.randrange(1000, 2000)

sender_account = account_init

receiver_account = get_accounts_in_shard(2)[1]

receiver_x_shard = get_accounts_in_shard(0)[0]

pair_id = f"token1_1prv_{random.randrange(1000, 10000)}"


def setup_module():
    INFO("Test set up")
    sender_bal = account_init.get_prv_balance()
    if sender_bal <= amount_init_token:
        COIN_MASTER.send_prv_to(account_init, amount_init_token - sender_bal + 10, privacy=0).subscribe_transaction()
        if COIN_MASTER.shard != account_init.shard:
            account_init.subscribe_cross_output_coin()


def teardown_module():
    INFO("Tear down")
    global contribute_success
    if contribute_success:
        account_init.withdraw_contribution(Constants.prv_token_id, custom_token_id,
                                           amount_init_token).subscribe_transaction()
    contribute_success = False


@pytest.mark.dependency()
@pytest.mark.parametrize('prv_contribute_amount, token_contribute_amount,token_init_amount',
                         [(amount_contribute, amount_contribute, amount_init_token)])
def test_init_ptoken(prv_contribute_amount, token_contribute_amount, token_init_amount):
    INFO('''
    Init a pToken
    Contribute pToken-PRV to pDex (mapping rate) => use pToken to pay fee
    ''')
    contribute_rate = [token_contribute_amount, prv_contribute_amount]

    STEP(1, "Initial new token")
    step1_result = account_init.init_custom_token_self(custom_token_symbol, token_init_amount)

    assert step1_result.get_error_msg() is None and INFO("Success to init new token"), "Failed to init new token"
    global custom_token_id
    custom_token_id = step1_result.get_token_id()
    INFO(f"Token id: {custom_token_id}")

    STEP(2, "subscribe transaction")
    step1_result.subscribe_transaction()

    STEP(3, "Get custom token balance")
    token_balance = account_init.get_token_balance(custom_token_id)
    INFO(f"Token balance: {token_balance}")

    STEP(4, "contribute token & PRV")
    # Contribute TOKEN:
    contribute_token_result = account_init.contribute_token(custom_token_id, token_contribute_amount, pair_id)
    INFO(f"Contribute {custom_token_id} Success, TxID: {contribute_token_result.get_tx_id()}")
    INFO("Subscribe contribution transaction")
    contribute_token_result.subscribe_transaction()
    # Contribute PRV:
    contribute_prv_result = account_init.contribute_prv(prv_contribute_amount, pair_id)
    global contribute_success
    contribute_success = True

    INFO("Contribute PRV Success, TxID: " + contribute_prv_result.get_tx_id())
    INFO("Subscribe contribution transaction")
    contribute_prv_result.subscribe_transaction()

    STEP(5, "Verify Contribution")
    rate = []
    for _ in range(0, 10):
        WAIT(10)
        rate = SUT.full_node.get_latest_rate_between(Constants.prv_token_id, custom_token_id)
        if rate is not None:
            break
    INFO(f"rate prv vs token: {rate}")
    assert rate == contribute_rate, "Contribution Failed"
    # breakpoint()


@pytest.mark.parametrize('sender,receiver,fee,fee_type,privacy,privacy_type', [
    # 1 shard
    pytest.param(sender_account, receiver_account, -1, 'token', 1, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(sender_account, receiver_account, -1, 'token', 0, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    (sender_account, receiver_account, 10, 'token', 1, 'prv'),
    (sender_account, receiver_account, 10, 'token', 0, 'prv'),
    (sender_account, receiver_account, -1, 'prv', 1, 'prv'),
    (sender_account, receiver_account, -1, 'prv', 0, 'prv'),
    (sender_account, receiver_account, 1, 'prv', 1, 'prv'),
    (sender_account, receiver_account, 1, 'prv', 0, 'prv'),
    (sender_account, receiver_account, 10, 'token', 1, 'token'),
    (sender_account, receiver_account, 10, 'token', 0, 'token'),
    (sender_account, receiver_account, -1, 'prv', 1, 'token'),
    (sender_account, receiver_account, -1, 'prv', 0, 'token'),
    (sender_account, receiver_account, 1, 'prv', 1, 'token'),
    (sender_account, receiver_account, 1, 'prv', 0, 'token'),
    # cross shard
    pytest.param(sender_account, receiver_x_shard, -1, 'token', 1, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    pytest.param(sender_account, receiver_account, -1, 'token', 0, 'prv',
                 marks=pytest.mark.xfail(reason="Cannot set token fee =-1")),
    (sender_account, receiver_x_shard, 10, 'token', 1, 'prv'),
    (sender_account, receiver_x_shard, 10, 'token', 0, 'prv'),
    (sender_account, receiver_x_shard, -1, 'prv', 1, 'prv'),
    (sender_account, receiver_x_shard, -1, 'prv', 0, 'prv'),
    (sender_account, receiver_x_shard, 1, 'prv', 1, 'prv'),
    (sender_account, receiver_x_shard, 1, 'prv', 0, 'prv'),
    (sender_account, receiver_x_shard, 10, 'token', 1, 'token'),
    (sender_account, receiver_x_shard, 10, 'token', 0, 'token'),
    (sender_account, receiver_x_shard, -1, 'prv', 1, 'token'),
    (sender_account, receiver_x_shard, -1, 'prv', 0, 'token'),
    (sender_account, receiver_x_shard, 1, 'prv', 1, 'token'),
    (sender_account, receiver_x_shard, 1, 'prv', 0, 'token')
])
@pytest.mark.dependency(depends=["test_init_ptoken"])
def test_send_token(sender, receiver, fee, fee_type, privacy, privacy_type):
    INFO(f'''
        Verify send Token from shard {sender.shard} to shard {receiver.shard}
        fee = {fee} {fee_type}
        privacy = {privacy}
        Privacy type = {privacy_type}
        ''')
    STEP(1, "get sender and receiver balance before sending")
    sender_token_bal_before = sender.get_token_balance(custom_token_id)
    INFO(f"Sender token balance before: {sender_token_bal_before}")

    sender_prv_bal_before = sender.get_prv_balance()
    INFO("sender prv balance before : " + str(sender_prv_bal_before))

    receiver_token_balance_before = receiver.get_token_balance(custom_token_id)
    INFO(f"Receiver token balance before: {receiver_token_balance_before}")

    receiver_prv_balance_before = receiver.get_prv_balance()
    INFO(f'Receiver prv balance before: {receiver_prv_balance_before}')

    STEP(2, f"send token: {token_amount_to_send}. Fee {fee}:{fee_type}. Privacy {privacy}:{privacy_type}")
    if fee_type == 'prv':
        if privacy_type == 'prv':
            sending_token_transaction = sender.send_token_to(receiver, custom_token_id,
                                                             token_amount_to_send, prv_fee=fee,
                                                             prv_privacy=privacy)
        else:
            sending_token_transaction = sender.send_token_to(receiver, custom_token_id,
                                                             token_amount_to_send, prv_fee=fee,
                                                             token_privacy=privacy)
    else:  # fee_type = 'token'
        if privacy_type == 'prv':
            sending_token_transaction = sender.send_token_to(receiver, custom_token_id,
                                                             token_amount_to_send, token_fee=fee,
                                                             prv_privacy=privacy)
        else:
            sending_token_transaction = sender.send_token_to(receiver, custom_token_id,
                                                             token_amount_to_send, token_fee=fee,
                                                             token_privacy=privacy)
    INFO("transaction_id: " + sending_token_transaction.get_tx_id())
    assert sending_token_transaction.get_error_msg() != 'Can not create tx' and INFO(
        "make successful transaction"), sending_token_transaction.get_error_trace().get_message()

    STEP(3, "Subscribe sending transaction")
    transaction_result = sending_token_transaction.subscribe_transaction()
    if sender.shard != receiver.shard:
        receiver.subscribe_cross_output_token()

    STEP(4, '''
            checking sender and receiver bal
            sending token use prv fee then: sender prv - fee, token - sent amount only
            sending token use token fee then: sender token - fee, prv no change
            ''')
    STEP(4.1, "check sender and receiver token balance after sent")
    sender_token_bal_after = sender.get_token_balance(custom_token_id)
    INFO(f"sender_token_balance_after:{sender_token_bal_after}")
    # Balance after = balance before - amount
    if fee_type == 'prv':
        assert sender_token_bal_after == sender_token_bal_before - token_amount_to_send, "sender balance incorrect"
    else:  # fee_type = 'token'
        assert sender_token_bal_after == sender_token_bal_before - token_amount_to_send - fee, \
            "sender balance incorrect"

    receiver_token_balance_after = receiver.get_token_balance(custom_token_id)
    INFO(f"Receiver token balance after: ")
    # Balance after = balance before + amount
    assert receiver_token_balance_before == receiver_token_balance_after - token_amount_to_send, \
        "receiver balance incorrect"

    STEP(4.2, "check sender and receiver PRV balance after sent")
    sender_prv_bal_after = sender.get_prv_balance()
    INFO(f"Sender prv balance after : {sender_prv_bal_after}")
    if fee_type == 'prv':
        assert sender_prv_bal_after == sender_prv_bal_before - transaction_result.get_fee(), \
            "incorrect prv balance of the address 1 "
    else:  # fee_type = 'token'
        assert sender_prv_bal_after == sender_prv_bal_before, \
            "incorrect prv balance of the address 1 "

    receiver_prv_balance_after = receiver.get_prv_balance()
    INFO(f"Receiver prv balance after : {receiver_prv_balance_after}")
    assert receiver_prv_balance_before == receiver_prv_balance_after, "incorrect prv balance of receiver"

    STEP(5, "privacy check")
    sending_token_transaction: Response
    transaction = sending_token_transaction.get_transaction_by_hash()
    if privacy == 0:  # if privacy = 0 then all privacy type must be the same
        INFO("Check transaction prv_privacy")
        assert transaction.get_proof_detail_input_coin_value_prv() != 0 and INFO(
            "info value PRV must be no privacy"), "info value PRV  is not privacy"

        INFO("Check transaction token privacy")
        assert transaction.get_proof_detail_input_coin_value_custom_token() != 0 and INFO(
            "info value token  must be no privacy"), "info value token is NOT privacy"

    else:  # privacy =1
        if privacy_type == 'token':
            INFO("Check transaction prv_privacy")
            assert transaction.get_proof_detail_input_coin_value_prv() != 0 and INFO(
                "info value PRV must be privacy"), "info value PRV  is privacy"

            INFO("Check transaction token privacy")
            assert transaction.get_proof_detail_input_coin_value_custom_token() == 0 and INFO(
                "info value token must be privacy"), "info value token is NOT privacy"
        else:  # privacy_type  = prv while not sending prv, only token then only prv privacy will be applied
            if fee_type == 'token':
                INFO("Check transaction prv_privacy")
                assert transaction.get_proof_detail_input_coin_value_prv() is None and INFO(
                    "info value PRV is no privacy"), "info value PRV is privacy"
            else:
                INFO("Check transaction prv_privacy")
                assert transaction.get_proof_detail_input_coin_value_prv() == 0 and INFO(
                    "info value PRV is no privacy"), "info value PRV is privacy"

            INFO("Check transaction token privacy")
            assert transaction.get_proof_detail_input_coin_value_custom_token() != 0 and INFO(
                "info value token must be privacy"), "info value token is NOT privacy"


@pytest.mark.dependency(depends=["test_init_ptoken"])
@pytest.mark.parametrize('sender,receiver', [(sender_account, receiver_account),
                                             (sender_account, receiver_x_shard)])
def test_send_token_insufficient_fund(sender, receiver):
    INFO("""
        Verify send Token to another address:
        - Not enough coin (insufficient fund)
        - Wrong input transaction (not enough fee)
        - Valid transaction (sending all token) 
        """)
    STEP(1, "Get sender, receiver token and prv balance before sending")
    sender_token_bal = sender.get_token_balance(custom_token_id)
    sender_prv_bal = sender_account.get_prv_balance()
    INFO(f"Sender token balance: {sender_token_bal}")
    INFO(f"Sender prv balance: {sender_prv_bal}")

    receiver_token_bal = receiver.get_token_balance(custom_token_id)
    receiver_prv_bal = receiver.get_prv_balance()
    INFO(f"Receiver token balance: {receiver_token_bal}")
    INFO(f"Receiver prv balance: {receiver_prv_bal}")

    STEP(2, "From sender send token to receiver - Not enough coin")
    # send current balance + 10
    step2_result = sender.send_token_to(receiver, custom_token_id, sender_token_bal + 10, prv_fee=-1)
    assert step2_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed"

    assert re.search(r'Not enough coin', step2_result.get_error_trace().get_message())

    STEP(3, "From sender send token to receiver - Wrong input transaction")
    # send current balance (lacking of fee)
    step3_result = sender.send_token_to(receiver, custom_token_id, sender_token_bal, token_fee=200)
    assert step3_result.get_error_msg() == 'Can not create tx'

    STEP(4, "From sender send token to receiver - success")
    # send current balance - fee (100)
    estimated_fee = 10
    step4_result = sender.send_token_to(receiver, custom_token_id, sender_token_bal - estimated_fee,
                                        token_fee=estimated_fee)
    assert step4_result.get_error_msg() != 'Can not create tx'
    INFO("TxID: " + step4_result.get_tx_id())

    STEP(5, "Subscribe transaction")
    step4_result.subscribe_transaction()

    if sender.shard != receiver.shard:
        receiver.subscribe_cross_output_token()

    STEP(6, "Check sender balance")
    sender_token_bal_after = sender.get_token_balance(custom_token_id)
    assert sender_token_bal_after == 0, "sender token balance must be 0"

    STEP(7, "Check receiver balance")
    receiver_token_bal_after = receiver.get_token_balance(custom_token_id)
    assert receiver_token_bal_after == receiver_token_bal + sender_token_bal - estimated_fee

    STEP(8, 'Return token to sender for the next run')
    receiver.send_token_to(sender, custom_token_id, receiver_token_bal_after - estimated_fee,
                           token_fee=estimated_fee).subscribe_transaction()
    if sender.shard != receiver.shard:
        sender.subscribe_cross_output_token()


@pytest.mark.dependency(depends=["test_init_ptoken"])
def test_send_token_and_prv_x_shard_token_and_prv_fee_multi_output():
    INFO('''
          Verify send Token to multi address XShard successfully
          Fee: token
          Fee : auto PRV
          Token_privacy = 1
          Prv_privacy =1

          ''')
    receiver_amount_dict = dict()
    receiver_amount_dict[receiver_account] = random.randrange(1000, 2000)
    receiver_amount_dict[receiver_x_shard] = random.randrange(1000, 2000)
    total_token_sent = 0

    STEP(1, "get sender balance before sending")
    sender_token_bal_before = sender_account.get_token_balance(custom_token_id)
    INFO(f"Sender token balance before: {sender_token_bal_before}")

    sender_prv_bal_before = sender_account.get_prv_balance()
    INFO("sender prv balance before : " + str(sender_prv_bal_before))

    STEP(2, "get receiver balance before sending")
    for account in receiver_amount_dict.keys():
        account.get_token_balance(custom_token_id)
        account.get_prv_balance()
        total_token_sent += receiver_amount_dict[account]

    # save output account state for later comparision
    receiver_amount_dict_copy = {}
    for acc in receiver_amount_dict.keys():
        acc_copy = copy.deepcopy(acc)
        receiver_amount_dict_copy[acc_copy] = receiver_amount_dict[acc]

    STEP(3, "send PRV and Token - Fee PRV auto estimated")
    token_fee = 200
    tx_result = sender_account.send_token_multi_output(receiver_amount_dict, custom_token_id, prv_fee=-1,
                                                       token_fee=token_fee, prv_privacy=1,
                                                       token_privacy=1)
    INFO(f"Transaction id: {tx_result.get_tx_id()}")
    assert tx_result.get_error_msg() != 'Can not create tx'

    STEP(4, "subcribe transaction")
    transaction_result = tx_result.subscribe_transaction()

    STEP(5, "check sender balance after sent")
    sender_token_bal_after = sender_account.get_token_balance(custom_token_id)
    INFO(f"Sender token balance after: {sender_token_bal_after}")

    # Balance token after = balance before - amount * n - fee
    assert sender_token_bal_after == sender_token_bal_before - total_token_sent - token_fee

    sender_prv_bal_after = sender_account.get_prv_balance()

    INFO(f"Sender prv balance after: {sender_prv_bal_after}")
    # Balance prv after = balance before - amount * n - fee
    assert sender_prv_bal_after == sender_prv_bal_before - transaction_result.get_fee()

    STEP(6, "check receiver balance ")
    for account in receiver_amount_dict.keys():
        try:
            account.subscribe_cross_output_token()
        except:
            pass
        amount_token_received = receiver_amount_dict[account]
        balance_token_after = account.get_token_balance(custom_token_id)
        for account_before in receiver_amount_dict_copy.keys():
            if account == account_before:
                if account_before.get_token_balance_cache(custom_token_id) is None:
                    assert balance_token_after == amount_token_received
                else:
                    assert balance_token_after == amount_token_received + account_before.get_token_balance_cache(
                        custom_token_id)

    STEP(7, "Check transaction privacy")
    INFO("Check transaction prv_privacy")
    assert tx_result.is_prv_privacy(), "transaction is non-privacy"

    INFO("Check transaction token privacy")
    assert tx_result.is_token_privacy(), "transaction is non-privacy"


@pytest.mark.dependency(depends=["test_init_ptoken"], reason="#761")
def est_crash_fullnode_when_token_receiver_null():
    prv_fee = prv_privacy = 0
    token_fee = 10
    token_privacy = 1
    param = [sender_account.private_key, None, prv_fee,
             prv_privacy,
             {
                 "Privacy": True,
                 "TokenID": custom_token_id,
                 "TokenName": "",
                 "TokenSymbol": "",
                 "TokenTxType": 1,
                 "TokenAmount": 0,
                 "TokenReceivers": {
                 },
                 "TokenFee": token_fee
             },
             "", token_privacy]
    SUT.full_node.rpc_connection().with_method('createandsendprivacycustomtokentransaction'). \
        with_params(param)
