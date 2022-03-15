from concurrent.futures import ThreadPoolExecutor

import json

from Configs.Configs import ChainConfig
from Helpers.Logging import INFO
from Objects.AccountObject import Account
from Configs.Constants import coin
from Helpers.Logging import config_logger
from Helpers.TestHelper import l6
from Objects.AccountObject import Account
from Objects.IncognitoTestCase import SUT, STAKER_ACCOUNTS, ACCOUNTS, COMMITTEE_ACCOUNTS

logger = config_logger(__name__)
stake_account = Account(
    "112t8sw4ZAc1wwbKog9NhE6VqpEiPii4reg8Zc5AVGu7BkxtPYv95dXRJtzP9CkepgzfUwTseNzgHXRovo9oDb8XrEpb5EgFhKdZhwjzHTbd")

shard_test = 1
fix_node = ChainConfig.FIX_BLOCK_VALIDATOR


def get_staker_by_tx_id(tx_id):
    default = 'd0e731f55fa6c49f602807a6686a7ac769de4e04882bb5eaf8f4fe209f46535d'
    if tx_id == default:
        return COMMITTEE_ACCOUNTS[0]
    acc_group = ACCOUNTS + STAKER_ACCOUNTS
    response = SUT().get_transaction_by_hash(tx_id)
    try:
        meta_data = response.get_meta_data()
    except:
        logger.info(f'Find staker of transaction by tx_id: {tx_id}: Error')
    pay_add_k_staker = meta_data.get_funder_payment_address()
    staker = acc_group.find_account_by_key(pay_add_k_staker)
    return staker


def set_consensus_for_node_by_node(proposer_index=None, num_of_no_vote=None, num_of_no_handle_vote=None,
                                   num_of_no_handle_msg=None, num_of_no_validate=None):
    HANDLER_shard = SUT.shards[shard_test]._node_list
    if proposer_index is None:
        with ThreadPoolExecutor() as executor:
            for node in HANDLER_shard:
                executor.submit(node.set_consensus_rule)
        return
    INFO(
        f'Testcase: proposer indx{proposer_index}\n\t{num_of_no_vote} no vote\n\t{num_of_no_handle_vote} no handle vote\n\t{num_of_no_handle_msg} no handle msg')
    list_remain_node = HANDLER_shard.copy()
    next_proposer = list_remain_node[proposer_index]
    INFO(f'Set default rule for proposer inx {proposer_index}')
    next_proposer.set_consensus_rule()
    list_remain_node.remove(next_proposer)
    thread_pool1 = []
    rule_vote = []
    rule_handle_msg = []
    rule_handle_vote = []
    rule_validate = []
    with ThreadPoolExecutor() as executor:
        for node in list_remain_node:
            thread1 = executor.submit(node.get_consensus_rule)
            thread_pool1.append(thread1)
    for th in thread_pool1:
        result = th.result()
        rule_v = result.get_vote_rule()
        rule_vote.append(rule_v)
        rule_h_m = result.get_handle_propose_rule()
        rule_handle_msg.append(rule_h_m)
        rule_h_v = result.get_handle_vote_rule()
        rule_handle_vote.append(rule_h_v)
        rule_val = result.get_validate_rule()
        rule_validate.append(rule_val)
    if num_of_no_vote == 0:
        rule_vote = ['vote'] * fix_node
    elif type(num_of_no_vote) is int:
        for i in range(num_of_no_vote):
            rule_vote[i] = 'no-vote'
    if num_of_no_handle_msg == 0:
        rule_handle_msg = ['handle-propose-message'] * fix_node
    elif type(num_of_no_handle_msg) is int:
        n = num_of_no_handle_msg - (fix_node - 1 - proposer_index)
        if n <= 0:
            list_node_no_handle_msg = HANDLER_shard[proposer_index + 1:proposer_index + 1 + num_of_no_handle_msg]
        else:
            list_node_no_handle_msg = HANDLER_shard[proposer_index + 1:] + HANDLER_shard[:n]
        for node in list_node_no_handle_msg:
            i = list_remain_node.index(node)
            rule_handle_msg[i] = 'no-handle-propose-message'
    if num_of_no_handle_vote == 0:
        rule_handle_vote = ['collect-vote'] * fix_node
    elif type(num_of_no_handle_vote) is int:
        for i in range(num_of_no_handle_vote):
            rule_handle_vote[i] = 'no-collect-vote'
    if num_of_no_validate == 0:
        rule_validate = ['validator-lemma2'] * fix_node
    elif type(num_of_no_validate) is int:
        for i in range(num_of_no_validate):
            rule_validate[i] = 'validator-no-validate'
    INFO('Set consensus rule for:')
    with ThreadPoolExecutor() as executor:
        for j in range(len(list_remain_node)):
            INFO(f'node {j}: {rule_vote[j]}_{rule_handle_vote[j]}_{rule_handle_msg[j]}_{rule_validate[j]}')
            executor.submit(list_remain_node[j].set_consensus_rule, vote_rule=rule_vote[j],
                            handle_vote_rule=rule_handle_vote[j], handle_propose_rule=rule_handle_msg[j],
                            validator_rule=rule_validate[j])


def create_param(name_feature, min_triger, percentage, json_str=True):
    config = {"MinTriggerBlockHeight": min_triger, "ForceBlockHeight": 1000000000, "RequiredPercentage": percentage}
    if json_str:
        param = json.dumps({name_feature: config})
        INFO("Create config")
        INFO(param)
        return param
    else:
        return {name_feature: config}
