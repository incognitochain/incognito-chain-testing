import copy

from Configs.Constants import coin
from Helpers.BlockChainMath import PdeMath
from Helpers.Logging import INFO, ERROR
from Helpers.TestHelper import ChainHelper
from Helpers.Time import get_current_date_time
from Objects.AccountObject import AccountGroup, Account, COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.Transactions import test_TRX008_init_contribute_send_custom_token as trx008

token_id_1 = "f8ac91fe56193f71cb4c86315750dbc0c0f3afcfa798a5455ec90bc783ca3e59"  # local 162
token_id_2 = "08803efd77bfaad73b13af202d2b5d68315a20e5405f1621aab954407944a451"  # local 162
# token_id_1 = '24a70af11054fe97bdde7f4d56e3a2b1aa6d8df459de370b61c782033d1b029f'  # TestNet2
# token_id_2 = '6836077e15731d4bffa9753a58cbebe8f5583a7288660fe1543667ad579e78b7'  # TestNet2

token_owner = Account(
    '112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA')
COIN_MASTER.top_up_if_lower_than(token_owner, coin(10000), coin(100000))

all_ptoken_in_chain = SUT().get_all_token_in_chain_list().get_tokens_info()
if token_id_1 not in all_ptoken_in_chain:
    trx008.account_init = token_owner
    token_id_1 = trx008.test_init_ptoken()
if token_id_2 not in all_ptoken_in_chain:
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
    if chain_id == 255 or chain_id == -1:
        height = SUT.beacons.get_node().get_beacon_best_state_info().get_beacon_height()
    elif chain_id is not None:
        height = SUT.shards[chain_id].get_node().get_shard_best_state_info(chain_id).get_shard_height()
    return height


def calculated_and_create_fork(chain_id, at_transfer_next_epoch=False, min_blocks_wait_fork=3, num_of_branch=2,
                               branch_tobe_continue=2, num_of_block_fork=5):
    """

    @param chain_id:
    @param at_transfer_next_epoch: True if create fork right at the time of epoch transfer, else False
    @param min_blocks_wait_fork: Chain will be forked after at least {num_of_block_wait} blocks
    @param num_of_branch:
    @param branch_tobe_continue:
    @param num_of_block_fork:
    @return:
    """
    chain_info = SUT().get_block_chain_info()
    beacon_height = chain_info.get_beacon_block().get_height()
    epoch_current = chain_info.get_epoch_number()
    block_per_epoch = chain_info.get_block_per_epoch_number()
    remain_block_epoch = chain_info.get_num_of_remain_block_of_epoch()
    block_fork_list = [0] * num_of_block_fork
    if chain_id != 255 and chain_id != -1:
        height_current = chain_info.get_shard_block(chain_id).get_height()
    else:
        height_current = beacon_height
    difference_height = beacon_height - height_current
    INFO(f'Beacon height current {beacon_height}')
    if at_transfer_next_epoch is True:
        INFO('Create fork right at the time of epoch transfer')
        if remain_block_epoch <= min_blocks_wait_fork:
            if block_per_epoch - (min_blocks_wait_fork - remain_block_epoch) >= num_of_block_fork:
                for i in range(num_of_block_fork):
                    block_fork_list[i] = ChainHelper.cal_first_height_of_epoch(epoch_current + 2) - int(
                        num_of_block_fork / 2) + i - difference_height
            else:
                for i in range(num_of_block_fork):
                    block_fork_list[i] = height_current + min_blocks_wait_fork + i
        else:
            if remain_block_epoch - min_blocks_wait_fork >= num_of_block_fork:
                for i in range(num_of_block_fork):
                    block_fork_list[i] = ChainHelper.cal_first_height_of_epoch(epoch_current + 1) - int(
                        num_of_block_fork / 2) + i - difference_height
            else:
                for i in range(num_of_block_fork):
                    block_fork_list[i] = height_current + min_blocks_wait_fork + i
    elif at_transfer_next_epoch is False:
        INFO('Create fork not at the time of epoch transfer')
        assert num_of_block_fork < block_per_epoch, ERROR(
            'The number of blocks fork is greater than the number of blocks per epoch')
        if remain_block_epoch <= min_blocks_wait_fork:
            if block_per_epoch - (min_blocks_wait_fork - remain_block_epoch) >= num_of_block_fork:
                for i in range(num_of_block_fork):
                    block_fork_list[i] = height_current + min_blocks_wait_fork + i
            else:
                for i in range(num_of_block_fork):
                    block_fork_list[i] = ChainHelper.cal_first_height_of_epoch(epoch_current + 2) \
                                         + 1 + i - difference_height
        else:
            if remain_block_epoch - min_blocks_wait_fork >= num_of_block_fork:
                for i in range(num_of_block_fork):
                    block_fork_list[i] = height_current + min_blocks_wait_fork + i
            else:
                for i in range(num_of_block_fork):
                    block_fork_list[i] = ChainHelper.cal_first_height_of_epoch(epoch_current + 1) \
                                         + 1 + i - difference_height
    elif at_transfer_next_epoch == 'random':
        INFO('Create fork at random time')
        random_block = int(ChainHelper.cal_random_height_of_epoch(epoch_current))
        if beacon_height + min_blocks_wait_fork < random_block:
            if (random_block - (beacon_height + min_blocks_wait_fork)) >= num_of_block_fork:
                for i in range(num_of_block_fork):
                    block_fork_list[i] = random_block - int(num_of_block_fork / 2) + i - difference_height
            else:
                for i in range(num_of_block_fork):
                    block_fork_list[i] = height_current + min_blocks_wait_fork + i
        else:
            random_block_next_epoch = int(ChainHelper.cal_random_height_of_epoch(epoch_current + 1))
            if (random_block_next_epoch - (beacon_height + min_blocks_wait_fork)) >= num_of_block_fork:
                for i in range(num_of_block_fork):
                    block_fork_list[i] = random_block_next_epoch - int(num_of_block_fork / 2) + i - difference_height
            else:
                assert random_block_next_epoch - (beacon_height + min_blocks_wait_fork) > 0, ERROR(
                    'The number of blocks to wait is too large')
                for i in range(num_of_block_fork):
                    block_fork_list[i] = height_current + min_blocks_wait_fork + i
    else:
        for i in range(num_of_block_fork):
            block_fork_list[i] = height_current + min_blocks_wait_fork + i
    real_blocks_wait = block_fork_list[0] - height_current
    INFO(
        f'Create fork on chain_id_{chain_id} at block_list {block_fork_list}, fork {num_of_branch} branchs, branch {branch_tobe_continue} tobe continue')
    INFO(f'Height_current {height_current}, chain will be forked after {real_blocks_wait} blocks')
    REQ_HANDLER = SUT.highways[0]
    REQ_HANDLER.create_fork(block_fork_list, chain_id, num_of_branch, branch_tobe_continue)
    return height_current, block_fork_list, real_blocks_wait


def verify_trading_prv_token(trade_amount_list, trade_order, rate_before):
    calculated_rate = copy.deepcopy(rate_before)
    estimate_amount_received_after_list = [0] * len(trade_order)
    for order in trade_order:
        trade_amount = trade_amount_list[order]
        print(str(order) + "--")
        received_amount_token_buy = PdeMath.cal_trade_receive(trade_amount, calculated_rate[0],
                                                              calculated_rate[1])
        calculated_rate[0] += trade_amount
        calculated_rate[1] -= received_amount_token_buy

        estimate_amount_received_after_list[order] = received_amount_token_buy
    return calculated_rate, estimate_amount_received_after_list
