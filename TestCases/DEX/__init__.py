import copy

from IncognitoChain.Configs.Constants import coin, PRV_ID
from IncognitoChain.Helpers.Logging import INFO, INFO_HEADLINE
from IncognitoChain.Helpers.TestHelper import calculate_actual_trade_received, l6
from IncognitoChain.Helpers.Time import get_current_date_time
from IncognitoChain.Objects.AccountObject import Account, COIN_MASTER, AccountGroup
from IncognitoChain.TestCases.Transactions import test_TRX008_init_contribute_send_custom_token as trx008

# contributor = ACCOUNTS[0]
token_owner = Account(
    '112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA')

# when token_id set to none, init new token and use it for the test
# otherwise, use token id for the test without initializing new token
# token_id = "a4442a68070fc615abee5e8c665808ebc1c670e5fd16f49ca8e992bf7c126739"
# token_id_1 = "4129f4ca2b2eba286a3bd1b96716d64e0bc02bd2cc1837776b66f67eb5797d79"  # testnet
# token_id_2 = "57f634b0d50e0ca8fb11c2d2f2989953e313b6b6c5c3393984adf13b26562f2b"  # testnet
# token_id_1 = "b9c7f272d283b570b9aa8ec756a22d311eaf16cab197843264a4eaaaffc46f4f"  # local
# token_id_2 = "78b3e0a7178ad910558529fb93224cae831af89a42df11044075fc66678cc801"  # local
token_id_1 = None
token_id_2 = None
token_id_0 = "00000000000000000000000000000000000000000000000000000000000000ff"  # token not yet added to PDE

need_withdraw_contribution_1 = False
need_withdraw_contribution_2 = False

COIN_MASTER.top_him_up_prv_to_amount_if(coin(10000), coin(100000), token_owner)

if token_id_1 is None:
    trx008.account_init = token_owner
    token_id_1 = trx008.test_init_ptoken()
    need_withdraw_contribution_1 = True

if token_id_2 is None:
    trx008.custom_token_symbol = get_current_date_time()
    trx008.account_init = token_owner
    token_id_2 = trx008.test_init_ptoken()
    need_withdraw_contribution_2 = True

acc_list_1_shard = AccountGroup(
    Account(
        "112t8rnYwrzsk7bQgYM6duFMfQsHDvoF3bLLEXQGSXayLzFhH2MDyHRFpYenM9qaPXRFcwVK2b7jFG8WHLgYamaqG8PzAJuC7sqhSw2RzaKx"),
    Account(
        "112t8rneWAhErTC8YUFTnfcKHvB1x6uAVdehy1S8GP2psgqDxK3RHouUcd69fz88oAL9XuMyQ8mBY5FmmGJdcyrpwXjWBXRpoWwgJXjsxi4j"),
    Account(
        "112t8rni5FF2cEVMZmmCzpnr4QuFnUvYymbkjk3LGp5GJs8c8wTMURmJbZGx8WgwkPodtwGr34Vu8KZat7gxZmSXu5h9LDuppnyzcEXSgKff"),
    Account(
        "112t8rnqawFcfb4TCLwvSMgza64EuC4HMPUnwrqG1wn1UFpyyuCBcGPMcuT7vxfFCehzpj3jexavU33qUUJcdSyz321b27JFZFj6smyyQRza"),
    Account(
        "112t8rnr8swHUPwFhhw8THdVtXLZqo1AqnoKrg1YFpTYr7k7xyKS46jiquN32nDFMNG85cEoew8eCpFNxUw4VB8ifQhFnZSvqpcyXS7jg3NP"),
    Account(
        "112t8rnuHvmcktny3u5p8WfgjPo7PEMHrWppz1y9verdCuMEL4D5esMsR5LUJeB5A4oR9u5SeTpkNocE4CE8NedJjbp3xBeZGLn7yMqS1ZQJ"),
    Account(
        "112t8rnxntm4qcc1kNxqQJEpz4DskFKXojYxaGVT3h7c7QjbWpgiVRv2qmLjQMUW8QxUm7HiyxqdQ35fdcAQ7SZ3cYmDADGfFkcENH6Pi8GH"),
    Account(
        "112t8rnzyZWHhboZMZYMmeMGj1nDuVNkXB3FzwpPbhnNbWcSrbytAeYjDdNLfLSJhauvzYLWM2DQkWW2hJ14BGvmFfH1iDFAxgc4ywU6qMqW"),
    Account(
        "112t8ro1aB8Hno84bCGkoPv4fSgdnjghbd5xHg7NmriQGexqy6J7jKL3iDWAEytKwpH6U85MkAaZmEGcV3uBH8kZiUcBHpc1CpskuwyqZNU4"),
    Account(
        "112t8ro3VxLStVFoFiZ2Grose15tyCXCbc9VR2YtHbZCd2GZQPYBMafmXws2DDNd8VKQqKhvw6wW51xyxvrTzLE5prRAjcWJiDWiU4EL3TUT")
)

