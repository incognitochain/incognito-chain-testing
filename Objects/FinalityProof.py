import re
from Objects import BlockChainInfoBaseClass


class FinalityProof(BlockChainInfoBaseClass):
    """
        {
        "Block": {
            "ValidationData": "{\"ProducerBLSSig\":\"c5C3Lm6qE40wplNMmXieLFJcTgKtRbwg5gqtSUHCJCQazflkl4nD0aPAr2mrGXFATTAMlv8NRn68zEc1VF3q5QA=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[0,1,2,3,4,5,6,7,8,9],\"AggSig\":\"kQfV9jYRh8ZaSvgVXiNLdnvZ9bvQahbhEPwcfBMo7JQ=\",\"BridgeSig\":[\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\",\"\"],\"PortalSig\":null}",
            "Body": {
                "Instructions": [],
                "CrossTransactions": {},
                "Transactions": []
            },
            "Header": {
                "Producer": "121VhftSAygpEJZ6i9jGkEd73hDwqP3FL41ZWySnJcwuD2sBTneYJ9vojnhwy5R13zRdmYAr1REhrnbrF8otmmvZN2zqUQhxCgwyYnCtNjTiTGuj5JwSy3YujuNsGPbjpj2wTRNdgL9wQoaDQRK2yZ1oM1bifyJXr8M5GeL3cfWpeZbePTWXWbb78a2jvbnKincxS9U4N6zDi9XkabuZEL5ofJ4Vfd2p4fabefvfCPArzPJont9JChv5pEw5kQpj2LUhBkVVmcn54xjPV7r7pMKTnFcbLgmXLibLn5Knx3RFy8prhDuYFcBWAaC3HQYMfVQmptC11yoGmBdiwcfdju15NgPZWpNhwF3AjFPt4s4DRMcU53hHCZnSmr7xGfZaP5xdjswZwYLVkexkkoW9Jxro24doiMVsYSTk2oEFgLwef3q2",
                "ProducerPubKeyStr": "121VhftSAygpEJZ6i9jGkEd73hDwqP3FL41ZWySnJcwuD2sBTneYJ9vojnhwy5R13zRdmYAr1REhrnbrF8otmmvZN2zqUQhxCgwyYnCtNjTiTGuj5JwSy3YujuNsGPbjpj2wTRNdgL9wQoaDQRK2yZ1oM1bifyJXr8M5GeL3cfWpeZbePTWXWbb78a2jvbnKincxS9U4N6zDi9XkabuZEL5ofJ4Vfd2p4fabefvfCPArzPJont9JChv5pEw5kQpj2LUhBkVVmcn54xjPV7r7pMKTnFcbLgmXLibLn5Knx3RFy8prhDuYFcBWAaC3HQYMfVQmptC11yoGmBdiwcfdju15NgPZWpNhwF3AjFPt4s4DRMcU53hHCZnSmr7xGfZaP5xdjswZwYLVkexkkoW9Jxro24doiMVsYSTk2oEFgLwef3q2",
                "ShardID": 0,
                "Version": 6,
                "PreviousBlockHash": "f892fd0ac786f08b132795d3caa686d3aa8bf75d4f73f6adb3cdfabecedabfb3",
                "Height": 5191,
                "Round": 1,
                "Epoch": 408,
                "CrossShardBitMap": "",
                "BeaconHeight": 8155,
                "BeaconHash": "ec3bf858d30fdcd2e513b83b633c0da78e28a67d451bf255cb9b3a1d332111a4",
                "TotalTxsFee": {},
                "ConsensusType": "bls",
                "Timestamp": 1633916820,
                "TxRoot": "0000000000000000000000000000000000000000000000000000000000000000",
                "ShardTxRoot": "95ebb98759c4fdadbdfcf08936ad1706e50f9418a3f49198413b01141d2f0d4f",
                "CrossTransactionRoot": "0000000000000000000000000000000000000000000000000000000000000000",
                "InstructionsRoot": "0000000000000000000000000000000000000000000000000000000000000000",
                "CommitteeRoot": "5f6bb41dbad16277f863d92db5be22926fbbe707652647f4b0f71bdf1fc46ee5",
                "PendingValidatorRoot": "0000000000000000000000000000000000000000000000000000000000000000",
                "StakingTxRoot": "0000000000000000000000000000000000000000000000000000000000000000",
                "InstructionMerkleRoot": "0000000000000000000000000000000000000000000000000000000000000000",
                "Proposer": "121VhftSAygpEJZ6i9jGkKZixz3MxWLn8H4bq6g9i1dxGkbJYni7TgHu4rrmzdnrzNeudRBVepuX66NTNzBP1vxjtVuFAYT7BkCkzKceR9CpQnYs2zJpZNhLeufPBFSpdYz397T2LQHnFAQit44f961H8z1LBbA5t8SEe9rs6GSf57iSkaDer752nZfKyn6arudjiDnzgMgi3uPh62wewSnJtZ71RXukKiYVFjAy9MCeAwHTfAzY28Fc7o4VnA185H9QDZSdY8b4pHDbk6Bx8dsMcFsVwDHv7kzWbprajj8KBqKm24SmjUCLm8HJ3BNuLUwtcd3vPZb1s5BavkK2LGbogWJW9PkrUwyBuffb9U11ziqEpBR92EfdfWJ9GwpsLqgx1KvirvAVZkzEswSf3vuBRe9QLWAXzP3Kq8BgpNJXVBMd",
                "ProposeTime": 1633918200,
                "CommitteeFromBlock": "326820bacbdfff9cf8cb84f6d71b819dfd1c699e185778ff1552679492435133",
                "FinalityHeight": 0
            }
        },
        "Data": {
            "FinalityProof": {
                "ReProposeHashSignature": null
            },
            "PreviousBlockHash": "f892fd0ac786f08b132795d3caa686d3aa8bf75d4f73f6adb3cdfabecedabfb3",
            "Producer": "121VhftSAygpEJZ6i9jGkEd73hDwqP3FL41ZWySnJcwuD2sBTneYJ9vojnhwy5R13zRdmYAr1REhrnbrF8otmmvZN2zqUQhxCgwyYnCtNjTiTGuj5JwSy3YujuNsGPbjpj2wTRNdgL9wQoaDQRK2yZ1oM1bifyJXr8M5GeL3cfWpeZbePTWXWbb78a2jvbnKincxS9U4N6zDi9XkabuZEL5ofJ4Vfd2p4fabefvfCPArzPJont9JChv5pEw5kQpj2LUhBkVVmcn54xjPV7r7pMKTnFcbLgmXLibLn5Knx3RFy8prhDuYFcBWAaC3HQYMfVQmptC11yoGmBdiwcfdju15NgPZWpNhwF3AjFPt4s4DRMcU53hHCZnSmr7xGfZaP5xdjswZwYLVkexkkoW9Jxro24doiMVsYSTk2oEFgLwef3q2",
            "ProducerTimeSlot": 27231947,
            "Proposer": "121VhftSAygpEJZ6i9jGkKZixz3MxWLn8H4bq6g9i1dxGkbJYni7TgHu4rrmzdnrzNeudRBVepuX66NTNzBP1vxjtVuFAYT7BkCkzKceR9CpQnYs2zJpZNhLeufPBFSpdYz397T2LQHnFAQit44f961H8z1LBbA5t8SEe9rs6GSf57iSkaDer752nZfKyn6arudjiDnzgMgi3uPh62wewSnJtZ71RXukKiYVFjAy9MCeAwHTfAzY28Fc7o4VnA185H9QDZSdY8b4pHDbk6Bx8dsMcFsVwDHv7kzWbprajj8KBqKm24SmjUCLm8HJ3BNuLUwtcd3vPZb1s5BavkK2LGbogWJW9PkrUwyBuffb9U11ziqEpBR92EfdfWJ9GwpsLqgx1KvirvAVZkzEswSf3vuBRe9QLWAXzP3Kq8BgpNJXVBMd",
            "ProposerTimeSlot": 27231970,
            "ReProposeSignature": "1f832nJtf5LSuvCPNhGp8B1Q1uiDZ5wQTwCM1YesXF1ZJ1w2Vyura48raVQABhBi9VqYnehvdBvFvXNQfSjWC8WJ8nCZ4AY",
            "RootHash": "ad0678675d7bd2b12a25e59f19f81374248c41ee40420259b8773d80635148b4"
        }
    """

    def get_block_detail(self):
        return self.dict_data['Block']

    def get_data(self):
        return self.dict_data['Data']

    def get_finality_proof(self):
        return self.get_data()["FinalityProof"]

    def get_producer(self):
        return self.get_data()["Producer"]

    def get_proposer(self):
        return self.get_data()["Proposer"]

    def get_producer_timeslot(self):
        return self.get_data()["ProducerTimeSlot"]

    def get_proposer_timeslot(self):
        return self.get_data()["ProposerTimeSlot"]

    def get_root_hash(self):
        return self.get_data()["RootHash"]

    def get_previous_block_hash(self):
        return self.get_data()["PreviousBlockHash"]

    def get_repropose_signature(self):
        return self.get_data()["ReProposeSignature"]

    def get_repropose_hash_signature(self):
        return self.get_finality_proof()["ReProposeHashSignature"]

    def get_finality_height(self):
        return self.get_block_detail()["Header"]["FinalityHeight"]

    # def get_previous_block_hash(self):
    #     return self.get_block_detail()["Header"]["PreviousBlockHash"]


