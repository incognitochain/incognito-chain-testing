from IncognitoChain.Helpers.Logging import INFO_HEADLINE, INFO
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS


def test_check_all_coin_v2():
    for acc in ACCOUNTS:
        INFO_HEADLINE(f'Checking all coin and token of {l6(acc.payment_key)}')
        for coin in acc.list_unspent_coin():
            INFO(f'coin: {coin}')
            assert coin.get_version() == 2, 'Coin is not v2'

        for tok in acc.list_unspent_token():
            INFO(f'token: {tok}')
            assert tok.get_version() == 2, 'Tok is not v2'