acc_list_n_shard = AccountGroup(
    Account(
        "112t8rnakdKxvk7VMKUB9qmsPY4czwnP24b82BnepcxHLX6kJ1dYQsR8d6xNTzwC9nEhJdocr9u19NAr4iSYXCeTBRu3YET8iADMAP3szdfw"),
    Account(
        "112t8rnbTkezohA4GLeUDpLFnuDbFvPcoCS1MxctvEu3rmUkvmoWJ37MnXDSscpVy6bKfSwjWigi9L3qhcUFo8yZLLsgPvYAn9fs1E62qNPS"),
    Account(
        "112t8rnjzNW1iKLjpNW9oJoD38pnVVgCiZWRuqGmMvcEgZEHjtg4tLRTAcfTCxNXrdzKcEmY9JVfX2Wb3JLaCjfRDEyGhXGK67VB297mZuwH"),
    Account(
        "112t8rnmcQXPkPG3nHhhmLjKeqZEjBHcFCSxBdwRy2L6nGXBwKopc5PYWPVXu14xmec34LXxu5JJcf3N6wUfsbbNWKVotAMNrswhE6adbBmu"),
    Account(
        "112t8rns2sxbuHFAAhtMksGhK9S1mFcyiGpKypzJuXJSmHZE8d4SqM3XNSy6i9QacqTeVmrneuEmNzF1kcwAvvf6d137PVJun1qnsxKr1gW6"),
    Account(
        "112t8rnuHvmcktny3u5p8WfgjPo7PEMHrWppz1y9verdCuMEL4D5esMsR5LUJeB5A4oR9u5SeTpkNocE4CE8NedJjbp3xBeZGLn7yMqS1ZQJ"),
    Account(
        "112t8rnxntm4qcc1kNxqQJEpz4DskFKXojYxaGVT3h7c7QjbWpgiVRv2qmLjQMUW8QxUm7HiyxqdQ35fdcAQ7SZ3cYmDADGfFkcENH6Pi8GH"),
    Account(
        "112t8rnzyZWHhboZMZYMmeMGj1nDuVNkXB3FzwpPbhnNbWcSrbytAeYjDdNLfLSJhauvzYLWM2DQkWW2hJ14BGvmFfH1iDFAxgc4ywU6qMqW"),
    Account(
        "112t8ro1aB8Hno84bCGkoPv4fSgdnjghbd5xHg7NmriQGexqy6J7jKL3iDWAEytKwpH6U85MkAaZmEGcV3uBH8kZiUcBHpc1CpskuwyqZNU4"),
    Account(
        "112t8ro3VxLStVFoFiZ2Grose15tyCXCbc9VR2YtHbZCd2GZQPYBMafmXws2DDNd8VKQqKhvw6wW51xyxvrTzLE5prRAjcWJiDWiU4EL3TUT")
)


def no_teardown_module():
    if need_withdraw_contribution_1:
        trx008.custom_token_id = token_id_1
        trx008.teardown_module()
    if need_withdraw_contribution_2:
        trx008.custom_token_id = token_id_2
        trx008.teardown_module()


def verify_sum_fee_prv_token(sum_fee_expected, token1, token2, pde_state_b4, pde_state_af):
    sum_fee_pool_b4 = pde_state_b4.sum_contributor_reward_of_pair(None, token1, token2)
    sum_fee_pool_af = pde_state_af.sum_contributor_reward_of_pair(None, token1, token2)
    INFO(f'Verify contributor reward of {l6(token1)}-{l6(token2)}, '
         f'Expected sum reward = {sum_fee_expected}, actual sum reward = {sum_fee_pool_af - sum_fee_pool_b4}')
    assert abs((abs(sum_fee_pool_af - sum_fee_pool_b4) / sum_fee_expected) - 1) < 0.001 \
           and INFO(f'Sum fee tokens {l6(token1)}-{l6(token2)} is correct')


