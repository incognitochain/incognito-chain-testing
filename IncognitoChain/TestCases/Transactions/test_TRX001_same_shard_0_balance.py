import re

import pytest

from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Objects.AccountObject import get_accounts_in_shard, Account

sender_account: Account = None
receiver_account: Account = None
init_sender_balance = None
init_receiver_balance = None


def setup_module():
    global sender_account, receiver_account, init_sender_balance, init_receiver_balance
    sender_account = get_accounts_in_shard(5)[0]
    receiver_account = get_accounts_in_shard(5)[1]
    init_sender_balance = sender_account.get_prv_balance()
    init_receiver_balance = receiver_account.get_prv_balance()
    if init_sender_balance > 0:
        sender_account.send_all_prv_to(receiver_account)


def teardown_module():
    if init_sender_balance == 0:
        receiver_account.send_prv_to(sender_account, init_sender_balance, privacy=0).subscribe_transaction()
    if receiver_account.shard != sender_account.shard:
        try:
            sender_account.subscribe_cross_output_coin()
        except:
            pass


@pytest.mark.parametrize('fee,privacy', [
    (-1, 0),
    (2, 0),
    pytest.param(-1, 1, marks=pytest.mark.xfail(reason="bug #")),
    pytest.param(2, 1, marks=pytest.mark.xfail(reason="bug #"))
])
def test_send_prv_same_shard_0_balance_with_fee_n_privacy(fee, privacy):
    INFO(f"Verify send PRV form account balance = 0 to another address X1hard with privacy={privacy} fee={fee}")

    STEP(1, "get balance of sender and receiver before sending")
    sender_balance = sender_account.get_prv_balance()
    INFO(f"sender balance: {sender_balance}")

    receiver_balance = receiver_account.get_prv_balance()
    INFO(f"receiver balance: {receiver_balance}")

    # sent with amount >0
    STEP(2, "from address1 send prv to address2 -- amount >0")
    send_result_2 = sender_account.send_prv_to(receiver_account, amount=1000, fee=fee, privacy=privacy)

    assert send_result_2.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed"
    assert re.search(r'-4001: -4001: -1013:',
                     send_result_2.get_error_trace().get_error_codes()), send_result_2.get_error_trace().get_error_codes()

    # sent with amount = 0
    STEP(3, "from address1 send prv to address2 -- amount =0")
    send_result_3 = sender_account.send_prv_to(receiver_account, amount=0, fee=fee, privacy=privacy)
    assert send_result_3.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed"
    assert re.search(r'input value less than output value', send_result_3.get_error_trace().get_message()), \
        "something went so wrong"

    # sent with amount < 0
    STEP(4, "from address1 send prv to address2 -- amount < 0")
    send_result_4 = sender_account.send_prv_to(receiver_account, amount=-1, fee=fee, privacy=0)

    assert send_result_4.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed"
    assert re.search(r'-4001: -4001: -1013:',
                     send_result_4.get_error_trace().get_error_codes()), "something went so wrong"
