import re

from Configs.Configs import ChainConfig
from Helpers.Logging import INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT

if ChainConfig.ACTIVE_SHARD != 8:
    fix_node = 12
else:
    fix_node = 8


def test_tracking_validation_by_height():
    INFO()
    beacon_bs = SUT().get_beacon_best_state_info()
    proposers_list = []
    for i in range(ChainConfig.ACTIVE_SHARD):
        committees = beacon_bs.get_shard_committees(i)
        proposers_list.append(committees[:fix_node])

    def info_by_height(shard, committee_shard):
        height = SUT().get_shard_best_state_info(shard).get_shard_height()
        height -= 1
        b4_propose_time = None
        while True:
            string = f'\n===    SHARD_{shard}  -  Height {height}    ====\n'
            try:
                data_block = SUT().get_shard_block_by_height(shard, height, level=2)
            except TypeError:
                WAIT(ChainConfig.BLOCK_TIME)
                continue
            proposer = data_block.get_proposer()
            producer = data_block.get_block_producer()
            propose_time = data_block.get_propose_time()
            produce_time = data_block.get_time()
            finality_height = data_block.get_finality_height()
            validation_data = data_block.get_validation_data()
            index_proposer = index_producer = None
            for j in range(len(committee_shard)):
                if index_proposer is None and committee_shard[j] == proposer:
                    if producer == proposer:
                        index_proposer = index_producer = j
                        break
                    index_proposer = j
                    continue
                if index_producer is None and committee_shard[j] == producer:
                    index_producer = j
                if index_producer and index_proposer is not None:
                    break
            string += f'\tTimeslot produce: {produce_time}\n'
            string += f'\tTimeslot propose: {propose_time}\n'
            string += f'\tProducer Idx: {index_producer}\n'
            string += f'\tProposer Idx: {index_proposer}\n'
            validators_str = re.match('([\D\d]+\\\"ValidatiorsIdx\\\"\:\[)([\d,]*)(\][\D\d]+)',
                                      validation_data).group(
                2)
            string += f'\tValidators Idx: {validators_str}\n'
            string += f'\tFinality Height: {finality_height}'
            INFO(string)
            if b4_propose_time is not None:
                if produce_time == b4_propose_time + ChainConfig.BLOCK_TIME and (propose_time - produce_time) < (
                        23 * ChainConfig.BLOCK_TIME):
                    assert finality_height == height - 1
                else:
                    assert finality_height == 0
            b4_propose_time = propose_time
            height += 1
            WAIT(ChainConfig.BLOCK_TIME)

    # with ThreadPoolExecutor() as executor:
    #     for i in range(ChainConfig.ACTIVE_SHARD):
    #         executor.submit(info_by_height, i, proposers_list[i])
    shard_test = 2
    info_by_height(shard_test, proposers_list[shard_test])
