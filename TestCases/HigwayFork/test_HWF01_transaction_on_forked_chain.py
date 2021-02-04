from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Constants import ChainConfig, coin
from Helpers.Logging import INFO
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER, Account, AccountGroup
from Objects.IncognitoTestCase import SUT
from TestCases.HigwayFork import acc_list_1_shard, get_beacon_height

receiver_same_shard = acc_list_1_shard[0]
receiver_cross_shard = Account(
    '112t8rnakdKxvk7VMKUB9qmsPY4czwnP24b82BnepcxHLX6kJ1dYQsR8d6xNTzwC9nEhJdocr9u19NAr4iSYXCeTBRu3YET8iADMAP3szdfw')
sender_list = acc_list_1_shard[1:7]
COIN_MASTER.top_him_up_prv_to_amount_if(coin(2), coin(5), sender_list)
amount = 10000


def setup_module():
    global beacon_height, block_fork
    INFO('Get beacon height current')
    beacon_bsd = SUT().get_block_chain_info()
    beacon_height = beacon_bsd.get_beacon_block().get_height()
    INFO(f'Beacon_height: {beacon_height}')
    block_fork = beacon_height + ChainConfig.BLOCK_PER_EPOCH
    block_fork_list = [block_fork, block_fork + 1, block_fork + 2]
    REQ_HANDLER = SUT.highways[0]
    REQ_HANDLER.transaction().create_fork(block_fork_list)


def test_transaction_on_forked_chain():
    global beacon_height
    INFO("Balance before")
    bal_b4_sender_dict = {}
    bal_b4_receiver = {}
    amount_receiver = {}
    fee_dict = {}
    for sender in sender_list:
        bal_b4_sender_dict[sender] = sender.get_prv_balance()
        fee_dict[sender] = []
    for receiver in [receiver_cross_shard, receiver_same_shard]:
        bal_b4_receiver[receiver] = receiver.get_prv_balance()
        amount_receiver[receiver] = 0

    INFO("Create and send transaction")
    thread_pool = []
    while beacon_height < block_fork + 10:
        with ThreadPoolExecutor() as executor:
            thread_height = executor.submit(get_beacon_height)
            for sender in sender_list[0:3]:
                thread_send_prv = executor.submit(sender.send_prv_to, receiver_same_shard, amount, privacy=0)
                thread_pool.append(thread_send_prv)
            for sender in sender_list[3:6]:
                thread_send_prv = executor.submit(sender.send_prv_to, receiver_cross_shard, amount, privacy=0)
                thread_pool.append(thread_send_prv)
        beacon_height = thread_height.result()
        INFO(f'Beacon_height: {beacon_height}')
        WAIT(5)

    for thread in thread_pool:
        try:
            tx = thread.result().get_transaction_by_hash()
            tx_id = tx.get_tx_id()
            INFO(f'TxID: {tx_id}')
            key = tx.get_input_coin_pub_key()
            sender = AccountGroup(*(sender_list)).find_account_by_key(key)
            fee_dict[sender].append(tx.get_fee())
            output_coin = tx.get_prv_proof_detail().get_output_coins()
            for coin in output_coin:
                if coin.get_value() == amount:
                    public_key = coin.get_public_key()
                    receiver = AccountGroup(*(receiver_same_shard, receiver_cross_shard)).find_account_by_key(
                        public_key)
                    amount_receiver[receiver] += amount
                    break
        except:
            params = thread.result().params()
            INFO(params)

    INFO('Verify balance')
    for sender in sender_list:
        assert sender.get_prv_balance() == bal_b4_sender_dict[sender] - sum(fee_dict[sender]) - amount * len(
            fee_dict[sender])
    for receiver in [receiver_cross_shard, receiver_same_shard]:
        assert receiver.get_prv_balance() == bal_b4_receiver[receiver] + amount_receiver[receiver]
