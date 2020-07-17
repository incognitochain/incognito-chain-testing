from IncognitoChain.Configs.Constants import coin
from IncognitoChain.Helpers.Time import get_current_date_time
from IncognitoChain.Objects.AccountObject import Account
from IncognitoChain.Objects.IncognitoTestCase import COIN_MASTER
from IncognitoChain.TestCases.Transactions import test_TRX008_init_contribute_send_custom_token as trx008

# contributor = ACCOUNTS[0]
token_owner = Account(
    '112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA',
    '12RxERBySmquLtM1R1Dk2s7J4LyPxqHxcZ956kupQX3FPhVo2KtoUYJWKet2nWqWqSh3asWmgGTYsvz3jX73HqD8Jr2LwhjhJfpG756')

# when token_id set to none, init new token and use it for the test
# otherwise, use token id for the test without initializing new token
# token_id = "a4442a68070fc615abee5e8c665808ebc1c670e5fd16f49ca8e992bf7c126739"
# token_id_1 = "0a35aa083cfdda82dcc07558fe128b6b835e764100d185dda3c4aef66283a1eb"  # testnet
# token_id_2 = "60e44a298d2b3f32629b7b8fc9f7ac05fd24158105af176038168875e7ea0006"  # testnet
token_id_1 = "4129f4ca2b2eba286a3bd1b96716d64e0bc02bd2cc1837776b66f67eb5797d79"  # testnet
token_id_2 = "57f634b0d50e0ca8fb11c2d2f2989953e313b6b6c5c3393984adf13b26562f2b"  # testnet
# token_id_1 = None
# token_id_2 = None

need_withdraw_contribution_1 = False
need_withdraw_contribution_2 = False

COIN_MASTER.top_him_up_prv_to_amount_if(coin(10000), coin(100000), token_owner)

if token_id_1 is None:
    trx008.account_init = token_owner
    trx008.test_init_ptoken()
    token_id_1 = trx008.custom_token_id
    need_withdraw_contribution_1 = True

if token_id_2 is None:
    trx008.custom_token_symbol = get_current_date_time()
    trx008.account_init = token_owner
    trx008.test_init_ptoken()
    token_id_2 = trx008.custom_token_id
    need_withdraw_contribution_2 = True

