import copy

from Configs.Constants import coin, PRV_ID
from Helpers.BlockChainMath import PdeMath
from Helpers.Logging import config_logger
from Helpers.TestHelper import l6
from Helpers.Time import get_current_date_time
from Objects.AccountObject import Account, COIN_MASTER, AccountGroup
from Objects.IncognitoTestCase import SUT

logger = config_logger(__name__)

token_owner = Account(
    '112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA')

# when token_id_* is not existed in chain, new token will be inited
# otherwise, use specified token id for the test without initializing new token
token_id_1 = "ef80ac984c6367c9c45f8e3b89011d00e76a6f17bd782e939f649fcf95a05b74_"  # testnet
token_id_2 = "d221245f42a29c405b0b1d60cd2932befc4e10c14116de8690cf65e9c577e216_"  # testnet
# token_id_1 = "730a20b67112f5290cc2dfe60b06c7003f63dcd9e8ad255f7cccd2126e41fabc"  # local v1
# token_id_2 = "f89631735938d5fb762017538279cb78f2831b1aa668e87b3c69d33403a9f785"  # local v1
token_id_0 = "00000000000000000000000000000000000000000000000000000000000000ff"  # token not yet added to PDE

need_withdraw_contribution_1 = False
need_withdraw_contribution_2 = False

token_owner.submit_key()
COIN_MASTER.top_up_if_lower_than(token_owner, coin(10000), coin(100000))

all_ptoken_in_chain = SUT().get_all_token_in_chain_list()
if token_id_1 not in all_ptoken_in_chain:
    # res = token_owner.init_custom_token(coin(2000000))
    res = token_owner.init_custom_token_new_flow(coin(2000000))
    res.subscribe_transaction()
    token_id_1 = res.get_token_id()
    token_owner.wait_for_balance_change(token_id_1, 0)
    logger.info(f" +++ token 1 = {token_id_1}")

if token_id_2 not in all_ptoken_in_chain:
    tok2_symbol = get_current_date_time()
    # res = token_owner.init_custom_token(coin(2000000))
    res = token_owner.init_custom_token_new_flow(coin(2000000))
    res.subscribe_transaction()
    token_id_2 = res.get_token_id()
    token_owner.wait_for_balance_change(token_id_2, 0)
    logger.info(f" +++ token 2 = {token_id_2}")

acc_list_1_shard = AccountGroup(
    Account(
        "112t8rnYp3xTkGXxiQXqCxDs4fq7LWpqSn9P3jbJEbMN25Pv5QvRKR6r9jxnwQciCVaE2RJ1vvvEMDPhbFBQcU1UKAKfDRc9m26xTuGdVxhD"),
    Account(
        "112t8rnbXrXZwnpafVHG8Trs45jF7HpneCQEaZfQYRSW65sdGonznVXqvfVxBN9r7qaYtL9aT4EUVynUmokFqiuvfC68J7cyTLb6s8jjT5AL"),
    Account(
        "112t8rncnPNEwcjcfrCoucCBQ37q3dmRADTHu4FLYA2uxRhgwfuK7DxzoiE6hyC99HqBzPBy46cm7MpXzrNYpMFS77x18NLiPe8Tz4cMf2Wi"),
    Account(
        "112t8rngdoWp9rKMM9iqqxr2Gr8qqpxoxEypePnpKhWGUSEQMwy78PorrdwDeA1uQAh75HB2m2XDPeHqTGGmFMxEWUvVXJYmBaxNf3bH1LuR"),
    Account(
        "112t8rnitkUvjWKeifhh94k8ijgUvSppJRzbASy7sbTUExKeeKYJSibEe4UzdGkcF5LwxW4PDbhiCpryMyBSU1B7LTdKsqo4sdoa3n8hJswQ"),
    Account(
        "112t8rnpwNLgHh2CLzdsnvVBXToEg3Pw2twQHopHpRbMGfF3xTXQUQv4SwFzFrpA4HAxiCi3dZoiEd5bb8uMCMtuby6dKpk3K8LvaLcHSqWF"),
    Account(
        "112t8rnqUDE49ekHGJBXStwHTV1AEL5thAQB3iVUVgbr5WebRrARzrzpEq4VpvpX6tFx8meECzxwRyGTukkNTFmQPKDy9a4HUzGMnpDakGvU"),
    Account(
        "112t8rnrNQHk91yNKwovrufg5KX2vZR2itfhtcrKpw1aHzdE7C5Z3Aepv9yMar8vaWWafnTUPP9xYb2u7R5MUD6P5FdRwQAm1E1BrbVA16Fw"),
    Account(
        "112t8rnsAaLxFXR6MLK8bG5Qvk2KMVqUprtE4rKfXsTDbhR4xZ52tYKpRhyamWrZbqGQ2FN9diD4TJCifUo4Kc9gHWzKVrqCSSdD3KHHk3T9"),
    Account(
        "112t8rnsqPitoxfdH9uWKNbP21HfzyN4eSAEPhc8EkdZEZdpTdS1jSsGhrcrPNQqFZ42aEND6a4KYeroHeSBeZQGYwaJ5gQHr5z4J684SWZp"),

)

