import pytest

from IncognitoChain.Configs.Constants import pbnb_id, PortalRedeemStatus, PortalUnloclCollateralReqStatus
from IncognitoChain.Drivers.BnbCli import BnbCli, encode_redeem_memo, build_bnb_proof
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.PortalObjects import RedeemReqInfo, UnlockCollateralReqInfo
from IncognitoChain.TestCases.Portal import portal_user, custodian_remote_address, portal_user_remote_addr, \
    find_custodian_account_by_incognito_addr, bnb_pass_phrase, redeem_amount

token = pbnb_id


@pytest.mark.parametrize("redeem_fee,expected", [
    (None, 'valid'),  # none means auto get fee
    (1, 'invalid')
])
def test_create_redeem_req(redeem_fee, expected):
    prv_bal_be4 = portal_user.get_prv_balance()
    tok_bal_be4 = portal_user.get_token_balance(token)
    test_redeem_amount = redeem_amount
    if expected == 'invalid':
        test_redeem_amount = redeem_amount * 10

    STEP(1.1, 'Create redeem req')
    redeem_req = portal_user.req_redeem_my_token(portal_user_remote_addr, pbnb_id, test_redeem_amount,
                                                 redeem_fee=redeem_fee)
    tx_block = redeem_req.subscribe_transaction()
    redeem_fee = redeem_req.params().get_portal_redeem_fee()
    tx_fee = tx_block.get_fee()
    tx_size = tx_block.get_tx_size()
    redeem_id = redeem_req.params().get_portal_redeem_req_id()
    STEP(1.2, 'Check tx fee and redeem fee')
    assert prv_bal_be4 - redeem_fee - tx_fee == portal_user.get_prv_balance()

    INFO(f"""Porting req is created with redeem amount = {test_redeem_amount} 
                                         redeem fee = {redeem_fee},
                                         redeem id = {redeem_id}, 
                                         tx fee = {tx_fee}, 
                                         tx size = {tx_size}
                                         user token bal after req = {portal_user.get_token_balance(pbnb_id)}
                                         user prv bal after req = {portal_user.get_prv_balance()}""")

    STEP(2, "Check req status")
    redeem_info = RedeemReqInfo()
    redeem_info.get_redeem_status_by_redeem_id(redeem_id)
    if expected == 'valid':
        assert redeem_info.get_status() == PortalRedeemStatus.WAITING
    else:
        assert redeem_info.data is None

    assert prv_bal_be4 - redeem_fee - tx_fee == portal_user.get_prv_balance()

    if expected == 'valid':
        STEP(3, "Check requester bal")
        assert tok_bal_be4 - redeem_amount == portal_user.get_token_balance(token)

        bnb_cli = BnbCli()
        encoded_redeem_memo = encode_redeem_memo(redeem_id,
                                                 redeem_info.get_matching_custodians()[0].get_incognito_addr())
        STEP(4, 'Custodian send BNB to user')
        bnb_send_amount = redeem_amount // 10
        send_bnb_tx = bnb_cli.send_bnb_to(custodian_remote_address, portal_user_remote_addr, bnb_send_amount,
                                          bnb_pass_phrase, encoded_redeem_memo)
        STEP(5, 'Submit proof to request unlock collateral')
        proof = build_bnb_proof(send_bnb_tx.get_tx_hash())
        custodian = find_custodian_account_by_incognito_addr(redeem_info.get_matching_custodians()[0].get_incognito_addr())
        custodian_status = custodian.get_my_portal_custodian_status()
        locked_collateral_before = custodian_status.get_locked_collateral(pbnb_id)
        holding_token = custodian_status.get_holding_token_amount(pbnb_id)
        sum_waiting_porting_req_lock_collateral = custodian.sum_my_waiting_porting_req_locked_collateral(pbnb_id)
        sum_waiting_redeem_req_holding_tok = custodian.sum_my_waiting_redeem_req_holding_token(pbnb_id)
        estimated_unlock_collateral = redeem_amount * (
            locked_collateral_before - sum_waiting_porting_req_lock_collateral) // (
                                          holding_token + sum_waiting_redeem_req_holding_tok)
        INFO(f"""Status before req unlock collateral:
                    redeem amount     = {redeem_amount}
                    locked collateral = {locked_collateral_before}
                    holding token     = {holding_token}
                    sum waiting colla = {sum_waiting_porting_req_lock_collateral}
                    sum holding token = {sum_waiting_redeem_req_holding_tok} 
                    estimated unlock  = {estimated_unlock_collateral}""")
        unlock_collateral_tx = custodian.req_unlock_collateral(pbnb_id, redeem_amount, redeem_id, proof)
        unlock_collateral_tx.subscribe_transaction()

        unlock_collateral_req_info = UnlockCollateralReqInfo()
        unlock_collateral_req_info.get_unlock_collateral_req_stat(unlock_collateral_tx.get_tx_id())
        assert unlock_collateral_req_info.get_status() == PortalUnloclCollateralReqStatus.ACCEPTED

        STEP(6, 'Verify custodian collateral')
        custodian_status = custodian.get_my_portal_custodian_status()
        locked_collateral_after = custodian_status.get_locked_collateral(pbnb_id)
        holding_token_after = custodian_status.get_holding_token_amount(pbnb_id)

        INFO(f"""Status after req unlock collateral:
                            redeem amount     = {redeem_amount}
                            locked collateral = {locked_collateral_after}
                            holding token     = {holding_token_after}
                            unlock amount     = {unlock_collateral_req_info.get_unlock_amount()}""")
        assert locked_collateral_before - locked_collateral_after == estimated_unlock_collateral

    else:
        STEP(3, "Redeem req reject, wait 60s to return token but not tx and redeem fee. Check requester bal")
        WAIT(60)
        assert tok_bal_be4 == portal_user.get_token_balance(token)
        assert prv_bal_be4 - tx_fee - redeem_fee == portal_user.get_prv_balance()