acc_list_1_shard = [
    Account(
        "112t8rnYwrzsk7bQgYM6duFMfQsHDvoF3bLLEXQGSXayLzFhH2MDyHRFpYenM9qaPXRFcwVK2b7jFG8WHLgYamaqG8PzAJuC7sqhSw2RzaKx",
        "12RxdaQkg3HzYAzfWb53osy9pbyHVqTd5m1hN6eghfjAXLwpy2m3QgGBRWVnmhH6sq1YScnYLC9aESWitaLTw9TNsJkhXiv88CAn6kf"),
    Account(
        "112t8rneWAhErTC8YUFTnfcKHvB1x6uAVdehy1S8GP2psgqDxK3RHouUcd69fz88oAL9XuMyQ8mBY5FmmGJdcyrpwXjWBXRpoWwgJXjsxi4j",
        "12Rx2NqWi5uEmMrT3fRVjhosBoGpjAQ9yxFmHckxZjyekU9YPdN622iVrwL3NwERvepotM6TDxPUo2SV4iDpW3NUukxeNCwJb2QTN9H"),
    Account(
        "112t8rni5FF2cEVMZmmCzpnr4QuFnUvYymbkjk3LGp5GJs8c8wTMURmJbZGx8WgwkPodtwGr34Vu8KZat7gxZmSXu5h9LDuppnyzcEXSgKff",
        "12Rvic7Pnf1d12ZB2hnYwGV6W9RLfHpkaSt2N5Xr5up8Hj93s2z8SQKRqQZ6ye2tFD2WKy28XTSQ1w9wiYN8RZtFbPipjxSUycJvbPT"),
    Account(
        "112t8rnqawFcfb4TCLwvSMgza64EuC4HMPUnwrqG1wn1UFpyyuCBcGPMcuT7vxfFCehzpj3jexavU33qUUJcdSyz321b27JFZFj6smyyQRza",
        "12S2DUBWE3shx2o5d14Nr9DVM6eocQMjbJZMrT9YXfbNwhg3sejnP1tqhaW8SrJ881Zo3vgdVPUf56WXrYnMjBRmeKWPKFiJKcoviUA"),
    Account(
        "112t8rnr8swHUPwFhhw8THdVtXLZqo1AqnoKrg1YFpTYr7k7xyKS46jiquN32nDFMNG85cEoew8eCpFNxUw4VB8ifQhFnZSvqpcyXS7jg3NP",
        "12S2ZZxMFr6kzDBd5jKWtAYsm47tbRDvRWC1RYTHZeXsG49JNMSsX4jSVYRTvfpTi11XPxqjmauRUX5myddMTwKuNZZw3CrsYUa82tc"),
    Account(
        "112t8rnuHvmcktny3u5p8WfgjPo7PEMHrWppz1y9verdCuMEL4D5esMsR5LUJeB5A4oR9u5SeTpkNocE4CE8NedJjbp3xBeZGLn7yMqS1ZQJ",
        "12Rr9rsUiXbG3JgdJNeFtLjGhYEWPaEpzvV5YDSzst7sU3sxgMaXBY5uWbRXGRLYGDTrzZ9KEcbNYZT8SHMErDkm6h6PcJrKdBC4tye"),
    Account(
        "112t8rnxntm4qcc1kNxqQJEpz4DskFKXojYxaGVT3h7c7QjbWpgiVRv2qmLjQMUW8QxUm7HiyxqdQ35fdcAQ7SZ3cYmDADGfFkcENH6Pi8GH",
        "12S4kCdFmeW78Rxi2RrdgQqwDrKjkCXX6LeQpES1EVRCwfsTqefPDvSV9oi1DwvERvwRvCGFbgvbqbfusCN29HN5rukngGkp7U5EVHF"),
    Account(
        "112t8rnzyZWHhboZMZYMmeMGj1nDuVNkXB3FzwpPbhnNbWcSrbytAeYjDdNLfLSJhauvzYLWM2DQkWW2hJ14BGvmFfH1iDFAxgc4ywU6qMqW",
        "12RwumVV4Q84rKknv24yATBeQmu9rtEMro91BuKhLnpnRsR1iaXBRtrWJZ6Mg2rFCfauvNvhjkhVKbYJYMW6bQAWbAj11UTo2Dy3XeT"),
    Account(
        "112t8ro1aB8Hno84bCGkoPv4fSgdnjghbd5xHg7NmriQGexqy6J7jKL3iDWAEytKwpH6U85MkAaZmEGcV3uBH8kZiUcBHpc1CpskuwyqZNU4",
        "12RqFNrzjApKLSxg786YmRQwq46LqbJKpPbLXUZTH7rbzxJ55nyiPWFEQbg6ZGjWmefNo3rp8LSLe8JTRw17vc3NszuJSkHg4Mm54xU"),
    Account(
        "112t8ro3VxLStVFoFiZ2Grose15tyCXCbc9VR2YtHbZCd2GZQPYBMafmXws2DDNd8VKQqKhvw6wW51xyxvrTzLE5prRAjcWJiDWiU4EL3TUT",
        "12Rrz9C7QcD3x5sCyp8o9a3nc3HCPasqtWJZnsb5B5wiaDx38rE7Je2oJdWr1DQMjiPrN8GG1ZHqxVNydL8RCqf4FRdzMzfJoBf5NKz"),
]

