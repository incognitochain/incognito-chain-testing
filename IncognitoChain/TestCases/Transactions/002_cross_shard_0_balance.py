import re

import pytest

from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Objects.AccountObject import get_accounts_in_shard

sender = get_accounts_in_shard(2)[0]
sender_balance = sender.get_prv_balance()

receiver = get_accounts_in_shard(4)[0]
receiver_balance = receiver.get_prv_balance()


def setup_function():
    if sender_balance == 0:
        return
    sender.send_all_prv_to(receiver).subscribe_transaction()


def teardown_function():
    receiver.send_prv_to(sender, sender_balance)


@pytest.mark.parametrize('fee,privacy', [(-1, 0), (2, 0), (-1, 1), (2, 1)])
def test_send_prv_cross_shard_0_balance_with_privacy_is(fee, privacy):
    INFO(f"Verify send PRV form account balance = 0  to another address XShard with privacy={privacy} fee={fee}")
    STEP(1, "get sender and receiver balance before sending")
    balance1b = sender.get_prv_balance()
    INFO(f"sender balance: {balance1b}")

    balance2b = receiver.get_prv_balance()
    INFO("receiver balance: " + str(balance2b))

    # sent with amount >0
    STEP(2, "send PRR -- amount >0")
    step2_result = sender.send_prv_to(receiver, 190, fee=fee, privacy=privacy)

    assert step2_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed"
    assert re.search(r'not enough output coin', step2_result.get_error_trace()), "something went so wrong"

    # sent with amount = 0
    STEP(3, "send PRV -- amount =0")
    step3_result = sender.send_prv_to(receiver, 0, fee=fee, privacy=privacy)
    assert step3_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed"
    assert re.search(r'input value less than output value' and INFO("something went so wrong"),
                     step3_result.get_error_trace())

    # sent with amount < 0
    STEP(4, "Send PRV -- amount < 0")
    step4_result = sender.send_prv_to(receiver, -1, fee=fee, privacy=privacy)
    assert step4_result.get_error_msg() == 'Can not create tx', "something went wrong, this tx must failed"
    assert re.search(r'not enough output coin', step4_result.get_error_trace()), "something went so wrong"
