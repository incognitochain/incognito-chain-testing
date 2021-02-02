import pytest

from Configs.Constants import coin, ChainConfig
from Helpers.KeyListJson import KeyListJson
from Helpers.Logging import INFO, STEP
from Helpers.TestHelper import ChainHelper
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT

key_list_file = KeyListJson()

stake_list = key_list_file.get_staker_accounts()
index_epoch_change = 499
block_per_epoch_b4 = 10
block_per_epoch_af = 20

list_staker_to_test = []
beacon_bsd = SUT().get_beacon_best_state_detail_info()
for staker in stake_list[36:]:  # trong file keylist.json, staker số 36 trở đi đã được run node
    if beacon_bsd.get_auto_staking_committees(staker) is None:
        list_staker_to_test.append(staker)
    if len(list_staker_to_test) >= 3:
        break

account_y = list_staker_to_test[0]
account_x = list_staker_to_test[1]
account_t = list_staker_to_test[2]

bal_b4_dict = {}
fee_dict = {}
bal_af_dict = {}


@pytest.mark.parametrize("the_stake, validator, receiver_reward, auto_re_stake", [
    (account_y, account_y, account_y, False),
    (account_y, account_y, account_x, False),
    (account_x, account_y, account_x, False),
    (account_x, account_y, account_y, False),
    (account_x, account_y, account_t, False),
    (account_y, account_y, account_y, True),
    (account_y, account_y, account_x, True),
    (account_x, account_y, account_x, True),
    (account_x, account_y, account_y, True),
    (account_x, account_y, account_t, True)])
def test_un_stake_when_waiting(the_stake, validator, receiver_reward, auto_re_stake):
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    if beacon_bsd.get_auto_staking_committees(validator) is True:
        pytest.skip(f'validator {validator.validator_key} is existed in committee with auto re-stake: True')
    elif beacon_bsd.get_auto_staking_committees(validator) is False:
        validator.stk_wait_till_i_am_out_of_autostaking_list()

    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1751), coin(1850), the_stake)
    bal_b4_stake = the_stake.get_prv_balance()

    INFO('Wait until after random')
    beacon_height_current = beacon_bsd.get_beacon_height()
    epoch = beacon_bsd.get_epoch()
    block_height_random = ChainHelper.cal_random_height_of_epoch(epoch, index_epoch_change, block_per_epoch_b4,
                                                                 block_per_epoch_af)
    if beacon_height_current < block_height_random:
        ChainHelper.wait_till_beacon_height(block_height_random, timeout=210)

    STEP(1, 'Staking')
    fee_stk = the_stake.stake(validator, receiver_reward, auto_re_stake=auto_re_stake).subscribe_transaction().get_fee()
    bal_af_stake = the_stake.wait_for_balance_change(from_balance=bal_b4_stake,
                                                     least_change_amount=(- fee_stk - ChainConfig.STK_AMOUNT))
    assert bal_af_stake == bal_b4_stake - fee_stk - ChainConfig.STK_AMOUNT

    validator.stk_wait_till_i_am_in_waiting_next_random()

    INFO(f'Wait 40s to shard confirm')
    WAIT(40)
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    if beacon_bsd.is_he_in_waiting_next_random(validator) is False:
        pytest.skip(f'validator {validator.validator_key} must exist in the list waiting for random')

    STEP(2, 'Un_staking')
    fee_un_stk = the_stake.stk_un_stake_tx(validator).subscribe_transaction().get_fee()
    bal_af_un_stake = the_stake.wait_for_balance_change(from_balance=bal_af_stake,
                                                        least_change_amount=(ChainConfig.STK_AMOUNT - fee_un_stk),
                                                        timeout=4000)
    assert bal_af_un_stake == bal_b4_stake - fee_stk - fee_un_stk

    WAIT(60)  # wait to he swap out, is not validator

    STEP(3, 'Verify validator swap out')
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    assert beacon_bsd.get_auto_staking_committees(validator) is None


