from Configs.Constants import coin
from Objects.IncognitoTestCase import ACCOUNTS

# declaration
test_pair = '4a380dd28b431f320f062f9ea7cd6942a700feb4c98553987f7a6b9ea48774d8-' \
            '634d4c6591c79f029b261c3663af77efc5ee60fcc4b6a0d7823a114180ea2e1f-' \
            'd19ed28ae13d6ec46004a0bfe654518331e667ea7865c986a7dae7388dcfae9d'
TOKEN_OWNER = ACCOUNTS[0]
# INIT_PAIR_IDS = []
INIT_PAIR_IDS = [test_pair]
POOL_X0 = 0
POOL_Y0 = 0
TOKEN_X = "634d4c6591c79f029b261c3663af77efc5ee60fcc4b6a0d7823a114180ea2e1f"
TOKEN_Y = "4a380dd28b431f320f062f9ea7cd6942a700feb4c98553987f7a6b9ea48774d8"

# ---------------------------- SET UP -------------------------------
ACCOUNTS.pde3_get_nft_ids()
ACCOUNTS.pde3_mint_nft()
# setup new token, un-comment to create new tokens
tx_init_x = TOKEN_OWNER.init_custom_token_new_flow(coin(10000000))
TOKEN_X = tx_init_x.get_token_id()
tx_init_x.get_transaction_by_hash()
tx_init_y = TOKEN_OWNER.init_custom_token_new_flow(coin(10000000))
TOKEN_Y = tx_init_y.get_token_id()
tx_init_y.get_transaction_by_hash()
TOKEN_OWNER.wait_for_balance_change(TOKEN_X, 0)
TOKEN_OWNER.wait_for_balance_change(TOKEN_Y, 0)

print(f"""   !!! Using tokens: 
    {TOKEN_X}
    {TOKEN_Y}""")

TOKEN_OWNER.top_up_if_lower_than(ACCOUNTS, coin(1000), coin(5000), TOKEN_X)
TOKEN_OWNER.top_up_if_lower_than(ACCOUNTS, coin(1000), coin(5000), TOKEN_Y)
