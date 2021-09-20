from Objects import BlockChainInfoBaseClass


class ShardBlock(BlockChainInfoBaseClass):
    """
 
        {
            "Hash": "f6726b044a29889cc8af051b647e18f9d71348487fcd580f123efff022920978",
            "ShardID": 0,
            "Height": 12806,
            "Confirmations": 708478,
            "Version": 1,
            "TxRoot": "0000000000000000000000000000000000000000000000000000000000000000",
            "Time": 1597251202,
            "PreviousBlockHash": "f2fad164d814015df3eb9499970435140c4df78bbe33849be7b9470307bb35b4",
            "NextBlockHash": "68603b961149bd06cc7e759e7789dbcfe6b493a3448c3ccd38dc93d6d8d2e3e4",
            "TxHashes": [],
            "Txs": null,
            "BlockProducer": "",
            "ValidationData": "{\"ProducerBLSSig\":\"8G6nYn/B5RLUrZJu8nAeZVQMN5npxiqRBhgNn7kPWV1tklnT7ltccW0q5xmlWSmJ7cFnJq0JLflnq5K69o3uYwA=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[0,1,2,3],\"AggSig\":\"nzKsuht7D+pmlSbDLxDTDrjwmvfhsdpafdAzQGdiAEE=\",\"BridgeSig\":[\"\",\"\",\"\",\"\"]}",
            "ConsensusType": "",
            "Data": "",
            "BeaconHeight": 12802,
            "BeaconBlockHash": "0e2ceb473f27625c2507ce30b0d5cebe6221d4cb702f8ab491c463b222515366",
            "Round": 1,
            "Epoch": 129,
            "Reward": 0,
            "RewardBeacon": 0,
            "Fee": 0,
            "Size": 0,
            "Instruction": [],
            "CrossShardBitMap": []
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
