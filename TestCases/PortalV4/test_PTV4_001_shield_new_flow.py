import pytest
import bitcoin
from subprocess import Popen, PIPE
from Configs.Constants import PBTC_ID, DAO_PRIVATE_K
from Helpers.Logging import STEP, INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT
from Objects.Portalv4Objects import PortalV4InfoBase
from TestCases.PortalV4 import TEST_SETTING_SHIELD_AMOUNT, all_users, bitcoinCLI, \
    buildProofPath, username, password, host, port, genOTMPath, MULTISIG_ADDRESS
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import PrivateKey, P2wshAddress, P2wpkhAddress, P2pkhAddress, P2shAddress
from bitcoinutils.script import Script
from multiprocessing import Lock


BTC_ADDRESS_TYPE = {"P2SH": "legacy", "P2PKH": "p2sh-segwit", "P2WSH": "bech32", "P2WPKH": "bech32"}
BTC_SHIELD = 1.575
PROOF_INVALID = "eyJNZXJrbGVQcm9vZnMiOlt7IlByb29mSGFzaCI6WzE4MiwyMzYsMTk4LDQxLDE5Myw4NCwxNjAsMTIxLDEzMiwyMjcsNTcsMTI1LDc0LDcsMTI3LDE2OSwxNDUsNzksMjA3LDIyNSwxOTIsMTE2LDE4OCwyMDMsMjQsMjAyLDE3MSwxODcsMTM1LDE5MCw2MywzMl0sIklzTGVmdCI6dHJ1ZX1dLCJCVENUeCI6eyJWZXJzaW9uIjoxLCJUeEluIjpbeyJQcmV2aW91c091dFBvaW50Ijp7Ikhhc2giOls5NiwzMywxMTIsMjgsMywxMTgsMTM1LDQwLDE5LDc3LDEsMjIzLDEwMCwxMTEsMjM4LDQzLDE2OCw4MSwxMDQsMTQwLDUyLDIxNiw2NSwxOTksODcsMjEsMjI2LDIzOCwyMzMsMTQwLDE3OSwzOF0sIkluZGV4IjowfSwiU2lnbmF0dXJlU2NyaXB0IjoiIiwiV2l0bmVzcyI6WyIiLCJNRVFDSUJHbU54WDFLUzNESWdpNUlEZkVPcmFPa1VFblR6L2F1UjdqTm51dGR4S3hBaUIzRTh0K1YwQktNNFBhTzJUemRZQXdZczh4cVp4Qk9kejE4N3lPMWJIWVRBRT0iLCJNRVFDSUZVS20yTC9WVFhnQm5POXNwazdMZkFtMmZ6WVVjL2hnMFAxUUZSdTk3Zm1BaUJNalZTOVM2cUFwM0JnRXA4aTF2czRCdFhhc1JoRGozWUZueFptaVBWQ0JnRT0iLCJNRVFDSUcrTEhHVFMvNW1PamxjWGFtdUZiZGxoWVZtdFY5VVV6S1Z5bU9TRklMYzFBaUFwcXNJeEZ2TnJQNU01Wk5hNlpTQlRKYW5KL00zNDF4Z3hHdlJsZnpSN0xnRT0iLCJVeUVETkNWT0pXNVM0R2dzOUx4TjVqNTlaNm4xSFdhTmR4czU4a3NNOVl1NDdha2hBdDFZRFZqd25lanM0TWc2RTFqaHRERWVEMG5JTEoxVm9DQUgrYzlGVUlJMklRTy9BODdLRi8waWFKdFRuSmgyMUt5b09ONkQ0ZFhtaVpIcWFranY0QTZlcHlFQ2JTWHdGZVpLNjJ4ZzdNTWdQTVAvSGxZeXhYWkdPTmpkSGZDOFU5Y3Zrdk5Vcmc9PSJdLCJTZXF1ZW5jZSI6OTY4MDAwfSx7IlByZXZpb3VzT3V0UG9pbnQiOnsiSGFzaCI6WzEzLDg2LDE2OCwxOCwxMzUsMTE0LDE5MSwzMiwxNDIsOTEsMTcxLDEyNywyNTIsMjMsMjAsMTc2LDI0NiwxNTIsMjI5LDEyMSw2NSwyNDksMTg1LDIxMyw1MiwxOTAsMjA4LDE2NSwxODksMTY5LDY3LDU0XSwiSW5kZXgiOjB9LCJTaWduYXR1cmVTY3JpcHQiOiIiLCJXaXRuZXNzIjpbIiIsIk1FVUNJUUN3MWJkamtoQ3VxMWVIZ08vRG1oQmJ1elZ0eGExK1pzK2NySlBqSlpHMy9RSWdZeXFmQW5mZzM5VGowc29zenBoUDRsZS9KOUtDMnFZb0VHQVg2Snh1ZExjQiIsIk1FVUNJUUNKc1JCRjZ3am9TdHFnUnhZYlZjcCs0ZldlVXBvdDB4RCswK1h5NlhlU2ZBSWdGdnRCeXF4NWxyV2krUnUxUTVkYS9ka2J3MldrdXZuWmszNUV5NDdqV280QiIsIk1FUUNJQTVSRUFVTHpjVW54RXNQLzdZV1Q1ZjVtSUk2bWpVV3d6b3VrSCtLY3FTTUFpQVBucFBRYktWa21URmtBYmdHRmw0Y1ZpRHdKcVpTdXdhQWIzL3BrWUpnSHdFPSIsIlV5RUR0Wm1HNGJ1V0d1RmwxV0xWSnpMdUR0ZW1tb3JHNjJxRVdEUklTRGdJcXhFaEF5ZUhLY0Q0UW5WWm5SRG5SUitQSmsrWVdwNCtpYVFmeU5TWFBsWFNMaHI0SVFMSmxvNGlIMUZJWWl6SGtuTU5wQkN2RUVkaWNRZlpQUGJaSm8yNDQ4YjIrQ0VDZXpBOS9zY2g3UE9lZlE2dURmSXc1ZzZtMVUxTGd1d1hKWnhhc1NFMTNrZFVyZz09Il0sIlNlcXVlbmNlIjo5NjgwMDB9XSwiVHhPdXQiOlt7IlZhbHVlIjo2OTAzMjAwLCJQa1NjcmlwdCI6ImRxa1VERXFpMitrWFdxTXY5OElEREd6M1RJMzJCbnFJckE9PSJ9LHsiVmFsdWUiOjY5MDMyMDAsIlBrU2NyaXB0IjoiZHFrVURFcWkyK2tYV3FNdjk4SURER3ozVEkzMkJucUlyQT09In0seyJWYWx1ZSI6NjAwMDAwMCwiUGtTY3JpcHQiOiJBQ0JLQlhhMTJaNXRhbm93K0hZRzhXTnROSHpJNWJSOS9jaDFpdlpaM3Z6L0h3PT0ifV0sIkxvY2tUaW1lIjowfSwiQmxvY2tIYXNoIjpbMTMzLDEwMiwxOTcsMjA2LDExNiwyMjAsMjM2LDE4LDE1MSwyMzAsMTg4LDc2LDIxMywxMDYsMTIzLDE3NCwxMDQsMjEsMTY5LDM1LDE5NSwyMDgsMTUyLDE1NywyMTEsNTAsMTY5LDE0LDIyMiwyMjgsMzIsODJdfQ=="

