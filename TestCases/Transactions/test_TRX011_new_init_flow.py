import pytest

from Configs.Configs import ChainConfig
from Helpers import TestHelper
from Helpers.Logging import STEP, INFO
from Objects.IncognitoTestCase import ACCOUNTS, SUT


def setup_function():
    INFO('Precondition check: test data must have at least 1 account for each shard')
    for shard in range(ChainConfig.ACTIVE_SHARD):
        assert ACCOUNTS.get_accounts_in_shard(shard) != [], f"Double check your test data. " \
                                                            f"There's no account in shard {shard}"


@pytest.mark.parametrize('init_shard,init_amount', [
    (1, 1000000000),
    (0, 1000000000)
])
def test_new_init_flow(init_shard, init_amount):
    token_name = f'random_{TestHelper.make_random_word()}'
    init_acc = ACCOUNTS.get_accounts_in_shard(init_shard)[0]

    STEP(1.1, f'Init token in shard {init_shard} with amount {init_amount}')
    init_acc.init_custom_token_new_flow(init_amount, token_name=token_name).expect_no_error().subscribe_transaction()

    STEP(1.2, f'Check owned token, the new token will not yet be minted')
    assert not init_acc.list_owned_custom_token().get_token_id_by_name(token_name)

    STEP(2, f'Wait for new token to be minted')
    SUT().wait_till_next_beacon_height(4)
    new_token = init_acc.list_owned_custom_token().get_token_id_by_name(token_name)
    INFO(f"New token id: {new_token}")

    STEP(3, f'Verify the inited token must also exist in other shards')
    final_result = True
    for shard in range(ChainConfig.ACTIVE_SHARD):
        if shard != init_shard:
            INFO(f'Sending list custom token request to shard {shard} to check')
            all_token = SUT.shards[shard].get_representative_node().get_all_token_in_chain_list()
            if new_token in all_token:
                INFO(f"token {new_token} is FOUND in shard {shard}")
            else:
                INFO(f"token {new_token} is NOT FOUND in shard {shard}")
                final_result = False
    assert final_result

    # STEP(3, f'Make sure other shard cannot re-init the same token')
