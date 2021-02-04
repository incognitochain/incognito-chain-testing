import concurrent
import random
from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Constants import ChainConfig, coin
from Helpers.Logging import INFO, ERROR
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import ACCOUNTS, SUT

sender_shard0 = ACCOUNTS.get_accounts_in_shard(0)[0]
sender_shard1 = ACCOUNTS.get_accounts_in_shard(1)[0]
receiver_shard0 = ACCOUNTS.get_accounts_in_shard(0)[1]
receiver_shard1 = ACCOUNTS.get_accounts_in_shard(1)[1]


def _setup_module():
    INFO('Get beacon height current')
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    beacon_height = beacon_bsd.get_beacon_height()
    block_fork = beacon_height + ChainConfig.BLOCK_PER_EPOCH
    block_fork_list = [block_fork, block_fork + 1, block_fork + 2]
    SUT.highways[0].transaction().create_fork(block_fork_list)


def verify_trx_create_and_send_prv(sender, receiver, amount):
    bal_b4_sender = sender.get_prv_balance()
    bal_b4_receiver = receiver.get_prv_balance()
    response = sender.send_prv_to(receiver, amount).subscribe_transaction()
    fee = response.get_fee()
    bal_af_sender = sender.wait_for_balance_change(from_balance=bal_b4_sender, least_change_amount=-1)
    bal_af_receiver = receiver.wait_for_balance_change(from_balance=bal_b4_receiver)
    assert bal_af_sender == bal_b4_sender - fee - amount and INFO('Pass'), ERROR("WRONG: Sender's balance incorrect")
    assert bal_af_receiver == bal_b4_receiver + amount and INFO('Pass'), ERROR("WRONG: Receiver's balance incorrect")


def test_transaction_on_forked_chain():
    i = 0
    while i < 1000:
        INFO('Top-up PRV for sender')
        COIN_MASTER.top_him_up_prv_to_amount_if(coin(5), coin(10), [sender_shard0, sender_shard1])

        beacon_bsd = SUT().get_beacon_best_state_detail_info()
        beacon_height = beacon_bsd.get_beacon_height()
        INFO(f'Verify create & send PRV at beacon height {beacon_height}')
        amount = random.randrange(100000, 1000000)
        INFO('Verify transaction cross shard')
        thread_pool = []

        executor1 = ThreadPoolExecutor()
        thread1 = executor1.submit(verify_trx_create_and_send_prv, sender_shard0, receiver_shard1, amount)
        thread_pool.append(thread1)

        executor2 = ThreadPoolExecutor()
        thread2 = executor2.submit(verify_trx_create_and_send_prv, sender_shard1, receiver_shard0, amount)
        thread_pool.append(thread2)

        concurrent.futures.wait(thread_pool)
        INFO('Verify transaction same shard')
        thread_pool = []

        executor1 = ThreadPoolExecutor()
        thread1 = executor1.submit(verify_trx_create_and_send_prv, sender_shard0, receiver_shard0, amount)
        thread_pool.append(thread1)

        executor2 = ThreadPoolExecutor()
        thread2 = executor2.submit(verify_trx_create_and_send_prv, sender_shard1, receiver_shard1, amount)
        thread_pool.append(thread2)

        concurrent.futures.wait(thread_pool)
        i += 1
        INFO('========================================================')
