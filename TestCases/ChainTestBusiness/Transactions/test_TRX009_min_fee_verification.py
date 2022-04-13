from Configs.Configs import ChainConfig
from Helpers.Logging import STEP, INFO
from Objects.IncognitoTestCase import ACCOUNTS

sender = ACCOUNTS[0]
receiver = ACCOUNTS[1]


# @pytest.mark.parametrize('fee', ['under', 'equal', 'over'])
def test_transaction_min_fee():
    # def test_transaction_min_fee(fee):
    send_amount = 200
    fee = 'equal'
    STEP(0, "get sender and receiver balance")
    sender.get_balance()
    receiver.get_balance()

    STEP(1, f"send prv with {fee} fee per kb, ({fee} {ChainConfig.MIN_FEE_PER_KB})")
    result = sender.send_prv_to(receiver, send_amount, ChainConfig.MIN_FEE_PER_KB)
    assert result.get_error_msg() is None
    result.subscribe_transaction()
    tx_block = result.get_transaction_by_hash()
    actual_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    assert actual_fee == ChainConfig.MIN_FEE_PER_KB * (tx_size + 1)
    INFO(f"Actual tx fee: {tx_block.get_fee()}")

    STEP(2, "Verify that prv is sent and received")
    if receiver.shard != sender.shard:
        receiver.subscribe_cross_output_coin()
    assert receiver.get_balance(cache='Yes') + send_amount == receiver.get_balance()
    assert sender.get_balance(cache='Yes') - send_amount - tx_block.get_fee() == sender.get_balance()
