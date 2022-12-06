import multiprocessing as mp

from APIs.BackEnd.CoinService.CoinService import CoinServiceApi
from ApiTesting import END_POINT_MAINNET_V2
from Helpers.Logging import CRITICAL
from environments.TestData.Account8000V2_full import account_list


def thread_submit_ota_key(cs_api, account):
    try:
        rs = cs_api.submit_ota_key(account.ota_k, account.shard)
        err = rs.get_error_msg()
        if err:
            CRITICAL(rs)
    except BaseException as be:
        CRITICAL(be)


if __name__ == "__main__":
    with mp.Pool() as mp_pool:
        CS = CoinServiceApi(END_POINT_MAINNET_V2)
        res_list = []
        for acc in account_list:
            res_list.append(mp_pool.apply_async(thread_submit_ota_key, (CS, acc)))

        for res in res_list:
            res.wait()