def verify_contributor_reward_prv_token(sum_fee_expected, token1, token2, pde_state_b4, pde_state_af):
    INFO_HEADLINE(f'Verify contributor reward of token pair {l6(token1)}-{l6(token2)}')
    contributors_of_pair = pde_state_b4.get_contributor_of_pair(token1, token2)
    sum_share_of_pair = pde_state_b4.sum_share_pool_of_pair(None, token1, token2)
    sum_split_reward = 0
    final_reward_result = True
    SUMMARY = ''
    for contributor in contributors_of_pair:
        INFO()
        share_of_contributor = pde_state_b4.get_pde_shares_amount(contributor, token1, token2)
        pde_reward_b4 = pde_state_b4.get_contributor_reward_amount(contributor, token1, token2)
        pde_reward_af = pde_state_af.get_contributor_reward_amount(contributor, token1, token2)
        actual_reward = pde_reward_af - pde_reward_b4
        if len(contributors_of_pair) > 1 and contributor == contributors_of_pair[-1]:
            # last contributor get all remaining fee as reward
            calculated_reward = sum_fee_expected - sum_split_reward
        else:
            calculated_reward = int(sum_fee_expected * share_of_contributor / sum_share_of_pair)
        sum_split_reward += calculated_reward

        INFO(f'''Verify PDE reward for contributor {l6(contributor)} with: 
                        reward before               : {pde_reward_b4}
                        reward after                : {pde_reward_af}
                        estimated additional reward : {calculated_reward}
                        share amount                : {share_of_contributor}
                        sum share of pair           : {sum_share_of_pair}
                        sum trading fee             : {sum_fee_expected}''')
        if actual_reward == calculated_reward == 0:
            SUMMARY += f'\tPde reward of {l6(contributor)}:{l6(token1)}-{l6(token2)} IS  correct: ' \
                       f'estimated/actual received {calculated_reward}/{actual_reward}\n'
            final_reward_result = final_reward_result and True
        elif actual_reward != 0 and calculated_reward == 0:
            SUMMARY += f'\tPde reward of {l6(contributor)}:{l6(token1)}-{l6(token2)} NOT correct: ' \
                       f'estimated/actual received {calculated_reward}/{actual_reward} \n'
            final_reward_result = final_reward_result and False
        elif abs(actual_reward / calculated_reward - 1) < 0.001:
            SUMMARY += f'\tPde reward of {l6(contributor)}:{l6(token1)}-{l6(token2)} IS  correct: ' \
                       f'estimated/actual received {calculated_reward}/{actual_reward}\n'
            final_reward_result = final_reward_result and True
        else:
            SUMMARY += f'\tPde reward of {l6(contributor)}:{l6(token1)}-{l6(token2)} NOT correct: ' \
                       f'estimated/actual received {calculated_reward}/{actual_reward} \n'
            final_reward_result = final_reward_result and False

    return final_reward_result, SUMMARY


def verify_trading_prv_token(trade_amount_list, trading_fees_list, trade_order, tx_fees_list, token_sell, token_buy,
                             pde_state_b4, balance_tok_sell_before):
    rate_before = pde_state_b4.get_rate_between_token(token_sell, token_buy)
    calculated_rate = copy.deepcopy(rate_before)
    estimate_amount_received_after_list = [0] * len(trade_order)
    estimate_bal_sell_after_list = [0] * len(trade_order)
    for order in trade_order:
        trade_amount = trade_amount_list[order]
        tx_fee = tx_fees_list[order]
        trading_fee = trading_fees_list[order]
        bal_tok_sell_b4 = balance_tok_sell_before[order]
        print(str(order) + "--")
        received_amount_token_buy = calculate_actual_trade_received(trade_amount, calculated_rate[0],
                                                                    calculated_rate[1])
        calculated_rate[0] += trade_amount
        calculated_rate[1] -= received_amount_token_buy

        # check balance
        estimate_bal_sell_after = bal_tok_sell_b4 - trade_amount
        if token_sell == PRV_ID:
            estimate_bal_sell_after -= (trading_fee + tx_fee)
        if token_buy == PRV_ID:
            received_amount_token_buy -= (trading_fee + tx_fee)

        # assert estimate_bal_buy_after == bal_tok_buy_after and INFO(f'{l6(trader.payment_key)} '
        #                                                             f'balance {l6(token_buy)} is correct')
        # assert estimate_bal_sell_after == bal_tok_sell_after and INFO(f'{l6(trader.payment_key)} '
        #                                                               f'balance {l6(token_sell)} is correct')
        estimate_amount_received_after_list[order] = received_amount_token_buy
        estimate_bal_sell_after_list[order] = estimate_bal_sell_after
    return calculated_rate, estimate_bal_sell_after_list, estimate_amount_received_after_list


def calculate_trade_order(trading_fees_list, amount_list):
    multiplier = 1000000000  # multiply with fee to avoid close to 0 priority, since fee is too small compare to amount
    trade_priority = [(fee * multiplier) / amount for fee, amount in zip(trading_fees_list, amount_list)]
    trade_priority_sorted = copy.deepcopy(trade_priority)
    trade_priority_sorted.sort(reverse=True)
    INFO("Trade Priority: " + str(trade_priority))
    INFO("Trade Priority: " + str(trade_priority_sorted))
    sort_order = sorted(range(len(trade_priority)), key=lambda k: trade_priority[k], reverse=True)
    INFO("Sort order: " + str(sort_order))
    return sort_order

# work around for privacy v2 "invalid token" bug, if not testing privacy v2, just comment these lines
# if ChainConfig.PRIVACY_VERSION == 2:
#     COIN_MASTER.top_him_up_prv_to_amount_if(1000, coin(1), acc_list_n_shard)
#     acc_list_n_shard.get_accounts_in_shard(5)[0]. \
#         pde_trade_prv(10, token_id_1, 1).expect_no_error().subscribe_transaction()
#     acc_list_n_shard.get_accounts_in_shard(5)[0]. \
#         pde_trade_prv(10, token_id_2, 1).expect_no_error().subscribe_transaction()