class ConsensusRule(BlockChainInfoBaseClass):
    """
    {
        "Lemma2Height": 55,
        "VoteRule": "no-vote",
        "CreateRule": "create-repropose",
        "HandleVoteRule": "collect-vote",
        "HandleProposeRule": "handle-propose-message",
        "InsertRule": "insert-and-broadcast",
        "ValidatorRule": "validator-lemma2"
    }
    """

    def get_vote_rule(self):
        return self.dict_data["VoteRule"]

    def get_create_rule(self):
        return self.dict_data["CreateRule"]

    def get_handle_vote_rule(self):
        return self.dict_data["HandleVoteRule"]

    def get_handle_propose_rule(self):
        return self.dict_data["HandleProposeRule"]

    def get_insert_rule(self):
        return self.dict_data["InsertRule"]

    def get_validate_rule(self):
        return self.dict_data["ValidatorRule"]


class ByzantinedetectorInfo(BlockChainInfoBaseClass):
    """
    {
        "BlackList": {
            "11YXuc5JbhYCVcMqJFiR9tMDQ5kjchRp4ZjEU6ax15YVno4yNQTYKVrcLjFrbnqybrhKzzfHM5MqybGP4w7QWybhwH2ZSFNvLb5P6jmw2CYqpegFzvUvPR238o5L2ZMbdMQ9Uo36ihJ49C8dFB63WXYAmmrUbSjJ2DtweRbbtnFuDJTRczFnM": {
                "Error": "error name: vote for block with same height but higher timeslot, block height 55, bigger vote block produce timeslot 27273891, smallest vote block produce timeSlot 27273890",
                "StartTime": "2021-11-09T04:51:00.485549484Z",
                "TTL": 2592000000000000
            },
            "12aESygi4pJyWLtruW4w15BCQKq3H9aPST6QVgEkX9aEsNwdToXV5FLpRrQtogKzffLsvs3QE7r7hm1EgSuHNcDszyDB2xe87brk8CVCBRbBNnUoaPBLrwxPnUa1tD7ZZcVbkz2FCfutKwjYxMTpjtfHL9HTFf3S7XVkUjBAJicgPsc5x5xxs": {
                "Error": "error name: vote for block with same height but higher timeslot, block height 55, bigger vote block produce timeslot 27273891, smallest vote block produce timeSlot 27273890",
                "StartTime": "2021-11-09T04:51:00.568184507Z",
                "TTL": 2592000000000000
            },
            "1Fd2hUS61WwYpBLD97roLZTMiovmtuBDg2hLFsrMWXWXBH5Bn1mTn89qiiVvcxLZd2dzpP6ZiAQQbYSxdb9HvEqpWTsxymwJxeJhzDTYp9w4cpm9K9w8WAVBcoyi9ME9mSWexXRGjj4Y2ZDTCZtW1qGtDJKMe1D5XcZCBiXfHJF12zcRRsjP7": {
                "Error": "error name: vote for block with same height but higher timeslot, block height 90, bigger vote block produce timeslot 27273927, smallest vote block produce timeSlot 27273926",
                "StartTime": "2021-11-09T05:27:00.564547185Z",
                "TTL": 2592000000000000
            },
            "1MyWFcKs9SACUpvyXoDWFLtbyqgRztM9P98XbVrw62SRkuvHvUsCjmfTSuu2V9VPWNMQzjmWxrVYraKSThh3cuzdmSBrMTtCXWfGAP4TbjGbdg4cw8PfsxZod6QWPSZKitZJbJuK8KxbiGRzrpWecBNTB62xL9L5Wv3sbxdFH9ctJZLk8g3Dy": {
                "Error": "error name: vote for block with same height but higher timeslot, block height 90, bigger vote block produce timeslot 27273927, smallest vote block produce timeSlot 27273926",
                "StartTime": "2021-11-09T05:29:00.38445381Z",
                "TTL": 2592000000000000
            },
            "1NY6MRXsZJf9Pbns7vJgqGNuUWEDNnD2AxijZaUXfm8eAhwNkXoRYUtQy3PVSndg4oioDsnmjbdSXeqxFqxuNRidpuVv3m2mZ26MKfUxwQxiQ6YbB7bgmsZRLWYPBc8fxXoeGwiLJL4GdR3Bb5414EQwLshXEPvg7q3SJTYBcmo797ka9XrHR": {
                "Error": "error name: vote for block with same height but higher timeslot, block height 55, bigger vote block produce timeslot 27273891, smallest vote block produce timeSlot 27273890",
                "StartTime": "2021-11-09T04:51:05.932547534Z",
                "TTL": 2592000000000000
            },
            "1ThpE7GxUPQpLm21uJ6KzHPsb1SRMEdLL5pbzcRTFEUuMdvheVcBEmTNGnJkkeiVw1rY9iWUYHT7Yn3FEQsDJPWCXnkaLsoQfnkN6EDzisVYo6spMY5kEnpJLvbCpWx4LK66CANdUQXCAfHw67sJmgPMXEE4dGTxMm1PPdFMhT5RavbQbVMe6": {
                "Error": "error name: vote for block with same height but higher timeslot, block height 35, bigger vote block produce timeslot 27273869, smallest vote block produce timeSlot 27273868",
                "StartTime": "2021-11-09T04:29:00.674400289Z",
                "TTL": 2592000000000000
            },
            "1W1QbbHkvqNJuRHESsiAzoGwdjR49a121LLqTpQveAFiitpzGSHiDDtifENZs7nsXNRQodwZM4C4JpMnzLnr6XSCbT6C3GXbyz6VhKe6JSABMetqMe5XnzBj7aQnUKohUkpikukpnhdQy7C1irokEBpRkfPWxTo3etPUhL3zH6rnVgX9Cnczo": {
                "Error": "error name: vote for block with same height but higher timeslot, block height 90, bigger vote block produce timeslot 27273927, smallest vote block produce timeSlot 27273926",
                "StartTime": "2021-11-09T05:27:00.417929966Z",
                "TTL": 2592000000000000
            }
        },
        "BlockWithSmallestTimeSlot": {},
        "VoteInTimeSlot": {}
    }
    """

    def get_black_list(self):
        return self.dict_data["BlackList"]

    def get_block_with_smallest_timeslot(self):
        return self.dict_data["BlockWithSmallestTimeSlot"]

    def get_vote_in_time_slot(self):
        return self.dict_data["VoteInTimeSlot"]

    def get_block_height_byzantine(self, bls_key=None):
        if bls_key is not None:
            data = self.get_black_list()[bls_key]["Error"]
            return re.match(r'(\D+)(\d+)', data).group(2)
        else:
            dict_data = {}
            for key, value in self.get_black_list().items():
                data = value["Error"]
                key = re.match(r'(bd-bl-\[-]--\[-]-)*([\w\d]+)', key).group(2)
                dict_data[key] = re.match(r'(\D+)(\d+)', data).group(2)
            return dict_data