acc_list_n_shard = AccountGroup(
    Account(
        "112t8rnX6KWVgJzJcv3wLzYR9QkxZCTBpXJLvGR3mttXHXS6DKwEmEBzDgG9jqxVZipKqHx9R7LSeKoY7xuePKpRBeqqcMzywAPS98HAVgcK"),
    Account(
        "112t8rncfybnr9aqaTyRYJW5VPfWKnYJHyFs9e6adDxrV7WSnMdVWWJgWWd6uqFMZTi6icoK99F6ws12NJrDvXcZT8hkVx4kLMDRaxFrT1Rz"),
    Account(
        "112t8rnZ5oiBWewuENMce4uHsPkLWz2F1HfuZUqf3WjohoooyBWZbS8pyA7w7YE3EuSVKjeA2pjbmazCgTpwCnYoHwgkG5E1ikcYLz49TYwT"),
    Account(
        "112t8rnYGEABmEo9yKgxLLnGcwmuRGzNXeXR3JHvKrV3duA2sRiRvHJyqg3NJfnvaJfqNnVMi778yCxLXctZ9A7CJBfV2JKWmByrWs9vmqcP"),
    Account(
        "112t8rnaw92Ca9SUL1gjoXFRW4LyvXqFzMqMFuRXzjL3sZSafJzqrXtbe9cgoqWWqUGGefZc8T9kteh6fghB28ZtvmWY7cxXDyT6VPJYxHYF"),
    Account(
        "112t8rnXNjzVfNr6HnKCmbVBgp25AsSUDkksDg6Uh22tgbPxj1QdXKZjTbc1DGjP8V9MoHZrphENLmgDNqFoR74aJGoi9oTLnoEtVUuLbMBD"),
    Account(
        "112t8rnXpyY8xWhpidmwZJnywQg81vb3Rrrre6LmH5Jt8k85SMybReAxskuHf6haMD27BmeuPZtF7EiMqVwx51vg3DoVutpxaDkhAZSBLmXe"),
    Account(
        "112t8rnZcU3WjtDoUiFSTjfN9ECbVRE89fC4h9Xo53qL2S2VCnM8cSQ98Kev2cYcGkAFWJpgdrgRRdyPeDpTQKqNaJLbwkA5mvrwBZKz45d7"),
    Account(
        "112t8rnYh6XbXnhjHKhWkjx5QrHCUaTwKNDnB4r6Ffv24ypVN7wZDU868vdXCiB1zLapuZfNax3au4zJP6RGTH2tkDpNGRiJELD1gdTkyiuW"),
    Account(
        "112t8rnby11gxmuz9M9YA5EQ7VEcFFC1g2PJkXTTLc6qvF4dQRdfJZtPfjwPi3FQghH7e5oXdXzWptDZXz6EKiXcty2PsFBm1rELqnzwNJwe"),
)

for acc in acc_list_1_shard + acc_list_n_shard:
    acc.submit_key()


