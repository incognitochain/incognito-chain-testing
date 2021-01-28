import pytest

from Configs.Constants import coin, ChainConfig
from Helpers.KeyListJson import KeyListJson
from Helpers.Logging import ERROR, INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT
from TestCases.Staking import staked_account, stake_account, account_t

key_list_file = KeyListJson()

fixed_validators = key_list_file.get_shard_fix_validator_accounts()
stake_list = key_list_file.get_staker_accounts()
staker = stake_list[-1]
bal_b4_dict = {}
fee_dict = {}
bal_af_dict = {}


def no_test_un_stake():
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    for staker in stake_list:
        if beacon_bsd.get_auto_staking_committees(staker):
            bal_b4_dict[staker] = staker.get_prv_balance()
            fee_dict[staker] = staker.stk_un_stake_tx().subscribe_transaction().get_fee()
    WAIT(100)
    for acc, bal in bal_b4_dict.items():
        assert acc.get_prv_balance() == bal + coin(1750) - fee_dict[acc], ERROR(f'ERROR: {acc.private_key}')


@pytest.mark.parametrize("the_stake, validator, receiver_reward, auto_re_stake", [
    (staked_account, staked_account, staked_account, False),
    (staked_account, staked_account, stake_account, False),
    (stake_account, staked_account, stake_account, False),
    (stake_account, staked_account, staked_account, False),
    (stake_account, staked_account, account_t, False),
    (staked_account, staked_account, staked_account, True),
    (staked_account, staked_account, stake_account, True),
    (stake_account, staked_account, stake_account, True),
    (stake_account, staked_account, staked_account, True),
    (stake_account, staked_account, account_t, True)])
def test_un_stake_when_waiting(the_stake, validator, receiver_reward, auto_re_stake):
    INFO('Staking')
    bal_b4_stake = the_stake.get_prv_balance()
    fee_stk = the_stake.stake(validator, receiver_reward, auto_re_stake=auto_re_stake).subscribe_transaction().get_fee()
    bal_af_stake = the_stake.wait_for_balance_change(from_balance=bal_b4_stake)
    assert bal_af_stake == bal_b4_stake - fee_stk - ChainConfig.STK_AMOUNT
    INFO('Un_staking')
    fee_un_stk = the_stake.stk_un_stake_tx().subscribe_transaction().get_fee()
    bal_af_un_stake = the_stake.wait_for_balance_change(from_balance=bal_af_stake)
    assert bal_af_un_stake == bal_b4_stake - fee_stk - fee_un_stk
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    assert beacon_bsd.get_auto_staking_committees(validator) is None


@pytest.mark.parametrize("the_stake, validator, receiver_reward, auto_re_stake", [
    pytest.param(staked_account, staked_account, staked_account, False,
                 marks=pytest.mark.xfail(reason="auto re stake = False, can not un stake")),
    pytest.param(staked_account, staked_account, stake_account, False,
                 marks=pytest.mark.xfail(reason="auto re stake = False, can not un stake")),
    (stake_account, staked_account, stake_account, False),
    (stake_account, staked_account, staked_account, False),
    (stake_account, staked_account, account_t, False),
    (staked_account, staked_account, staked_account, True),
    (staked_account, staked_account, stake_account, True),
    (stake_account, staked_account, stake_account, True),
    (stake_account, staked_account, staked_account, True),
    (stake_account, staked_account, account_t, True)
])
def test_un_stake_when_pending(the_stake, validator, receiver_reward, auto_re_stake):
    INFO('Staking')
    bal_b4_stake = the_stake.get_prv_balance()
    fee_stk = the_stake.stake(validator, receiver_reward, auto_re_stake=auto_re_stake).subscribe_transaction().get_fee()
    bal_af_stake = the_stake.wait_for_balance_change(from_balance=bal_b4_stake)
    assert bal_af_stake == bal_b4_stake - fee_stk - ChainConfig.STK_AMOUNT
