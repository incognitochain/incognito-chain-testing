import pytest

from subprocess import Popen, PIPE
from Configs.Constants import PBTC_ID
from Helpers.Logging import STEP, INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT
from Objects.Portalv4Objects import PortalV4InfoBase
from TestCases.PortalV4 import TEST_SETTING_UNSHIELD_AMOUNT, all_users, bitcoinCLI, \
    buildProofPath, username, password, host, port

BTC_ADDRESS_TYPE = {"P2SH": "legacy", "P2PKH": "p2sh-segwit", "P2WSH": "bech32", "P2WPKH": "bech32"}
FEE_BTC = 50000
TEST_SETTING_UNSHIELD_AMOUNT = int(0.1 * 1e9)
TEST_SETTING_UNSHIELD_AMOUNT_REFUND = 50000
MAX_REPLACE_FEE_PERCENT = 20
PROOF_SUBMIT_UTXO_INVALID = "eyJNZXJrbGVQcm9vZnMiOlt7IlByb29mSGFzaCI6WzExNSwwLDgxLDE5OCwxMjksMTg2LDQzLDE0LDEwNiwyNCwxMjIsMTY5LDE1NCwxMDgsNDQsMTIyLDEwNSwxMSwxNTYsMjYsMjAsMzQsMTk0LDEzMCwzNSwyNDYsNjEsMjI4LDU1LDcwLDE2NCwxMzNdLCJJc0xlZnQiOnRydWV9XSwiQlRDVHgiOnsiVmVyc2lvbiI6MiwiVHhJbiI6W3siUHJldmlvdXNPdXRQb2ludCI6eyJIYXNoIjpbMTQ5LDI1LDI0Myw1MSwxNTMsMTcsMjI0LDE0MCwxMjQsMTkwLDI0NSw4NCwyMiwyNDcsMzksMTE0LDIxNSwxNjYsMywxOTEsNSwyMzAsMzIsMTgwLDIyMSwyMjMsMjIzLDY5LDEyNiwxMTEsNTYsMjQ4XSwiSW5kZXgiOjB9LCJTaWduYXR1cmVTY3JpcHQiOiJSekJFQWlCSHg2dEZkVjdUUE5kTWZBdSttVWdwdTIzM0Z2czZJOFlmOWVDdTVvVmU3QUlnY0JGdDkxYTRRRU1IVlNRdHhFYmE0OUs3VHFndlM3VUloRFo0aG83Y3doa0JJUUphYUlFTW9JVE9CaG9nODU2NWQvZE04ZDZ2eGI0Ylc5NEp1NllhMGw2L3N3PT0iLCJXaXRuZXNzIjpudWxsLCJTZXF1ZW5jZSI6NDI5NDk2NzI5NX1dLCJUeE91dCI6W3siVmFsdWUiOjEwMDAwMDAwLCJQa1NjcmlwdCI6IkFDQUVBU0I0bWhaaktGeVk0c3lPTlJicXdmTk9qTkZGTDU3WEhmaVR1RWdZZ0E9PSJ9LHsiVmFsdWUiOjk4OTUwMDAwMCwiUGtTY3JpcHQiOiJkcWtVd1VYK29wYVdvN0pRTkxqZmhPZGU4V1VGMWRHSXJBPT0ifV0sIkxvY2tUaW1lIjowfSwiQmxvY2tIYXNoIjpbNDYsMzksMzksMjI1LDE2NCwxMzIsNTMsNDEsMzAsOCwyNywyMzcsMTA3LDE0OSw0MCwxOTUsNDksMTg4LDIzLDIzNywxNDksMjEsMTgxLDc4LDE3NSw1NywxNzYsMTg0LDIwNywzNCwxMTMsNjJdfQ=="


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


@pytest.mark.parametrize("token, unshield_amount, user, payment_mode, desired_status, replace_fee, n_unshield",
                         [
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[1], "P2SH", "valid","no_replace_fee", 1),
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[2], "P2SH", "invalid", "no_replace_fee",1),
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[2], "P2SH", "DoubleSubmitProof", "no_replace_fee", 2),
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[0], "P2SH", "SubmitInvalidProof","no_replace_fee", 1),

                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[1], "P2SH", "valid", "replace_fee", 1),
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[1], "P2SH", "valid", "replace_fee", 2),
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[1], "P2SH", "DoubleSubmitProof", "replace_fee", 2),
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[0], "P2SH", "underMinFee", "replace_fee", 1),
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[0], "P2SH", "overMaxFee", "replace_fee", 1),
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[0], "P2SH", "LimitTime", "replace_fee",2), # n_unshield must be greater 1
                             (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT, all_users[0], "P2SH", "afterBtcConfirmed","replace_fee", 2),

                             # (PBTC_ID, TEST_SETTING_UNSHIELD_AMOUNT_REFUND, all_users[1], "P2SH", "refund", False)

                         ])
