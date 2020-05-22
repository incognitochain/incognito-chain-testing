import pytest

from IncognitoChain.Configs.Constants import pbnb_id, PortalPortingStatusByPortingId, PortalPortingStatusByTxId, \
    PortalPtokenReqStatus
from IncognitoChain.Drivers.BnbCli import BnbCli, encode_porting_memo, build_bnb_proof
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.PortalObjects import PortingReqInfo, PTokenReqInfo
from IncognitoChain.TestCases.Portal import portal_user, porting_amount, portal_user_remote_addr, bnb_pass_phrase


@pytest.mark.parametrize("porting_fee,expected", [
    (None, "valid"),
    (1, "invalid")
])
def test_create_porting_request(porting_fee, expected):
    prv_bal_be4 = portal_user.get_prv_balance()
    tok_bal_be4 = portal_user.get_token_balance(pbnb_id)

    STEP(1, f"Create a {expected} porting request")
    porting_req = portal_user.create_porting_request(pbnb_id, porting_amount, porting_fee=porting_fee)
    porting_id = porting_req.params().get_portal_register_id()
    porting_fee = porting_req.params().get_portal_porting_fee()
    tx_block = porting_req.subscribe_transaction()
    tx_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    tx_id = porting_req.get_tx_id()
    INFO(f"""Porting req is created with porting fee = {porting_fee},
                                         porting id = {porting_id}, 
                                         tx fee = {tx_fee}, 
                                         tx size = {tx_size}
                                         prv bal after req = {portal_user.get_prv_balance()}""")

    STEP(2, "Check req status")
    porting_req_info = PortingReqInfo()
    porting_req_info.get_porting_req_by_tx_id(tx_id)

    if expected == 'valid':
        assert porting_req_info.get_status() == PortalPortingStatusByTxId.ACCEPTED

        porting_req_info.get_porting_req_by_porting_id(porting_id)
        assert porting_req_info.get_status() == PortalPortingStatusByPortingId.WAITING
    else:
        assert porting_req_info.get_status() == PortalPortingStatusByTxId.REJECTED

    STEP(3, 'Verify balance')
    assert prv_bal_be4 - porting_fee - tx_fee == portal_user.get_prv_balance()

    if expected == 'valid':
        STEP(4, 'Send BNB to custodian')
        memo_encoded = encode_porting_memo(porting_req_info.get_porting_id())
        custodian = porting_req_info.get_custodians()[0]
        bnb_cli = BnbCli()
        bnb_send_amount = porting_amount // 10
        bnb_send_tx = bnb_cli.send_bnb_to(portal_user_remote_addr, custodian.get_remote_address(),
                                          bnb_send_amount, bnb_pass_phrase, memo_encoded)

        STEP(5, 'Submit proof to request ported token')
        balance_before_req = portal_user.get_token_balance(pbnb_id)
        proof = build_bnb_proof(bnb_send_tx.get_tx_hash())
        req_tx = portal_user.req_ported_ptoken(porting_id, pbnb_id, porting_amount, proof)
        req_tx.subscribe_transaction()
        token_req_info = PTokenReqInfo(req_tx.get_result())
        ported_token_req = token_req_info.get_ptoken_req_by_tx_id(req_tx.get_tx_id())
        ported_token_req_status = ported_token_req.get_status()
        assert ported_token_req_status == PortalPtokenReqStatus.ACCEPTED, \
            f'Req for ported token is rejected. CODE = {ported_token_req_status}'

        STEP(6, 'Verify user balance')
        balance_after_req = portal_user.wait_for_balance_change(pbnb_id, balance_before_req)
        assert balance_after_req == balance_before_req + porting_amount
    else:
        STEP(4, "Porting req fail, wait 60s to return porting fee (only take tx fee), verify user balance")
        WAIT(60)
        assert portal_user.get_prv_balance() == prv_bal_be4 - tx_fee
