import json
import os
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Queue, Empty

from Configs.Constants import coin
from Helpers.Logging import INFO, INFO_HEADLINE, ERROR
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import ACCOUNTS
from Objects.NodeObject import Node

FULL_NODE_SEND = Node(url="http://51.79.76.38:8334")  # full node to send proof
FULL_NODE_LIST = [  # list of full node to create proof
    Node(url="http://51.79.76.38:8334"),
    Node(url="http://51.79.76.38:8334"),
    Node(url="http://51.79.76.38:8334"),
    Node(url="http://51.79.76.38:8334"),
    Node(url="http://51.79.76.38:8334"),
]
SEND_AMOUNT = 1
LOOP = 10
NUM_OF_SENDER = 100  # num of tx = LOOP * NUM_OF_SENDER
SHARD = 2

create_thread = []
send___thread = []
executor_create = ThreadPoolExecutor()
executor___send = ThreadPoolExecutor()
PROOF_QUEUE = Queue()


def lock_then_create(acc, node):
    try:
        is_lock = acc.cache['lock']
    except KeyError:
        is_lock = False
    except Exception as e:
        print(f" ### {e}")
        is_lock = False

    if not is_lock:
        try:
            proof = acc.req_to(node).create_tx_proof(acc, SEND_AMOUNT)
        except AssertionError:
            print('create error')
            proof = 'busy'

        if isinstance(proof, str) and 'busy' not in proof:
            acc.cache['lock'] = True
            PROOF_QUEUE.put({acc: proof})
            print('created')
        else:
            acc.cache['lock'] = False
            print(" ### create err")
    else:
        pass


def send_then_release():
    try:
        acc, proof = PROOF_QUEUE.get(timeout=3).popitem()
    except Empty:
        return

    try:
        is_lock = acc.cache['lock']
    except KeyError:
        is_lock = False
    except Exception as e:
        print(f"send fff {e}")
        is_lock = False

    print(f'is lock : {is_lock}')

    if is_lock:
        res = FULL_NODE_SEND.send_proof(proof)
        acc.cache['lock'] = False
        print(':::: sent')
        return res


def test_create_proofs_self_send():
    # shard = random.randrange(len(ACCOUNTS))
    senders = ACCOUNTS[SHARD][:NUM_OF_SENDER]
    COIN_MASTER.top_up_if_lower_than(senders, coin(3), coin(5))

    INFO_HEADLINE(f' PREPARE TEST DATA, 1 SHARD TX, SHARD {SHARD}, SELF SEND')

    global send___thread, create_thread
    # while run:
    num_of_full_node = len(FULL_NODE_LIST)
    j = 0
    for i in range(LOOP):
        print(f"::: LOOP {i + 1}")
        try:
            for sender in senders:
                j += 1
                t_create = executor_create.submit(lock_then_create, sender, FULL_NODE_LIST[j % num_of_full_node])
                create_thread.append(t_create)
                t___send = executor___send.submit(send_then_release, )
                send___thread.append(t___send)
        except KeyboardInterrupt:
            print("::: STOP LOOPING")
            break

    summarize()


def summarize(sig=None, frame=None):
    global run
    run = False
    SHUT_DOWN_WAIT = True
    SUMMARY = {}
    INFO_HEADLINE(f"Current queue size {PROOF_QUEUE.qsize()}")
    if len(create_thread) != 0:
        INFO_HEADLINE(f"SHUT DOWN {len(create_thread)} CREATE PROOF SERVICE...")
        executor___send.shutdown(wait=SHUT_DOWN_WAIT)
    else:
        INFO_HEADLINE(f"{len(create_thread)} CREATE PROOF SERVICE...")

    if len(send___thread) != 0:
        INFO_HEADLINE(f"SHUT DOWN {len(send___thread)} SEND PROOF SERVICE...")
        executor_create.shutdown(wait=SHUT_DOWN_WAIT)
    else:
        INFO_HEADLINE(f"{len(send___thread)} SEND PROOF SERVICE...")

    INFO_HEADLINE("SUMMARIZING, PLEASE WAIT...")
    WAIT(60)
    result_thread = []
    with ThreadPoolExecutor(max_workers=100) as exe:
        for thread in send___thread:
            try:
                res = thread.result()
                if res is not None:
                    r = exe.submit(res.get_transaction_by_hash, retry=False)
                    result_thread.append(r)
            except AttributeError:
                ERROR(f'thread return : {thread.result()}')

    for t in result_thread:
        try:
            height = t.result().get_block_height()
            SUMMARY[height] += 1
        except ValueError:
            continue
        except KeyError:
            SUMMARY[height] = 1

    INFO(f""" SUMMARY==================================================
Total: {sum(SUMMARY.values())} blocks
Block height : num of block in height
{json.dumps(SUMMARY, indent=3)}
-----------------------------------------------------------
===========================================================================
            """)
    if sig is not None:
        os._exit(1)

# signal.signal(signal.SIGINT, summarize)
