from Objects import BlockChainInfoBaseClass


class ShardBlock(BlockChainInfoBaseClass):
    """
 
        {
            "Hash": "4b4133fad60b071652c447d6bc7db0ea8be073d54c9cb7d1130acbf58b1211b0",
            "ShardID": 0,
            "Height": 7120,
            "Confirmations": 1,
            "Version": 6,
            "TxRoot": "0000000000000000000000000000000000000000000000000000000000000000",
            "Time": 1637037600,
            "PreviousBlockHash": "30c61196305404e68411a05f24be251bdaa0e4618a6056a55817e19c9f857b17",
            "NextBlockHash": "",
            "TxHashes": [],
            "Txs": null,
            "BlockProducer": "121VhftSAygpEJZ6i9jGkKZixz3MxWLn8H4bq6g9i1dxGkbJYni7TgHu4rrmzdnrzNeudRBVepuX66NTNzBP1vxjtVuFAYT7BkCkzKceR9CpQnYs2zJpZNhLeufPBFSpdYz397T2LQHnFAQit44f961H8z1LBbA5t8SEe9rs6GSf57iSkaDer752nZfKyn6arudjiDnzgMgi3uPh62wewSnJtZ71RXukKiYVFjAy9MCeAwHTfAzY28Fc7o4VnA185H9QDZSdY8b4pHDbk6Bx8dsMcFsVwDHv7kzWbprajj8KBqKm24SmjUCLm8HJ3BNuLUwtcd3vPZb1s5BavkK2LGbogWJW9PkrUwyBuffb9U11ziqEpBR92EfdfWJ9GwpsLqgx1KvirvAVZkzEswSf3vuBRe9QLWAXzP3Kq8BgpNJXVBMd",
            "ValidationData": "{\"ProducerBLSSig\":\"6f6HkOqGRXbA9CbRUWm1I3HWPVRPG8ZicwZtkEyb/Cg1VhZcAXtN6t7CkqYzR2ujbAsB5B7kYdaO9PjkBfo9DAE=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],\"AggSig\":\"JC+8IxH7eQ/ETMyVQIicQGI6vHNacV6kz3LBaNcmhOs=\",\"BridgeSig\":[\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\"],\"PortalSig\":null}",
            "ConsensusType": "",
            "Data": "",
            "BeaconHeight": 7195,
            "BeaconBlockHash": "ee9371210c74d85573db521c85724c5854d8ca3917240d0e931ae1e074ba3cdb",
            "Round": 1,
            "Epoch": 360,
            "Reward": 0,
            "RewardBeacon": 0,
            "Fee": 0,
            "Size": 0,
            "CommitteeFromBlock": "875995dc4fd95a8c36b6b5652d62d33e790033de027343971ea3983247b34acd",
            "Instruction": [],
            "CrossShardBitMap": [],
            "ProposeTime": 1637037780,
            "Proposer": "121VhftSAygpEJZ6i9jGkMtdVkuSDwxaYnUsHEnjbJBckPp1XrTBEyVHnx66bGCZiXesZMcZBxQD2fqaeWPZuTLw4Av7wrTeSnNLg8ErTbhFfhJD5nrTSCdCbnLbmybQiVYtUGcgMtRmnxAriaVL5dEBNkvNuUoxVzKXSSitnRAFQfA4BpPX1S8vR7zWtJP77CsYo47tnvcu8jSCEtjwEjGNeuNZPSzfnqBRyztYP1sMDgBvvJxUvMm8nTAxMm6YYVabVEdPBkJE89ZN5ZB7NE3SLxB4exqVKrcEoXVwGgJkWwdLaiQxFrDVgP2gi4RjGKpyrhvNCjjyU63Kp5aBFRcb8epkrByBERwDib6yeHmTZ22qFDQmsrdpVPGeafBvhuhNghKv9impjsbpBusu6BiEcSC7H5CEz9XzrGBWgDxvK9VC",
            "SubsetID": 0,
            "SigningCommittee": null,
            "FinalityHeight": 0
        }
    """

    def get_block_hash(self):
        return self.dict_data['Hash']

    def shard_id(self):
        return self.dict_data['ShardID']

    def get_height(self):
        return self.dict_data['Height']

    def get_confirmations(self):
        return self.dict_data['Confirmations']

    def get_version(self):
        return self.dict_data['Version']

    def get_tx_root(self):
        return self.dict_data['TxRoot']

    def get_time(self):
        return self.dict_data['Time']

    def get_previous_block_hash(self):
        return self.dict_data['PreviousBlockHash']

    def get_next_block_hash(self):
        return self.dict_data['NextBlockHash']

    def get_tx_hashes(self):
        return self.dict_data['TxHashes']

    def get_txs(self):
        return self.dict_data['Txs']

    def get_block_producer(self):
        return self.dict_data['BlockProducer']

    def get_validation_data(self):
        return self.dict_data['ValidationData']

    def get_consensus_type(self):
        return self.dict_data['ConsensusType']

    def get_data(self):
        return self.dict_data['Data']

    def get_beacon_height(self):
        return self.dict_data['BeaconHeight']

    def get_beacon_block_hash(self):
        return self.dict_data['BeaconBlockHash']

    def get_round(self):
        return self.dict_data['Round']

    def get_epoch(self):
        return self.dict_data['Epoch']

    def get_reward(self):
        return self.dict_data['Reward']

    def get_reward_beacon(self):
        return self.dict_data['RewardBeacon']

    def get_fee(self):
        return self.dict_data['Fee']

    def get_size(self):
        return self.dict_data['Size']

    def get_instruction(self):
        # todo: need clarification
        return self.dict_data['Instruction']

    def get_cross_shard_bitmap(self):
        # todo: need clarification
        return self.dict_data['CrossShardBitMap']

    def get_propose_time(self):
        return self.dict_data['ProposeTime']

    def get_proposer(self):
        return self.dict_data['Proposer']

    def get_subset_id(self):
        return self.dict_data['SubsetID']

    def get_signing_committee(self):
        return self.dict_data['SigningCommittee']

    def get_finality_height(self):
        return self.dict_data['FinalityHeight']
