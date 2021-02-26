from Helpers.TestHelper import KeyExtractor
from Objects import BlockChainInfoBaseClass


class CommitteeState(BlockChainInfoBaseClass):
    def get_auto_staking(self, user=None):
        """

        @param user: Account obj
        @return: if user not None, return True/False/None (if user not found in this auto staking list of this state).
        if user is None, return the whole autostaking list
        """
        auto_staking_list = self.data['autoStaking']
        if user is None:
            return auto_staking_list

        com_pub_k = KeyExtractor.committee_public_k(user)
        for key, state in auto_staking_list.items():
            if key == com_pub_k:
                return state

        return None

    def _get_committee_list(self, list_index):
        return self.data['committee'][str(list_index)]

    def get_shard_committee_list(self, shard_id):
        """
        @param shard_id:
        @return: list of committee public key of shard
        """
        return self._get_committee_list(shard_id)

    def get_beacon_committee_list(self):
        """
        @return: list of  committee public key of beacon
        """
        return self._get_committee_list(-1)

    def get_shard_committee_size(self, shard_id):
        return len(self.get_shard_committee_list(shard_id))

    def get_beacon_committee_size(self):
        return len(self.get_beacon_committee_list())

    def count_num_of_shard(self):
        all_committee_list = self.data['committee']
        return len(all_committee_list) - 1  # -1 of beacon committee list
