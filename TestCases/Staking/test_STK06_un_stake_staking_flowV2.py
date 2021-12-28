"This testscript only use for staking flow V2."

import pytest

from Configs.Configs import ChainConfig
from Configs.Constants import coin
from Helpers.Logging import INFO, STEP, ERROR
from Helpers.TestHelper import ChainHelper
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.Staking import account_x, account_y, account_t

staking_flowv3 = True  # True if staking flow v3 is enable in chain config, or else, False


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
    (account_x, account_y, account_t, True),
])
def test_un_stake_when_waiting(the_stake, validator, receiver_reward, auto_re_stake):
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    if beacon_bsd.get_auto_staking_committees(validator) is True:
        pytest.skip(f'validator {validator.validator_key} is existed in committee with auto re-stake: True')
    elif beacon_bsd.get_auto_staking_committees(validator) is False:
        validator.stk_wait_till_i_am_out_of_autostaking_list()

    COIN_MASTER.top_up_if_lower_than(the_stake, coin(1751), coin(1850))
    bal_b4_stake = the_stake.get_balance()

    INFO('Calculate & wait to execute test at block that before transfer epoch time min 5 blocks')
    chain_info = SUT().get_block_chain_info()
    remaining_block_epoch = chain_info.get_beacon_block().get_remaining_block_epoch()
    if remaining_block_epoch >= ChainConfig.RANDOM_TIME:
        SUT().wait_till_next_beacon_height(remaining_block_epoch - ChainConfig.RANDOM_TIME)
    elif remaining_block_epoch < 5:
        ChainHelper.wait_till_next_epoch(1, ChainConfig.RANDOM_TIME)

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
    WAIT(60)  # wait to he swap out, is not validator

    STEP(3, 'Verify validator swap out')
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    assert beacon_bsd.get_auto_staking_committees(validator) is None

    STEP(4, 'Verify balance')
    bal_af_un_stake = the_stake.wait_for_balance_change(from_balance=bal_af_stake,
                                                        least_change_amount=(ChainConfig.STK_AMOUNT - fee_un_stk),
                                                        timeout=4000)
    assert bal_af_un_stake == bal_b4_stake - fee_stk - fee_un_stk


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
    (account_x, account_y, account_t, True),
])
def test_un_stake_when_exist_pending(the_stake, validator, receiver_reward, auto_re_stake):
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    if beacon_bsd.get_auto_staking_committees(validator) is True:
        pytest.skip(f'validator {validator.validator_key} is existed in committee with auto re-stake: True')
    elif beacon_bsd.get_auto_staking_committees(validator) is False:
        validator.stk_wait_till_i_am_out_of_autostaking_list()

    COIN_MASTER.top_up_if_lower_than(the_stake, coin(1751), coin(1850))
    bal_b4_stake = the_stake.get_balance()

    STEP(1, 'Staking')
    fee_stk = the_stake.stake(validator, receiver_reward, auto_re_stake=auto_re_stake).subscribe_transaction().get_fee()
    bal_af_stake = the_stake.wait_for_balance_change(from_balance=bal_b4_stake,
                                                     least_change_amount=(- fee_stk - ChainConfig.STK_AMOUNT))
    assert bal_af_stake == bal_b4_stake - fee_stk - ChainConfig.STK_AMOUNT

    if staking_flowv3:
        validator.stk_wait_till_i_am_in_sync_pool()
        validator.stk_wait_till_i_am_in_shard_pending(sfv3=staking_flowv3)
    else:
        validator.stk_wait_till_i_am_in_shard_pending()

    STEP(2, 'Un_staking')
    if auto_re_stake:
        fee_un_stk = the_stake.stk_un_stake_tx(validator).subscribe_transaction().get_fee()
        bal_af_un_stake = the_stake.wait_for_balance_change(from_balance=bal_af_stake, least_change_amount=-fee_un_stk)
        assert bal_af_un_stake == bal_af_stake - fee_un_stk

        WAIT(60)  # wait to convert status auto re-stake

        STEP(2.1, 'Verify auto staking is False')
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
        assert beacon_bsd.get_auto_staking_committees(validator) is False
    else:
        tx = the_stake.stk_un_stake_tx(validator)
        if tx.get_tx_id() is not None:
            ERROR(f'Trx stop auto staking be created, tx_id: {tx.get_tx_id()}')
            WAIT(50)
            res = tx.get_transaction_by_hash(time_out=0)
            if res.dict_data:
                fee = res.get_fee()
                bal_af_un_stake = the_stake.wait_for_balance_change(from_balance=bal_af_stake, least_change_amount=-fee)
                assert bal_af_un_stake == bal_af_stake - fee

    STEP(3, 'Verify cannot unstake when auto stake is False')
    the_stake.stk_un_stake_tx(validator).expect_error()


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
    (account_x, account_y, account_t, True),
])
def test_un_stake_when_exist_sync_pool(the_stake, validator, receiver_reward, auto_re_stake):
    if not staking_flowv3:
        pytest.skip('Only test for staking flow v3')
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    if beacon_bsd.get_auto_staking_committees(validator) is True:
        pytest.skip(f'validator {validator.validator_key} is existed in committee with auto re-stake: True')
    elif beacon_bsd.get_auto_staking_committees(validator) is False:
        validator.stk_wait_till_i_am_out_of_autostaking_list()

    COIN_MASTER.top_up_if_lower_than(the_stake, coin(1751), coin(1850))
    bal_b4_stake = the_stake.get_balance()

    STEP(1, 'Staking')
    fee_stk = the_stake.stake(validator, receiver_reward, auto_re_stake=auto_re_stake).subscribe_transaction().get_fee()
    bal_af_stake = the_stake.wait_for_balance_change(from_balance=bal_b4_stake,
                                                     least_change_amount=(- fee_stk - ChainConfig.STK_AMOUNT))
    assert bal_af_stake == bal_b4_stake - fee_stk - ChainConfig.STK_AMOUNT

    validator.stk_wait_till_i_am_in_sync_pool()

    STEP(2, 'Un_staking')
    if auto_re_stake:
        fee_un_stk = the_stake.stk_un_stake_tx(validator).subscribe_transaction().get_fee()
        bal_af_un_stake = the_stake.wait_for_balance_change(from_balance=bal_af_stake, least_change_amount=-fee_un_stk)
        assert bal_af_un_stake == bal_af_stake - fee_un_stk

        WAIT(60)  # wait to convert status auto re-stake

        STEP(2.1, 'Verify auto staking is False')
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
        assert beacon_bsd.get_auto_staking_committees(validator) is False
    else:
        tx = the_stake.stk_un_stake_tx(validator)
        if tx.get_tx_id() is not None:
            ERROR(f'Trx stop auto staking be created, tx_id: {tx.get_tx_id()}')
            WAIT(50)
            res = tx.get_transaction_by_hash(retry=False)
            if res.dict_data:
                fee = res.get_fee()
                bal_af_un_stake = the_stake.wait_for_balance_change(from_balance=bal_af_stake, least_change_amount=-fee)
                assert bal_af_un_stake == bal_af_stake - fee

    STEP(3, 'Verify cannot unstake when auto stake is False')
    the_stake.stk_un_stake_tx(validator).expect_error()


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
    (account_x, account_y, account_t, True),
])
def test_un_stake_when_exist_shard_committee(the_stake, validator, receiver_reward, auto_re_stake):
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    if beacon_bsd.get_auto_staking_committees(validator) is True:
        pytest.skip(f'validator {validator.validator_key} is existed in committee with auto re-stake: True')
    elif beacon_bsd.get_auto_staking_committees(validator) is False:
        validator.stk_wait_till_i_am_out_of_autostaking_list()

    COIN_MASTER.top_up_if_lower_than(the_stake, coin(1751), coin(1850))
    bal_b4_stake = the_stake.get_balance()

    STEP(1, 'Staking')
    fee_stk = the_stake.stake(validator, receiver_reward, auto_re_stake=auto_re_stake).subscribe_transaction().get_fee()
    bal_af_stake = the_stake.wait_for_balance_change(from_balance=bal_b4_stake,
                                                     least_change_amount=(- fee_stk - ChainConfig.STK_AMOUNT))
    assert bal_af_stake == bal_b4_stake - fee_stk - ChainConfig.STK_AMOUNT

    validator.stk_wait_till_i_am_committee()

    STEP(2, 'Un_staking')
    if auto_re_stake:
        fee_un_stk = the_stake.stk_un_stake_tx(validator).subscribe_transaction().get_fee()
        bal_af_un_stake = the_stake.wait_for_balance_change(from_balance=bal_af_stake, least_change_amount=-fee_un_stk)
        assert bal_af_un_stake == bal_af_stake - fee_un_stk

        WAIT(60)  # wait to convert status auto re-stake

        STEP(2.1, 'Verify auto staking is False')
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
        assert beacon_bsd.get_auto_staking_committees(validator) is False

    STEP(3, 'Verify cannot unstake when auto stake is False')
    the_stake.stk_un_stake_tx(validator).expect_error()
