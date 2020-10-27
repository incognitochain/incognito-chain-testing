from IncognitoChain.Configs.Constants import coin, ChainConfig
from IncognitoChain.Helpers.Logging import INFO, ERROR
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Objects.AccountObject import Account, COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import SUT

stake_account = Account(
    "112t8sw4ZAc1wwbKog9NhE6VqpEiPii4reg8Zc5AVGu7BkxtPYv95dXRJtzP9CkepgzfUwTseNzgHXRovo9oDb8XrEpb5EgFhKdZhwjzHTbd")

# Prepare coin to test
if stake_account.get_prv_balance() < coin(1750):
    COIN_MASTER.send_prv_to(stake_account, coin(1850) - stake_account.get_prv_balance_cache(),
                            privacy=0).subscribe_transaction()
    if stake_account.shard != COIN_MASTER.shard:
        stake_account.subscribe_cross_output_coin()


def stake_and_check_balance_after_stake(account):
    """
    Function to stake and check balance after stake
    :param account: account to stake
    :return: transaction id and balance of account after stake
    """
    INFO('Get epoch number')
    beacon_state = SUT.REQUEST_HANDLER.get_beacon_best_state_info()
    beacon_height = beacon_state.get_beacon_height()
    epoch_number = beacon_state.get_epoch()
    INFO(f'Ready to stake at epoch: {epoch_number}, beacon height: {beacon_height}')

    INFO('Stake and check balance after stake')
    balance_before_staking = account.get_prv_balance()
    stake_response = account.stake_and_reward_me(auto_re_stake=False)
    stake_response.subscribe_transaction()
    stake_fee = stake_response.get_transaction_by_hash().get_fee()
    balance_after_staking = stake_account.get_prv_balance()
    tx_id = stake_response.get_tx_id()
    assert balance_before_staking == balance_after_staking + stake_fee + coin(1750)

    return balance_after_staking, tx_id, epoch_number, beacon_height


