import pytest

from subprocess import Popen, PIPE
from Configs.Constants import PBTC_ID
from Helpers.Logging import STEP, INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT
from Objects.Portalv4Objects import PortalV4InfoBase
from TestCases.PortalV4 import TEST_SETTING_SHIELD_AMOUNT, all_users, bitcoin, \
    MULTISIG_ADDRESS, buildProofPath, username, password, host, port

BTC_ADDRESS_TYPE = {"P2SH": "legacy", "P2PKH": "p2sh-segwit", "P2WSH": "bech32", "P2WPKH": "bech32"}


def createAndSendRawTx(accountaddress, inputs, outputs, memo):
    if memo != "":
        outputs.append({"data": memo.encode('utf-8').hex()})
    # print(outputs)
    rawtx = bitcoin.createrawtransaction(inputs, outputs)
    # print('\n' + rawtx + '\n')

    # extract private key by address
    dumpprivatekey = bitcoin.dumpprivkey(accountaddress)
    # print('dumpprivatekey :' + dumpprivatekey + '\n')

    # sign raw tx
    rawtxsigned = bitcoin.signrawtransactionwithkey(rawtx, [dumpprivatekey])
    INFO(f"Raw transaction (HEX) = {rawtxsigned['hex']}")
    # print(rawtxsigned['hex'])

    # broadcast raw transaction
    txid = bitcoin.sendrawtransaction(rawtxsigned['hex'])
    return txid


def balanceBaseInputs(inputs):
    for x in inputs:
        tx = bitcoin.gettransaction(x["txid"])
        print(tx)


def setup_module():
    INFO("setup ....")


@pytest.mark.parametrize("token, shield_amount, user, payment_mode, desired_status",
                         [
                             (PBTC_ID, TEST_SETTING_SHIELD_AMOUNT, all_users[0], "P2SH", "valid"),
                             (PBTC_ID, TEST_SETTING_SHIELD_AMOUNT, all_users[1], "P2PKH", "valid"),
                             (PBTC_ID, TEST_SETTING_SHIELD_AMOUNT, all_users[2], "P2WSH", "valid"),
                             (PBTC_ID, TEST_SETTING_SHIELD_AMOUNT, all_users[3], "P2WPKH", "valid"),
                             (PBTC_ID, TEST_SETTING_SHIELD_AMOUNT, all_users[1], "P2SH", "invalid"),  # memo NULL
                         ])
def test_shield(token, shield_amount, user, payment_mode, desired_status):
    STEP(0, "Preparation before test")
    # get portal state before
    PSI_before_test = SUT().get_latest_portal_v4_state_info()
    list_output_init = PSI_before_test.get_list_utxo(token)
    total_output_amt_init = PSI_before_test.sum_output_amount_all_utxo(token)

    # create new account for gen new block
    account = bitcoin.getnewaddress("acc", BTC_ADDRESS_TYPE[payment_mode])
    # print(account)

    # one more account for testing
    account1 = bitcoin.getnewaddress("acc1", BTC_ADDRESS_TYPE[payment_mode])
    print(account1)

    # generate 200 block first to enable transfer feature only run once
    # only for regtest
    for i in range(2):
        WAIT(2)
        bitcoin.generatetoaddress(1, account)

    # send to an address
    txid = bitcoin.sendtoaddress(account1, 10)
    for i in range(6):
        WAIT(2)
        bitcoin.generatetoaddress(1, account)

    STEP(1, "Send BTC ")

    # send BTC
    # transfer token to an address
    listUTXOs = bitcoin.listunspent(6, 9999999, [account1], True)
    # print(listUTXOs)
    inputs = []
    for x in listUTXOs:
        inputs.append({"txid": x["txid"], "vout": x["vout"]})
    # balanceBaseInputs(inputs)
    # print(inputs)
    amt_btc_shield = 0.0005
    amt_btc_shield_remain = 9.9945
    outputs = [{MULTISIG_ADDRESS: amt_btc_shield}, {account1: amt_btc_shield_remain}]
    memo = "PS1-" + user.payment_key
    # print('\n' + memo)
    if desired_status == "invalid":
        memo = ""
    btc_txid = createAndSendRawTx(account1, inputs, outputs, memo)
    for i in range(7):
        WAIT(2)
        bitcoin.generatetoaddress(1, account)
    # print(newtxid)
    INFO(f"BTC txhash = {btc_txid}")

    STEP(2, "Submit proof to request pToken")
    bal_token_before_submit = user.get_token_balance(token)
    bal_prv_before_submit = user.get_prv_balance()

    process = Popen(
        [buildProofPath, "-txhash", btc_txid, "-username", username, "-password", password, "-host", host + ":" + port],
        stdout=PIPE)
    (output, err) = process.communicate()

    proof = output.decode("utf-8").split(' ')[2]
    INFO(f"Proof : {proof}")
    # breakpoint()
    WAIT(100)

    shield_req = user.portal_v4_shield_req(token, user.private_key, proof)
    shield_req.subscribe_transaction()
    # print(shield_req.get_tx_id())
    WAIT(10)

    STEP(3, "Verify balance ")
    shield_req_status = PortalV4InfoBase().get_shield_req_status(shield_req.get_tx_id(), True)
    bal_token_after_submit = user.get_token_balance(token)
    bal_prv_after_submit = user.get_prv_balance()
    if desired_status == "invalid":
        assert shield_req_status == 0
        assert bal_token_after_submit == bal_token_before_submit
    else:
        assert shield_req_status == 1
        assert bal_token_after_submit == bal_token_before_submit + (amt_btc_shield * 1e9)

    STEP(4, "Verify portal state")
    #     check UTXO update
    PSI_af_shield = SUT().get_latest_portal_v4_state_info()
    list_output_af_shield = PSI_af_shield.get_list_utxo(token)
    total_output_amt_af_shield = PSI_af_shield.sum_output_amount_all_utxo(token)
    if desired_status == "invalid":
        assert total_output_amt_init == total_output_amt_af_shield
        assert PSI_af_shield.find_utxo_by_txHash_amount(token, btc_txid, int(amt_btc_shield * 1e8)) == False
    else:
        assert total_output_amt_init + int(amt_btc_shield * 1e8) == total_output_amt_af_shield
        assert PSI_af_shield.find_utxo_by_txHash_amount(token, btc_txid, int(amt_btc_shield * 1e8)) == True

# def test_mint_pToken_cross_shard():
#     Pass
#
# def test_shield_n_output_btc():
#     Pass
#
# def test_shield_with_n_input_to_m_output_btc():
#     Pass
#
# def test_shield_wait_confirmation_block():
#     Pass
#
# def test_shield_double_submit_proof():
#     Pass
