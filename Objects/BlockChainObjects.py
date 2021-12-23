from Drivers.Response import RPCResponseBase
from Objects import BlockChainInfoBaseClass


class BlockChainCore(RPCResponseBase):
    def get_chain_name(self):
        return self.get_result('ChainName')

    def _get_best_blocks_raw(self):
        return self.get_result('BestBlocks')

    def get_beacon_block(self):
        return BlockChainCore.BlockChainBlock(self._get_best_blocks_raw()['-1'])

    def get_shard_block(self, shard_num=None):
        return BlockChainCore.BlockChainBlock(self._get_best_blocks_raw()[str(shard_num)])

    def get_all_height(self):
        return {i: raw['Height'] for i, raw in self._get_best_blocks_raw().items()}

    def get_num_of_shard(self):
        return len(self._get_best_blocks_raw()) - 1  # block "-1" is beacon block

    def get_active_shards(self):
        """
        only has this field since "Dynamic committee size"
        :return:
        """
        return self.get_result('ActiveShards')

    def get_epoch_number(self):
        return self.get_beacon_block().get_epoch()

    def get_block_per_epoch_number(self):
        return self.get_beacon_block().get_epoch_block()

    def get_num_of_remain_block_of_epoch(self):
        return self.get_beacon_block().get_remaining_block_epoch()

    def __str__(self):
        string = f'beacon : {self.get_beacon_block()}\n'
        for i in range(self.get_active_shards()):
            shard_info = self.get_shard_block(i)
            string += f"shard {i}: {shard_info}\n"
        return string

    def cal_fist_height_of_epoch(self):
        return self.get_beacon_block().get_height() + self.get_num_of_remain_block_of_epoch() \
               - self.get_block_per_epoch_number() + 1

    def cal_last_height_of_epoch(self):
        return self.get_beacon_block().get_height() + self.get_num_of_remain_block_of_epoch()

    class BlockChainBlock(BlockChainInfoBaseClass):
        def get_height(self):
            return self.dict_data['Height']

        def get_hash(self):
            return self.dict_data['Hash']

        def total_txs(self):
            return self.dict_data['TotalTxs']

        def get_block_producer(self):
            return self.dict_data['BlockProducer']

        def get_validation_data(self):
            return self.dict_data['ValidationData']

        def get_epoch(self):
            return self.dict_data['Epoch']

        def get_time(self):
            return self.dict_data['Time']

        def get_remaining_block_epoch(self):
            return self.dict_data['RemainingBlockEpoch']

        def get_epoch_block(self):
            return self.dict_data['EpochBlock']

        def __str__(self):
            return f'epoch: {self.get_epoch()} | height: {self.get_height()} | ' \
                   f'time: {self.get_time()} | hash: {self.get_hash()}'