def find_public_key_in_beacon_best_state_detail(account, balance_after_staking, thread_result_beacon, stake_at_epoch,
                                                stake_at_beacon_height):
    """
    Function to find public key in beacon best state detail
    :param account: account for testing
    :param balance_after_staking: balance of account testing
    :param thread_result_beacon: thread result of beacon objs
    :return: None
    """
    shard_waiting_next_random_bool = False
    shard_waiting_current_random_bool = False
    shard_pending_validator_bool = False
    swap_out_of_committee_bool = False
    shard_committee_bool = False
    epoch_before = 0
    beacon_height_before = 0
    count_committee_times = 0
    position_committee = 0
    shard_id_in_shard_committee = 0

    for beacon in thread_result_beacon:
        # Find public key of account stake in candidate shard waiting next random
        if beacon.get_candidate_shard_waiting_next_random() != []:
            for candidate_shard_waiting_next_random in beacon.get_candidate_shard_waiting_next_random():
                if account.public_key == candidate_shard_waiting_next_random.get_inc_public_key() and shard_waiting_next_random_bool == False:
                    shard_waiting_next_random_bool = True
                    auto_staking_variable = False
                    public_key_in_shard_waiting_next_random = account.public_key
                    epoch_in_shard_waiting_next_random = beacon.get_epoch()
                    beacon_height_in_shard_waiting_next_random = beacon.get_beacon_height()
                    shard_height_in_shard_waiting_next_random_0 = beacon.get_best_shard_height(0)
                    shard_height_in_shard_waiting_next_random_1 = beacon.get_best_shard_height(1)
                    for auto_staking in beacon.get_auto_staking_committees():
                        if account.public_key == auto_staking.get_inc_public_key():
                            auto_staking_variable = auto_staking.is_auto_staking()
                    INFO(f""" 
                            ************* Candidate Shard Waiting For Next Random *********
                            - Public key: {public_key_in_shard_waiting_next_random}
                            - Epoch: {epoch_in_shard_waiting_next_random}
                            - BeaconHeight: {beacon_height_in_shard_waiting_next_random}
                            - Best Shard Height 0: {shard_height_in_shard_waiting_next_random_0}
                            - Best Shard Height 1: {shard_height_in_shard_waiting_next_random_1}
                            - Auto Staking: {auto_staking_variable}
                            ****************************************************************
                                """)

                if account.public_key == candidate_shard_waiting_next_random.get_inc_public_key() and \
                        beacon.get_beacon_height() > stake_at_beacon_height + ChainConfig.BLOCK_PER_EPOCH and beacon.get_epoch() == stake_at_epoch + 1:
                    ERROR(f""" 
                            ************* Candidate Shard Waiting For Next Random *********
                            - Public key of committee: {account.public_key} exist in candidate shard waiting for next random
                            - Epoch: {beacon.get_epoch()}
                            - BeaconHeight: {beacon.get_beacon_height()}
                            ****************************************************************
                                """)
                elif account.public_key == candidate_shard_waiting_next_random.get_inc_public_key() and \
                        beacon.get_beacon_height() > stake_at_beacon_height + ChainConfig.BLOCK_PER_EPOCH / 2 and beacon.get_epoch() == stake_at_epoch:
                    ERROR(f""" 
                            ************* Candidate Shard Waiting For Next Random *********
                            - Public key of committee: {account.public_key} exist in candidate shard waiting for next random
                            - Epoch: {beacon.get_epoch()}
                            - BeaconHeight: {beacon.get_beacon_height()}
                            ****************************************************************
                                """)

        # Find public key of account stake in candidate shard waiting current random
        if beacon.get_candidate_shard_waiting_current_random() != []:
            for candidate_shard_waiting_current_random in beacon.get_candidate_shard_waiting_current_random():
                if account.public_key == candidate_shard_waiting_current_random.get_inc_public_key() and shard_waiting_current_random_bool == False:
                    shard_waiting_current_random_bool = True
                    public_key_in_shard_waiting_current_random = account.public_key
                    epoch_in_shard_waiting_current_random = beacon.get_epoch()
                    beacon_height_in_shard_waiting_current_random = beacon.get_beacon_height()
                    shard_height_in_shard_waiting_current_random_0 = beacon.get_best_shard_height(0)
                    shard_height_in_shard_waiting_current_random_1 = beacon.get_best_shard_height(1)
                    INFO(f""" 
                            ************ Candidate Shard Waiting For Current Random ********
                            - Public key: {public_key_in_shard_waiting_current_random}
                            - Epoch: {epoch_in_shard_waiting_current_random}
                            - BeaconHeight: {beacon_height_in_shard_waiting_current_random}
                            - Best Shard Height 0: {shard_height_in_shard_waiting_current_random_0}
                            - Best Shard Height 1: {shard_height_in_shard_waiting_current_random_1}
                            ****************************************************************
                                """)

                if account.public_key == candidate_shard_waiting_current_random.get_inc_public_key() and \
                        beacon.get_beacon_height() > (
                        stake_at_epoch * ChainConfig.BLOCK_PER_EPOCH - ChainConfig.BLOCK_PER_EPOCH / 2 + 1) and beacon.get_epoch() == stake_at_epoch:
                    ERROR(f""" 
                            ************* Candidate Shard Waiting For Current Random *********
                            - Public key of committee: {account.public_key} exist in candidate shard waiting for current random
                            - Epoch: {beacon.get_epoch()}
                            - BeaconHeight: {beacon.get_beacon_height()}
                            ****************************************************************
                                """)
                elif account.public_key == candidate_shard_waiting_current_random.get_inc_public_key() and \
                        beacon.get_beacon_height() > ((
                                                              stake_at_epoch + 1) * ChainConfig.BLOCK_PER_EPOCH - ChainConfig.BLOCK_PER_EPOCH / 2 + 1) and beacon.get_epoch() == stake_at_epoch + 1:
                    ERROR(f""" 
                            ************* Candidate Shard Waiting For Current Random *********
                            - Public key of committee: {account.public_key} exist in candidate shard waiting for current random
                            - Epoch: {beacon.get_epoch()}
                            - BeaconHeight: {beacon.get_beacon_height()}
                            ****************************************************************
                                """)

        # Find public key of account stake in shard pending validator
        for key, value in beacon.get_shard_pending_validator().items():
            if value != []:
                for committee in value:
                    if account.public_key == committee.get_inc_public_key() and shard_pending_validator_bool == False:
                        shard_pending_validator_bool = True
                        public_key_in_shard_pending_validator = account.public_key
                        epoch_in_shard_pending_validator = beacon.get_epoch()
                        beacon_height_in_shard_pending_validator = beacon.get_beacon_height()
                        shard_id_in_shard_pending_validator = key
                        shard_height_in_shard_pending_validator_0 = beacon.get_best_shard_height(0)
                        shard_height_in_shard_pending_validator_1 = beacon.get_best_shard_height(1)
                        INFO(f""" 
                            ****************** Shard Pending Validator *********************
                            - Public key: {public_key_in_shard_pending_validator}
                            - Epoch: {epoch_in_shard_pending_validator}
                            - Beacon Height: {beacon_height_in_shard_pending_validator}
                            - Shard ID: {shard_id_in_shard_pending_validator}
                            - Best Shard Height 0: {shard_height_in_shard_pending_validator_0}
                            - Best Shard Height 1: {shard_height_in_shard_pending_validator_1}
                            ****************************************************************
                                    """)

        # Find public key and the location of account stake in shard committee
        for key, value in beacon.get_shard_committees().items():
            count_committee = 0
            for committee in value:
                if account.public_key == committee.get_inc_public_key():
                    epoch_after = beacon.get_epoch()
                    beacon_height_after = beacon.get_beacon_height()
                    shard_committee_bool = True
                    if epoch_after > epoch_before and beacon_height_after >= beacon_height_before + ChainConfig.BLOCK_PER_EPOCH:
                        count_committee_times = count_committee_times + 1
                        epoch_before = epoch_after
                        beacon_height_before = beacon_height_after
                        public_key_in_shard_committee = account.public_key
                        epoch_in_shard_committee = beacon.get_epoch()
                        beacon_height_in_shard_committee = beacon.get_beacon_height()
                        shard_id_in_shard_committee = key
                        shard_height_in_shard_committee_0 = beacon.get_best_shard_height(0)
                        shard_height_in_shard_committee_1 = beacon.get_best_shard_height(1)
                        # Find the location of the public key of account stake in shard committee
                        for index in range(len(value)):
                            if account.public_key == value[index].get_inc_public_key():
                                position_committee = index + 1
                        INFO(f""" 
                            ********************** Shard Committee *************************
                            - The number of occurrences of validator {account.validator_key} in shard committee is {count_committee_times}
                            - Public key: {public_key_in_shard_committee}
                            - Epoch: {epoch_in_shard_committee}
                            - BeaconHeight: {beacon_height_in_shard_committee}
                            - Shard ID: {shard_id_in_shard_committee}
                            - Best Shard Height 0: {shard_height_in_shard_committee_0}
                            - Best Shard Height 1: {shard_height_in_shard_committee_1}
                            - Position: {position_committee}
                            ****************************************************************
                                    """)

                if account.public_key != committee.get_inc_public_key() and shard_committee_bool == True and shard_id_in_shard_committee == key:
                    count_committee = count_committee + 1

                if count_committee == len(value) and swap_out_of_committee_bool == False:
                    swap_out_of_committee_bool = True
                    INFO(f""" 
                        ********************** Shard Committee *************************
                        - Validator key {account.validator_key} no longer a committee
                        - Epoch: {beacon.get_epoch()}
                        - BeaconHeight: {beacon.get_beacon_height()}
                        ****************************************************************
                                """)

                    INFO(f'Balance before refund (after staking) = {balance_after_staking}')
                    balance_after_refund = account.wait_for_balance_change(from_balance=balance_after_staking,
                                                                           timeout=180)

                    INFO(f"Verify that balance after refund +1750 prv = {balance_after_refund}")
                    assert balance_after_refund == balance_after_staking + coin(1750), \
                        f'Error: Balance before refund {balance_after_staking} and Balance after refund {balance_after_refund} are not equal'

                    prv_reward_amount = account.stk_get_reward_amount()
                    INFO(f"Total PRV reward amount on {count_committee_times} epoch: {prv_reward_amount}")

                    avg_prv_reward = prv_reward_amount / count_committee_times
                    INFO(f'AVG PRV reward per 1 epoch = {avg_prv_reward}')

                    INFO('Withdraw PRV reward and verify balance')
                    account.stk_withdraw_reward_to_me().subscribe_transaction()
                    prv_bal_after_withdraw_reward = account.wait_for_balance_change(from_balance=balance_after_refund,
                                                                                    timeout=180)

                    INFO(f'Expect reward amount to received {prv_reward_amount}')
                    assert prv_bal_after_withdraw_reward == balance_after_refund + prv_reward_amount


