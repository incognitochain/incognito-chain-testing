from Helpers.KeyListJson import KeyListJson
from Objects.AccountObject import Account

key_list_file = KeyListJson()

account_list = [
    Account(
        '113eynEFtvRbNjpNm4EspqjjXabHVJqSucsvmCBn8K7dpPtHifmc9CCaFkXkDYjRUZKoAqiJBAySM24DB4UtBZ7mbYmXt5F8kf36yZ92nA6f'),
    Account(
        '113Y9qGr5qnpjr8eQ7rR7sLxtt172VLReupx4ywUXcUpJB2CqxhJg4Bq48GanxVL58sXi1Qu7jEDghwxq4yyXT2847J5BRvK1JJ6uA1V4Gdk'),
    Account(
        '113VQvd48jDrSroFS1a7ny1ZFgzuXPP7B8oTcdqeJfdVfQ9ZMFF7aLcMdMLLy8pCB8S9xQigXe56UMh43ZpMjFdApy6A9iKdm4T7XVHE3iJU'),
    Account(
        '113e7krzDoXBy8HP7gYTooCEQjZwTCD8w5o4VL3G5rZMQXugt4vP2nP8sAJbQEhaL6Y8p24GiC7V6JDgQw7K4XSqhrKdiGEcCWnAJqJqmUcX'),
    Account(
        '113jSHZo3pTU5YXj7KPv5QVnSe798kkeMM9i3JVqxsuStJHJupHQ1eGhiPsyKj6iDiRdArt9acBfkM1r4kG1EcJ892WvrDXcTyBX7VybsEwy'),
    Account(
        '113STxbkyK8MMcfuhj1cVaq8ysBPyZ1NcGir3k2eMTSLvdj78YMMsfyY3db2r7zjjyJ37n99dSWFTppyMPdFM25HsirpAabA34kGMT24394y'),
    Account(
        '1136vNE33gGfYA6EizeFJzayaNuCyjHZVF4yBaGjZZLqyTmcg7qy2xkQ9RKVpc82UTQDcMwCzNixkG1chFM1vkwEzWQv7YvHJG6RSvz8tKdy'),
    Account(
        '113AkECram2PDU7draKuM8Fc37AsSBb7AB8SAhwyWbjYWtsSHCByN6b3n5itSfGtJkBKSre625xGadp7NEpSZ1WHnKTfnxhcGD2sTWMRu77j')
]

beacons = key_list_file.get_beacon_accounts().account_list

# committees = key_list_file.get_shard_fix_validator_accounts().account_list

stakers = key_list_file.get_staker_accounts().account_list