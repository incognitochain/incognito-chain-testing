from IncognitoChain.Helpers.Logging import WARNING
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Objects import BlockChainInfoBaseClass


class Coin(BlockChainInfoBaseClass):
    """
    sample:
        {
            "PublicKey": "1oQKfimdKiDzfhD5qLA1L2AJbemf98ptG2fBvefjdZSnQvN53j",
            "CoinCommitment": "1Q6fdoVgt41ghd4nZfWnEHjqiArFwTdcSbwEAsPZSNj1q7Cgbj",
            "SNDerivator": "1dBfNj4W8rp9VCaa1uXEuF8tGySA5vDdt6qPzSiaZ7d8J61ZC3",
            "SerialNumber": "12goiYnQ9Xp98nVrKFUSSxNy3x2acoRnBviacMjCo57ZeLtkkaZ",
            "Randomness": "12oodDDkWsR1BAFHYz3sx1mAaEjdPcFabmE5pTHheyUbCxawh4G",
            "Value": "1000",
            "Info": "13PMpZ4",
            "CoinDetailsEncrypted": "13PMpZ4"
        }
    """

    def __str__(self):
        serial_num = l6(str(self.get_serial_num()))
        k_image = l6(str(self.get_key_image()))
        ver = f'v{self.get_version()}'
        value = self.get_value()
        return "%6s : %6s : %2s : %s" % (serial_num, k_image, ver, value)

    def get_index(self):
        try:  # new
            return self.data['Index']
        except KeyError:  # old coin has no index
            return None

    def get_public_key(self):
        return self.data['PublicKey']

    def get_commitment(self):
        try:
            return self.data['CoinCommitment']
        except KeyError:
            return self.data['Commitment']

    def get_serial_num(self):
        try:  # old
            return self.data['SerialNumber']
        except:  # new coin's SN is now key image
            return None

    def get_serial_num_derivator(self):
        return self.data['SNDerivator']

    def get_randomness(self):
        return self.data['Randomness']

    def get_value(self):
        return self.data['Value']

    def get_info(self):
        return self.data['Info']

    def get_detail_encrypted(self):
        try:  # old
            return self.data['CoinDetailsEncrypted']
        except KeyError:  # new
            return None

    def get_key_image(self):
        try:  # new
            return self.data['KeyImage']
        except KeyError:  # old
            return None

    def get_version(self):
        try:
            return self.data['Version']
        except KeyError:
            WARNING('Error while get coin version. Assume ver=1')
            return 1