def find_public_key_in_shard_best_state_detail(account, staking_tx_id, thread_result_shard_id):
    """
    Function to find public key in shard best state detail
    :param account: account for testing
    :param staking_tx_id: staking transaction id
    :param thread_result_shard_id: thread result of shard objs
    :return: None
    """
    shard_pending_validator_bool = False
    shard_committee_bool = False
    check_staking_tx = False
    swap_out_of_committee_bool = False
    position_committee = 0
    count_committee_times = 0
    shard_height_before = 0
    count_staking_tx = 0

    for shard_id in thread_result_shard_id:
        # Find staking transaction
        if shard_id.get_staking_tx() != []:
            for index_staking_tx in shard_id.get_staking_tx():
                for key, value in index_staking_tx.items():
                    if staking_tx_id == value and check_staking_tx == False:
                        check_staking_tx = True
                        INFO(f"""
                            ************ Found transaction id: {value} in staking transaction ***************
                            - Public Key: {account.public_key}
                            - Shard ID: {shard_id.get_shard_id()}
                            ***********************************************************
                                """)

        # Find public key of account stake in shard pending validator
        if shard_id.get_shard_pending_validator() != []:
            for committee in shard_id.get_shard_pending_validator():
                if account.public_key == committee.get_inc_public_key() and shard_pending_validator_bool == False:
                    shard_pending_validator_bool = True
                    public_key_in_shard_pending_validator = account.public_key
                    epoch_in_shard_pending_validator = shard_id.get_epoch()
                    shard_height_in_shard_pending_validator = shard_id.get_shard_height()
                    beacon_height_in_shard_pending_validator = shard_id.get_beacon_height()
                    shard_id_in_shard_pending_validator = shard_id.get_shard_id()
                    INFO(f"""
                            *********** Shard {shard_id_in_shard_pending_validator} Pending Validator ********
                            - Public key: {public_key_in_shard_pending_validator}
                            - Epoch: {epoch_in_shard_pending_validator}
                            - Beacon Height: {beacon_height_in_shard_pending_validator}
                            - Shard ID: {shard_id_in_shard_pending_validator}
                            - Shard Height: {shard_height_in_shard_pending_validator}
                            ************************************************************
                                """)

        # Find public key of account stake in shard committee
        if shard_id.get_shard_committee() != []:
            count_committee = 0
            for committee in shard_id.get_shard_committee():
                if account.public_key == committee.get_inc_public_key():
                    shard_committee_bool = True
                    shard_height_after = shard_id.get_shard_height()
                    if shard_height_after >= shard_height_before + ChainConfig.BLOCK_PER_EPOCH:
                        shard_height_before = shard_height_after
                        count_committee_times = count_committee_times + 1
                        public_key_in_shard_committee = account.public_key
                        epoch_in_shard_shard_committee = shard_id.get_epoch()
                        shard_height_in_shard_committee = shard_id.get_shard_height()
                        beacon_height_in_shard_committee = shard_id.get_beacon_height()
                        shard_id_in_shard_committee = shard_id.get_shard_id()
                        # Find the location of the public key of account stake in shard committee
                        for index in range(len(shard_id.get_shard_committee())):
                            if account.public_key == shard_id.get_shard_committee()[index].get_inc_public_key():
                                position_committee = index + 1
                        INFO(f"""
                            ****************** Shard {shard_id_in_shard_committee} Committee *****************
                            - The number of occurrences of validator {account.validator_key} in shard committee is {count_committee_times}
                            - Public key: {public_key_in_shard_committee}
                            - Epoch: {epoch_in_shard_shard_committee}
                            - Beacon Height: {beacon_height_in_shard_committee}
                            - Shard ID: {shard_id_in_shard_committee}
                            - Shard Height: {shard_height_in_shard_committee}
                            - Position: {position_committee}
                            ************************************************************
                                    """)
            for committee in shard_id.get_shard_committee():
                if account.public_key != committee.get_inc_public_key() and shard_committee_bool == True:
                    count_committee = count_committee + 1
                    if count_committee == len(shard_id.get_shard_committee()) and swap_out_of_committee_bool == False:
                        swap_out_of_committee_bool = True
                        INFO(f""" 
                            ****************** Shard {shard_id.get_shard_id()} Committee *****************
                            - Validator key {account.validator_key} no longer a committee
                            - Epoch: {shard_id.get_epoch()}
                            - BeaconHeight: {shard_id.get_beacon_height()}
                            ****************************************************************
                                    """)
                        for index_staking_tx in shard_id.get_staking_tx():
                            for key, value in index_staking_tx.items():
                                if staking_tx_id != value:
                                    count_staking_tx = count_staking_tx + 1
                        if count_staking_tx == len(shard_id.get_staking_tx()):
                            INFO(f""" 
                            ****************** Shard {shard_id.get_shard_id()} Committee *****************
                            - Staking transaction id: {staking_tx_id} does not exist in StakingTx
                            - Epoch: {shard_id.get_epoch()}
                            - BeaconHeight: {shard_id.get_beacon_height()}
                            ****************************************************************
                                        """)
                        else:
                            ERROR(f""" 
                            ****************** Shard {shard_id.get_shard_id()} Committee *****************
                            - Staking transaction id: {staking_tx_id} exists in StakingTx
                            - Epoch: {shard_id.get_epoch()}
                            - BeaconHeight: {shard_id.get_beacon_height()}
                            ****************************************************************
                                        """)


