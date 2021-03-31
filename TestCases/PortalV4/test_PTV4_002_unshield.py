import pytest

from subprocess import Popen, PIPE
from Configs.Constants import PBTC_ID
from Helpers.Logging import STEP, INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT
from Objects.Portalv4Objects import PortalV4InfoBase
from TestCases.PortalV4 import TEST_SETTING_UNSHIELD_AMOUNT, all_users, bitcoin, \
    buildProofPath, username, password, host, port

BTC_ADDRESS_TYPE = {"P2SH": "legacy", "P2PKH": "p2sh-segwit", "P2WSH": "bech32", "P2WPKH": "bech32"}
FEE_BTC = 50000
TEST_SETTING_UNSHIELD_AMOUNT = int(0.1 * 1e9)


def get_utxo_key(list_utxo):
    list_key = []
    for i in list_utxo:
        key = i.get_key()
        list_key.append(key)
    return list_key


def sum_amount_list_ustxo(list_utxo):
    amt = 0
    for i in range(len(list_utxo)):
        amt += list_utxo[i].get_output_amt()
    return amt


def setup_module():
    INFO("setup ....")


@pytest.mark.parametrize("token, unshield_amount, user, payment_mode, desired_status, replace_fee",
                         [
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[0], "P2SH", "valid", True),
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[0], "P2SH", "valid", False),

                         ])
