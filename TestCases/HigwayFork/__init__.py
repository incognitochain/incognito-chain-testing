import copy

from Configs.Constants import coin
from Helpers.Logging import INFO, ERROR
from Helpers.TestHelper import ChainHelper, calculate_actual_trade_received
from Helpers.Time import get_current_date_time
from Objects.AccountObject import AccountGroup, Account, COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.Transactions import test_TRX008_init_contribute_send_custom_token as trx008

token_id_1 = "f8ac91fe56193f71cb4c86315750dbc0c0f3afcfa798a5455ec90bc783ca3e59"  # local 162
token_id_2 = "08803efd77bfaad73b13af202d2b5d68315a20e5405f1621aab954407944a451"  # local 162
# token_id_1 = '24a70af11054fe97bdde7f4d56e3a2b1aa6d8df459de370b61c782033d1b029f'  # TestNet2
# token_id_2 = '6836077e15731d4bffa9753a58cbebe8f5583a7288660fe1543667ad579e78b7'  # TestNet2
# token_id_1 = None
# token_id_2 = None

token_owner = Account(
    '112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA')
COIN_MASTER.top_him_up_prv_to_amount_if(coin(10000), coin(100000), token_owner)

if token_id_1 is None:
    trx008.account_init = token_owner
    token_id_1 = trx008.test_init_ptoken()

if token_id_2 is None:
    trx008.custom_token_symbol = get_current_date_time()
    trx008.account_init = token_owner
    token_id_2 = trx008.test_init_ptoken()

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


def get_block_height(chain_id):
    chain_info = SUT().get_block_chain_info()
    if chain_id != 255:
        height = chain_info.get_shard_block(chain_id).get_height()
    else:
        height = chain_info.get_beacon_block().get_height()
    return height


def create_fork(cID, num_of_branch, branch_tobe_continue=2, num_of_block_list=5):
    chain_info = SUT().get_block_chain_info()
    height_current = chain_info.get_beacon_block().get_height()
    epoch = chain_info.get_beacon_block().get_epoch()
    height_transfer_next_epoch = ChainHelper.cal_first_height_of_epoch(epoch + 1)
    block_fork_list = []
    for i in range(-int(num_of_block_list / 2), num_of_block_list - int(num_of_block_list / 2)):
        block_fork_list.append(height_transfer_next_epoch + i)
    num = block_fork_list[0] - height_current
    assert num >= 5 and INFO(f'Chain will be forked after {num} blocks'), \
        ERROR(
            f'Epoch {epoch + 1} is coming, remain {height_transfer_next_epoch - height_current} block, rerun testscript')
    if cID != 255:  # is not beacon
        height_current = chain_info.get_shard_block(cID).get_height()
        block_fork_list = [height_current + num]
        for i in range(1, num_of_block_list):
            block_fork_list.append(height_current + num + i)
    INFO(
        f'Create fork on chain_id{cID} at block_list {block_fork_list}, fork {num_of_branch} branchs, branch {branch_tobe_continue} tobe continue')
    REQ_HANDLER = SUT.highways[0]
    # REQ_HANDLER.create_fork(block_fork_list, cID, num_of_branch, branch_tobe_continue)
    return height_current, block_fork_list


def verify_trading_prv_token(trade_amount_list, trade_order, rate_before):
    calculated_rate = copy.deepcopy(rate_before)
    estimate_amount_received_after_list = [0] * len(trade_order)
    for order in trade_order:
        trade_amount = trade_amount_list[order]
        print(str(order) + "--")
        received_amount_token_buy = calculate_actual_trade_received(trade_amount, calculated_rate[0],
                                                                    calculated_rate[1])
        calculated_rate[0] += trade_amount
        calculated_rate[1] -= received_amount_token_buy

        estimate_amount_received_after_list[order] = received_amount_token_buy
    return calculated_rate, estimate_amount_received_after_list