def find_committee_public_key_in_beacon_best_state(account, balance_after_staking, thread_result_beacon, stake_at_epoch,
                                                   stake_at_beacon_height):
    """
    Function to find committee public key in beacon best state detail
    :param account: account for testing
    :param balance_after_staking: balance of account testing after staking
    :param thread_result_beacon: thread result of beacon objs
    :return:
    """
    shard_waiting_next_random_bool = False
    shard_waiting_current_random_bool = False
    shard_pending_validator_bool = False
    shard_committee_bool = False
    swap_out_of_committee_bool = False
    epoch_before = 0
    beacon_height_before = 0
    count_committee_times = 0
    position_committee = 0
    shard_id_in_shard_committee = 0

    for beacon in thread_result_beacon:
        # Find committee public key of account stake in candidate shard waiting next random
        if beacon.get_candidate_shard_waiting_next_random() != []:
            for candidate_shard_waiting_next_random in beacon.get_candidate_shard_waiting_next_random():
                if account.committee_public_k == candidate_shard_waiting_next_random and shard_waiting_next_random_bool == False:
                    shard_waiting_next_random_bool = True
                    committee_public_key_in_shard_waiting_next_random = account.committee_public_k
                    epoch_in_shard_waiting_next_random = beacon.get_epoch()
                    beacon_height_in_shard_waiting_next_random = beacon.get_beacon_height()
                    shard_height_in_shard_waiting_next_random_0 = beacon.get_best_shard_height(0)
                    shard_height_in_shard_waiting_next_random_1 = beacon.get_best_shard_height(1)
                    auto_staking_variable = beacon.get_auto_staking_committees(account.committee_public_k)
                    INFO(f"""
                            ************* Candidate Shard Waiting For Next Random *********
                            - Committee Public Key: {l6(committee_public_key_in_shard_waiting_next_random)}
                            - Epoch: {epoch_in_shard_waiting_next_random}
                            - Beacon Height: {beacon_height_in_shard_waiting_next_random}
                            - Best Shard Height 0: {shard_height_in_shard_waiting_next_random_0}
                            - Best Shard Height 1: {shard_height_in_shard_waiting_next_random_1}
                            - Auto Staking: {auto_staking_variable}
                            ****************************************************************
                                """)

                if account.committee_public_k == candidate_shard_waiting_next_random and \
                        beacon.get_beacon_height() > stake_at_beacon_height + ChainConfig.BLOCK_PER_EPOCH and beacon.get_epoch() == stake_at_epoch + 1:
                    ERROR(f""" 
                            ************* Candidate Shard Waiting For Next Random *********
                            - Committee public key: {l6(account.committee_public_k)} exist in candidate shard waiting for next random
                            - Epoch: {beacon.get_epoch()}
                            - BeaconHeight: {beacon.get_beacon_height()}
                            ****************************************************************
                                """)
                elif account.committee_public_k == candidate_shard_waiting_next_random and \
                        beacon.get_beacon_height() > stake_at_beacon_height + ChainConfig.BLOCK_PER_EPOCH / 2 and beacon.get_epoch() == stake_at_epoch:
                    ERROR(f""" 
                            ************* Candidate Shard Waiting For Next Random *********
                            - Committee public key: {l6(account.committee_public_k)} exist in candidate shard waiting for next random
                            - Epoch: {beacon.get_epoch()}
                            - BeaconHeight: {beacon.get_beacon_height()}
                            ****************************************************************
                                """)

        # Find committee public key of account stake in candidate shard waiting current random
        if beacon.get_candidate_shard_waiting_current_random() != []:
            for candidate_shard_waiting_current_random in beacon.get_candidate_shard_waiting_current_random():
                if account.committee_public_k == candidate_shard_waiting_current_random and shard_waiting_current_random_bool == False:
                    shard_waiting_current_random_bool = True
                    committee_public_key_in_shard_waiting_current_random = account.committee_public_k
                    epoch_in_shard_waiting_current_random = beacon.get_epoch()
                    beacon_height_in_shard_waiting_current_random = beacon.get_beacon_height()
                    shard_height_in_shard_waiting_current_random_0 = beacon.get_best_shard_height(0)
                    shard_height_in_shard_waiting_current_random_1 = beacon.get_best_shard_height(1)
                    INFO(f"""
                            ************ Candidate Shard Waiting For Current Random ********
                            - Committee Public Key: {l6(committee_public_key_in_shard_waiting_current_random)}
                            - Epoch: {epoch_in_shard_waiting_current_random}
                            - Beacon Height: {beacon_height_in_shard_waiting_current_random}
                            - Best Shard Height 0: {shard_height_in_shard_waiting_current_random_0}
                            - Best Shard Height 1: {shard_height_in_shard_waiting_current_random_1}
                            ****************************************************************
                                """)

                if account.committee_public_k == candidate_shard_waiting_current_random and \
                        beacon.get_beacon_height() > (
                        stake_at_epoch * ChainConfig.BLOCK_PER_EPOCH - ChainConfig.BLOCK_PER_EPOCH / 2 + 1) and beacon.get_epoch() == stake_at_epoch:
                    ERROR(f"""
                            ************ Candidate Shard Waiting For Current Random ********
                            - Committee public key: {l6(account.committee_public_k)} exist in candidate shard waiting for current random
                            - Epoch: {beacon.get_epoch()}
                            - Beacon Height: {beacon.get_beacon_height()}
                            ****************************************************************
                                """)
                elif account.committee_public_k == candidate_shard_waiting_current_random and \
                        beacon.get_beacon_height() > ((
                                                              stake_at_epoch + 1) * ChainConfig.BLOCK_PER_EPOCH - ChainConfig.BLOCK_PER_EPOCH / 2 + 1) and beacon.get_epoch() == stake_at_epoch + 1:
                    ERROR(f"""
                            ************ Candidate Shard Waiting For Current Random ********
                            - Committee public key: {l6(account.committee_public_k)} exist in candidate shard waiting for current random
                            - Epoch: {beacon.get_epoch()}
                            - Beacon Height: {beacon.get_beacon_height()}
                            ****************************************************************
                                """)

        # Find committee public key of account stake in shard pending validator
        for key, value in beacon.get_shard_pending_validator().items():
            if value != []:
                for pending_validator in value:
                    if account.committee_public_k == pending_validator and shard_pending_validator_bool == False:
                        shard_pending_validator_bool = True
                        committee_public_key_in_shard_pending_validator = account.committee_public_k
                        epoch_in_shard_pending_validator = beacon.get_epoch()
                        beacon_height_in_shard_pending_validator = beacon.get_beacon_height()
                        shard_id_in_shard_pending_validator = key
                        shard_height_in_shard_pending_validator_0 = beacon.get_best_shard_height(0)
                        shard_height_in_shard_pending_validator_1 = beacon.get_best_shard_height(1)
                        INFO(f"""
                            ****************** Shard Pending Validator *********************
                            - Committee Public Key: {l6(committee_public_key_in_shard_pending_validator)}
                            - Epoch: {epoch_in_shard_pending_validator}
                            - Beacon Height: {beacon_height_in_shard_pending_validator}
                            - Shard ID: {shard_id_in_shard_pending_validator}
                            - Best Shard Height 0: {shard_height_in_shard_pending_validator_0}
                            - Best Shard Height 1: {shard_height_in_shard_pending_validator_1}
                            ****************************************************************
                                    """)

        # Find committee public key and the location of account stake in shard committee
        for key, value in beacon.get_shard_committees().items():
            count_committee = 0
            for committee_public_key in value:
                if account.committee_public_k == committee_public_key:
                    epoch_after = beacon.get_epoch()
                    beacon_height_after = beacon.get_beacon_height()
                    shard_committee_bool = True
                    if epoch_after > epoch_before and beacon_height_after >= beacon_height_before + ChainConfig.BLOCK_PER_EPOCH:
                        epoch_before = epoch_after
                        beacon_height_before = beacon_height_after
                        count_committee_times = count_committee_times + 1
                        committee_public_key_in_shard_committee = account.committee_public_k
                        epoch_in_shard_committee = beacon.get_epoch()
                        beacon_height_in_shard_committee = beacon.get_beacon_height()
                        shard_id_in_shard_committee = key
                        shard_height_in_shard_committee_0 = beacon.get_best_shard_height(0)
                        shard_height_in_shard_committee_1 = beacon.get_best_shard_height(1)
                        # Find the location of the committee public key of account stake in shard committee
                        for index in range(len(value)):
                            if account.committee_public_k == value[index]:
                                position_committee = index + 1
                        INFO(f"""
                            ********************** Shard Committee *************************
                            - The number of occurrences of validator {account.validator_key} in shard committee is {count_committee_times}
                            - Committee Public Key: {l6(committee_public_key_in_shard_committee)}
                            - Epoch: {epoch_in_shard_committee}
                            - BeaconHeight: {beacon_height_in_shard_committee}
                            - Shard ID: {shard_id_in_shard_committee}
                            - Best Shard Height 0: {shard_height_in_shard_committee_0}
                            - Best Shard Height 1: {shard_height_in_shard_committee_1}
                            - Position: {position_committee}
                            ****************************************************************
                                    """)

                if account.committee_public_k != committee_public_key and shard_committee_bool == True and shard_id_in_shard_committee == key:
                    count_committee = count_committee + 1

                if count_committee == len(value) and swap_out_of_committee_bool == False:
                    swap_out_of_committee_bool = True
                    INFO(f""" 
                        ********************** Shard Committee *************************
                        - Validator key {account.validator_key} no longer a committee
                        - Epoch: {beacon.get_epoch()}
                        - BeaconHeight: {beacon.get_beacon_height()}
                        ****************************************************************
                                """)

                    INFO(f'Balance before refund (after staking) = {balance_after_staking}')
                    balance_after_refund = account.wait_for_balance_change(from_balance=balance_after_staking,
                                                                           timeout=180)

                    INFO(f"Verify that balance after refund +1750 prv = {balance_after_refund}")
                    assert balance_after_refund == balance_after_staking + coin(1750), \
                        f'Error: Balance before refund {balance_after_staking} and Balance after refund {balance_after_refund} are not equal'

                    prv_reward_amount = account.stk_get_reward_amount()
                    INFO(f"Total PRV reward amount on {count_committee_times} epoch: {prv_reward_amount}")

                    avg_prv_reward = prv_reward_amount / count_committee_times
                    INFO(f'AVG PRV reward per 1 epoch = {avg_prv_reward}')

                    INFO('Withdraw PRV reward and verify balance')
                    account.stk_withdraw_reward_to_me().subscribe_transaction()
                    prv_bal_after_withdraw_reward = account.wait_for_balance_change(
                        from_balance=balance_after_refund, timeout=180)

                    INFO(f'Expect reward amount to received {prv_reward_amount}')
                    assert prv_bal_after_withdraw_reward == balance_after_refund + prv_reward_amount


