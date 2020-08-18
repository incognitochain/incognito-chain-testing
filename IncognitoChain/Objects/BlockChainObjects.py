from IncognitoChain.Objects import BlockChainInfoBaseClass

"""
Sample raw data:
{
    "ChainName": "testnet",
    "BestBlocks": {
        "-1": {
            "Height": 33213,
            "Hash": "be20713f8320c536c248cc8ac1c93efdb940e175bf32f8184502efc00476c7f3",
            "TotalTxs": 0,
            "BlockProducer": "121VhftSAygpEJZ6i9jGkEqPGAXcmKffwMbzpwxnEfzJxen4oZKPukWAUBbqvV5xPnowZ2eQmAj2mEebG2oexebQPh1MPFC6vEZAk6i7AiRPrZmfaRrRVrBp4WXnVJmL3xK4wzTfkR2rZkhUmSZm112TTyhDNkDQSaBGJkexrPbryqUygazCA2eyo6LnK5qs7jz2RhhsWqUTQ3sQJUuFcYdf2pSnYwhqZqphDCSRizDHeysaua5L7LwS8fY7KZHhPgTuFjvUWWnWSRTmV8u1dTY5kcmMdDZsPiyN9WfqjgVoTFNALjFG8U4GMvzV3kKwVVjuPMsM2XqyPDVpdNQUgLnv2bJS8Tr22A9NgF1FQfWyAny1DYyY3N5H3tfCggsybzZXzrbYPPgokvEynac91y8hPkRdgKW1e7FHzuBnEisPuKzy",
            "ValidationData": "{\"ProducerBLSSig\":\"XYWUJdEdEJEFPsccrwHLyCzMeys1CguVkgvNrxqTSoB8QZMBZ1s+w8FHAdPMgmatxBUBV2kyl1cT2joAM/Jz+AE=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[1,2,3],\"AggSig\":\"kioGS1h+7CHeEJbEgxY30oyZMg45bc9yacAn4Y0kCy4=\",\"BridgeSig\":[\"\",\"\",\"\"]}",
            "Epoch": 333,
            "Time": 1594003770,
            "RemainingBlockEpoch": 87,
            "EpochBlock": 100
        },
        "0": {
            "Height": 33213,
            "Hash": "8fb05310410742752fdd337ba2786eb90578e8daa5504bf46fbc3e90e03867b4",
            "TotalTxs": 24,
            "BlockProducer": "121VhftSAygpEJZ6i9jGkGco4dFKpqVXZA6nmGjRKYWR7Q5NngQSX1adAfYY3EGtS32c846sAxYSKGCpqouqmJghfjtYfHEPZTRXctAcc6bYhR3d1YpB6m3nNjEdTYWf85agBq5QnVShMjBRFf54dK25MAazxBSYmpowxwiaEnEikpQah2W4LY9P9vF9HJuLUZ4BnknoXXK3BVkGHsimy5RXtvNet2LqXZgZWHX5CDj31q7kQ2jUGJHr862MgsaHfT4Qq8o4u71nhgtzKBYgw9fvXqJUU6EVynqJCVdqaDXmUvjanGkaZb9vQjaXVoHyf6XRxVSbQBTS5G7eb4D4V3RucXRLQp34KTadmmNQUxnCoPQztVcuDQwNqy9zRXPPAdw7pWvv7P7p4HuQVAHKqvJskMNk3v971WBH5VpZA1XMkmtu",
            "ValidationData": "{\"ProducerBLSSig\":\"FJ1LpHjhuk/ZX8Iv5SZIvhSJpY3JZsLY4Pt0jHy2h80+xYHBI//FR050rGdv7av8zmbSNAv+HTSEPS9OZ/dxXgE=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[0,1,2,3],\"AggSig\":\"ooD6sse/f6HhXPcjTt7FXoH9RJdb7SbEMJF2Y/ogAu4=\",\"BridgeSig\":[\"\",\"\",\"\",\"\"]}",
            "Epoch": 0,
            "Time": 1594003770,
            "RemainingBlockEpoch": 0,
            "EpochBlock": 0
        },
        "1": {
            "Height": 33212,
            "Hash": "6bc66e25ce3e74eff29ca012424357731ceddb96ee8c9ea57f0d9edc61ed6a38",
            "TotalTxs": 3,
            "BlockProducer": "121VhftSAygpEJZ6i9jGk6PZ3JW4ENRd48339y3RkjomvmfKfiEJLLxN8dAjJ1tdCfZwbGgGqJjtU3P76QPdLXXwRuTtEBLgrL4m2mYwMP36aqyVVDyzHBg3VkjXCdJzqKXXuKg1FnWdZoH4kFtAZHmGFUxar2NtQ2Boe1vyccf56ffNoQcUvv1tsbmWRPXmqapQv5j79K4pRF6uz9T9R76BbTB2RyL542sgxbRvJQUvXgzN3xZTMhoLNBoEJbkyE8xPqHbdiVthVBcTm5N3yapTxZEYSwd29drpkn46wBkNdHurbfLXqFwoAeEXyPRuMJBY7wm7jS7D3BDLUeLnosGjvyVuqzNDiMSZYWtjBJpwAEEEPkirBdAkSzvzpXU1akvSwJ8YL6cQau8LM9pTfLQCvEkF7QXpHLmLFwJhV1QqtPAR",
            "ValidationData": "{\"ProducerBLSSig\":\"PhQV7FpoSVqMGIf6Uh7Qy3YfFeZBDvYVaWiI8EpKSax4yGfmY4pUcLLzdSnnNu/WTfq5CGLgbCrhnW36QEIGWAE=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[0,1,2,3],\"AggSig\":\"H0DDMaws4kv4w47KyPrnkzV6OOgyxLJiqdCd31/7irY=\",\"BridgeSig\":[\"\",\"\",\"\",\"\"]}",
            "Epoch": 0,
            "Time": 1594003770,
            "RemainingBlockEpoch": 0,
            "EpochBlock": 0
        },
        "2": {
            "Height": 33210,
            "Hash": "8a745b8354f74613e5619315dbfa9076d9b5f055de5e71d0848ef43386c75b8b",
            "TotalTxs": 10,
            "BlockProducer": "121VhftSAygpEJZ6i9jGkFVKGZDvyVMuieXL1f1DUHFqWkWZyRjxHNhfDCv8Ey3uKk4rtRVJ6NFz3BhvMpww6Ucn9cmKhbbSMLEamMmFVtu6mR7tuiyUWYNdvVT7XhgtN6ceJDVPtSEAeNCjcG6xKbEyt1ba4cRRjUdTcGNJRj6HUuKWeZiuQyuyhBdWiMux2ABgJHmMMRCYtC3TfyPAg4VvSLjERAhaMburiYvHeHzPWJAsYp1LCrLiF6rWkGDACeyujhHkRDzxxtawrJ3R5TZkaERLAipHiKpWqTysZhZ3nxU9uyC9an78jigJFAU6EFFXmX7rMoSL8hd2LkgtEoVF9nGPF3gsfoQGeJx1HR6vxMjwSa5TpYoaKXEaqKY3ahZXu1Arr2xWTuQtEtJEukRiiTLHHYRebLHR1E9c8WUxiJZN",
            "ValidationData": "{\"ProducerBLSSig\":\"aH5Ue9NzhQayKVuAPFRePq76QdIBSGL/pmuYVZQ4QnNwAm9+1bUrGbWKQLTyKrTS0Zxl/9Zpso6YFSiKKemV+QA=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[0,1,3],\"AggSig\":\"hx5O0o7MyYX6P3oyR4vQCAY+jWvDSkSDQkiu3vyllC4=\",\"BridgeSig\":[\"\",\"\",\"\"]}",
            "Epoch": 0,
            "Time": 1594003770,
            "RemainingBlockEpoch": 0,
            "EpochBlock": 0
        },
        "3": {
            "Height": 33212,
            "Hash": "734c4f9a5e4c501d2a3b97e64d4e52f9512124e27c0ea29df94ad6df7b8255b7",
            "TotalTxs": 1,
            "BlockProducer": "121VhftSAygpEJZ6i9jGkFD9PvvUxiopjrh8nKRcDMqTfeg5P3dGK8MWzYG1Dwk2SUtnbNEPPtMGUbPDHak2Tx9rwKVxjkbcrVyCyWDdRUfuQnA2EHy2y852888VVU5YgckgJ2srofMgSH5tG1GLAGKrYzaUDKdwbCQaj9HJ9ieeRUg6nr6Vh6eQkL9qz7afk28jYFfQo9b8pmpTLjpvGvHdh8SCFXELyaLbns3FoD3uZw3skY36KS2KmhQCmc8zDdiRQuHos8kyxYtE6tMPuSw28uwyZ6QbfEoAiuSmCcFkdL2CiG84TPazFHQaZtFTVV8HHq3G2kgXsVcy1y5ydFWTfPZEVsB6jSzPezuujvjmERt7nEyurNM3q39sVyXjanni1fgGj6XCGStaRPaxye8KSLFGTgbfVrZfvf6BfCaAgP5s",
            "ValidationData": "{\"ProducerBLSSig\":\"4+VNmXpDTFvwhZyNi37yUBTC1W1r0DrF2OHuvwRA+xMziP5zetFkWfA/tBmDPu+a3oBbhbup/4G5SNsz0U3XZwA=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[1,2,3],\"AggSig\":\"A42BkXshSikshfxh/T4bsua9WHNwgIklb0rZueE4DeY=\",\"BridgeSig\":[\"\",\"\",\"\"]}",
            "Epoch": 0,
            "Time": 1594003770,
            "RemainingBlockEpoch": 0,
            "EpochBlock": 0
        },
        "4": {
            "Height": 33212,
            "Hash": "1c0ed221e4edd2762226481b918925b4fd9b3ed45a597dbee0e9e4b04c5a4141",
            "TotalTxs": 1,
            "BlockProducer": "121VhftSAygpEJZ6i9jGkCH8YaNkcF3v7ieeocbagdmyh9kkzw2xmReK6kMpV9u9YBF4StcUEWQJaFADJ6eKmU1jytFYPoyrQgdsq3Zvq57mqetimfiXCxD3PDn65tXov4sjzFGyCXWxNGYQS7ooKNCWrxvsxqfByso4e95m6wtmeHQU8tM9h1zuHnkHLFS5SxxnEJ6q4PSidwAVHPi7Su2H858jZRBAAmiF9VVCgN4LRhryeDUQJX3SJEJ8MS8ZjVuYQpM7viFLQ5f7vGuU942wq8yWU9VnXxEgSR8CqGS33emQm6FUYhqPb3QHZQ9eSMtdon6WXNvNLN19EDCNp3dYGgurMmvV57yLyvx8DdgyBAfM5QezsCMKVrbEzxZv9wM1uP2wJJK7EgzpT73HpNrgTa59XtMBDd1UEPoNJtgjMC4Z",
            "ValidationData": "{\"ProducerBLSSig\":\"WR5fphzsuf4CJaHnjtTIg/Dy1F8UMpWuInnKYQU9jNsy1VWYaheyXPVdtNp42NrpWZM+js+O69rxiFO3m/JkzAE=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[0,1,3],\"AggSig\":\"m3/Zvw3rKeIdilt872B5DKM7eKCQQoEGwl+LOfxBP2c=\",\"BridgeSig\":[\"\",\"\",\"\"]}",
            "Epoch": 0,
            "Time": 1594003770,
            "RemainingBlockEpoch": 0,
            "EpochBlock": 0
        },
        "5": {
            "Height": 33213,
            "Hash": "f00fca0d0103de193cb39fab5c063f2908ca0c0de5b57938d77afee70a7bbde6",
            "TotalTxs": 42,
            "BlockProducer": "121VhftSAygpEJZ6i9jGkCVYqzKy84ALdUsvdniXng58VKsRQpAT9HazXb4dr6kkCNwp4US1BHv5eVwyWwW4Hzt3LPdPs1r9LRA4qWaodsz4ZWSHZUP3sHEVAKLmmrXsnvGLDmDbk2himKc1RmrjdSHeJNbXQuDQjBrnouCev3WXHYWeHpvtTfPT4oJTzn26qEDDyc5CPR4Lv1YMzXvwa1CAeF9LEUHCRYwwMHjsjiaS64Kpdtp1yAMdCqMfMuD7qT9Wu5MzfMhnaQaxJUheSmsYWuFiML5ETqapUxvLxfZfZpy629fQ2QgYNXbhbWCoV56Utueh3NxmpogfMeyvgSCnXLAeuE6awt5vf16nz3a7HBJTYKdY4CYKUngTfs8EAGaGo86SBmGtUGszp32H3BvFaVLTxaUasXpD99ggBa2yGefo",
            "ValidationData": "{\"ProducerBLSSig\":\"qg9ImktxRRxbkmWGsFC9P8S7iQVwhEkE5dGi4M++gE98p/WL2p505pdquvtmYoxVn6D5yN7VxmLqWsS4cfVUrwE=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[1,2,3],\"AggSig\":\"q+S1ZidHMg8jXMVF9La2d65hryRZRY2vYxJFfAjP/8E=\",\"BridgeSig\":[\"\",\"\",\"\"]}",
            "Epoch": 0,
            "Time": 1594003770,
            "RemainingBlockEpoch": 0,
            "EpochBlock": 0
        },
        "6": {
            "Height": 33211,
            "Hash": "bb23b9328abac8beb15fa4b05bb308abbe56065f0619ed9436fa5b9ea872daab",
            "TotalTxs": 1,
            "BlockProducer": "121VhftSAygpEJZ6i9jGkRhr2EHg4P5WVG2eKpfbKHwfrXyjLHy3XAXczUQUgJ8Ja9e6HiuRMGrxjAoNReqSZpJczqQHEA8VcPofBgpxeCykTAWTvP5XrqVrfRH7zsGaYywVVrRzdGqU8FqmCeSZEBrYTkgNsgmsyhq3b73brkt6MWowThtVJxSmCaeFmHmHza1HbyChL6YUgES5RDfwBvLMgJR7g3mCe3HgRf8GwEqTvpxdFa3FQGQ4G5xAtqY7pCiVSABkT727qaoD4jzqGEsEvDgKdSV79nUHGNqnFppgXnxMp9h6YQSxDKkCjgEcXsMUj9HFQtfunLZXcanMg6coX2oy5ZV3ckAdE6HTXy5q47699Yz5GxLFYDh2iPZAKGgeNoB9W2EHr3REQ8J3Fq9St9vt23yJWhLGBhXiTadRmDsc",
            "ValidationData": "{\"ProducerBLSSig\":\"ySJB9BR6+60/ytS9HMCOwr51pIEp6dCyCbu/sp0DOFl6+FC6uhP6Xw12OCIDQFA6XiSlVU+gm01JoaOw0caqDwE=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[0,1,2,3],\"AggSig\":\"KEkWMs7qEUfnqwtn+Lxsy6iRbkt8DisIHKGOf8fNhrU=\",\"BridgeSig\":[\"\",\"\",\"\",\"\"]}",
            "Epoch": 0,
            "Time": 1594003770,
            "RemainingBlockEpoch": 0,
            "EpochBlock": 0
        },
        "7": {
            "Height": 33213,
            "Hash": "bf0bb79cfa2e038f21f9b7308c2edaf47af403826d4b8ba19c47106104dfc2f3",
            "TotalTxs": 1,
            "BlockProducer": "121VhftSAygpEJZ6i9jGkLU7Ld4EVGEveUDaE982EySj8wEq4peVurKg3qxMdXLjiy1zY8or3RKqoderQ35JRWqLtJhVVrpwjSvmNzTfxHYQArAYnzJyASK6PLVJkLJDtWFCSDvf8GgfupkbUVmevYYe9fYKs7PvqPNbh5DJBzYhQnVMPzzYVuTrgXycxKcQ8iC2PkDyGpYmEDMCcsGNM3p334NgCK6ZVnQ5KUzkE44sYizwS5SCeT3s5K4YNvMa9p5TNMhJsLSaedMGBkw17RXGhhT1KBMgC4QvDwvmvyEaqS58j8PcdwqV9bpaE3S9KgWrYFbWVrBgmBZG1nDgCNvkdXhbHP5ZvPuyNk8QzHqUVfsjoawzicrXMsfdneb3GGBnevY8CKVhfXE6ZqcoUKcy83MEKEXUgMqhBQCTAiAYhXS5",
            "ValidationData": "{\"ProducerBLSSig\":\"fFs9opKe7pUNSiYMUu2Sqt3QwsnzlP0/5duselHoQmZsioBCwPrb/m21bC1m6AiN0KfEToHTYa04GyZnkpazzAE=\",\"ProducerBriSig\":null,\"ValidatiorsIdx\":[0,1,2,3],\"AggSig\":\"gI47SJO/B4dx7PdDDE36abkThzPNqVX6kr6A128tMa8=\",\"BridgeSig\":[\"\",\"\",\"\",\"\"]}",
            "Epoch": 0,
            "Time": 1594003770,
            "RemainingBlockEpoch": 0,
            "EpochBlock": 0
        }
    }
"""


class BlockChainCore(BlockChainInfoBaseClass):
    def get_chain_name(self):
        return self.data['ChainName']

    def _get_best_blocks_raw(self):
        return self.data['BestBlocks']

    def get_beacon_block(self):
        return BlockChainCore.BlockChainBlock(self._get_best_blocks_raw()['-1'])

    def get_shard_block(self, shard_num=None):
        return BlockChainCore.BlockChainBlock(self._get_best_blocks_raw()[str(shard_num)])

    def get_num_of_shard(self):
        return len(self._get_best_blocks_raw()) - 1  # block "-1" is beacon block

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