acc_list_n_shard = [
    Account(
        "112t8rnakdKxvk7VMKUB9qmsPY4czwnP24b82BnepcxHLX6kJ1dYQsR8d6xNTzwC9nEhJdocr9u19NAr4iSYXCeTBRu3YET8iADMAP3szdfw",
        "12RxnTs5KqyQUzGF4R2w68j3biJD29iDsFiVgC4GRy5X85anUrq1rg8P4aUyDRuS5desg9WANRptifcissMBPETyMeBE8KEh7LmQ6m7"),
    Account(
        "112t8rnbTkezohA4GLeUDpLFnuDbFvPcoCS1MxctvEu3rmUkvmoWJ37MnXDSscpVy6bKfSwjWigi9L3qhcUFo8yZLLsgPvYAn9fs1E62qNPS",
        "12Rv7iLGR4m2116m6X44yyY531WQ4j7Eroxnkv2CZKHeieDtmHUEeerq9RkPkvb8N4S3NxcBdJPDe4jHKeapzTxSVpRcGGK7NPUc1eF"),
    Account(
        "112t8rnjzNW1iKLjpNW9oJoD38pnVVgCiZWRuqGmMvcEgZEHjtg4tLRTAcfTCxNXrdzKcEmY9JVfX2Wb3JLaCjfRDEyGhXGK67VB297mZuwH",
        "12Rryj5pw8jmf6Pxs4FFxWs6YW8eBbJd1m2vGiFaguyH9rSQwuqeTqvDuUrReNSVd2w6mfr1SrCZYocU1Wrh9xhWS9rXEYGWuDz2VAp"),
    Account(
        "112t8rnmcQXPkPG3nHhhmLjKeqZEjBHcFCSxBdwRy2L6nGXBwKopc5PYWPVXu14xmec34LXxu5JJcf3N6wUfsbbNWKVotAMNrswhE6adbBmu",
        "12S1hPUUsFFsWswuCUk8uMh5b4WHXzycsQWPVgqenJChvCTKSUyevZn8Fu3b9w6HoZYyi5UxgWdQuEER1adxW5xeDxbnc5sQzCZu2my"),
    Account(
        "112t8rns2sxbuHFAAhtMksGhK9S1mFcyiGpKypzJuXJSmHZE8d4SqM3XNSy6i9QacqTeVmrneuEmNzF1kcwAvvf6d137PVJun1qnsxKr1gW6",
        "12RsetaMufaKaYpg7zJ3CL82n7Nhg9q4nRWNu4YHFms3BFVM2Ghm6jWfCJbYM1JV1aqDjBFCQFdL3MYQhX3xhETohBjcH2xjkyRBGi7"),
    Account(
        "112t8rnuHvmcktny3u5p8WfgjPo7PEMHrWppz1y9verdCuMEL4D5esMsR5LUJeB5A4oR9u5SeTpkNocE4CE8NedJjbp3xBeZGLn7yMqS1ZQJ",
        "12Rr9rsUiXbG3JgdJNeFtLjGhYEWPaEpzvV5YDSzst7sU3sxgMaXBY5uWbRXGRLYGDTrzZ9KEcbNYZT8SHMErDkm6h6PcJrKdBC4tye"),
    Account(
        "112t8rnxntm4qcc1kNxqQJEpz4DskFKXojYxaGVT3h7c7QjbWpgiVRv2qmLjQMUW8QxUm7HiyxqdQ35fdcAQ7SZ3cYmDADGfFkcENH6Pi8GH",
        "12S4kCdFmeW78Rxi2RrdgQqwDrKjkCXX6LeQpES1EVRCwfsTqefPDvSV9oi1DwvERvwRvCGFbgvbqbfusCN29HN5rukngGkp7U5EVHF"),
    Account(
        "112t8rnzyZWHhboZMZYMmeMGj1nDuVNkXB3FzwpPbhnNbWcSrbytAeYjDdNLfLSJhauvzYLWM2DQkWW2hJ14BGvmFfH1iDFAxgc4ywU6qMqW",
        "12RwumVV4Q84rKknv24yATBeQmu9rtEMro91BuKhLnpnRsR1iaXBRtrWJZ6Mg2rFCfauvNvhjkhVKbYJYMW6bQAWbAj11UTo2Dy3XeT"),
    Account(
        "112t8ro1aB8Hno84bCGkoPv4fSgdnjghbd5xHg7NmriQGexqy6J7jKL3iDWAEytKwpH6U85MkAaZmEGcV3uBH8kZiUcBHpc1CpskuwyqZNU4",
        "12RqFNrzjApKLSxg786YmRQwq46LqbJKpPbLXUZTH7rbzxJ55nyiPWFEQbg6ZGjWmefNo3rp8LSLe8JTRw17vc3NszuJSkHg4Mm54xU"),
    Account(
        "112t8ro3VxLStVFoFiZ2Grose15tyCXCbc9VR2YtHbZCd2GZQPYBMafmXws2DDNd8VKQqKhvw6wW51xyxvrTzLE5prRAjcWJiDWiU4EL3TUT",
        "12Rrz9C7QcD3x5sCyp8o9a3nc3HCPasqtWJZnsb5B5wiaDx38rE7Je2oJdWr1DQMjiPrN8GG1ZHqxVNydL8RCqf4FRdzMzfJoBf5NKz"),
]


def teardown_module():
    if need_withdraw_contribution_1:
        trx008.custom_token_id = token_id_1
        trx008.teardown_module()
    if need_withdraw_contribution_2:
        trx008.custom_token_id = token_id_2
        trx008.teardown_module()
