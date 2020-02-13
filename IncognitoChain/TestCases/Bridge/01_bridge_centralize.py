from IncognitoChain.Helpers.Logging import *
from IncognitoChain.Helpers.Time import get_current_date_time, WAIT

from IncognitoChain.Objects.AccountObject import get_accounts_in_shard
from IncognitoChain.Objects.IncognitoTestCase import SUT

# sender_account = get_accounts_in_shard(0)[1]
receiver_account = get_accounts_in_shard(0)[0]
# init_sender_balance = sender_account.get_prv_balance()
# init_receiver_balance = receiver_account.get_prv_balance()

token_name = get_current_date_time()
token_id = "0000000000000000000000000000000000000000000000000000" + token_name
# token_id = "0000000000000000000000000000000000000000000000000000110220174656"
# token_name = "110220174656"
token_amount = int(token_name)


def setup_function():
    """
    double check token balance (total supply) with RPC listalltoken in chain
    double check api of aPhuong, to see which one is decentralized token
    decide token-id to be test
    :return:
    """
    # sender_account.send_all_prv_to(receiver_account).subscribe_transaction()


def teardown_function():
    """
    burn/withdraw decentralize token
    :return:
    """
    # receiver_account.send_prv_to(sender_account, init_sender_balance, privacy=0).subscribe_transaction()


def test_init_centralize_token():
    """
    1Shard
    init new token id
    verify new token id in list_all_token
    verify new token id in list_bridge_token
    verify user received new token
    verify amount
    """
    INFO("Initialize a completely new centralize token")

    STEP(1, "check receiver balance before init token")
    receiver_balance_before = receiver_account.get_token_balance(token_id)
    INFO(f"receiver balance: {receiver_balance_before}")

    STEP(2, "init new token")
    SUT.full_node.issue_centralize_token(receiver_account, token_id, token_name, token_amount).subscribe_transaction()
    INFO(f"new token id: {token_id} initialized")

    STEP(3, "check new token in getallbridgetokens")
    bridge_token_list = SUT.full_node.bridge().get_bridge_token_list().get_result()
    found_token_id = False
    for token in bridge_token_list:
        if token['tokenId'] == token_id:
            assert token['amount'] == token_amount and INFO(
                f"the getallbridgetokens has found TokenId with correct token amount: {token_amount}")
            found_token_id = True
            break
    assert found_token_id, f"tokenId {token_id} not found in getallbridgetokens"

    # STEP(4, "check new token in listprivacycustomtoken")
    # all_token_list = SUT.full_node.bridge().get_all_token_list().get_result()
    # found_token_id = False
    # for token in all_token_list['ListCustomToken']:
    #     if token['ID'] == token_id:
    #         assert token['Amount'] == token_amount and INFO(
    #             f"the listprivacycustomtoken has found TokenId with correct token amount: {token_amount}")
    #         found_token_id = True
    #         break
    # assert found_token_id, f"tokenId {token_id} not found in listprivacycustomtoken"

    STEP(5, "check receiver balance after init token")
    WAIT(90)
    receiver_balance_after = receiver_account.get_token_balance(token_id)
    assert receiver_balance_after == token_amount and INFO(
        f"receiver balance: {receiver_balance_after}"), "receiver balance is not correct"


def test_send_centralize_token_1shard():
    pass


def test_send_centralize_token_xshard():
    pass


def test_burn_centralize_token():
    pass


def test_withdraw_centralize_token():
    pass
