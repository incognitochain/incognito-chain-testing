import json
import signal

import pytest

from Configs.Configs import TestConfig
from Helpers.Logging import INFO
from Objects.IncognitoTestCase import SUT

# config.prepare_coin_precondition = False
salary_log_file = 'salary_log.txt'
salary_log = open(salary_log_file, 'w+')


def close_file_then_quit(sig, frame):
    salary_log.close()
    INFO('Salary log file closed. Quit now')
    exit(0)


signal.signal(signal.SIGINT, close_file_then_quit)


@pytest.mark.parametrize("num_of_epoch_to_monitor", [
    100
])
def test_monitor_total_reward_decrease_over_time(num_of_epoch_to_monitor):
    bb_reward_dict = {}
    last_bb = None
    last_last_bb = None

    for i in range(num_of_epoch_to_monitor):
        INFO()
        bb = SUT().get_first_beacon_block_of_epoch(-1)
        sum_ = bb.sum_all_reward()
        try:
            last_sum = last_bb.sum_all_reward()
            last_last_sum = last_last_bb.sum_all_reward()
            delta_1 = last_sum - sum_
            delta_2 = last_last_sum - sum_
            delta_perc_1 = round((delta_1 / last_sum) * 100, 2)
            delta_perc_2 = round((delta_2 / last_last_sum) * 100, 2)
            INFO(f'TOTAL REWARD DECREASE COMPARE TO LAST EPOCH     = {delta_1} ~ {delta_perc_1}%')
            INFO(f'TOTAL REWARD DECREASE COMPARE TO 2nd LAST EPOCH = {delta_2} ~ {delta_perc_2}%')
            if delta_1 != 0 and delta_2 != 0:
                lines = f"epoch {bb.get_epoch()} reward decrease {delta_perc_1} compare to {last_bb.get_epoch()}\n", \
                        f"epoch {bb.get_epoch()} reward decrease {delta_perc_2} compare to {last_last_bb.get_epoch()}\n"
                salary_log.writelines(lines)
        except AttributeError as e:
            pass
        last_last_bb = last_bb
        last_bb = bb
        bb_reward_dict[bb.get_height()] = sum_
    salary_log.close()
    INFO(json.dumps(bb_reward_dict, indent=3))