def find_committee_public_key_in_shard_best_state(account, staking_tx_id, thread_result_shard_id):
    """
    Function to find committee public key in shard best state detail
    :param account:
    :param staking_tx_id:
    :param thread_result_shard_id:
    :return:
    """
    shard_pending_validator_bool = False
    shard_committee_bool = False
    check_staking_tx = False
    swap_out_of_committee_bool = False
    count_committee_times = 0
    shard_height_before = 0
    position_committee = 0
    count_staking_tx = 0

    for shard_id in thread_result_shard_id:
        # Find staking transaction
        if shard_id.get_staking_tx() != []:
            for index_staking_tx in shard_id.get_staking_tx():
                for key, value in index_staking_tx.items():
                    if staking_tx_id == value and account.committee_public_k == key and check_staking_tx == False:
                        check_staking_tx = True
                        INFO(f"""
                            ************ Found transaction id: {value} in StakingTx ***************
                            - Committee Public Key: {l6(account.committee_public_k)}
                            - Shard ID: {shard_id.get_shard_id()}
                            ***********************************************************
                                """)

        # Find committee public key of account stake in shard pending validator
        if shard_id.get_shard_pending_validator() != []:
            for committee in shard_id.get_shard_pending_validator():
                if account.committee_public_k == committee and shard_pending_validator_bool == False:
                    shard_pending_validator_bool = True
                    committee_public_key_in_shard_pending_validator = account.committee_public_k
                    epoch_in_shard_pending_validator = shard_id.get_epoch()
                    shard_height_in_shard_pending_validator = shard_id.get_shard_height()
                    beacon_height_in_shard_pending_validator = shard_id.get_beacon_height()
                    shard_id_in_shard_pending_validator = shard_id.get_shard_id()
                    INFO(f"""
                            *********** Shard {shard_id_in_shard_pending_validator} Pending Validator ********
                            - Committee Public Key: {l6(committee_public_key_in_shard_pending_validator)}
                            - Epoch: {epoch_in_shard_pending_validator}
                            - Beacon Height: {beacon_height_in_shard_pending_validator}
                            - Shard ID: {shard_id_in_shard_pending_validator}
                            - Shard Height: {shard_height_in_shard_pending_validator}
                            ************************************************************
                                """)

        # Find committee public key of account stake in shard committee
        if shard_id.get_shard_committee() != []:
            count_committee = 0
            for committee in shard_id.get_shard_committee():
                if account.committee_public_k == committee:
                    shard_committee_bool = True
                    shard_height_after = shard_id.get_shard_height()
                    if shard_height_after >= shard_height_before + ChainConfig.BLOCK_PER_EPOCH:
                        shard_height_before = shard_height_after
                        count_committee_times = count_committee_times + 1
                        committee_public_key_in_shard_committee = account.committee_public_k
                        epoch_in_shard_shard_committee = shard_id.get_epoch()
                        shard_height_in_shard_committee = shard_id.get_shard_height()
                        beacon_height_in_shard_committee = shard_id.get_beacon_height()
                        shard_id_in_shard_committee = shard_id.get_shard_id()
                        # Find the location of the public key of account stake in shard committee
                        for index in range(len(shard_id.get_shard_committee())):
                            if account.committee_public_k == shard_id.get_shard_committee()[index]:
                                position_committee = index + 1
                        INFO(f"""
                            ****************** Shard {shard_id_in_shard_committee} Committee *****************
                            - The number of occurrences of validator {account.validator_key} in shard committee is {count_committee_times}
                            - Committee Public Key: {l6(committee_public_key_in_shard_committee)}
                            - Epoch: {epoch_in_shard_shard_committee}
                            - Beacon Height: {beacon_height_in_shard_committee}
                            - Shard ID: {shard_id_in_shard_committee}
                            - Shard Height: {shard_height_in_shard_committee}
                            - Position: {position_committee}
                            ************************************************************
                                    """)

            for committee in shard_id.get_shard_committee():
                if account.committee_public_k != committee and shard_committee_bool == True:
                    count_committee = count_committee + 1
                    if count_committee == len(shard_id.get_shard_committee()) and swap_out_of_committee_bool == False:
                        swap_out_of_committee_bool = True
                        INFO(f""" 
                            ****************** Shard {shard_id.get_shard_id()} Committee *****************
                            - Validator key {account.validator_key} no longer a committee
                            - Epoch: {shard_id.get_epoch()}
                            - BeaconHeight: {shard_id.get_beacon_height()}
                            ****************************************************************
                                    """)
                        for index_staking_tx in shard_id.get_staking_tx():
                            for key, value in index_staking_tx.items():
                                if staking_tx_id != value:
                                    count_staking_tx = count_staking_tx + 1
                        if count_staking_tx == len(shard_id.get_staking_tx()):
                            INFO(f""" 
                            ****************** Shard {shard_id.get_shard_id()} Committee *****************
                            - Staking transaction id: {staking_tx_id} does not exist in StakingTx
                            - Epoch: {shard_id.get_epoch()}
                            - BeaconHeight: {shard_id.get_beacon_height()}
                            ****************************************************************
                                    """)
                        else:
                            ERROR(f"""
                            ****************** Shard {shard_id.get_shard_id()} Committee *****************
                            - Staking transaction id: {staking_tx_id} exists in StakingTx
                            - Epoch: {shard_id.get_epoch()}
                            - BeaconHeight: {shard_id.get_beacon_height()}
                            ****************************************************************    
                                    """)
