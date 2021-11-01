from Configs.Constants import coin
from Objects.IncognitoTestCase import ACCOUNTS

# declaration
TOKEN_OWNER = ACCOUNTS[0]
INIT_PAIR_IDS = ['0000000000000000000000000000000000000000000000000000000000000004-'
                 'afdfa234db3c777f22143efe81f67de404285153995bd081ea07a8a811c98b95-'
                 '1d9ab7e48e6ccb4102b5f2badb10eda8344c59f2a884f0405b7efce6b89d5d9e',

                 '5f2372bba385631c1a2198085fced693d629403279459121b422bb480a7935ee-'
                 'afdfa234db3c777f22143efe81f67de404285153995bd081ea07a8a811c98b95-'
                 '4c92663de9f902003cc9f06b23345ae83675d49612f7e7428baab6a7de9ed71e']
TOKEN_X = "afdfa234db3c777f22143efe81f67de404285153995bd081ea07a8a811c98b95"
TOKEN_Y = "5f2372bba385631c1a2198085fced693d629403279459121b422bb480a7935ee"

# ---------------------------- SET UP -------------------------------
ACCOUNTS.pde3_get_nft_ids()
ACCOUNTS.pde3_mint_nft()

# Mint new ptoken if needed
__token_amount = coin(10000000)  # 10 mil
__token_list = [TOKEN_X, TOKEN_Y]
for token in __token_list:
    if TOKEN_OWNER.get_balance(token) < __token_amount / 100:
        tx_init = TOKEN_OWNER.init_custom_token_new_flow(__token_amount)
        __token_list[__token_list.index(token)] = tx_init.get_token_id()
        tx_init.get_transaction_by_hash()
        TOKEN_OWNER.wait_for_balance_change(token, 0)

TOKEN_X, TOKEN_Y = __token_list
print(f"""   !!! Using tokens: 
    {TOKEN_X}
    {TOKEN_Y}""")

TOKEN_OWNER.top_up_if_lower_than(ACCOUNTS, coin(1000), coin(5000), TOKEN_X)
TOKEN_OWNER.top_up_if_lower_than(ACCOUNTS, coin(1000), coin(5000), TOKEN_Y)