@pytest.mark.parametrize("the_stake, validator, receiver_reward, auto_re_stake", [
    pytest.param(account_y, account_y, account_y, False,
                 marks=pytest.mark.xfail(reason="auto re stake = False, can not un stake")),
    pytest.param(account_y, account_y, account_x, False,
                 marks=pytest.mark.xfail(reason="auto re stake = False, can not un stake")),
    pytest.param(account_x, account_y, account_x, False,
                 marks=pytest.mark.xfail(reason="auto re stake = False, can not un stake")),
    pytest.param(account_x, account_y, account_y, False,
                 marks=pytest.mark.xfail(reason="auto re stake = False, can not un stake")),
    (account_x, account_y, account_t, False),
    (account_y, account_y, account_y, True),
    (account_y, account_y, account_x, True),
    (account_x, account_y, account_x, True),
    (account_x, account_y, account_y, True),
    (account_x, account_y, account_t, True)
])
def _test_un_stake_when_exist_pending(the_stake, validator, receiver_reward, auto_re_stake):
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    if beacon_bsd.get_auto_staking_committees(validator) is True:
        pytest.skip(f'validator {validator.validator_key} is existed in committee with auto re-stake: True')
    elif beacon_bsd.get_auto_staking_committees(validator) is False:
        validator.stk_wait_till_i_am_out_of_autostaking_list()

    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1751), coin(1850), the_stake)
    bal_b4_stake = the_stake.get_prv_balance()

    STEP(1, 'Staking')
    fee_stk = the_stake.stake(validator, receiver_reward, auto_re_stake=auto_re_stake).subscribe_transaction().get_fee()
    bal_af_stake = the_stake.wait_for_balance_change(from_balance=bal_b4_stake,
                                                     least_change_amount=(- fee_stk - ChainConfig.STK_AMOUNT))
    assert bal_af_stake == bal_b4_stake - fee_stk - ChainConfig.STK_AMOUNT

    validator.stk_wait_till_i_am_in_shard_pending()

    STEP(2, 'Un_staking')
    fee_un_stk = the_stake.stk_un_stake_tx(validator).subscribe_transaction().get_fee()
    bal_af_un_stake = the_stake.wait_for_balance_change(from_balance=bal_af_stake, least_change_amount=-fee_un_stk)
    assert bal_af_un_stake == bal_af_stake - fee_un_stk

    WAIT(60)  # wait to convert status auto re-stake

    STEP(3, 'Verify auto staking is False')
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    assert beacon_bsd.get_auto_staking_committees(validator) is False


@pytest.mark.parametrize("the_stake, validator, receiver_reward, auto_re_stake", [
    pytest.param(account_y, account_y, account_y, False,
                 marks=pytest.mark.xfail(reason="auto re stake = False, can not un stake")),
    pytest.param(account_y, account_y, account_x, False,
                 marks=pytest.mark.xfail(reason="auto re stake = False, can not un stake")),
    pytest.param(account_x, account_y, account_x, False,
                 marks=pytest.mark.xfail(reason="auto re stake = False, can not un stake")),
    pytest.param(account_y, account_y, account_x, False,
                 marks=pytest.mark.xfail(reason="auto re stake = False, can not un stake")),
    (account_x, account_y, account_x, False),
    (account_x, account_y, account_y, False),
    (account_x, account_y, account_t, False),
    (account_y, account_y, account_y, True),
    (account_y, account_y, account_x, True),
    (account_x, account_y, account_x, True),
    (account_x, account_y, account_y, True),
    (account_x, account_y, account_t, True)
])
def test_un_stake_when_exist_shard_committee(the_stake, validator, receiver_reward, auto_re_stake):
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    if beacon_bsd.get_auto_staking_committees(validator) is True:
        pytest.skip(f'validator {validator.validator_key} is existed in committee with auto re-stake: True')
    elif beacon_bsd.get_auto_staking_committees(validator) is False:
        validator.stk_wait_till_i_am_out_of_autostaking_list()

    COIN_MASTER.top_him_up_prv_to_amount_if(coin(1751), coin(1850), the_stake)
    bal_b4_stake = the_stake.get_prv_balance()

    STEP(1, 'Staking')
    fee_stk = the_stake.stake(validator, receiver_reward, auto_re_stake=auto_re_stake).subscribe_transaction().get_fee()
    bal_af_stake = the_stake.wait_for_balance_change(from_balance=bal_b4_stake,
                                                     least_change_amount=(- fee_stk - ChainConfig.STK_AMOUNT))
    assert bal_af_stake == bal_b4_stake - fee_stk - ChainConfig.STK_AMOUNT

    validator.stk_wait_till_i_am_committee()

    STEP(2, 'Un_staking')
    fee_un_stk = the_stake.stk_un_stake_tx(validator).subscribe_transaction().get_fee()
    bal_af_un_stake = the_stake.wait_for_balance_change(from_balance=bal_af_stake, least_change_amount=-fee_un_stk)
    assert bal_af_un_stake == bal_af_stake - fee_un_stk

    WAIT(60)  # wait to convert status auto re-stake

    STEP(3, 'Verify auto staking is False')
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    assert beacon_bsd.get_auto_staking_committees(validator) is False