def test_shield(token, unshield_amount, user, payment_mode, desired_status, replace_fee):
    STEP(0, "Preparation before test")
    # get portal state before
    PSI_before_test = SUT().get_latest_portal_v4_state_info()
    list_utxo_init = PSI_before_test.get_list_utxo(token)
    total_output_amt_init = PSI_before_test.sum_output_amount_all_utxo(token)

    # get balance pToken
    bal_prv_int = user.get_prv_balance()
    bal_ptoken_int = user.get_token_balance(token)

    STEP(1, "Call unshield req")
    INFO()
    #  call unshield req
    unshield_req = user.portal_v4_unshield_req(token, unshield_amount, user.get_remote_addr(token, "P2SH"))
    unshield_req.subscribe_transaction(unshield_req.get_tx_id())

    # get unshield_req_status (status =0 wating)
    unshield_req_status = PortalV4InfoBase().get_unshield_req_status(unshield_req.get_tx_id(), True)
    assert unshield_req_status == 0

    # get balance pToken after burn
    bal_prv_af_burn = user.get_prv_balance()  ##  - fee
    bal_ptoken_af_burn = user.get_token_balance(token)
    assert bal_prv_af_burn < bal_prv_int
    assert bal_ptoken_af_burn == bal_ptoken_int - unshield_amount

    STEP(2, "Verify portal state")
    INFO()
    # update WaitingUnshieldRequests
    PSI_af_burn = SUT().get_latest_portal_v4_state_info()
    list_utxo_af_burn = PSI_af_burn.get_list_utxo(token)

    list_waiting_unshield_obj = PSI_af_burn.get_list_unshield_waiting(token)
    list_waiting_unshield_tmp = []
    for i in list_waiting_unshield_obj:
        list_waiting_unshield_tmp.append(i.get_unshield_id())
    list_waiting_unshield = set(list_waiting_unshield_tmp)
    assert PSI_af_burn.find_unshield_in_waiting_by_id(token, unshield_req.get_tx_id()) == True

    # verify way to group unshield to batch
    # pick UTXO
    list_utxo_expect = PSI_af_burn.pick_utxo(token, unshield_amount)

    # Wait 15 beacon block
    WAIT(20 * 10)

    # create batchID with unsheild in ProcessedUnshieldRequests
    PSI_af_batching = SUT().get_latest_portal_v4_state_info()
    batch_id = PSI_af_batching.find_batch_id_by_unshield_id(token, unshield_req.get_tx_id())
    assert batch_id is not None
    INFO(f"Batch ID = {batch_id}")
    # breakpoint()
    # TO DO compare list utxo
    assert PSI_af_batching.get_batch_with_batch_id(token, batch_id).compare_list_utxo_in_batch(list_utxo_expect) == True
    # clear unshieldID in WaitingUnshieldRequests
    list_unshield_waiting_af_batching = set(PSI_af_batching.get_list_unshield_waiting(token))
    assert list_waiting_unshield - list_unshield_waiting_af_batching == list_waiting_unshield
    # clear utxo in list UTXO
    assert set(get_utxo_key(list_utxo_expect)) - set(get_utxo_key(list_utxo_init)) == set()
    assert set(get_utxo_key(list_utxo_expect)) - set(get_utxo_key(list_utxo_af_burn)) == set()
    # get unshield_req_status (status =1 process)
    assert PortalV4InfoBase().get_unshield_req_status(unshield_req.get_tx_id(), True) == 1

    STEP(3, "send RAW transaction BTC")
    # cal rpc get raw transaction
    raw_btc_transaction = PortalV4InfoBase().get_raw_btc_transaction(batch_id)
    INFO(f"Raw transaction BTC : {raw_btc_transaction}")

    #     send to BTC network
    txhash_btc = bitcoin.sendrawtransaction(raw_btc_transaction)
    account = bitcoin.getnewaddress("acc", "legacy")
    INFO(f"BTC txHash : {txhash_btc}")

    if replace_fee == False:
        # 6 confirmation block
        INFO("Waiting 6 btc confirmation block ")
        for i in range(7):
            WAIT(2)
            bitcoin.generatetoaddress(1, account)

    else:
        STEP(3.1, " Replacement fee")
        INFO()
        WAIT(100)
        PSI_replace_fee = SUT().get_latest_portal_v4_state_info()
        beacon_height = PSI_replace_fee.get_last_beacon_height_replace_fee(token, batch_id)
        #     check time to trick replace fee : get beacon height in batch + 5 minutes

        #      calculator fee
        last_fee = PSI_replace_fee.get_last_fee(token, batch_id)
        fee = last_fee + last_fee * 0.16

        #   call rpc replace fee
        replace_fee_req = user.replace_fee(token, batch_id, int(fee))
        replace_fee_req.subscribe_transaction()
        # breakpoint()
        #   check replace fee status
        assert PortalV4InfoBase().get_replace_fee_status(replace_fee_req.get_tx_id()) == 1

        STEP(3.2, "send raw transaction btc with replace fee")
        #     get transaction raw
        WAIT(5)
        raw_btc_rpl_fee_transaction = PortalV4InfoBase().get_raw_replace_fee_btc_transaction(replace_fee_req.get_tx_id())
        INFO(f"Raw transaction BTC : {raw_btc_rpl_fee_transaction}")
        #     send to BTC network
        txhash_btc = bitcoin.sendrawtransaction(raw_btc_rpl_fee_transaction)
        account = bitcoin.getnewaddress("acc", "legacy")
        INFO(f"BTC replace fee txHash : {txhash_btc}")

        # 6 confirmation block
        for i in range(7):
            WAIT(2)
            bitcoin.generatetoaddress(1, account)
    INFO("Waiting push BTC header block to Incognito chain")
    WAIT(100)

    STEP(4, "submit confirm utxo")
    INFO()
    # proof btc of tx send from multisig -> end_user wallet
    process = Popen([buildProofPath, "-txhash", txhash_btc, "-username", username, "-password", password, "-host",
                     host + ":" + port], stdout=PIPE)
    (output, err) = process.communicate()
    proof_btc = output.decode("utf-8").split(' ')[2]
    INFO(f"Proof : {proof_btc}")
    submit_proof_req = user.submit_proof_confirm_unshield(proof_btc, token, batch_id)
    submit_proof_req.subscribe_transaction()
    WAIT(30)
    assert PortalV4InfoBase().get_submit_proof_confirm_status(submit_proof_req.get_tx_id()) == 1
    assert PortalV4InfoBase().get_unshield_req_status(unshield_req.get_tx_id()) == 2
    amount_remain_utxo = sum_amount_list_ustxo(list_utxo_expect) - (unshield_amount / 10)
    PSI_af_confirm_utxo = SUT().get_latest_portal_v4_state_info()
    if amount_remain_utxo <= 0:
        assert PSI_af_confirm_utxo.find_utxo_by_txHash_amount(token, txhash_btc, int(amount_remain_utxo)) == False
    else:
        assert PSI_af_confirm_utxo.find_utxo_by_txHash_amount(token, txhash_btc, int(amount_remain_utxo)) == True

    assert total_output_amt_init - int(PSI_af_confirm_utxo.sum_output_amount_all_utxo(token)) == int(TEST_SETTING_UNSHIELD_AMOUNT/10)
