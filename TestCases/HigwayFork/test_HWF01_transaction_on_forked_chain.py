import pytest
from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Constants import coin
from Helpers.Logging import INFO, STEP, ERROR, DEBUG
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER, Account, AccountGroup
from Objects.IncognitoTestCase import SUT
from TestCases.HigwayFork import acc_list_1_shard, get_block_height, create_fork

receiver_same_shard = acc_list_1_shard[0]
receiver_cross_shard = Account(
    '112t8rnakdKxvk7VMKUB9qmsPY4czwnP24b82BnepcxHLX6kJ1dYQsR8d6xNTzwC9nEhJdocr9u19NAr4iSYXCeTBRu3YET8iADMAP3szdfw')
sender_list = acc_list_1_shard[1:7]
COIN_MASTER.top_him_up_prv_to_amount_if(coin(2), coin(5), sender_list)
amount = 10000


@pytest.mark.parametrize('cID1, num_of_branch1, cID2, num_of_branch2', [
    (0, 2, None, None),
    (255, 2, None, None),
    (1, 2, 255, 2),
    (1, 2, 0, 2),
])
def test_transaction_on_forked_chain(cID1, num_of_branch1, cID2, num_of_branch2):
    STEP(0, "Balance before")
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

    STEP(1, f'Create fork on chain_id {cID1} & chain_id {cID2}')
    with ThreadPoolExecutor() as executor:
        if cID1 is not None:
            thread = executor.submit(create_fork, cID1, num_of_branch1)
        if cID2 is not None:
            executor.submit(create_fork, cID2, num_of_branch2)
    height_current, block_fork_list = thread.result()

    STEP(2, "Create and send transaction")
    thread_pool = []
    thread_pool_view = []
    while height_current < block_fork_list[-1] + 3:
        with ThreadPoolExecutor() as executor:
            thread_height = executor.submit(get_block_height, cID1)
            for cID in [cID1, cID2]:
                if cID == 255:
                    thread_view_detail = executor.submit(SUT.beacons.get_node().system_rpc().get_all_view_detail, -1)
                elif cID is not None:
                    thread_view_detail = executor.submit(SUT.beacons.get_node().system_rpc().get_all_view_detail, cID)
            thread_pool_view.append(thread_view_detail)
            for sender in sender_list[0:3]:
                thread_send_prv = executor.submit(sender.send_prv_to, receiver_same_shard, amount, privacy=0)
                thread_pool.append(thread_send_prv)
            for sender in sender_list[3:6]:
                thread_send_prv = executor.submit(sender.send_prv_to, receiver_cross_shard, amount, privacy=0)
                thread_pool.append(thread_send_prv)
        height_current = thread_height.result()
        INFO(f'Beacon_height: {height_current}')
        WAIT(10)
    WAIT(30)  # wait balance change
    for thread in thread_pool_view:
        result = thread.result()
        INFO(result.get_result())
    for thread in thread_pool:
        result = thread.result()
        try:
            tx = result.subscribe_transaction()
            height = tx.get_block_height()
            shard = tx.get_shard_id()
            INFO(f'Shard {shard}-height {height}')
            key = tx.get_input_coin_pub_key()
            sender = AccountGroup(*sender_list).find_account_by_key(key)
            fee_dict[sender].append(tx.get_fee())
            output_coin = tx.get_prv_proof_detail().get_output_coins()
            for coin in output_coin:
                if coin.get_value() == amount:
                    public_key = coin.get_public_key()
                    receiver = AccountGroup(*(receiver_same_shard, receiver_cross_shard)).find_account_by_key(
                        public_key)
                    amount_receiver[receiver] += amount
                    break
        except AssertionError:
            ERROR(result.get_error_msg())
            DEBUG(result)

    INFO('Verify balance')
    for sender in sender_list:
        assert sender.get_prv_balance() == bal_b4_sender_dict[sender] - sum(fee_dict[sender]) - amount * len(
            fee_dict[sender])
    for receiver in [receiver_cross_shard, receiver_same_shard]:
        assert receiver.get_prv_balance() == bal_b4_receiver[receiver] + amount_receiver[receiver]
