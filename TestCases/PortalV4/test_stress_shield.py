from concurrent.futures.thread import ThreadPoolExecutor
import pytest
from Configs.Constants import PBTC_ID
from Helpers.Logging import INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import ACCOUNTS
from TestCases.PortalV4.test_PTV4_001_shield_new_flow import test_shield_new_flow as shield_btc
from multiprocessing import Lock



# def _do_shield():
#     while(len(ACCOUNTS) < 0):
#         counter = len(ACCOUNTS) - 1
#         INFO(f"Shielding for Account : {counter} ")
#         test_shield_new_flow(PBTC_ID,BTC_SHIELD_AMOUNT,ACCOUNTS[counter], "P2SH", "valid")
#         if counter == 1:
#             counter = len(ACCOUNTS)
#     INFO("End process")

def print_test():
    print("aaaaaaa1")
    print("aaaaaaa2")
    print("aaaaaaa3")
    print("aaaaaaa4")
    print("aaaaaaa5")
    print("aaaaaaa6")
    print("aaaaaaa7")
    lock =Lock()
    lock.acquire()
    print("aaaaaaa8")
    WAIT(3)
    print("aaaaaaa9")
    print("aaaaaaa10")
    lock.release()


def test_sumit_theard():
    INFO("Start process ")
    with ThreadPoolExecutor(max_workers= len(ACCOUNTS)) as executor:
        counter = len(ACCOUNTS) -1
        while(counter > 0):
            counter -= 1
            INFO(f"Shielding for Account : {counter} ")
            executor.submit(shield_btc, PBTC_ID, 0.1, ACCOUNTS[counter], "P2PKH", "loadtest")
            # executor.submit(print_test)
            if counter == 1:
                WAIT(5)
                counter = len(ACCOUNTS)
    INFO("End process")




