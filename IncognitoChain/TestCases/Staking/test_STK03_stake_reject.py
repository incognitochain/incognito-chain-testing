import pytest
import re

from IncognitoChain.Configs.Constants import coin
from IncognitoChain.Helpers.Logging import STEP
from IncognitoChain.Objects.IncognitoTestCase import COIN_MASTER
from IncognitoChain.TestCases.Staking import stake_account, amount_stake_under_1750, \
    amount_stake_over_1750


def setup_function():
    if stake_account.get_prv_balance() < coin(1750):
        COIN_MASTER.send_prv_to(stake_account, coin(1850) - stake_account.get_prv_balance_cache(),
                                privacy=0).subscribe_transaction()
        if stake_account.shard != COIN_MASTER.shard:
            stake_account.subscribe_cross_output_coin()


@pytest.mark.parametrize('amount_prv_stake', [
    amount_stake_under_1750,
    amount_stake_over_1750
])
def test_stake_under_over_1750_prv(amount_prv_stake):
    STEP(0, 'Get balance account before staking')
    balance_before_stake = stake_account.get_prv_balance()

    STEP(1, f"Send {amount_prv_stake} PRV to stake")
    stake_response = stake_account.stake_and_reward_me(amount_prv_stake, auto_re_stake=False)

    STEP(2, "Verify that the transaction was rejected and PRV was not sent")
    assert stake_response.get_error_msg() == 'Can not send tx', "something went wrong, this tx must failed"
    assert re.search(r'Reject not sansity tx transaction', stake_response.get_error_trace().get_message()), "something went so wrong"
    assert balance_before_stake == stake_account.get_prv_balance()