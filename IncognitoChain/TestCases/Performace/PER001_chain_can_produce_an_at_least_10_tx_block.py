from threading import Thread

from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Objects.AccountObject import Account
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Performace import account_list


def test_max_tx_in_same_block():

    def sending_prv(sender: Account, receiver: Account):
        tx = sender.send_prv_to(receiver, 100, shard_id=shard)
        transaction_list.append(tx)

    STEP(1, "Prepare bunch of addresses that has PRV - same shard")

    accounts_send = account_list[0:len(account_list) - 1]
    accounts_receive = accounts_send.copy()
    accounts_receive.reverse()

    shard = accounts_send[0].shard

    STEP(2, 'Send 100 nano PRV to each others at the same time')
    thread_list = list()
    transaction_list = list()

    for index in range(0, len(accounts_send)):
        thread = Thread(target=sending_prv, args=(accounts_send[index], accounts_receive[index],))
        thread.start()
        thread_list.append(thread)

    # wait for all sending thread to complete
    for thread in thread_list:
        thread.join()

    # subscribe the last transaction to make sure all transactions are handled
    transaction_list[len(transaction_list) - 1].subscribe_transaction()

    STEP(3, 'Get transaction by hash of each tx_id => check that them all in same block-height (or block-height + 1)')
    block_height = transaction_list[0].get_transaction_by_hash().get_block_height()
    INFO(f'Expect all transactions must has same block height as {block_height} or {block_height + 1}')
    for index in range(0, len(transaction_list)):
        transaction = transaction_list[index]
        tx_block_height = transaction.get_transaction_by_hash().get_block_height()
        assert (block_height == tx_block_height or block_height + 1 == tx_block_height) \
               and INFO(f'{index}: tx = {transaction.get_tx_id()}, block height = {tx_block_height}')

    STEP(4, 'Verify that block contains at least 10 tx')
    tx_in_block_count = 0
    tx_hashes = SUT.full_node.system_rpc().retrieve_block_by_height(block_height, shard).get_tx_hashes()
    for transaction in transaction_list:
        if transaction.get_tx_id() in tx_hashes:
            tx_in_block_count += 1
    assert tx_in_block_count >= 10 and INFO(f'Total tx in block {block_height} = {tx_in_block_count}')