def test_shield(token, unshield_amount, user, payment_mode, desired_status, replace_fee, n_unshield):
    STEP(0, "Preparation before test")
    # get portal state before
    PSI_before_test = SUT().get_latest_portal_v4_state_info()
    list_utxo_init = PSI_before_test.get_list_utxo(token)
    total_output_amt_init = PSI_before_test.sum_output_amount_all_utxo(token)

    for i in PSI_before_test.get_list_wallet_address(token):
        bitcoinCLI.importaddress(i)
        WAIT(1)
    bal_prv_int = user.get_prv_balance()
    bal_ptoken_int = user.get_token_balance(token)
    STEP(1, "Call unshield req")
    if replace_fee == "no_replace_fee" and desired_status == "invalid":
        unshield_amount = bal_ptoken_int + 1
    #  call unshield req
    unshield_id_list = []
    for i in range(n_unshield):
        INFO(f"Unshield {i + 1}/{n_unshield}")
        # get balance pToken
        bal_prv = user.get_prv_balance()
        bal_ptoken = user.get_token_balance(token)
        unshield_req = user.portal_v4_unshield_req(token, unshield_amount, user.get_remote_addr(token, "P2SH"))
        if replace_fee == "no_replace_fee" and desired_status == "invalid":
            bal_ptoken_af_burn_fail = user.wait_for_balance_change(token, from_balance=bal_ptoken_int,
                                                                   least_change_amount=-1,
                                                                   timeout=50)
            assert bal_ptoken_af_burn_fail == bal_ptoken
            unshield_req.expect_error("Not enough coin")
            return
        assert unshield_req.get_transaction_by_hash(unshield_req.get_tx_id(), time_out=40).is_none() == False
        bal_ptoken_af_burn = user.wait_for_balance_change(token, from_balance=bal_ptoken, least_change_amount=-1)
        unshield_id_list.append(unshield_req.get_tx_id())
        if desired_status == "refund":
            unshield_req_status = PortalV4InfoBase().get_unshield_req_status(unshield_req.get_tx_id(), True)
            assert unshield_req_status == 3
            bal_prv_af_burn = user.wait_for_balance_change(from_balance=bal_prv, least_change_amount=-1,
                                                           timeout=100)  ##  - fee
            bal_ptoken_af_refund = user.wait_for_balance_change(token, from_balance=bal_ptoken_af_burn,
                                                                least_change_amount=1,
                                                                timeout=100)
            assert bal_prv_af_burn < bal_prv_int
            assert bal_ptoken_af_refund == bal_ptoken_af_burn + unshield_amount
            return

    # get unshield_req_status (status =0 wating)
    for unshield_id_tmp in unshield_id_list:
        unshield_req_status = PortalV4InfoBase().get_unshield_req_status(unshield_id_tmp, True)
        assert unshield_req_status == 0
    # get balance pToken after burn
    bal_prv_af_burn = user.wait_for_balance_change(from_balance=bal_prv_int, least_change_amount=-1,
                                                   timeout=100)  ##  - fee
    bal_ptoken_af_burn = user.wait_for_balance_change(token, from_balance=bal_ptoken_int, least_change_amount=-1,
                                                      timeout=100)
    assert bal_prv_af_burn < bal_prv_int
    assert bal_ptoken_af_burn == bal_ptoken_int - int(unshield_amount * n_unshield)

    STEP(2, "Verify portal state")
    INFO()
    # update WaitingUnshieldRequests
    PSI_af_burn = SUT().get_latest_portal_v4_state_info()
    list_utxo_af_burn = PSI_af_burn.get_list_utxo(token)

    list_waiting_unshield_obj = PSI_af_burn.get_list_unshield_waiting(token)
    list_waiting_unshield_id = set()
    for i in list_waiting_unshield_obj:
        list_waiting_unshield_id.add(i.get_unshield_id())
    for unshield_id_tmp in unshield_id_list:
        assert PSI_af_burn.find_unshield_in_waiting_by_id(token, unshield_id_tmp) == True

    # verify way to group unshield to batch
    # pick UTXO
    list_utxo_expect = PSI_af_burn.pick_utxo(token, int(unshield_amount * n_unshield))

    # Wait 15 beacon block
    WAIT(20 * 10)

    # create batchID with unsheild in ProcessedUnshieldRequests
    PSI_af_batching = SUT().get_latest_portal_v4_state_info()
    batch_id = PSI_af_batching.find_batch_id_by_unshield_id(token, unshield_id_list[0])
    assert batch_id is not None
    INFO(f"Batch ID = {batch_id}")

    # TO DO compare list utxo
    assert PSI_af_batching.get_batch_with_batch_id(token, batch_id).compare_list_utxo_in_batch(list_utxo_expect) == True
    # clear unshieldID in WaitingUnshieldRequests
    list_unshield_waiting_af_batching = PSI_af_batching.get_list_unshield_waiting(token)
    list_unshieldID_waiting_af_batching = set()
    for i in list_unshield_waiting_af_batching:
        list_unshieldID_waiting_af_batching.add(i.get_unshield_id())
    assert list_waiting_unshield_id - list_unshieldID_waiting_af_batching == list_waiting_unshield_id
    # clear utxo in list UTXO
    assert set(get_utxo_key(list_utxo_expect)) - set(get_utxo_key(list_utxo_init)) == set()
    assert set(get_utxo_key(list_utxo_expect)) - set(get_utxo_key(list_utxo_af_burn)) == set()
    # get unshield_req_status (status =1 process)
    for unshield_id_tmp in unshield_id_list:
        assert PortalV4InfoBase().get_unshield_req_status(unshield_id_tmp, True) == 1

    STEP(3, "send RAW transaction BTC")
    # cal rpc get raw transaction
    raw_btc_transaction = PortalV4InfoBase().get_raw_btc_transaction(batch_id)
    INFO(f"Raw transaction BTC : {raw_btc_transaction}")

    #     send to BTC network
    txhash_btc = bitcoinCLI.sendrawtransaction(raw_btc_transaction)
    account = bitcoinCLI.getnewaddress("acc", "legacy")
    INFO(f"BTC txHash : {txhash_btc}")

    if replace_fee == "no_replace_fee":
        # 6 confirmation block
        INFO("Waiting 6 btc confirmation block ")
        for i in range(7):
            WAIT(2)
            bitcoinCLI.generatetoaddress(1, account)

    else:
        STEP(3.1, " Replacement fee")
        INFO()
        PSI_replace_fee = SUT().get_latest_portal_v4_state_info()
        beacon_height = PSI_replace_fee.get_last_beacon_height_replace_fee(token, batch_id)
        #     check time to trick replace fee : get beacon height in batch + 5 minutes
        txhash_btc = ""
        fee = 0
        for replace_fee_times in range(n_unshield):  # set total_replace_fee_times = n_unshield
            # breakpoint()
            if desired_status == "LimitTime" and replace_fee_times > 0:
                WAIT(1)
            else:
                WAIT(100)
            #      calculator fee
            INFO(f" Relacement fee Times : {replace_fee_times + 1}/{n_unshield}")
            PSI_replace_fee_n = SUT().get_latest_portal_v4_state_info()
            last_fee = PSI_replace_fee_n.get_last_fee(token, batch_id)
            if desired_status == "underMinFee":
                fee = last_fee - 10
            elif desired_status == "overMaxFee":
                fee = last_fee + int(last_fee * (MAX_REPLACE_FEE_PERCENT / 100)) + 10
            else:
                fee = last_fee + int(last_fee * (MAX_REPLACE_FEE_PERCENT / 100))
            INFO(f"NEW FEE = {fee}")
            # breakpoint()
            #   call rpc replace fee
            replace_fee_req = user.replace_fee(token, batch_id, int(fee))
            assert replace_fee_req.get_transaction_by_hash(replace_fee_req.get_tx_id()).is_none() == False

            #   check replace fee status
            if desired_status == "underMinFee" or desired_status == "overMaxFee" or (
                    desired_status == "LimitTime" and replace_fee_times > 0):
                assert PortalV4InfoBase().get_replace_fee_status(replace_fee_req.get_tx_id()) == 0
            else:
                assert PortalV4InfoBase().get_replace_fee_status(replace_fee_req.get_tx_id()) == 1

            STEP(3.2, f"send raw transaction btc with replace fee {replace_fee_times + 1}/{n_unshield}")
            #     get transaction raw
            WAIT(5)
            raw_btc_rpl_fee_transaction = PortalV4InfoBase().get_raw_replace_fee_btc_transaction(
                replace_fee_req.get_tx_id())
            if desired_status == "underMinFee" or desired_status == "overMaxFee" or (
                    desired_status == "LimitTime" and replace_fee_times > 0):
                raw_btc_rpl_fee_transaction == None
                return
            else:
                raw_btc_rpl_fee_transaction != None
            INFO(f"Raw transaction BTC : {raw_btc_rpl_fee_transaction}")
            #     send to BTC network
            txhash_btc = bitcoinCLI.sendrawtransaction(raw_btc_rpl_fee_transaction)
            account = bitcoinCLI.getnewaddress("acc", "legacy")
            INFO(f"BTC replace fee txHash : {txhash_btc}")

        # 6 confirmation block
        for i in range(7):
            WAIT(2)
            bitcoinCLI.generatetoaddress(1, account)
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
    if desired_status == "SubmitInvalidProof":
        submit_proof_req = user.submit_proof_confirm_unshield(PROOF_SUBMIT_UTXO_INVALID, token, batch_id)
        assert submit_proof_req.get_transaction_by_hash(submit_proof_req.get_tx_id(), time_out=20).is_none() == False
        WAIT(20)
        assert PortalV4InfoBase().get_submit_proof_confirm_status(submit_proof_req.get_tx_id()) == 0
        for unshield_id_tmp in unshield_id_list:
            assert PortalV4InfoBase().get_unshield_req_status(unshield_id_tmp) == 1
        PSI_af_confirm_utxo_fail = SUT().get_latest_portal_v4_state_info()
        sum_output_amount = PSI_af_confirm_utxo_fail.sum_output_amount_all_utxo(token)
        assert total_output_amt_init - sum_output_amount == int(sum_amount_list_ustxo(PSI_af_confirm_utxo_fail.get_batch_with_batch_id(token,batch_id).get_list_utxo_in_batch()))
        return
    else:
        submit_proof_req = user.submit_proof_confirm_unshield(proof_btc, token, batch_id)
        assert submit_proof_req.get_transaction_by_hash(submit_proof_req.get_tx_id()).is_none() == False
        WAIT(30)
        assert PortalV4InfoBase().get_submit_proof_confirm_status(submit_proof_req.get_tx_id()) == 1
        for unshield_id_tmp in unshield_id_list:
            assert PortalV4InfoBase().get_unshield_req_status(unshield_id_tmp) == 2

        amount_remain_utxo = sum_amount_list_ustxo(list_utxo_expect) - ((unshield_amount * n_unshield) / 10)
        PSI_af_confirm_utxo = SUT().get_latest_portal_v4_state_info()
        sum_output_amount = PSI_af_confirm_utxo.sum_output_amount_all_utxo(token)
        if amount_remain_utxo <= 0:
            assert PSI_af_confirm_utxo.find_utxo_by_txHash_amount(token, txhash_btc, int(amount_remain_utxo)) == False
        else:
            assert PSI_af_confirm_utxo.find_utxo_by_txHash_amount(token, txhash_btc, int(amount_remain_utxo)) == True

        assert total_output_amt_init - int(PSI_af_confirm_utxo.sum_output_amount_all_utxo(token)) == int(
            (unshield_amount * n_unshield) / 10)

    if desired_status == "DoubleSubmitProof":
        INFO(f"Proof Again : {proof_btc}")
        submit_proof_req = user.submit_proof_confirm_unshield(proof_btc, token, batch_id)
        assert submit_proof_req.get_transaction_by_hash(submit_proof_req.get_tx_id(), time_out=20).is_none() == False
        WAIT(30)
        assert PortalV4InfoBase().get_submit_proof_confirm_status(submit_proof_req.get_tx_id()) == 0  # submit fail
        for unshield_id_tmp in unshield_id_list:
            assert PortalV4InfoBase().get_unshield_req_status(unshield_id_tmp) == 2
        PSI_af_double_confirm_utxo = SUT().get_latest_portal_v4_state_info()
        sum_output_amount_af_double_confirm_utxo = PSI_af_double_confirm_utxo.sum_output_amount_all_utxo(token)
        assert sum_output_amount_af_double_confirm_utxo == sum_output_amount

    if desired_status == "afterBtcConfirmed":
        fee -= 10
        replace_fee_req = user.replace_fee(token, batch_id, int(fee))
        assert replace_fee_req.get_transaction_by_hash(replace_fee_req.get_tx_id(), time_out=20).is_none() == False
        assert PortalV4InfoBase().get_replace_fee_status(replace_fee_req.get_tx_id()) == 0