def verify_sum_fee_prv_token(sum_fee_expected, token1, token2, pde_state_b4, pde_state_af):
    sum_fee_pool_b4 = pde_state_b4.sum_contributor_reward_of_pair(None, token1, token2)
    sum_fee_pool_af = pde_state_af.sum_contributor_reward_of_pair(None, token1, token2)
    logger.info(f'Verify contributor reward of {l6(token1)}-{l6(token2)}, '
         f'Expected sum reward = {sum_fee_expected}, actual sum reward = {sum_fee_pool_af - sum_fee_pool_b4}')
    assert abs((abs(sum_fee_pool_af - sum_fee_pool_b4) / sum_fee_expected) - 1) < 0.001 \
           and logger.info(f'Sum fee tokens {l6(token1)}-{l6(token2)} is correct')


def verify_contributor_reward_prv_token(sum_fee_expected, token1, token2, pde_state_b4, pde_state_af):
    logger.info(f' !!!!!!! Verify contributor reward of token pair {l6(token1)}-{l6(token2)}')
    contributors_of_pair = pde_state_b4.get_contributor_of_pair(token1, token2)
    sum_share_of_pair = pde_state_b4.sum_share_pool_of_pair(None, token1, token2)
    sum_split_reward = 0
    final_reward_result = True
    SUMMARY = ''
    for contributor in contributors_of_pair:
        logger.info()
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

        logger.info(f'''Verify PDE reward for contributor {l6(contributor)} with: 
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
        received_amount_token_buy = PdeMath.cal_trade_receive(trade_amount, calculated_rate[0],
                                                              calculated_rate[1])
        calculated_rate[0] += trade_amount
        calculated_rate[1] -= received_amount_token_buy

        # check balance
        estimate_bal_sell_after = bal_tok_sell_b4 - trade_amount
        if token_sell == PRV_ID:
            estimate_bal_sell_after -= (trading_fee + tx_fee)
        if token_buy == PRV_ID:
            received_amount_token_buy -= (trading_fee + tx_fee)

        # assert estimate_bal_buy_after == bal_tok_buy_after and logger.info(f'{l6(trader.payment_key)} '
        #                                                             f'balance {l6(token_buy)} is correct')
        # assert estimate_bal_sell_after == bal_tok_sell_after and logger.info(f'{l6(trader.payment_key)} '
        #                                                               f'balance {l6(token_sell)} is correct')
        estimate_amount_received_after_list[order] = received_amount_token_buy
        estimate_bal_sell_after_list[order] = estimate_bal_sell_after
    return calculated_rate, estimate_bal_sell_after_list, estimate_amount_received_after_list


def calculate_trade_order(trading_fees_list, amount_list):
    multiplier = 1000000000  # multiply with fee to avoid close to 0 priority, since fee is too small compare to amount
    trade_priority = [(fee * multiplier) / amount for fee, amount in zip(trading_fees_list, amount_list)]
    trade_priority_sorted = copy.deepcopy(trade_priority)
    trade_priority_sorted.sort(reverse=True)
    logger.info("Trade Priority: " + str(trade_priority))
    logger.info("Trade Priority: " + str(trade_priority_sorted))
    sort_order = sorted(range(len(trade_priority)), key=lambda k: trade_priority[k], reverse=True)
    logger.info("Sort order: " + str(sort_order))
    return sort_order

# work around for privacy v2 "invalid token" bug, if not testing privacy v2, just comment these lines
# if ChainConfig.PRIVACY_VERSION == 2:
#     COIN_MASTER.top_up_if_lower_than(acc_list_n_shard, 1000, coin(1))
#     acc_list_n_shard.get_accounts_in_shard(5)[0]. \
#         pde_trade_prv(10, token_id_1, 1).expect_no_error().subscribe_transaction()
#     acc_list_n_shard.get_accounts_in_shard(5)[0]. \
#         pde_trade_prv(10, token_id_2, 1).expect_no_error().subscribe_transaction()

# for acc in ACCOUNTS + acc_list_n_shard + acc_list_1_shard:
#     try:
#         acc.convert_token_to_v2().subscribe_transaction()
#     except:
#         pass

# WAIT(60)
#     acc.convert_token_to_v2(token_id_1, 10)
#     acc.convert_token_to_v2(token_id_2, 10)