def createAndSendRawTx(accountaddress, inputs, outputs, memo):
    if memo != "":
        outputs.append({"data": memo.encode('utf-8').hex()})
    # print(outputs)
    rawtx = bitcoinCLI.createrawtransaction(inputs, outputs)
    # print('\n' + rawtx + '\n')

    # extract private key by address
    dumpprivatekey = bitcoinCLI.dumpprivkey(accountaddress)
    # print('dumpprivatekey :' + dumpprivatekey + '\n')

    # sign raw tx
    rawtxsigned = bitcoinCLI.signrawtransactionwithkey(rawtx, [dumpprivatekey])
    INFO(f"Raw transaction (HEX) = {rawtxsigned['hex']}")
    # print(rawtxsigned['hex'])

    # broadcast raw transaction
    txid = bitcoinCLI.sendrawtransaction(rawtxsigned['hex'])
    return txid


def balanceBaseInputs(inputs):
    for x in inputs:
        tx = bitcoinCLI.gettransaction(x["txid"])
        print(tx)


def setup_module():
    INFO("setup ....")


@pytest.mark.parametrize("token, shield_amount, user, payment_mode, desired_status",
                         [
                             (PBTC_ID, BTC_SHIELD, all_users[1], "P2SH", "valid"),
                             (PBTC_ID, BTC_SHIELD, all_users[1], "P2PKH", "valid"),
                             (PBTC_ID, BTC_SHIELD, all_users[1], "P2WSH", "valid"),
                             (PBTC_ID, BTC_SHIELD, all_users[1], "P2WPKH", "valid"),
                             (PBTC_ID, BTC_SHIELD, all_users[1], "P2PKH", "invalid"),# send btc to wrong address
                             (PBTC_ID, BTC_SHIELD, all_users[1], "P2SH", "MintPtokenCrossShard"),
                             # (PBTC_ID, BTC_SHIELD, all_users[1], "P2SH", "InvalidConfirmationBlock"),
                             (PBTC_ID, BTC_SHIELD, all_users[1], "P2SH", "DoubleSubmitProof"),
                             (PBTC_ID, BTC_SHIELD, all_users[1], "P2SH", "SubmitInvalidProof")

                         ])
