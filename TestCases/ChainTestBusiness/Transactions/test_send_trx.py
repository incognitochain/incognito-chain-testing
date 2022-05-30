import concurrent
import random
from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Configs import ChainConfig
from Helpers.Logging import INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import ACCOUNTS, SUT


def test_send_trx():
    INFO()

    def create_send(sender, receiver):
        bal_sender_b4 = sender.get_balance()
        amount = random.randrange(9900, 10000000)
        tx = sender.send_prv_to(receiver, amount, fee=500, privacy=2)
        if tx.get_result() is None:
            print(f'{tx.get_error_msg()} - {tx.get_error_trace()}')
            tx_id = None
        else:
            tx_id = tx.get_tx_id()
        return bal_sender_b4, amount, tx_id

    while True:
        for receiver in ACCOUNTS:
            bal_recv_b4 = receiver.get_balance()
            senders = ACCOUNTS.clone()
            senders.remove(receiver)
            bal_senders_b4 = [0] * len(senders)
            amounts = [0] * len(senders)
            tx_id_pool = [0] * len(senders)
            thread_pool = []
            with ThreadPoolExecutor() as e:
                for sender in senders:
                    thread = e.submit(create_send, sender, receiver)
                    thread_pool.append(thread)
            for i in range(len(thread_pool)):
                bal_senders_b4[i], amounts[i], tx_id_pool[i] = thread_pool[i].result()
            sum_amount = sum(amounts)
            block_wait = 50
            result_sender = False
            result_receiver = False
            while block_wait > 0:
                WAIT(ChainConfig.BLOCK_TIME * 5)
                block_wait -= 6
                if not result_sender:
                    for i in range(len(senders)):
                        fee = SUT().transaction().get_tx_by_hash(tx_id_pool[i]).get_fee()
                        try:
                            assert senders[i].get_balance() == bal_senders_b4[i] - amounts[i] - fee
                            result_sender = result_sender or True
                        except:
                            INFO(tx_id_pool[i])
                            result_sender = result_sender and False
                        INFO(result_sender)
                if not result_receiver:
                    bal = receiver.get_balance()
                    try:
                        assert bal == bal_recv_b4 + sum_amount
                        result_receiver = result_receiver or True
                    except:
                        result_receiver = result_receiver and False
                        INFO(f'{bal} != {bal_recv_b4 + sum_amount}')
                if result_sender and result_receiver:
                    break
            assert result_sender and result_receiver


def test_defragment():
    INFO()
    while True:
        thread_pool = []
        executor = ThreadPoolExecutor()
        for acc in ACCOUNTS:
            thread = executor.submit(acc.count_unspent_output_coins)
            thread_pool.append(thread)
        concurrent.futures.wait(thread_pool)
        ll = 0
        for thread in thread_pool:
            n = thread.result()
            acc = ACCOUNTS[ll]
            if n < 2:
                ACCOUNTS.remove(acc)
                continue
            INFO(f'Unspent coin: {n}')
            executor.submit(acc.defragment_account)
            ll += 1
        WAIT(60)
        executor.shutdown()
