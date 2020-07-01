from IncognitoChain.Objects import BlockChainInfoBaseClass


class BlockChainCore(BlockChainInfoBaseClass):
    def get_chain_name(self):
        return self.data['ChainName']

    def get_best_blocks_raw(self):
        return self.data['BestBlocks']

    def get_beacon_block(self):
        return BlockChainBlock(self.get_best_blocks_raw()['-1'])

    def get_shard_block(self, shard_num):
        return BlockChainBlock(self.get_best_blocks_raw()[str(shard_num)])


class BlockChainBlock(BlockChainInfoBaseClass):
    def get_height(self):
        return self.data['Height']

    def get_hash(self):
        return self.data['Hash']

    def total_txs(self):
        return self.data['TotalTxs']

    def get_block_producer(self):
        return self.data['BlockProducer']

    def get_validation_data(self):
        return self.data['ValidationData']

    def get_epoch(self):
        return self.data['Epoch']

    def get_time(self):
        return self.data['Time']

    def get_remaining_block_epoch(self):
        return self.data['RemainingBlockEpoch']

    def get_epoch_block(self):
        return self.data['EpochBlock']
