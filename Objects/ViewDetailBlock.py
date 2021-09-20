from Helpers.TestHelper import l6
from Objects import BlockChainInfoBaseClass


class AllViewDetail(BlockChainInfoBaseClass):
    """
    [
        {
            "Hash": "041e115a4002ac08b92dccd97a495e97fe119fb98400dd6763a00e67a8623a18",
            "Height": 28410,
            "PreviousBlockHash": "ec67d3686875c7bae0dad600202b23a32c582d1cc1cb842f054b613dca1f7ec3",
            "Round": 1,
            "Timeslot": 1613873260
        },
        {
            "Hash": "db1a2886f15e10696610dbadad7f3a544a29a16ef59fe2d897ada241c52597ad",
            "Height": 28411,
            "PreviousBlockHash": "041e115a4002ac08b92dccd97a495e97fe119fb98400dd6763a00e67a8623a18",
            "Round": 1,
            "Timeslot": 1613873270
        }
    ]
    """

    def view_hash_follow_height(self):
        list_raw = self.dict_data
        dict_heights = {}
        for raw in list_raw:
            block = AllViewDetail.BlockView(raw)
            height = block.get_height()
            if dict_heights.get(height) is None:
                dict_heights[height] = [l6(block.get_block_hash())]
            else:
                dict_heights[height].append(l6(block.get_block_hash()))
        return dict_heights

    def num_of_hash_follow_height(self):
        dict_heights = self.view_hash_follow_height()
        dict_num_of_hash = {}
        for height, list_hash in dict_heights.items():
            dict_num_of_hash[height] = len(list_hash)
        return dict_num_of_hash

    class BlockView(BlockChainInfoBaseClass):
        def get_block_hash(self):
            return self.dict_data['Hash']

        def get_height(self):
            return self.dict_data['Height']

        def get_previous_block_hash(self):
            return self.dict_data['PreviousBlockHash']

        def get_round(self):
            return self.dict_data['Round']

        def get_time(self):
            return self.dict_data['Timeslot']