def test_shield_new_flow(token, shield_amount, user, payment_mode, desired_status):
    STEP(0, "Preparation before test")
    # get portal state before
    lock =Lock()
    PSI_before_test = SUT().get_latest_portal_v4_state_info()
    list_output_init = PSI_before_test.get_list_utxo(token)
    total_output_amt_init = PSI_before_test.sum_output_amount_all_utxo(token)

    setup('regtest')
    # create new account for gen new block
    account = bitcoinCLI.getnewaddress("acc", BTC_ADDRESS_TYPE[payment_mode])

    # account address type = P2PKH.
    account1 = bitcoinCLI.getnewaddress("acc1", BTC_ADDRESS_TYPE[payment_mode])
    # print(account1)

    # account address type = P2WSH
    accountP2SH = bitcoinCLI.getnewaddress("acc3")
    priP2SHStr = bitcoinCLI.dumpprivkey(accountP2SH)
    priP2SHInst = PrivateKey(priP2SHStr)
    pubP2SH = priP2SHInst.get_public_key().to_hex()
    redeem_script_p2sh = Script([pubP2SH, 'OP_CHECKSIG'])
    fromAddressP2SH = P2shAddress.from_script(redeem_script_p2sh)

    # account address type = P2WSH
    accountP2WSH = bitcoinCLI.getnewaddress("acc4")
    priP2WSHStr = bitcoinCLI.dumpprivkey(accountP2WSH)
    priP2WSHInst = PrivateKey(priP2WSHStr)
    accountP2WSH2 = bitcoinCLI.getnewaddress("acc5")
    priP2WSHStr2 = bitcoinCLI.dumpprivkey(accountP2WSH2)
    priP2WSHInst2 = PrivateKey(priP2WSHStr2)
    accountP2WSH3 = bitcoinCLI.getnewaddress("acc6")
    priP2WSHStr3 = bitcoinCLI.dumpprivkey(accountP2WSH3)
    priP2WSHInst3 = PrivateKey(priP2WSHStr3)
    p2wsh_witness_script = Script(
        ['OP_2', priP2WSHInst.get_public_key().to_hex(), priP2WSHInst2.get_public_key().to_hex(),
         priP2WSHInst3.get_public_key().to_hex(), 'OP_3', 'OP_CHECKMULTISIG'])
    fromAddress = P2wshAddress.from_script(p2wsh_witness_script)

    # only for regtest
    for i in range(2):
        WAIT(2)
        bitcoinCLI.generatetoaddress(1, account)

    # send to an address
    bitcoinCLI.importaddress(fromAddress.to_string())
    bitcoinCLI.importaddress(fromAddressP2SH.to_string())

    bitcoinCLI.sendtoaddress(account1, 10)
    bitcoinCLI.sendtoaddress(fromAddressP2SH.to_string(), 10)
    bitcoinCLI.sendtoaddress(fromAddress.to_string(), 10)

    for i in range(6):
        WAIT(2)
        bitcoinCLI.generatetoaddress(1, account)

    # generater MultisigAdrress of user
    process = Popen(
        [genOTMPath, "-paymentAddr", str(user.payment_key), "-networkID", "0"],
        stdout=PIPE)
    (output, err) = process.communicate()
    user_btc_address = output.decode("utf-8").split(' ')[0]
    script_hash = output.decode("utf-8").split(' ')[1]
    pk = output.decode("utf-8").split(' ')[2]

    print("scrip_hash: " + script_hash)
    # breakpoint()
    INFO(f"MultiSigsAddress : {user_btc_address}")
    bitcoinCLI.importaddress(user_btc_address)

    lock.acquire()
    STEP(1, "Send BTC ")
    # send BTC
    to_addr = Script(
        [
            'OP_3',
            pk.split('\n')[1],
            pk.split('\n')[2],
            pk.split('\n')[3],
            pk.split('\n')[4],
            'OP_4',
            'OP_CHECKMULTISIG'
        ]
    )

    if payment_mode == "P2PKH" or payment_mode == "P2WPKH":
        listUTXOs = bitcoinCLI.listunspent(6, 9999999, [account1], True)
        inputs = []
        for x in listUTXOs:
            inputs.append({"txid": x["txid"], "vout": x["vout"]})
        # balanceBaseInputs(inputs)
        # print(inputs)
        amt_btc_shield_remain = 10 - 0.005 - BTC_SHIELD
        outputs = [{user_btc_address: BTC_SHIELD}, {account1: amt_btc_shield_remain}]
        # print(outputs)
        # memo = "PS1-" + user.payment_key
        memo = ""

        if desired_status == "invalid":
            outputs = [{MULTISIG_ADDRESS: BTC_SHIELD}, {account1: amt_btc_shield_remain}]
        btc_txid = createAndSendRawTx(account1, inputs, outputs, memo)

    elif payment_mode == "P2SH":
        print(fromAddressP2SH.to_string())
        listUTXOs = bitcoinCLI.listunspent(6, 9999999, [fromAddressP2SH.to_string()], True)
        print(listUTXOs)
        inputs = []
        for x in listUTXOs:
            inputs.append(TxInput(x["txid"], x["vout"]))
        txout = TxOutput(to_satoshis(BTC_SHIELD), to_addr.to_p2wsh_script_pub_key())
        txchange = TxOutput(to_satoshis(10 - 0.005 - BTC_SHIELD), redeem_script_p2sh.to_p2sh_script_pub_key())
        tx = Transaction(inputs, [txout, txchange])
        # print raw transaction
        print("\nRaw unsigned transaction:\n" + tx.serialize())
        # breakpoint()
        sig = priP2SHInst.sign_input(tx, 0, redeem_script_p2sh)
        # set the scriptSig (unlocking script)
        inputs[0].script_sig = Script([sig, redeem_script_p2sh.to_hex()])
        signed_tx = tx.serialize()
        # print raw signed transaction ready to be broadcasted
        print("\nRaw P2SH signed transaction:\n" + signed_tx)
        btc_txid = bitcoinCLI.sendrawtransaction(signed_tx)

    else:
        listUTXOs = bitcoinCLI.listunspent(6, 9999999, [fromAddress.to_string()], True)
        inputs = []
        for x in listUTXOs:
            inputs.append(TxInput(x["txid"], x["vout"]))
        txout = TxOutput(to_satoshis(BTC_SHIELD), to_addr.to_p2wsh_script_pub_key())
        # txout2 = TxOutput(to_satoshis(BTC_SHIELD/2), to_addr.to_p2wsh_script_pub_key())
        txchange = TxOutput(to_satoshis(10 - 0.005 - BTC_SHIELD), p2wsh_witness_script.to_p2wsh_script_pub_key())
        # tx = Transaction(inputs, [txout, txout2, txchange], has_segwit=True)
        tx = Transaction(inputs, [txout, txchange], has_segwit=True)
        # print raw transaction
        print("\nRaw P2WSH unsigned transaction:\n" + tx.serialize())
        sig1 = priP2WSHInst.sign_segwit_input(tx, 0, p2wsh_witness_script, to_satoshis(10))
        sig2 = priP2WSHInst2.sign_segwit_input(tx, 0, p2wsh_witness_script, to_satoshis(10))
        tx.witnesses.append(Script(['OP_0', sig1, sig2, p2wsh_witness_script.to_hex()]))
        signed_tx = tx.serialize()
        # print raw signed transaction ready to be broadcasted
        print("\nRaw signed transaction:\n" + signed_tx)
        btc_txid = bitcoinCLI.sendrawtransaction(signed_tx)

    for i in range(4):
        WAIT(2)
        bitcoinCLI.generatetoaddress(1, account)
    INFO(f"BTC txhash = {btc_txid}")
    lock.release()

    if desired_status == "InvalidConfirmationBlock":
        WAIT(2)
        bitcoinCLI.generatetoaddress(1, account)
    else:
        for i in range(7):
            WAIT(2)
            bitcoinCLI.generatetoaddress(1, account)
    # print(newtxid)
    # INFO(f"BTC txhash = {btc_txid}")

    STEP(2, "Submit proof to request pToken")
    bal_token_before_submit = user.get_token_balance(token)
    bal_prv_before_submit = user.get_prv_balance()

    process = Popen(
        [buildProofPath, "-txhash", btc_txid, "-username", username, "-password", password, "-host", host + ":" + port],
        stdout=PIPE)
    (output, err) = process.communicate()

    proof = output.decode("utf-8").split(' ')[2]
    INFO(f"Proof : {proof}")

    WAIT(100)
    lock.acquire()
    if desired_status == "MintPtokenCrossShard":
        shield_req = user.portal_v4_shield_req(token, DAO_PRIVATE_K, proof)
    elif desired_status == "SubmitInvalidProof":
        shield_req = user.portal_v4_shield_req(token, user.private_key, PROOF_INVALID)
    else:

        shield_req = user.portal_v4_shield_req(token, user.private_key, proof)

    assert shield_req.get_transaction_by_hash(shield_req.get_tx_id()).is_none() == False
    lock.release()

    STEP(3, "Verify balance ")
    shield_req_status = PortalV4InfoBase().get_shield_req_status(shield_req.get_tx_id(), True)
    bal_token_after_submit = user.wait_for_balance_change(token, from_balance=bal_token_before_submit, timeout=100)
    if desired_status != "MintPtokenCrossShard":
        bal_prv_after_submit = user.wait_for_balance_change(from_balance=bal_prv_before_submit, least_change_amount=-1,
                                                            timeout=200)
    if desired_status == "invalid" or desired_status == "InvalidConfirmationBlock" or desired_status == "SubmitInvalidProof":
        assert shield_req_status == 0
        assert bal_token_after_submit == bal_token_before_submit
    else:
        assert shield_req_status == 1
        assert bal_token_after_submit == bal_token_before_submit + int(BTC_SHIELD * 1e9)

    STEP(4, "Verify portal state")
    #     check UTXO update
    PSI_af_shield = SUT().get_latest_portal_v4_state_info()
    total_output_amt_af_shield = PSI_af_shield.sum_output_amount_all_utxo(token)
    if desired_status == "invalid" or desired_status == "InvalidConfirmationBlock" or desired_status == "SubmitInvalidProof":
        assert total_output_amt_init == total_output_amt_af_shield
        assert PSI_af_shield.find_utxo_by_txHash_amount(token, btc_txid, int(round(BTC_SHIELD * 1e8))) == False
    else:
        assert total_output_amt_init + int(round(BTC_SHIELD * 1e8)) == total_output_amt_af_shield
        assert PSI_af_shield.find_utxo_by_txHash_amount(token, btc_txid, int(round(BTC_SHIELD * 1e8))) == True

    if desired_status == "DoubleSubmitProof":
        STEP(5, "Test double submit proof")
        bal_token_before_double_submit = user.get_token_balance(token)
        shield_req = user.portal_v4_shield_req(token, user.private_key, proof)
        assert shield_req.get_transaction_by_hash(shield_req.get_tx_id()).is_none() == False

        STEP(5.1, "Verify balance ")
        shield_req_status = PortalV4InfoBase().get_shield_req_status(shield_req.get_tx_id(), True)
        bal_token_after_submit = user.wait_for_balance_change(token, from_balance=bal_token_before_double_submit,
                                                              timeout=50)
        assert shield_req_status == 0
        assert bal_token_after_submit == bal_token_before_double_submit

        STEP(5.2, "Verify portal state")
        #     check UTXO update
        PSI_af_shield = SUT().get_latest_portal_v4_state_info()
        total_output_amt_af_double_submit = PSI_af_shield.sum_output_amount_all_utxo(token)
        assert PSI_af_shield.find_utxo_by_txHash_amount(token, btc_txid, int(round(BTC_SHIELD * 1e8))) == True
        assert total_output_amt_af_shield == total_output_amt_af_double_submit

