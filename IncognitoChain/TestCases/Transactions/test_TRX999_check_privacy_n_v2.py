import pytest

from IncognitoChain.Configs.Constants import PRV_ID
from IncognitoChain.Helpers.Logging import INFO_HEADLINE, INFO, STEP
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS


@pytest.mark.parametrize('token, account_list', [
    (PRV_ID, ACCOUNTS),
    # ('token',ACCOUNTS)
])
def test_convert_coin_to_v2(token_id, account_list):
    for account in account_list:
        custom_token_list = []
        if token_id != PRV_ID:
            STEP(0, f'Find all custom token id of this account {l6(account.payment_key)}')
            all_token = account.get_all_custom_token_balance()
            for token_bal in all_token:
                custom_token_list.append(token_bal['TokenID'])

        INFO_HEADLINE(f"Convert f{l6(token_id)} of user {l6(account.payment_key)} to v2")
        STEP(1, 'Get balance before convert')
        prv_bal_before = account.get_prv_balance()
        token_bal_before = account.get_token_balance(token_id)

        STEP(2, " Check current coin version, must be v1, otherwise, skip the test")
        if token_id == PRV_ID:
            for coin in account.list_unspent_coin():
                if coin.get_version() != 1:
                    pytest.skip(f'ver 1 coin found: {coin}')
        else:
            for coin in account.list_unspent_token():
                if coin.get_version() != 1:
                    pytest.skip(f'ver 1 coin found: {coin}')
        STEP(3, 'Convert coin to v2')
        convert_tx_list = []
        if token_id == PRV_ID:
            convert_tx = account.convert_prv_to_v2().subscribe_transaction()
            convert_tx_list.append(convert_tx)
        else:
            for token in custom_token_list:
                convert_tx = account.convert_token_to_v2(token).subscribe_transaction()
                convert_tx_list.append(convert_tx)

        convert_fee = 0
        for tx in convert_tx_list:
            convert_fee += tx.get_fee()

        STEP(4, 'Check balance after convert')
        prv_bal_after = account.get_prv_balance()
        assert prv_bal_before == prv_bal_after - convert_fee
        if token_id != PRV_ID:
            for token in custom_token_list:
                token_bal_after = account.get_token_balance(token)
                assert token_bal_before == token_bal_after

        STEP(5, 'Check coin version after convert')
        if token_id == PRV_ID:
            for coin in account.list_unspent_coin():
                assert coin.get_version() == 2, f'ver 1 coin found after convert: {coin}'
        else:
            for coin in account.list_unspent_token():
                assert coin.get_version() == 2, f'ver 1 coin found after convert: {coin}'

        STEP(6, 'Convert again, must fail')
        if token_id == PRV_ID:
            convert_tx = account.convert_prv_to_v2()
            convert_tx.expect_error()
            assert convert_tx.get_error_msg() == 'Can not create tx'
            assert 'Have switched all coins ver 1, there is no coins ver 1 left' in \
                   convert_tx.get_error_trace().get_message()
        else:
            for token in custom_token_list:
                convert_tx = account.convert_token_to_v2(token).subscribe_transaction()
                assert convert_tx.get_error_msg() == 'Can not create tx'
                assert 'Have switched all coins ver 1, there is no coins ver 1 left' in \
                       convert_tx.get_error_trace().get_message()


def test_check_all_coin_v2():
    for acc in ACCOUNTS:
        INFO_HEADLINE(f'Checking all coin and token of {l6(acc.payment_key)}')
        for coin in acc.list_unspent_coin():
            INFO(f'coin: {coin}')
            assert coin.get_version() == 2, 'Coin is not v2'

        for tok in acc.list_unspent_token():
            INFO(f'token: {tok}')
            assert tok.get_version() == 2, 'Tok is not v2'
