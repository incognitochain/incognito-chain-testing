import copy
import math
import unittest

import pytest

import topology.NodeList_dcs as NodeList
from libs.AutoLog import INFO, WAIT, STEP, assert_true, DEBUG
from libs.DecentralizedExchange import DEX
from libs.Transaction import Transaction
from libs.WebSocket import WebSocket


class test_dex(unittest.TestCase):
    print(
        """
        TEST SUITE DECENTRALIZED EXCHANGE
        """)
    testData = {
        "count": 100,
        "trade_amount": 8712 * 100000,
        "tx_fee": 5,
        "trading_fee": 0,
        "slippage": 7,
        "TokenName": ["AUTO-pETH", "AUTO-pBNB"],
        "TokenSymbol": ["ApETH", "ApBNB"],
        "TokenAmount": 1000000000000000000,
        "797d79": "4129f4ca2b2eba286a3bd1b96716d64e0bc02bd2cc1837776b66f67eb5797d79",
        "562f2b": "57f634b0d50e0ca8fb11c2d2f2989953e313b6b6c5c3393984adf13b26562f2b",
        "000004": "0000000000000000000000000000000000000000000000000000000000000004",
        # "797d79": "0c1e0dded579a13cb5f9034d810b892d6109fd2ad269f545ee2df0e760cda5d6",
        # "562f2b": "a78c34f9dd6adb186d7f371f676b0d6de1603c87a31c281aedf769aad6a57661",

        "amount_contribution_797d79": 3000 * 1000000000,
        "amount_contribution_562f2b": 5000 * 1000000000,
        "amount_contribution_000004": 1900 * 1000000000,
        # "amount_contribution_797d79": 29461,
        # "amount_contribution_562f2b": 24623623,

        "token_ownerPrivateKey": [
            "112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA",
            "112t8rnxntm4qcc1kNxqQJEpz4DskFKXojYxaGVT3h7c7QjbWpgiVRv2qmLjQMUW8QxUm7HiyxqdQ35fdcAQ7SZ3cYmDADGfFkcENH6Pi8GH",
            "112t8rnX6ThEU1nYpyYeerYU47EmrTA1AWJguAAbJLyot8ETdUydT4yT4zahyyme78bAAbNZmhzHGva57b7XTf6BFiA9uzGiQMdxFfSGDdwi"
        ],
        "token_ownerPaymentAddress": [
            "12RxERBySmquLtM1R1Dk2s7J4LyPxqHxcZ956kupQX3FPhVo2KtoUYJWKet2nWqWqSh3asWmgGTYsvz3jX73HqD8Jr2LwhjhJfpG756",
            "12S4kCdFmeW78Rxi2RrdgQqwDrKjkCXX6LeQpES1EVRCwfsTqefPDvSV9oi1DwvERvwRvCGFbgvbqbfusCN29HN5rukngGkp7U5EVHF",
            "12RxiiobVPEoo4djdueSsDcT79BgcBQtiZfwMTwTt9a6tfN9gEbsor7BgxsHxb8DeufMo2BTDxn11wnm3ANDHGL1e8Y7NXWZmQLMiLC"
        ],
        "privateKey": {
            0: [
                "112t8rnakdKxvk7VMKUB9qmsPY4czwnP24b82BnepcxHLX6kJ1dYQsR8d6xNTzwC9nEhJdocr9u19NAr4iSYXCeTBRu3YET8iADMAP3szdfw",
                "112t8rnbTkezohA4GLeUDpLFnuDbFvPcoCS1MxctvEu3rmUkvmoWJ37MnXDSscpVy6bKfSwjWigi9L3qhcUFo8yZLLsgPvYAn9fs1E62qNPS",
                "112t8rnjzNW1iKLjpNW9oJoD38pnVVgCiZWRuqGmMvcEgZEHjtg4tLRTAcfTCxNXrdzKcEmY9JVfX2Wb3JLaCjfRDEyGhXGK67VB297mZuwH",
                "112t8rnmcQXPkPG3nHhhmLjKeqZEjBHcFCSxBdwRy2L6nGXBwKopc5PYWPVXu14xmec34LXxu5JJcf3N6wUfsbbNWKVotAMNrswhE6adbBmu",
                "112t8rns2sxbuHFAAhtMksGhK9S1mFcyiGpKypzJuXJSmHZE8d4SqM3XNSy6i9QacqTeVmrneuEmNzF1kcwAvvf6d137PVJun1qnsxKr1gW6",
                "112t8rnsFHcBxrzXs4V7e1k3epnpXoop9r7av3KUXG8wMyqYnHBp9BgFbXWsjsKnzsmbusKF4WLGaaZ4rywzZx2d7xtWZeDxWk9irmdoVfG2",
                "112t8rnvk4KQQuzmXpTss9Jezvf9PvHvK8PXzDTei4hTTBUJaJAF6JeKC3VYx7uKJEwpjFt8ZZEC8EBozPXUtaWWDLduDYpbC6ErmTcPyqop",
                "112t8rnyMutLkLcXqwyJVuFjUtwSxkk2Qm9FbBkbGEMWQ2yG4kMzzr2s9ThjN1dq1ThZC87evvfQ2dVvKjnvDTheoHv9bUibJaioLyebhZUY",
                "112t8ro26YAXf9sMzSB8GQUPaUsAkxHjKTMDKbXNHjqPg4q8w658hoCCjnZmPeLRvbuYadkhXGUjaZrqYmGNa91mdNXjAupDk2DhSXJXs3NS",
                "112t8ro5SDP4PZXs4tBR5JA6Modb8ax3HQ5sEesmesawA4gE6Jypy1s9rhoXu143kUBMdp3qjTd4PZufrBChNZyr5HkUYYQpWuH7DZpgaCeE"
            ],
            1: [
                "112t8rnXHSFhmnyduga9tE5vh5CpTX1Ydu8murPuyQi3FYwxESW6eCPVG7vy62vjeRuM8PDfDDLf6wfXekJM5QbdHAryj2XcN4JAZq5y1Tri",
                "112t8rnY2iHyuYKFDDtb7wZV2TuyG1vECqJs7DWZezZ8DB7BEKiYw7Dh2PFnf3Y6zZdQjqNG6JEZNJRM4gYwsxo1GFniHXmfZYXZGPM544Ek",
                "112t8rnZqbTrW3BPYhCkw5FsFht9PwDBqJm3TogWjkQHr6WimG5v9g3eBPgKGm2yeuaLsn4eLPHvZGr8vBg7MLSWdU4tee1shqJ26sRSaSUo",
                "112t8rnZywqj5s4nMRUp9NF9jX5ypZMxLStTvVweLowoF7Tpk8gwm6w1d9T2x2CQD1gbByKVBeUJsfB8eaJ7sVcxend1A7qjT2kdX6hH7uri",
                "112t8rnb7Ld1PyzdMrcFnZhXiXfuDAj7KwyqQ3KyRAmpyeg8VUFmp6wZVUXE6A3YvwZZKPhnNMv62R14TJCCj91aEGuaLKW8bTs2FD83hTCG",
                "112t8rndKzDhNcapS29umfdLiTZULG7nbcAiTwGfpLfoh6yhsbS9uPkhxuAYCuPKVrptPPG5q9Yx5M9Yhn9X4QYWQN6nPXhkMkdZwpyRQShi",
                "112t8rng5fFuJjbnWZYQ5NXQEqodQriM7fB9NUCS8ehV1TsoeZv1CYKGhCk523SVhiRNnikDbhcVmP4B9CsYfYJdTqdbFrPYjnud5md9eHUv",
                "112t8rngSnUVFi6JEmqAo5c1Mam2qyzDKDSMMosHj6hqH7NPKMiQUjpshJesAK8Gm7pHMpAYvwe1zmR4ffCsNEB7sUB1CQxj2GU6t2AQVpyK",
                "112t8rngcEnEv8gahJqD1sJCRqbRXX4vQiE7ywWzmWmPsNvqfbts7KbHJYPcdYemzpGCQSM6JVfoPhQGGMNfrWiYBTs8TuvZTrtqjCdH6EaH",
                "112t8rnhSagitC6n7MYanGNFZ5AWue3oF3MBErr3ANhmWPN32jCKMsC5SBeHRXq8XB8ApMQiRYPw7tUC1bvRg87Dt8eZcYM9JtVkxqc9NmyY"

            ],
            2: [
                "112t8rnZ5UZouZU9nFmYLfpHUp8NrvQkGLPD564mjzNDM8rMp9nc9sXZ6CFxCGEMuvHQpYN7af6KCPJnq9MfEnXQfntbM8hpy9LW8p4qzPxS",
                "112t8rnan3pbXtdvfKSk3kti1tFcFpVSq5wp7c3hhLk7E4jQih2zsv8ynjpP1UQivExGwbMf9Ezp9qmKBJuHhNZPAzheqX4WTV8LfrdZY5Mh",
                "112t8rncuhys7YDSqXfjVFjU52b6A9HHcUac2tLXSoqxduYSZHuQsZxybFtrhNqRqCKMMAzXTiJKE98vaXmzrqVQKT4kXUuRbuUAQyhUhuKK",
                "112t8rngzFxPgY5Nqfp7H2pGaWqQgsrqHo5K7okZnTZbTJmNaJcPt8rUk1sdYhBfjTgSX47PDwqxXW97PWiXyq33SV6njKfGqwUu2UjXHbNA",
                "112t8rnqLy56zy3wYGstLJzj4LYasXK29n6a1cRJAQuq62VrJgeQpCGTqtaQnVWgZ123Qe5MCTV87UqbiwpqjvFHV4opPBEhsW2knXZsaKvR",
                "112t8rntSe2VmyJ5Bp7J4PC7umK56QabXGQwYavoGbvzHb4DJZzShpC83x2yioCwEtqBi6BnTyun1AT3ezsmWkanspEmjEp79JAbG5mukRcT",
                "112t8rnvBzFzXoYy3GMB2dvgv7eXEURec9Z1Kmdcm6xa8EiNihXUY4mYTA9oJ74mvgLaoNt1JsTCDyDt9K8PUQJkkW51spqmXqRJ1mFkoXFT",
                "112t8ro4W78VPdNuMoS3HJf8yyHtSdZNJZ8pn2h4KvXXEqMBNs4hyvoYFJuZSiHKNCF3k9gozpVpGzJfPus7VbYn86wKPkZSxhQQPrtshprc",
                "112t8ro57adWNUxiLvQfsqxjBR7GcRvTAutvSUfCzw6kRA2aqvyecjsdqNEZ4Jf5VLz9j6VFZqmWZTnnZxhJ9YkMmBcgaa3vL7cuwgg7Tctp",
                "112t8ro5hxHgy6rxMmtsSCcp6hEzVjvat91uca4TzEidMZnZLrptMtMP9zSYzUf9eNVfdo7SoWcyAmBtdMmdDzQVenxkLhr8keMQmTHnkgBS"

            ],
            3: [
                "112t8rnYE7yUhkfy6Cgac1QkkkXDtxgoHtnWQLMBWimKS3neKov7m11FicLLgsV5PJdxmSBhN9aURP3PmQdbAUKdYLp8hWwoyVNZUSgjP5yq",
                "112t8rnnHW1XeTieGFTvxKMGLd6dUj861TXESWBUMvTDghxgMqBrnhohAc7r7hPUAwr3rdK45JtA4iniEJmuRaaXrkmSb1xMUw3cPxgMqD38",
                "112t8rnnvKQLMTGwsakt7YuY6MgzYvHjehq2ntWEPXoHG3BS3RqqqEye1DgzMA8HJ7W8jBjzMqgkEWMUPSXVgy1KG3Tq8DACbkswLm5YpVUh",
                "112t8rnogExSysUT12NNKPumyJQXAUNCQ8BFaqN37PbH2g9KFMbDAaEqxinHn9Z1ewvT2YYwDCiePYq1aLQthvhTNuFFUTKVLQMqVDpdTYtp",
                "112t8rnou7bokSk2ksEw95P5WUNzcycjL3rQMriJ7e83JTV1xc4CiuCyrSiuCHDWBzwAGeeAo8jpri8VnMb8NY5wKfvRDYUEDjvtuoZN4Gkb",
                "112t8rntmnxDWgigct9HPLunwBFLDYvauFWXRmKSyyBk6if4hsjgXt8GPPqZ4eZE63gUxaPSpdBimbVLEDRfcpxc8K3zjhiM432ZYJFTUPCb",
                "112t8rnu1KN6WySPbZmyz8nx1dPQSgLqsbFCzE5DF5ufBPSRrjhGkvsAw6RDu1RZXE1FDhMRsRHrcTcHSYyxd4X53NbNpNao6n2nhs8KDQqp",
                "112t8rnwhNfnhSSUjFiEphvmf5rqBpCWBJF6Q6S2f8Ednh5iBH2gAama4gLsvTaWnCCWtXNU5DZdsfyi9HVrfd3R3Y2iLYh3REPYjC65c923",
                "112t8rnwqdWmymXeKt5NGDPwEhK5w2JqS8sLtHK7UKBjnVQDEH6nrmtzacNJxLE6VqRj1jo1CiLJeHZoHMvK4ZjESkLFajBiDvZHmagFdkA3",
                "112t8ro1TUxqAx3eWJYXpR5Aidex8LcKSFeb1kYkiFFpsFawsy9qQpx93D1MoSCxtKYFtEfmxsbeiWpRRaHpWsknKmWtCN2psAqnEY4jA9As"

            ],
            4: [
                "112t8rnXMLt6jfCTH36GwDPkh9AUDvaAD2JDdrdBqVrxiBcKMaeyuXh6HD18iAP38HN5icCqSw7UwCqWPCyruYsjqBzmK6WwMjCdVJ322UMw",
                "112t8rnXoTm5MRpyYDbtwYZQEBELvFabVKFV3sUEAQnWcrEBuWxvefMFbzrzRj8mwDTe7ThuUfAi11SX3woKPrL8FKUp6aPNzhi2zBFf5DAK",
                "112t8rncFcEcgru414MHRYsBwpjUGfZF4sWa5Zwhr5Qt7d5u3mGR7oYAem4zN3qpigdA2nmkZQ2KYXnU6E6TZvg1XiHi46xxzvm1HAMSaC5K",
                "112t8rncjmB4QPYi9pucPiXDBgapkYk7wTBNpbg5wwE1zoC7MYhPL5HAwPE34NU8SWK7WB8QnXBAoGotNbSJq3B3eWiYyL4mp22nqVufAHqj",
                "112t8rndwosixUewQZxZ9CdtVy7Zb8vmBi26JpiKTJRaNZx4JMhnXsiwRuXM2JHR627LbgCPwaNQCNP4mQKvBqWiM4oCQnrNw2JgGWWFbT1W",
                "112t8rnf2a3ccCRcABxZceyc6y8fPRaAjXxvA9t7yJ1rhQtYLhVbo2fDHjuWAXLZbd4TDNwQXm7q2zk1q3PY3X1NRDuaSpGzGnJoVM6typHb",
                "112t8rnf66LJGHv5tqi3coUChfTw4fH4JDcJoPxY6SQbTc3WoDFmekQcbcjT6VRaw7iuiN9RuQz9AVaJztwksvzkK3h5JciXtZEZBHx3YNYn",
                "112t8rnhMLNZ81i9vH9UK514NErAATv4TLF3h9GhUrx7eE1k9pfcmZcB5VmYfYZfCnUF6NGJ9mA8iXWTDXGBpyh7VeQWctRY51QrRyu3QU3b",
                "112t8rnhmw3ABEMfptzDxSPPCyf8GPnMkNYLWA1q341FVuUZ6h2PpE815Hr3anr5omihZgFcc7pBG8oiScjU2vSe1aoyi1bKTPq9cZ7YFLhk",
                "112t8rnpq9pGi2DLqp5yWqwPxRAWkRVGtyb1xGKXUmW5Dxox7pwT6twao3RBugiMj9pDZizmi9ohfqAEv4ggRaXhoPzXnvutV4YU2qekJg5M"

            ],
            5: [
                "112t8rnYwrzsk7bQgYM6duFMfQsHDvoF3bLLEXQGSXayLzFhH2MDyHRFpYenM9qaPXRFcwVK2b7jFG8WHLgYamaqG8PzAJuC7sqhSw2RzaKx",
                "112t8rneWAhErTC8YUFTnfcKHvB1x6uAVdehy1S8GP2psgqDxK3RHouUcd69fz88oAL9XuMyQ8mBY5FmmGJdcyrpwXjWBXRpoWwgJXjsxi4j",
                "112t8rni5FF2cEVMZmmCzpnr4QuFnUvYymbkjk3LGp5GJs8c8wTMURmJbZGx8WgwkPodtwGr34Vu8KZat7gxZmSXu5h9LDuppnyzcEXSgKff",
                "112t8rnqawFcfb4TCLwvSMgza64EuC4HMPUnwrqG1wn1UFpyyuCBcGPMcuT7vxfFCehzpj3jexavU33qUUJcdSyz321b27JFZFj6smyyQRza",
                "112t8rnr8swHUPwFhhw8THdVtXLZqo1AqnoKrg1YFpTYr7k7xyKS46jiquN32nDFMNG85cEoew8eCpFNxUw4VB8ifQhFnZSvqpcyXS7jg3NP",
                "112t8rnuHvmcktny3u5p8WfgjPo7PEMHrWppz1y9verdCuMEL4D5esMsR5LUJeB5A4oR9u5SeTpkNocE4CE8NedJjbp3xBeZGLn7yMqS1ZQJ",
                "112t8rnxntm4qcc1kNxqQJEpz4DskFKXojYxaGVT3h7c7QjbWpgiVRv2qmLjQMUW8QxUm7HiyxqdQ35fdcAQ7SZ3cYmDADGfFkcENH6Pi8GH",
                "112t8rnzyZWHhboZMZYMmeMGj1nDuVNkXB3FzwpPbhnNbWcSrbytAeYjDdNLfLSJhauvzYLWM2DQkWW2hJ14BGvmFfH1iDFAxgc4ywU6qMqW",
                "112t8ro1aB8Hno84bCGkoPv4fSgdnjghbd5xHg7NmriQGexqy6J7jKL3iDWAEytKwpH6U85MkAaZmEGcV3uBH8kZiUcBHpc1CpskuwyqZNU4",
                "112t8ro3VxLStVFoFiZ2Grose15tyCXCbc9VR2YtHbZCd2GZQPYBMafmXws2DDNd8VKQqKhvw6wW51xyxvrTzLE5prRAjcWJiDWiU4EL3TUT"
            ],
            6: [
                "112t8rnaPYWa3YFQ1GXC6XHJawYQKbsHs5GShFtxtwRtUaGkyiWkrtPNv5gdbHPEgubuZQbZrh4Sbj3jb94BSZtsUVEeg97xZ67sibxKEwcb",
                "112t8rnbhcH4FBtrkR9qNLGHUMdM4Z8Sau1hpXif6xATpGWiMLUB1TYfbLkpdgoJ8sRKDDeyy7rPta8wVWySAGqH6SDrLi88NLgGw4Ca571c",
                "112t8rneQvmymBMxTEs1LzpfN7n122hmwjoZ2NZWtruHUE82bRN14xHSvdWc1Wu3wAoczMMowRC2iifXbZRgiu9GuJLYvRJr7VLuoBfhfF8h",
                "112t8rnfSkqPibUF3CWWZAECvGdVfRGSeVgn5k6KumohCPuiewYRGkABGx3ascvT99rddmN4NhY7paKdU4c86egrkJ3hzevovW8rBt4pNp9g",
                "112t8rnfuHwKo5fmeJ1U7gTUVJyXYZ8APAwY86HFvSTV5BaqEXRWhmaNAqMqVkc9ehF95JmE8XBv3XGfPr3r6ooEtWntJrAv9SzybqbQwtoX",
                "112t8rniPgJuKm4ifQwmF9qyCKbR6m7ZmWDHVHCCK8nU1dmm5rQut2LQm2q1A4WvsR136gyRLFYXcAmZoTSGuDp3z4CXyFHbihWxTAxg3Bd7",
                "112t8rnj8BdZssCmFUkJerouK4a2vq5q8xqUD7byq19tb97fwjUBn8GH2xFPdQoHuudb9be7MjdiPZ7XU3gWBH6ZaKqu4dE4m6Miyvc4Y9Nn",
                "112t8rnjig1SE7e9voqsEozygUurw8WAag1G6EpQk99NrJRY8Cytj7tFu5fcNdyTKDoHafssbcy7gi3jK8jq49Eiz1KFt4593NgNtZyjCaX6",
                "112t8rnkYE7mwFbncuQEa3YaDkJuKxPqWoizUWghae7NoasenRWbDWZAZJp9M4p529YEMS8KdfKmgXkDTmoZd98ou3ZsUXZz4KJrMsbU1V8W",
                "112t8rnm6JQ3fBsPTm3644rZ6wbKtnzbysBsjiRUixMf1Mc9fuSyWBwuv2eU4WEB7avKDA4M3cPWL6eeNaWVXiDyLPsRT1vFpaWa8Teufn71"
            ],
            7: [
                "112t8rnYTc4aAM4wy5h7oWKs1RAusVHmVG9M2tFKYWhjLndnfHnKDd193sjkiiR2aN5NWc1XM1ryxFv67NjAdRHHEnAosPy2UY8NepVMbHHB",
                "112t8rnZUndVHejwoZT7P5mnHNzA5QMTxJrJWpboPuXS7Ka6nKYr7KvCJboYx4mWTcfPwUvKzFUMP9PmWmM7DTht94aYFZZnwbxJubLTPbMM",
                "112t8rnbzh8o8ufBJ847bH9chDUpMRbfqdYRDVi8H5pwr2oX5poTEm6LXdPw23e69KTJJKbHPcsfX3HAJvz3sK2NUYdmag21PrbdYLXK7cwe",
                "112t8rndTYwXQ8sFvYeCMuGixubQX5JmozKBb6f3c9jWgZsDcwRawjG3ESjyMc9HM6Bp4rXdv9D2NWYynFAJkxHNRYJURYeF75GUEi5xb8hg",
                "112t8rndnqTVVtmHHUkUKWKvHKR6Cngd7jg7cZ83JucNZBTcFijutRaLkm5eokFdKAdetVgRtnGXDp1GZKAAcSdB1UxKk9yHTyLnuCXDNTVB",
                "112t8rniZP5hk9X3RjCFx9CXyoxmJFcqM6sNM7Yknng6D4jS3vwTxcQ6hPZ3h3mZHx2JDNxfGxmwjiHN3A34gktcMhgXUwh8EXpo7NCxiuxJ",
                "112t8rniqSuDK8vdvHXGzkDzthVG6tsNtvZpvJEvZc5fUg1ts3GDPLWMZWFNbVEpNHeGx8vPLLoyaJRCUikMDqPFY1VzyRbLmLyWi4YDrS7h",
                "112t8rnkQMPXNhfDRQsckiszqiC5VLU7EudTnYcrBaAQSc6qSt4kn6feEaHbBtRQsJiG17sRxCpCmWntwDyV2CtS4jeGkPxTXKoqTxqWsY1M",
                "112t8rnn4JiG8TejjT8XVWnXYnS4Qju8XhpnAcLPN3jTrGMB2E4waJjfP8faXN5GvVpMRumhUshANF6DvQUFUBULMoPpSjFdV6tqrERsVa13",
                "112t8rnoNEkkhKQ3BS267985dik9ivyu7qMYXMqJpAeAEksxYLF1fXBPZMwCZk9DNsYYAvQruJWx9MF4LB12DLunV4eLE4dRg758AMVtPrbu"
            ],
            9: [
                "112t8rnb3xwqqd3ZUU1HooFkQhdaKJshqcEepYKxds6DNH5w3d5ExpcjW4J5eAUyGnoPcXbbfkDv6fzbaikEnRke3TTvKc7mPAQBWMFekR6M",
                "112t8rnXuCwHHCimQ8JhsQhtVx3sfxyYtnCh2n5ZNb2u948Ya2Jgj8csPttBHK6aiLDn7KpxpQ89Bp1PH6Fy6ZxkWeCGWQ8D4eSBejpDNNnh",
                "112t8rnXMRrjgSsyKqtovrcMxTQWXUAwECWkGkk9SwxjcR9KuFUZDL4FrTZ9qPr7wZeEPuoYdu7SW3PYz5ZN5ZCaDcSHpJPJ7ij1VY7zTXpz",
                "112t8rnZ1Y85WUcruY1micAgAho9Q6WULZhYbUKiSUV37t6b59UEA8GAw3qiH6KZQxFBsDPk5AVzdDDAgDSpn7UVSp2zRZ9FkqUnrWGCFeku",
                "112t8rnXhx8AUDiyCPxwQkmScqGduf3sbkqb1E4TbQQiqsCCNDtUzz7peGtrcA42ig95fcrMP9EbuV3Djrh2n8uRs1PzrtUZikGUt4JLFCuh",
                "112t8rnXHUZhuLgEygYaDWQ6RYqcJqWdjNic9xtUbvrKFVK9pUoNcBvPcweY6d1r3v6VB77GMHq9oeH6U3igeZ2RafvSm6DHP7L1GVYBidMZ",
                "112t8rnZqpBtD4HwAsD7s1ihgd4UmrqCcb91ZzE2kLRtAckcTKvL8PcD45i6o4p2sa8ByanRAcFvyRKhZwfpB2UWpcQTZ6u8bdy4KA2Hpxjo",
                "112t8rna6Mhu6RqHzvwSDF4nSoVU33pwn1Vta6pSmeFUbX2QaaTm4LbC837VVvyaKiybbKcL6xrVLdfRj9VukYupbS1sw9qJ8qL6DWPozMNN",
                "112t8rnedoadSV8GAgFBTCxU3fsBg4oeKwwdb1PL1Kpffr3Yo9MudwBndVNfcRPScSZrukJRF31YQakqLbfqvx4JfbDAZWX1D8R68UFeK3B9",
                "112t8rngM8HHKPyrR1vkxPn7doRkT29az1vY7G8APuPJSagTk8tkHZMjn8qBsvesCqYYzfCfsL6dvJ7NMR6afhK8LKjGxKiuDZFUT2JpGURX"
            ],
            8: [
                "112t8rnakdKxvk7VMKUB9qmsPY4czwnP24b82BnepcxHLX6kJ1dYQsR8d6xNTzwC9nEhJdocr9u19NAr4iSYXCeTBRu3YET8iADMAP3szdfw",
                "112t8rnbTkezohA4GLeUDpLFnuDbFvPcoCS1MxctvEu3rmUkvmoWJ37MnXDSscpVy6bKfSwjWigi9L3qhcUFo8yZLLsgPvYAn9fs1E62qNPS",
                "112t8rnjzNW1iKLjpNW9oJoD38pnVVgCiZWRuqGmMvcEgZEHjtg4tLRTAcfTCxNXrdzKcEmY9JVfX2Wb3JLaCjfRDEyGhXGK67VB297mZuwH",
                "112t8rnmcQXPkPG3nHhhmLjKeqZEjBHcFCSxBdwRy2L6nGXBwKopc5PYWPVXu14xmec34LXxu5JJcf3N6wUfsbbNWKVotAMNrswhE6adbBmu",
                "112t8rns2sxbuHFAAhtMksGhK9S1mFcyiGpKypzJuXJSmHZE8d4SqM3XNSy6i9QacqTeVmrneuEmNzF1kcwAvvf6d137PVJun1qnsxKr1gW6",
                "112t8rnuHvmcktny3u5p8WfgjPo7PEMHrWppz1y9verdCuMEL4D5esMsR5LUJeB5A4oR9u5SeTpkNocE4CE8NedJjbp3xBeZGLn7yMqS1ZQJ",
                "112t8rnxntm4qcc1kNxqQJEpz4DskFKXojYxaGVT3h7c7QjbWpgiVRv2qmLjQMUW8QxUm7HiyxqdQ35fdcAQ7SZ3cYmDADGfFkcENH6Pi8GH",
                "112t8rnzyZWHhboZMZYMmeMGj1nDuVNkXB3FzwpPbhnNbWcSrbytAeYjDdNLfLSJhauvzYLWM2DQkWW2hJ14BGvmFfH1iDFAxgc4ywU6qMqW",
                "112t8ro1aB8Hno84bCGkoPv4fSgdnjghbd5xHg7NmriQGexqy6J7jKL3iDWAEytKwpH6U85MkAaZmEGcV3uBH8kZiUcBHpc1CpskuwyqZNU4",
                "112t8ro3VxLStVFoFiZ2Grose15tyCXCbc9VR2YtHbZCd2GZQPYBMafmXws2DDNd8VKQqKhvw6wW51xyxvrTzLE5prRAjcWJiDWiU4EL3TUT"

            ]
        },
        "paymentAddr": {
            0: [
                "12RxnTs5KqyQUzGF4R2w68j3biJD29iDsFiVgC4GRy5X85anUrq1rg8P4aUyDRuS5desg9WANRptifcissMBPETyMeBE8KEh7LmQ6m7",
                "12Rv7iLGR4m2116m6X44yyY531WQ4j7Eroxnkv2CZKHeieDtmHUEeerq9RkPkvb8N4S3NxcBdJPDe4jHKeapzTxSVpRcGGK7NPUc1eF",
                "12Rryj5pw8jmf6Pxs4FFxWs6YW8eBbJd1m2vGiFaguyH9rSQwuqeTqvDuUrReNSVd2w6mfr1SrCZYocU1Wrh9xhWS9rXEYGWuDz2VAp",
                "12S1hPUUsFFsWswuCUk8uMh5b4WHXzycsQWPVgqenJChvCTKSUyevZn8Fu3b9w6HoZYyi5UxgWdQuEER1adxW5xeDxbnc5sQzCZu2my",
                "12RsetaMufaKaYpg7zJ3CL82n7Nhg9q4nRWNu4YHFms3BFVM2Ghm6jWfCJbYM1JV1aqDjBFCQFdL3MYQhX3xhETohBjcH2xjkyRBGi7",
                "12S3NUP7YvVXjXuey4d1w6txk2zeFNAMWg5jkXWwBALSv5mwf6pmsMA5RTenX2Qi2amvVYxcHvw2k1kkQjY4ACLRGNjhnqF9DUikCxx",
                "12RxR9X5NZdGqWV26vfFD7xgGJK8SoTidkrVGQoGMc7usoETa5vR1JWohybPNMBfjL7uwsBGui27xB5aWmR87aDGuLA2aSaVC25Jjmg",
                "12Rs8TgdKZo71Lxyx8YzQU8xQwEnmvu2gixX2cBBjZFgG1nn72zTonimHXQs2i6FWRsQsEFu1tQ3yrfGoFgHwEmujQEBdb6p4Z69AQw",
                "12S1AiFtuGGWaCrhSE77f5W5r5VMLxe8rdTMW79JR17yVFfMG3cuYa9SsWX4GCbUk1jU8v4HQMXUjcfz1XNhNKCkQakVnQQPVw2i4Mx",
                "12RyHwnxFB4H1NiaKVZ5gDT4hJs4QQemyt9cdbKt6pYGrZ4tjXkKQZxqa2g9CVRZ5Q3Lbmu3SwRDCN9Tk6nVZEKME8hPNzhW9Uzkfzq"
            ],
            1: [
                "12Rqdqkv3w4uyfSTYTkoegWSHSoex75QLuHiS4C1MzwMztieSPai59mprYovV6WC963SP4p9sH5uS3eFYomefPrvvMKhuafER6YV3Kv",
                "12S27wMrcSRDKADayf64CNbZxsMYDSni5vSov2fwfFJdjwpCgvC8fn2dxnF5rigiJfC8zzeVVSjtDtmKu2Mq2kAtMMZ6xiE7dEgTG3f",
                "12S4ABWjWm47uyTow9PR5u73WeYA8wme1518Hf6t9rcvdooZ2daUMXrBSXRCkggjFtQQjKWq9QyBA48jWYgsjRZ7TG1CrpmypWzL8HQ",
                "12S247vyiWMUe6idWR45sQ4WEw5aesXyFkhfpx3rSrY5LZFQ7zbRBSxSosy4dsN79SSjDmQrBcZFDphav3NrYfUnQ5jXD1PfGWtArhu",
                "12S5kdWp7MzLK6NnqGNi6TAquNxYzZg1Pps55hEMpRr9ey2Hd3ttjhqodPxeYtWKhbjXrgYsgrKCgxbDmHpL1MZMmuviRUZJ5D2nxaN",
                "12S2fnQRQdPjVEMZ9dViKm29i1S3x4kCxFsRFszMvrZsktYRpbXUJTHQf8SxMQ3Nxk8WfcqVs6Cqj7v4wsUp93mc8UjAkEvJeMsQvt6",
                "12Ry3hZENSK7LQPZT7mGTRcHoPYL1xgMHmMH4KfpdN9oyBtCVPeKE1DTKxs84ZQ22Hx1WPhzm6njSLzqVz3kf9cyhJZN4bckY3q21xT",
                "12S16tKA3UFz5n6uuaPJ6cPgAWXpLsszdypicvbb8Hr7p369CYfdoyW8X9ZZ6qTrWEi57H1Y3w3V3YFptue4UZLDceuK61qEEYYthDo",
                "12S4iynmbQnrcEt4CUFfXxnnaieKxjtUYQUeWsXsv9vfwPVw2B8Ncxia6ARTNjWJEtSvdTspYXd3hXRK9CumTSU5xuehFhBLVLWJWMM",
                "12S5JVsCqhUS8LsY5vsz9QztRHA3mbwUgJfGLL4ynTVFeryb43jaBUHJhxZnL5P59x7uYXDyNH565WVrHBiH2n1izxVja2cYJ9vFpo9"
            ],
            2: [
                "12Rw9oesEgd8t5NGrfqxtWTCzh1eDif55miqZ1kFzj5zeQ6UQnNB9JXRn5Vc5QVbBaiFhoYdYPnQZ5tWwcBpse5EJXM3Av6qEV2wspv",
                "12RxCyrWFCkpzfnMcnN8MuDrXkFAsEAkhyn4zHhy3n6CNZPYJ4cNDesBGycwu62PJn8rQ8uLiC5zSYDiXFa9hXtQMUJvVCMT2uUNn8G",
                "12RrHMmXoSMVw3bzK83Ba7AFZkkSRWrvu35Eu3YNKJ8uM1MRcdotFEgYs5SzQuxJENddreCPjh8JpD4t8GsGPpMjuAnyLDuiV6pxAJA",
                "12RpneuTB2Q3ks1J2fvwkNDfEDRcYSCDjLpMFGa9eMUJ9cFzjuBKbb33VXw9yE2i1Ln4ggCSTdCqSisprRZRLXyNvbCrDXJdDjW7aaQ",
                "12S6oUasGQHHsmmvocadAZzFPgkfugmhdVQH48tKcqY4GCznPBjVK6BurPCs1sPE9cjLzz5Ftso8f5DToxYTQv2vn9GkUV7N9kSzskc",
                "12Rzt7nHZq7tZq5JALxDcv824rRieh5JWbGgGDt2KzP6z6dhpHKWEVubYzrz1PGXktku4oRgSV6oE9xVz328MLNmHZLG5mX6Bx2Gb45",
                "12RuV6MZ51ASHcJp7HhN7ghXguLveSQcSzQNv4YryFJicgxSteU6ecQyfDJimn4kGa87UcR7j4vvag7gYZRvNRhNo1ydTU5cnihVtJw",
                "12RuKbi34mBBk6uJEuCN6YyCWnFSGMxopDc9ZoK5kh2ULuuoWL41dVk1h9F2WDok7oXDTdFDYRgKoczwthYNJJyE9yz4Fcb5aXF46rp",
                "12S6htjvjcnMo5D2Tsv542e3W7gEjW13WDCkGWtmuww6xh42n1j67buozNyGjsUMCVoBKyr42crZXGFyA5jWV38jEJjwLe38P1wbCjJ",
                "12RsDDusiQLs8h5AHjfks1BunYSb7c8sNc5MDsNqZDLnB4TVNTWbZiAJnqpNUqCNDs7GuSBS1P3CRb7v8xNKeJSaeUc5rEZGFEDADgo"

            ],
            3: [
                "12RzEtZfyexVDnoTzsTwPNVSyhvN6ZgfxNE3C6fNzJWCp2UJjYbfNJ4CuhxhHspsU2AFCPM9Tb4gwtL2B713FtabgkyJcv5BPXd96rP",
                "12RvGHi8MLymSWCpv9HaogJYXqL3BZEydP3k62EEJP7LwtqTy31KmpedYfeoQpEE2jateXPd3GdoCZKvjSvZAB4JUpYzpK3QGU5dKeB",
                "12RuRByiywZ4mrrDFfSY64GJoeu7MjJuwmWMrrYuNifeYD5seDCKJFSPVAHd6UMyJ1HmQV9ZGvednYmVguojvGF6PKsu1G37w9FmD2b",
                "12S1Gc4LH7MmeRUx39JEiZGyGsQz831GEGQtcTixDMqitGMaxiTd7g9doF2ZmgZBAtKPZ7EUcmFU8RRNzn72dpLSEXSTh8Gyux3xpK4",
                "12RvgoKjQRdYS4X8NgizSNvHoGnpHDnyGmrodmNJjY3La7EUR5UkNMcSG6XEDiBEVzMrZ878JjZBA6NPotHCa1t8uSjPHhwsHGwqZT5",
                "12S6VTLMi7GTR4qVdK8Rh6Zavcz331C6E3waDDGtxYGuW1RMmFQ5iWwcwRs5vLxVKmJJwJys39ME5rbzUpeiEUDSU6nE6awkBzWjVBy",
                "12S5NXh5dgCp8RyZ8wSrY2XN2ZsDA31iHN28Vruh4ALhsXJ7T594Jk5LkyFRhP2kKnR3amdWwbq5deUz7Pww2pjLY3VHeqcFZyZD7ew",
                "12S46m6mF9PH8EMUH65JJX6VajSqYarpL4P1hsy8KeAsXreBeTxuewy6UghN9bJD9WX3N1a4VLkKVRM68G7J7ey39VXLMTxfsWaePc3",
                "12Rw1JjhYr9MCak8XDbhD2zjqM5qQ8MeHQ7Fq5JGK1s16Yx4p5xRA4Geo4brre6Xh5LSGb4nzUke5S7UcJWCWRKfB8sVopHRcAFJ7vd",
                "12RqPWVRy7k4emQxAyzUb1q2UnttmAJo7pzoQkQSuhDS9B75yq3nCfs2m9seWmJgcKgmqcPZGLypgtJU7KGybGPapSZNMMrNce1btAj"
            ],
            4: [
                "12S4GsG1Gp479rAM8XZWuzBU9vwKMk7csbxS6LjLdvphXffkYN2Tx7LWCwvmddsZe8WenpF1ZmN7nCoeuecgynGE8whLs7MUuC7t27K",
                "12Rzz7BdMwsh88pg9YhEQTJc1oYGghymZhWdJrsXgfC8decJ7uxkwkptQ3jSnJdC6geAUXiofdxvYY8oScKMcGSxSbYNvzAKympKdhN",
                "12S25vH6kvqqe1wLfxCMG1RJp25DZirzBWte8PDREjci3MVAQf276EcdgCdmH3VAQ3ivcfDcjyZUiS5sUKYdGQRkuKS3292pcNCoo15",
                "12S3PdJvtPr6hWdtZm4g6z2S4JeapPyogKEuP83SmzfUJrgRYRcUAarSn9C96VKGfLrmmwNCECjPKhBBL7FvWqxT8rszDfGRQfsj6kE",
                "12RrqTNjaCnyKi2N1EVjLtQaTUN6hpKbKBEYi7Cz89ZqGnSYsCeZXqhtmX3MHD4m1DKzsDNuNLbP9ANBaMVQqGFGX49SxACGPhf44u6",
                "12S6xzV1LavEAPmztFYAfx8LgUY4fwYC4mVCQP2TTjE2TT49iDBHuiwQGEr7RsFnzbGv2mD7bgfgWT1eBcpY9oK8YaYdEVsC3nNobTz",
                "12Rukeu5HQRGCNmUj9oK753mSZz1oUn6MeUQCRwd5t1DckFtThAoWMHrkgBYMEmJ95tbEcBshFbYWt6zdQVecdg6xRD7TnqFXL4Jji6",
                "12RuNxhBbgJXAsDkFuyUbwbKRRzcKFbUmv4nshADjo7Z313qfC7X3f3CrbfVpD3KtGQdCmoTzTpTmCooRJiG2SSfuNhbqhDt48GUgAF",
                "12S44xGxJjNiuJze9V9AoqsLSAy7N32T3xCBkH5ockymfqgMkTk246LXigfApoDCiYxyyDszVwYwhsYg7pP5YMMKP4PbWNZUGR1z35p",
                "12S6i33cVoMZCw8QPkvrPssTjaqpxpgGTgaPTjBdDESQPHSRnGSd4kTViYTmLN8NXmEQuJhCiDuc4H3Q1avAw5hCUMTCpx5bxSFdx2z"
            ],
            5: [
                "12RxdaQkg3HzYAzfWb53osy9pbyHVqTd5m1hN6eghfjAXLwpy2m3QgGBRWVnmhH6sq1YScnYLC9aESWitaLTw9TNsJkhXiv88CAn6kf",
                "12Rx2NqWi5uEmMrT3fRVjhosBoGpjAQ9yxFmHckxZjyekU9YPdN622iVrwL3NwERvepotM6TDxPUo2SV4iDpW3NUukxeNCwJb2QTN9H",
                "12Rvic7Pnf1d12ZB2hnYwGV6W9RLfHpkaSt2N5Xr5up8Hj93s2z8SQKRqQZ6ye2tFD2WKy28XTSQ1w9wiYN8RZtFbPipjxSUycJvbPT",
                "12S2DUBWE3shx2o5d14Nr9DVM6eocQMjbJZMrT9YXfbNwhg3sejnP1tqhaW8SrJ881Zo3vgdVPUf56WXrYnMjBRmeKWPKFiJKcoviUA",
                "12S2ZZxMFr6kzDBd5jKWtAYsm47tbRDvRWC1RYTHZeXsG49JNMSsX4jSVYRTvfpTi11XPxqjmauRUX5myddMTwKuNZZw3CrsYUa82tc",
                "12Rr9rsUiXbG3JgdJNeFtLjGhYEWPaEpzvV5YDSzst7sU3sxgMaXBY5uWbRXGRLYGDTrzZ9KEcbNYZT8SHMErDkm6h6PcJrKdBC4tye",
                "12S4kCdFmeW78Rxi2RrdgQqwDrKjkCXX6LeQpES1EVRCwfsTqefPDvSV9oi1DwvERvwRvCGFbgvbqbfusCN29HN5rukngGkp7U5EVHF",
                "12RwumVV4Q84rKknv24yATBeQmu9rtEMro91BuKhLnpnRsR1iaXBRtrWJZ6Mg2rFCfauvNvhjkhVKbYJYMW6bQAWbAj11UTo2Dy3XeT",
                "12RqFNrzjApKLSxg786YmRQwq46LqbJKpPbLXUZTH7rbzxJ55nyiPWFEQbg6ZGjWmefNo3rp8LSLe8JTRw17vc3NszuJSkHg4Mm54xU",
                "12Rrz9C7QcD3x5sCyp8o9a3nc3HCPasqtWJZnsb5B5wiaDx38rE7Je2oJdWr1DQMjiPrN8GG1ZHqxVNydL8RCqf4FRdzMzfJoBf5NKz"
            ],
            6: [
                "12S11Dwh2dkmUZNcvv16rb9vrsQMytN5YjoVvHsgfTuKSVHTk3jSYbh4QFRpAQjQvBeuHirFEqMmMZoe83af4pDKLSYWe8u5AieSxFJ",
                "12S1LnhXGzuThgh3iNKFFUuym3bp94AFUcVwEoDEAUPvaRe1NcQho2cr1Ec85LzcS6fqRV6vYwyBw56YCPN6Yps8TMghnkXC1YSgUQA",
                "12S6o4t7umfUeXfum6e8AHMKMkr8pXjCwNRPF1zvemfxzCCwiXEc5boXD8j2729rF5oZ2zPMkbuFWqj7xf48rTpcF445Kwn1P25N4Mi",
                "12RzG7oD2zKMGKAnM7Ygiz2sVCvQr1pWcC9P5szB2JgA9xFcobR2piyVmQYcKTHb7jTU7h1bfLt7U3W9sqGGCJVypQEYXi4T7RRuabg",
                "12RtmWcLNZPSH9nGjCSdY16ijpdNU2FnLeGpR1zJW4xUmxecjuWuSp8j2AgZmV6a4w5fFmbqWaJhv1StjiSz26Z4GwNPaVfxfFXSoYU",
                "12RvuQ4JmZakP7oRz8jVJWFXzNkpDnVSABUey92WWmMK5X9A9Z7nVm68fm6HU9pJmYQJq6dwRUNSkg8drepTMQJ6M38g32mVCdgp9C9",
                "12Rr6EN9NK4xsKBsfaKNYsRZSQTXw79fesVUs5bwu243CmAZy3rxc8BQRhQ6k99R5LCZKJQnodFLawvy5znrkUhokGJ5VTtLiurbS72",
                "12RxuhWbUiSDJZgkWi9FMXdeFkcVZR72gBnrHA5Gwtr1asbRPHb3gbkw5TyJXF9oNP91WbWxLWdXzwoGSU2vhJCYQfLZQzC3eoQfZso",
                "12Rw4PBkP9YRwbM9pusj9NbDjFD8Jd9J7k1wFnAhzTMRuZfsE6P7He5aps9rLjoWKmXjhbrEcLQ9Mp8RBveCtPrtKFB4fduodTHeYNS",
                "12S1uR85vg2PNEsYncbUSooWS4yCZk1CHVdoN5KmoAeara58C2cpa8hT2WmtbTvRJ6vfwitLtTTfYkb7o3p371vYoEwmHEADPLL6fmB"
            ],
            7: [
                "12RvkfiH36X9tDMFXWyzvSHTXRPy45LrfJgmT57wK2T1diTiMSQUDqAMm84a8V5kDEQXjWe1FbFGmgBUhhuP9s8Mih4xzWd83eNDSCG",
                "12RsB8NVfdGBJiyCqYeAa43V9eDCrXQge5hT6CjwkYKjnv7mjU774dFbmTQ7KgXYAcJk8yuayJA3U5rdoMAuLYQ2BHPhrx6j3vjTsej",
                "12S3PGWSdw1aMQw3fDyo3h6dH3HBixx3SLhghBh8vwY6jxrQHArFinrJAjLkxsciwHo7FzAYqsxhAXgPdRH1TAxd8uBQzm1jzroU6jb",
                "12S1rZ7PQ7PaSAmQVTHzxbJdFERbZNGBA77q6pUeGB7rQEV9Gtb5NXQbibRuoeysug3m1tPuc9uEGmWaMxan6iV1noRs2zTpBtSgJTW",
                "12S4nz1EviUWK6xY5TVNQtMEQuDgGERNbtCyC3w5n3bJTF5CP2UtnkpvRngzmo9a3odG8fnWGLUeEtb11pSS28aZa3gwn3b1zpsMsjH",
                "12RveNXPRAADMg8qivCXF7P2LS83BwfMiHvYx7WmD64znJX78LASf3GL9WS6HM1W48zQDMS5AZjeZojVvCDS7kCdrxANvcnEGa3R4MY",
                "12S17M4WZzF5eT1E7unbCbMVXxFUSo3otREHneuumRESux1azmvxXyoutFiHFaEjvAGtEztRWZKvb163dEtJ6jy4nMDQePa3xGSu3Lz",
                "12RwKbciB4Y7oEEU8hbrjySmc5Jcw4Bx2RbJRCp1XydPmHZoT2EpigLaGMRQFNJDuwmhb5SFiMzTJ6dFsykRiPsA2c1aYbKLCV5yT9A",
                "12RrS73n9HSQEVCW9P6h65VHdzagHRsb6VwTzcpswwc1ncJxrdQt52Ftkeo5bENbY5hXMSKqCGom4961JS15qgaBhqCbA39mWp7cGCu",
                "12RvMo7KYYc38aeC25XbDzfV13WHB5WPGoeLgp6pbx5xUQs6xJDEQqzm9mA8fegA2uuDUGLVQEFvePT5hCdCrGmVyDpYJ2YoX7Bkm6R"
            ],
            9: [
                "12RrPp11mPovVGLLYAF31TAXnpRYMxL1Lzhn5XnYsrJZhuP136BuEtHyo8ZLzwbeFGLUycxrcyfa9cATkF3cbJoGPeisZ7jwx2TFiYn",
                "12RwSij6ep5oB6TnzcRStonLR3GU1GAx4epV8pEUACZQJk95caKTtr1iZF25wmCpwRMDcrfEbuRpHo5PpdzSGhtNnvFeSumW8P9z44z",
                "12S2QGPpbShZZhd3fMtWPuBoZLTSSFFUk1FVkefGh1GtbBvnsXXhYiLCM6Vx8aMoN2SLaNmVkfVnA8CMxhEBfjbMoiU31vzmDdn3NBG",
                "12RymW5bBZBq6e5Eo6nAgk3umeqawASUaiBtvWMQ2cusZWTWaSCqcAjNtUPonah9Ke9Y7s7BYsAA82kqpzzybPXcQdvxqaxG8LJ2i5S",
                "12RtJMc4pWTUW9iCiaQ6AJgP6LQJsfYCmHUMbjcFehadyHpFhw27UxG1rQsbVSRiV6RRB8kYFHt7mYRrqNY4msNDKEWkh29Ykqq16vb",
                "12S13ciK8obsDCYSh2XGnahkAS2QcGLL1kQyAmMdE19h3qxUcpGcis7DmfmwbmBv4a6sHLtPDHF97qjbiP3BCBCM5C7gHBKmpEDZQz1",
                "12S58N3X96FxvThCjXmbSaPoM57oMkdwMYkmyR8otvXMZmHGDff2ZLLk9X98f7t9jhyE7nvR7ajk9n7Bx1Q83BQHyckHhbH9mqJ9cpZ",
                "12RrodoPoJThjotapCt5WeLKnZzPi17k8cHk3HYguXnvobaqfa1Dbhhsboax3oj11nfDNd6HnSseWKtcyrrCiZ48bWwkhR7Mwec6JUT",
                "12RpnJ65EAJiJH8LYGyzKBQQEBLs3Um2YRTFf7v79tnnM7fF27bVDWeJ3bZTwSucbDC3VoUqMi3NuDGodAfmH88nHJmhv8AWgRfXeNv",
                "12RyiCu4kFCjbwqh3w2yuug2Xq24iACa6Ndbu4RdetVYjfW6j7XkpGGiv9rHVcCKQXEjCMBz4qT3yCvDbm9awaZPW1MJSEto2KCpBPY"
            ],
            8: [
                "12RxnTs5KqyQUzGF4R2w68j3biJD29iDsFiVgC4GRy5X85anUrq1rg8P4aUyDRuS5desg9WANRptifcissMBPETyMeBE8KEh7LmQ6m7",
                "12Rv7iLGR4m2116m6X44yyY531WQ4j7Eroxnkv2CZKHeieDtmHUEeerq9RkPkvb8N4S3NxcBdJPDe4jHKeapzTxSVpRcGGK7NPUc1eF",
                "12Rryj5pw8jmf6Pxs4FFxWs6YW8eBbJd1m2vGiFaguyH9rSQwuqeTqvDuUrReNSVd2w6mfr1SrCZYocU1Wrh9xhWS9rXEYGWuDz2VAp",
                "12S1hPUUsFFsWswuCUk8uMh5b4WHXzycsQWPVgqenJChvCTKSUyevZn8Fu3b9w6HoZYyi5UxgWdQuEER1adxW5xeDxbnc5sQzCZu2my",
                "12RsetaMufaKaYpg7zJ3CL82n7Nhg9q4nRWNu4YHFms3BFVM2Ghm6jWfCJbYM1JV1aqDjBFCQFdL3MYQhX3xhETohBjcH2xjkyRBGi7",
                "12Rr9rsUiXbG3JgdJNeFtLjGhYEWPaEpzvV5YDSzst7sU3sxgMaXBY5uWbRXGRLYGDTrzZ9KEcbNYZT8SHMErDkm6h6PcJrKdBC4tye",
                "12S4kCdFmeW78Rxi2RrdgQqwDrKjkCXX6LeQpES1EVRCwfsTqefPDvSV9oi1DwvERvwRvCGFbgvbqbfusCN29HN5rukngGkp7U5EVHF",
                "12RwumVV4Q84rKknv24yATBeQmu9rtEMro91BuKhLnpnRsR1iaXBRtrWJZ6Mg2rFCfauvNvhjkhVKbYJYMW6bQAWbAj11UTo2Dy3XeT",
                "12RqFNrzjApKLSxg786YmRQwq46LqbJKpPbLXUZTH7rbzxJ55nyiPWFEQbg6ZGjWmefNo3rp8LSLe8JTRw17vc3NszuJSkHg4Mm54xU",
                "12Rrz9C7QcD3x5sCyp8o9a3nc3HCPasqtWJZnsb5B5wiaDx38rE7Je2oJdWr1DQMjiPrN8GG1ZHqxVNydL8RCqf4FRdzMzfJoBf5NKz"

            ]
        }
    }

    ### ENVIRONMENT SETUP:
    fullnode = DEX(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    fullnode_trx = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    fullnode_ws = WebSocket(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['ws'])
    # shard0 = DEX(NodeList.shard0[3]['ip'], NodeList.shard0[3]['rpc'])
    # shard0_trx = Transaction(NodeList.shard0[3]['ip'], NodeList.shard0[3]['rpc'])
    # shard7 = DEX(NodeList.shard7[3]['ip'], NodeList.shard7[3]['rpc'])
    # shard7_trx = Transaction(NodeList.shard7[3]['ip'], NodeList.shard7[3]['rpc'])
    shard0 = DEX(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard0_trx = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard7 = DEX(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard7_trx = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])

    def cal_actualReceived(self, trade_amount, pool_token2Sell, pool_token2Buy):
        remain = (pool_token2Buy * pool_token2Sell) / (trade_amount + pool_token2Sell)
        # print("-remain before mod: " + str(remain))
        if (pool_token2Buy * pool_token2Sell) % (trade_amount + pool_token2Sell) != 0:
            remain = math.floor(remain) + 1
            # print("-remain after mod: " + str(remain))

        received_amount = pool_token2Buy - remain
        print("-expecting received amount: " + str(received_amount))
        return received_amount

    def cal_actualContribution(self, contribution_token1_amount, contribution_token2_amount, token1_pool, token2_pool):
        actual_contribution_token1 = min(contribution_token1_amount,
                                         math.floor(contribution_token2_amount * token1_pool / token2_pool))
        print("actual_contribution_token1 in min: %d" % actual_contribution_token1)
        actual_contribution_token2 = math.floor(actual_contribution_token1 * token2_pool / token1_pool)
        print("actual_contribution_token2 in mul: %d" % actual_contribution_token2)

        if actual_contribution_token1 == contribution_token1_amount:
            actual_contribution_token1 = math.floor(actual_contribution_token2 * token1_pool / token2_pool)
            print("actual_contribution_token1 in iff: %d" % actual_contribution_token1)

        refund_token1 = contribution_token1_amount - actual_contribution_token1
        refund_token2 = contribution_token2_amount - actual_contribution_token2
        return actual_contribution_token1, actual_contribution_token2, \
               refund_token1, refund_token2

    @pytest.mark.run
    def test_DEX10_contributePRV(self):
        print("""
        test_DEX01_contribute:
        - contribute a pair of token 797d79 vs 000004
        - checking token rate after contribute
        - check share amount after contribute
        - check the amount of refund and the actual amount contribution
        """)
        STEP(0, "Checking env - checking waiting contribution list, pDEX share amount")
        assert_true(self.fullnode.get_waitingContribution(self.testData['797d79'],
                                                          self.testData['token_ownerPaymentAddress'][0]) == False,
                    "Found 797d79")
        assert_true(self.fullnode.get_waitingContribution(self.testData['000004'],
                                                          self.testData['token_ownerPaymentAddress'][0]) == False,
                    "Found 000004")
        balance_797d79_B = self.fullnode_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                    self.testData['797d79'])[0]
        balance_000004_B = self.fullnode_trx.getBalance(self.testData['token_ownerPrivateKey'][0])
        owner_shareamount_B = self.fullnode.get_pdeshares(self.testData['000004'], self.testData['797d79'],
                                                          [self.testData['token_ownerPaymentAddress'][0]] +
                                                          self.testData['paymentAddr'][0] +
                                                          self.testData['paymentAddr'][5] +
                                                          self.testData['paymentAddr'][9])
        INFO("797d79 balance before contribution: " + str(balance_797d79_B))
        INFO("000004 balance before contribution: " + str(balance_000004_B))
        INFO("owner_shareamount before contribution: " + str(owner_shareamount_B))
        rate_B = self.fullnode.get_latestRate(self.testData["000004"], self.testData["797d79"])
        INFO("rate 000004 vs 797d79 before contribute : " + str(rate_B))

        STEP(1, "Contribute 797d79")
        contribute_token1 = self.fullnode.contribute_token(self.testData['token_ownerPrivateKey'][0],
                                                           self.testData['token_ownerPaymentAddress'][0],
                                                           self.testData['797d79'],
                                                           self.testData['amount_contribution_797d79'], "797d79_PRV")
        INFO("Contribute 797d79 Success, TxID: " + contribute_token1)
        ws_tx1 = self.fullnode_ws.subcribePendingTransaction(contribute_token1)
        tx_fee = ws_tx1[2]

        STEP(2, "Verifying contribution 797d79")
        step2_result = False
        for i in range(0, 10):
            WAIT(10)
            if self.fullnode.get_waitingContribution(self.testData['797d79'],
                                                     self.testData['token_ownerPaymentAddress'][0]):
                step2_result = True
                INFO("The 797d79 found in waiting contribution list")
                break
        assert_true(step2_result == True, "The 797d79 NOT found in waiting contribution list")

        STEP(3, "Contribute PRV")
        contribute_token2 = self.fullnode.contribute_prv(self.testData['token_ownerPrivateKey'][0],
                                                         self.testData['token_ownerPaymentAddress'][0],
                                                         self.testData['amount_contribution_000004'], "797d79_PRV")

        INFO("Contribute PRV Success, TxID: " + contribute_token2)
        ws_tx2 = self.fullnode_ws.subcribePendingTransaction(contribute_token2)
        tx_fee = tx_fee + ws_tx2[2]

        STEP(4, "Verifying 797d79 disappeared in waiting list")
        step4_result = False
        for i in range(0, 10):
            WAIT(10)
            if not self.fullnode.get_waitingContribution(self.testData['797d79'],
                                                         self.testData['token_ownerPaymentAddress'][0]):
                step4_result = True
                INFO("The 797d79 NOT found in waiting contribution list")
                break
        assert_true(step4_result == True, "The 797d79 is still found in waiting contribution list")

        balance_797d79_A = self.fullnode_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                    self.testData['797d79'])[0]
        balance_000004_A = self.fullnode_trx.getBalance(self.testData['token_ownerPrivateKey'][0])
        INFO("797d79 balance after contribution (before refund): " + str(balance_797d79_A))
        INFO("000004 balance after contribution (before refund): " + str(balance_000004_A))

        assert_true((balance_797d79_A + self.testData['amount_contribution_797d79']) == balance_797d79_B,
                    "797d79 balance is wrong")
        assert_true((balance_000004_A + self.testData[
            'amount_contribution_000004'] + tx_fee == balance_000004_B), "000004 balance is wrong")

        STEP(5, "Check rate 797d79 vs 000004")
        rate_A = self.fullnode.get_latestRate(self.testData["000004"], self.testData["797d79"])
        INFO("rate 000004 vs 797d79 after contribute : " + str(rate_A))
        owner_shareamount_A = self.fullnode.get_pdeshares(self.testData['000004'], self.testData['797d79'],
                                                          [self.testData['token_ownerPaymentAddress'][0]] +
                                                          self.testData['paymentAddr'][0] +
                                                          self.testData['paymentAddr'][5] +
                                                          self.testData['paymentAddr'][9])
        INFO("owner_shareamount after contribution: " + str(owner_shareamount_A))

        expect_797d79_contribution, expect_000004_contribution, refund_797d79, refund_000004 = \
            self.cal_actualContribution(
                self.testData['amount_contribution_797d79'], self.testData['amount_contribution_000004'], rate_B[1],
                rate_B[0])

        for _ in range(0, 10):
            WAIT(10)
            balance_797d79_A2 = self.fullnode_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                         self.testData['797d79'])[0]
            if balance_797d79_A2 > balance_797d79_A or refund_797d79 == 0:
                break
        for _ in range(0, 10):
            balance_000004_A2 = self.fullnode_trx.getBalance(self.testData['token_ownerPrivateKey'][0])
            if balance_000004_A2 > balance_000004_A or refund_000004 == 0:
                break
            WAIT(10)
        INFO("Contribution amount submitted 797d79 and 000004: %d & %d " % (
            self.testData['amount_contribution_797d79'], self.testData['amount_contribution_000004']))
        INFO(
            "Expect 797d79 and 000004 contribution: %d & %d" % (expect_797d79_contribution, expect_000004_contribution))

        _, api_contribute_prv, api_return_prv, _, api_contribute_d79, api_return_d79 = \
            self.fullnode.get_contributionStatus(
                "797d79_PRV")

        INFO("From API: %d %d %d %d" % (api_contribute_prv, api_contribute_d79, api_return_prv, api_return_d79))
        INFO(
            "Actual 797d79 and 000004 contribution: %d & %d" % (
                balance_797d79_B - balance_797d79_A2, balance_000004_B - balance_000004_A2 - tx_fee))
        INFO("797d79 balance after contribution (after refund): " + str(balance_797d79_A2))
        INFO("000004 balance after contribution (after refund): " + str(balance_000004_A2))

        assert_true(math.floor(
            (api_contribute_prv * sum(owner_shareamount_B) / rate_B[0])
            + owner_shareamount_B[0]) == owner_shareamount_A[0],
                    "Contribution shares amount is wrong", "Contribution shares amount is correct")
        assert_true(balance_797d79_A2 + api_contribute_d79 == balance_797d79_B,
                    "Balance 797d79 is wrong, refund is wrong", "Balance 797d79 is correct")
        assert_true(balance_000004_A2 + api_contribute_prv + tx_fee == balance_000004_B,
                    "Balance 000004 is wrong, refund is wrong", "Balance 000004 is correct")

    @pytest.mark.run
    def test_DEX11_contributePRV_revert(self):
        print("""
        test_DEX01_contribute_revert:
        - contribute a pair of token 000004 vs 797d79
        - checking token rate after contribute
        - check share amount after contribute
        - check the amount of refund and the actual amount contribution
        """)
        STEP(0, "Checking env - checking waiting contribution list, pDEX share amount")
        assert_true(self.fullnode.get_waitingContribution(self.testData['797d79'],
                                                          self.testData['token_ownerPaymentAddress'][0]) == False,
                    "Found 797d79", "NOT Found 797d79")
        assert_true(self.fullnode.get_waitingContribution(self.testData['000004'],
                                                          self.testData['token_ownerPaymentAddress'][0]) == False,
                    "Found 000004", "NOT Found 000004")
        balance_797d79_B = self.fullnode_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                    self.testData['797d79'])[0]
        balance_000004_B = self.fullnode_trx.getBalance(self.testData['token_ownerPrivateKey'][0])
        owner_shareamount_B = self.fullnode.get_pdeshares(self.testData['000004'], self.testData['797d79'],
                                                          [self.testData['token_ownerPaymentAddress'][0]] +
                                                          self.testData['paymentAddr'][0] +
                                                          self.testData['paymentAddr'][5] +
                                                          self.testData['paymentAddr'][9])
        INFO("797d79 balance before contribution: " + str(balance_797d79_B))
        INFO("000004 balance before contribution: " + str(balance_000004_B))
        INFO("owner_shareamount before contribution: " + str(owner_shareamount_B))
        rate_B = self.fullnode.get_latestRate(self.testData["000004"], self.testData["797d79"])
        INFO("rate 000004 vs 797d79 before contribute : " + str(rate_B))

        STEP(1, "Contribute 000004")
        contribute_token1 = self.fullnode.contribute_prv(self.testData['token_ownerPrivateKey'][0],
                                                         self.testData['token_ownerPaymentAddress'][0],
                                                         self.testData['amount_contribution_000004'], "000004_797d79")
        INFO("Contribute 000004 Success, TxID: " + contribute_token1)
        ws_tx1 = self.fullnode_ws.subcribePendingTransaction(contribute_token1)
        tx_fee = ws_tx1[2]

        STEP(2, "Verifying contribution 000004")
        step2_result = False
        for i in range(0, 10):
            WAIT(10)
            if self.fullnode.get_waitingContribution(self.testData['000004'],
                                                     self.testData['token_ownerPaymentAddress'][0]):
                step2_result = True
                INFO("The 000004 found in waiting contribution list")
                break
        assert_true(step2_result == True, "The 000004 NOT found in waiting contribution list")

        STEP(3, "Contribute 797d79")
        contribute_token2 = self.fullnode.contribute_token(self.testData['token_ownerPrivateKey'][0],
                                                           self.testData['token_ownerPaymentAddress'][0],
                                                           self.testData['797d79'],
                                                           self.testData['amount_contribution_797d79'], "000004_797d79")
        INFO("Contribute 797d79 Success, TxID: " + contribute_token2)
        ws_tx2 = self.fullnode_ws.subcribePendingTransaction(contribute_token2)
        tx_fee = ws_tx2[2] + tx_fee

        STEP(4, "Verifying 000004 disappeared in waiting list")
        step4_result = False
        for i in range(0, 10):
            if not self.fullnode.get_waitingContribution(self.testData['000004'],
                                                         self.testData['token_ownerPaymentAddress'][0]):
                step4_result = True
                INFO("The 000004 NOT found in waiting contribution list")
                break
            WAIT(10)
        assert_true(step4_result == True, "The 000004 is still found in waiting contribution list")

        balance_797d79_A = self.fullnode_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                    self.testData['797d79'])[0]
        balance_000004_A = self.fullnode_trx.getBalance(self.testData['token_ownerPrivateKey'][0])
        INFO("797d79 balance after contribution (before refund): " + str(balance_797d79_A))
        INFO("000004 balance after contribution (before refund): " + str(balance_000004_A))

        assert_true((balance_797d79_A + self.testData['amount_contribution_797d79']) == balance_797d79_B,
                    "797d79 balance is wrong")
        assert_true((balance_000004_A + self.testData['amount_contribution_000004'] + tx_fee == balance_000004_B),
                    "000004 balance is wrong")

        STEP(5, "Check rate 797d79 vs 000004")
        rate_A = self.fullnode.get_latestRate(self.testData["000004"], self.testData["797d79"])
        INFO("rate 000004 vs 797d79 after contribute : " + str(rate_A))
        owner_shareamount_A = self.fullnode.get_pdeshares(self.testData['000004'], self.testData['797d79'],
                                                          [self.testData['token_ownerPaymentAddress'][0]] +
                                                          self.testData['paymentAddr'][0] +
                                                          self.testData['paymentAddr'][5] +
                                                          self.testData['paymentAddr'][9])
        INFO("owner_shareamount after contribution: " + str(owner_shareamount_A))

        expect_000004_contribution, expect_797d79_contribution, refund_000004, refund_797d79 = \
            self.cal_actualContribution(
                self.testData['amount_contribution_000004'], self.testData['amount_contribution_797d79'], rate_B[0],
                rate_B[1])

        STEP(6, "Calculate actual contribution_amount, refund, rate, shares, after contribution")
        for _ in range(0, 10):
            WAIT(10)
            balance_797d79_A2 = self.fullnode_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                         self.testData['797d79'])[0]
            if balance_797d79_A2 > balance_797d79_A or refund_797d79 == 0:
                break
        for _ in range(0, 10):
            balance_000004_A2 = self.fullnode_trx.getBalance(self.testData['token_ownerPrivateKey'][0])
            if balance_000004_A2 > balance_000004_A or refund_000004 == 0:
                break
            WAIT(10)
        INFO("Contribution amount submitted 000004 & 797d79: %d & %d " % (
            self.testData['amount_contribution_000004'], self.testData['amount_contribution_797d79']))
        INFO("Expecting 000004 & 797d79 contribution: %d & %d" % (
            expect_000004_contribution, expect_797d79_contribution))
        INFO("Actual 000004 & 797d79 contribution: %d & %d" % (balance_000004_B - balance_000004_A2 - tx_fee,
                                                               balance_797d79_B - balance_797d79_A2))
        _, api_contribute_prv, api_return_prv, _, api_contribute_d79, api_return_d79 = \
            self.fullnode.get_contributionStatus(
                "797d79_PRV")

        INFO("From API: %d %d %d %d" % (api_contribute_prv, api_contribute_d79, api_return_prv, api_return_d79))
        INFO("797d79 balance after contribution (after refund): " + str(balance_797d79_A2))
        INFO("000004 balance after contribution (after refund): " + str(balance_000004_A2))

        assert_true(math.floor(
            (api_contribute_prv * sum(owner_shareamount_B) / rate_B[0])
            + owner_shareamount_B[0]) == owner_shareamount_A[0],
                    "Contribution shares amount is wrong", "Contribution shares amount is correct")
        assert_true(balance_797d79_A2 + api_contribute_d79 == balance_797d79_B,
                    "Balance 797d79 is wrong, refund is wrong", "Balance 797d79 is correct")
        assert_true(balance_000004_A2 + api_contribute_prv + tx_fee == balance_000004_B,
                    "Balance 000004 is wrong, refund is wrong", "Balance 000004 is correct")

    @pytest.mark.run
    def test_DEX14_bulkSwap_1Shard(self):
        print("""
        test_DEX02_bulkSwap_1Shard:
        - 10 address make trading at same time
        - difference trading fee
        - highest trading fee get better price
        """)

        STEP(0, "Checking balance")
        balance_797d79_B = []
        balance_000004_B = []
        balance_797d79_A = []
        balance_000004_A = []
        privatekey_alias = []
        trading_fee = [7, 2, 1, 6, 9, 2, 3, 5, 8, 4]

        # trade_amount_000004 = self.testData['trade_amount']
        trade_amount_797d79 = self.testData['trade_amount']

        for i in range(0, len(self.testData['privateKey'][0])):
            balance_797d79_temp, _ = self.shard0_trx.get_customTokenBalance(self.testData['privateKey'][0][i],
                                                                            self.testData['797d79'])
            balance_000004_temp = self.shard0_trx.getBalance(self.testData['privateKey'][0][i])

            assert_true(balance_797d79_temp > trade_amount_797d79,
                        "This " + self.testData['privateKey'][0][i][-6:] + " balance 797d79 less than trading amount")

            balance_000004_B.append(balance_000004_temp)
            balance_797d79_B.append(balance_797d79_temp)
            privatekey_alias.append(self.testData['privateKey'][0][i][-6:])

        INFO("Privatekey_alias                  : " + str(privatekey_alias))
        INFO("797d79 balance before trade       : " + str(balance_797d79_B))
        INFO("000004 balance before trade       : " + str(balance_000004_B))
        rate_B = self.fullnode.get_latestRate(self.testData["797d79"], self.testData["000004"])
        INFO("Rate 797d79 vs 000004 - Before Trade : " + str(rate_B))

        # breakpoint()

        STEP(2, "trade 797d79 at same time")
        txid_list = []
        for i in range(0, len(privatekey_alias)):
            trade_txid = self.shard0.trade_token(self.testData['privateKey'][0][i],
                                                 self.testData['paymentAddr'][0][i],
                                                 self.testData['797d79'], trade_amount_797d79,
                                                 self.testData['000004'],
                                                 1, trading_fee[i])
            txid_list.append(trade_txid)
        INFO("Transaction id list               : " + str(txid_list))

        STEP(3, "Wait for Tx to be confirmed")
        txfee_list = []
        step3_result = False
        for txid in txid_list:
            print(txid[-6:])
            for i in range(0, 10):
                tx_confirm = self.shard0_trx.get_txbyhash(txid)
                if tx_confirm[0] != "":
                    step3_result = True
                    txfee_list.append(self.shard0_trx.get_txfee(txid)[0])
                    DEBUG("the " + txid + " is confirmed")
                    break
                else:
                    print("shardid: " + str(tx_confirm[1]))
                    WAIT(10)
            assert_true(step3_result == True, "The " + txid + " is NOT yet confirmed")

        STEP(4, "CHECK BALANCE AFTER")
        for i in range(0, len(self.testData['privateKey'][0])):
            tmp_token1Balance_A = False
            for _ in range(0, 10):
                tmp_token1Balance_A = self.shard0_trx.getBalance(self.testData['privateKey'][0][i])
                if tmp_token1Balance_A > balance_000004_B[i]:
                    break
                if i < 3:
                    WAIT(10)
            if tmp_token1Balance_A is not False:
                balance_000004_A.append(tmp_token1Balance_A)
                tmp_token2Balance_A, _ = self.shard0_trx.get_customTokenBalance(self.testData['privateKey'][0][i],
                                                                                self.testData['797d79'])
                balance_797d79_A.append(tmp_token2Balance_A)
            else:
                # ERROR("Wait time expired, 000004 did NOT increasse")
                assert_true(tmp_token1Balance_A != False, "Wait time expired, 000004 did NOT increase")

        INFO("Privatekey_alias                  : " + str(privatekey_alias))
        INFO("797d79 balance after trade        : " + str(balance_797d79_A))
        INFO("000004 balance after trade        : " + str(balance_000004_A))

        STEP(5, "Check rate 797d79 vs 000004")
        rate_A = self.fullnode.get_latestRate(self.testData["797d79"], self.testData["000004"])
        INFO("rate 797d79 vs 000004 - After Trade  : " + str(rate_A))

        STEP(6, "Double check the algorithm ")
        result_797d79 = []
        result_000004 = []
        result_rate = copy.deepcopy(rate_B)
        trade_priority = []

        for i in range(0, len(trading_fee)):
            trade_priority.append(trade_amount_797d79 / trading_fee[i])
        print("Trade Priority: " + str(trade_priority))

        sort_order = sorted(range(len(trade_priority)), key=lambda k: trade_priority[k])
        print("Sort order: " + str(sort_order))

        for order in sort_order:
            print(str(order) + "--")
            received_amount_000004 = self.cal_actualReceived(trade_amount_797d79, result_rate[0], result_rate[1])

            if received_amount_000004 == balance_000004_A[order] - balance_000004_B[order] - txfee_list[order]:
                result_000004.append(str(order) + "Received_True")
            else:
                result_000004.append(str(order) + "Received_False")
                print("  Actual received: %d" % (balance_000004_A[order] - balance_000004_B[order] - txfee_list[order]))

            if trade_amount_797d79 == balance_797d79_B[order] - balance_797d79_A[order] - trading_fee[order]:
                result_797d79.append(str(order) + "Trade_True")
            else:
                result_797d79.append(str(order) + "Trade_False")
                print("  Actual Trade amount: %d " % (
                        balance_797d79_B[order] - balance_797d79_A[order] - trading_fee[order]))

            result_rate[1] = result_rate[1] - received_amount_000004
            result_rate[0] = result_rate[0] + trade_amount_797d79 + trading_fee[order]

        # sort result before print
        result_797d79.sort()
        result_000004.sort()
        INFO("--")
        INFO("tx fee list   : " + str(txfee_list))
        INFO("result_797d79 : " + str(result_797d79))
        INFO("result_000004 : " + str(result_000004))
        INFO("rate 797d79 vs 000004 - Before Trade   : " + str(rate_B))
        INFO("rate 797d79 vs 000004 - After Trade    : " + str(rate_A))
        INFO("rate 797d79 vs 000004 - Calulated Trade: " + str(result_rate))
        assert_true(result_rate == rate_A, "Pair Rate is WRONG after Trade", "Pair Rate is correct")

    @pytest.mark.run
    def test_DEX15_bulkSwap_nShard(self):
        print("""
                test_DEX15_bulkSwap_nShard:
                - 10 address make trading at same time
                - difference trading fee
                - highest trading fee get better price
                """)

        STEP(0, "Checking balance")
        balance_797d79_B = []
        balance_000004_B = []
        balance_797d79_A = []
        balance_000004_A = []
        privatekey_alias = []
        trading_fee = [7, 2, 1, 6, 9, 2, 3, 5, 8, 4]

        trade_amount_000004 = self.testData['trade_amount']
        # trade_amount_797d79 = self.testData['trade_amount']

        for i in range(0, len(self.testData['privateKey'][8])):
            balance_797d79_temp, _ = self.shard0_trx.get_customTokenBalance(self.testData['privateKey'][8][i],
                                                                            self.testData['797d79'])
            balance_000004_temp = self.shard0_trx.getBalance(self.testData['privateKey'][8][i])

            assert_true(balance_000004_temp > trade_amount_000004,
                        "This " + self.testData['privateKey'][8][i][-6:] + " balance 797d79 less than trading amount")

            balance_000004_B.append(balance_000004_temp)
            balance_797d79_B.append(balance_797d79_temp)
            privatekey_alias.append(self.testData['privateKey'][8][i][-6:])

        INFO("Privatekey_alias                  : " + str(privatekey_alias))
        INFO("797d79 balance before trade       : " + str(balance_797d79_B))
        INFO("000004 balance before trade       : " + str(balance_000004_B))
        rate_B = self.fullnode.get_latestRate(self.testData["000004"], self.testData["797d79"])
        INFO("Rate 000004 vs 797d79 - Before Trade : " + str(rate_B))

        # breakpoint()

        STEP(2, "trade 000004 at same time")
        txid_list = []
        for i in range(0, len(privatekey_alias)):
            trade_txid = self.shard0.trade_prv(self.testData['privateKey'][8][i],
                                               self.testData['paymentAddr'][8][i],
                                               trade_amount_000004,
                                               self.testData['797d79'],
                                               1, trading_fee[i])
            txid_list.append(trade_txid)
        INFO("Transaction id list               : " + str(txid_list))

        STEP(3, "Wait for Tx to be confirmed")
        tx_fee_list = []
        step3_result = False
        for txid in txid_list:
            print(txid[-6:])
            for i in range(0, 10):
                tx_confirm = self.shard0_trx.get_txbyhash(txid)
                if tx_confirm[0] != "":
                    step3_result = True
                    tx_fee, _ = self.shard0_trx.get_txfee(txid)
                    tx_fee_list.append(tx_fee)
                    DEBUG("the " + txid + " is confirmed, tx fee: " + str(tx_fee))
                    break
                else:
                    print("shardid: " + str(tx_confirm[1]))
                    WAIT(10)
            assert_true(step3_result == True, "The " + txid + " is NOT yet confirmed")

        STEP(4, "CHECK BALANCE AFTER")
        for i in range(0, len(self.testData['privateKey'][8])):
            tmp_token2Balance_A = False
            for _ in range(0, 10):
                tmp_token2Balance_A, _ = self.shard0_trx.get_customTokenBalance(self.testData['privateKey'][8][i],
                                                                                self.testData['797d79'])
                if tmp_token2Balance_A > balance_797d79_B[i]:
                    break
                if i < 3:
                    WAIT(10)
            if tmp_token2Balance_A is not False:
                balance_797d79_A.append(tmp_token2Balance_A)
                tmp_token1Balance_A = self.shard0_trx.getBalance(self.testData['privateKey'][8][i])
                balance_000004_A.append(tmp_token1Balance_A)
            else:
                assert_true(tmp_token2Balance_A != False, "Wait time expired, 797d79 did NOT increase")

        INFO("Privatekey_alias                  : " + str(privatekey_alias))
        INFO("797d79 balance after trade        : " + str(balance_797d79_A))
        INFO("000004 balance after trade        : " + str(balance_000004_A))

        STEP(5, "Check rate 797d79 vs 000004")
        rate_A = self.fullnode.get_latestRate(self.testData["000004"], self.testData["797d79"])
        INFO("rate 000004 vs 797d79 - After Trade  : " + str(rate_A))

        STEP(6, "Double check the algorithm ")
        result_797d79 = []
        result_000004 = []
        result_rate = copy.deepcopy(rate_B)
        trade_priority = []

        for i in range(0, len(trading_fee)):
            trade_priority.append(trade_amount_000004 / trading_fee[i])
        print("Trade Priority: " + str(trade_priority))

        sort_order = sorted(range(len(trade_priority)), key=lambda k: trade_priority[k])
        print("Sort order: " + str(sort_order))

        for order in sort_order:
            print(str(order) + "--")
            received_amount_797d79 = self.cal_actualReceived(trade_amount_000004, result_rate[0], result_rate[1])

            if received_amount_797d79 == balance_797d79_A[order] - balance_797d79_B[order]:
                result_797d79.append(str(order) + "Received_True")
            else:
                result_797d79.append(str(order) + "Received_False")
                print("  Actual received: %d" % (balance_797d79_A[order] - balance_797d79_B[order]))

            if trade_amount_000004 == balance_000004_B[order] - balance_000004_A[order] - trading_fee[order] - \
                    tx_fee_list[order]:
                result_000004.append(str(order) + "Trade_True")
            else:
                result_000004.append(str(order) + "Trade_False")
                print("  Actual Trade amount: %d " % (
                        balance_000004_B[order] - balance_000004_A[order] - trading_fee[order] - tx_fee_list[order]))

            result_rate[1] = result_rate[1] - received_amount_797d79
            result_rate[0] = result_rate[0] + trade_amount_000004 + trading_fee[order]

        # sort result before print
        result_797d79.sort()
        result_000004.sort()

        INFO("---")
        INFO("tx fee list: " + str(tx_fee_list))
        INFO("result_797d79 : " + str(result_797d79))
        INFO("result_000004 : " + str(result_000004))
        INFO("rate 797d79 vs 000004 - Before Trade   : " + str(rate_B))
        INFO("rate 797d79 vs 000004 - After Trade    : " + str(rate_A))
        INFO("rate 797d79 vs 000004 - Calulated Trade: " + str(result_rate))
        assert_true(result_rate == rate_A, "Pair Rate is WRONG after Trade", "Pair Rate is correct")

    @pytest.mark.run
    def test_DEX16_addLiquidity_nshard(self):
        print("""
            test_DEX03_addLiquidity_1shard
            - 1shard, 10 contribution at a time
            """)
        STEP(0, "Calculate contribution pair")
        commit_797d79_B = []
        commit_000004_B = []
        balance_797d79_B = []
        balance_000004_B = []
        balance_797d79_A = []
        balance_000004_A = []
        privatekey_alias = []
        # share_797d79_B = []
        # share_797d79_A = []
        rate_B = self.fullnode.get_latestRate(self.testData["797d79"], self.testData["000004"])

        for i in range(0, len(self.testData['privateKey'][8])):
            balance_797d79_temp = self.fullnode_trx.get_customTokenBalance(self.testData['privateKey'][8][i],
                                                                           self.testData['797d79'])[0]

            balance_000004_temp = self.fullnode_trx.getBalance(self.testData['privateKey'][8][i])

            ## commit_000004_temp = math.floor(balance_000004_temp * 0.1)  ## contribute 10% balance
            commit_797d79_temp = math.floor(balance_797d79_temp * 0.1)  ## contribute 10% balance

            commit_000004_temp = math.floor(commit_797d79_temp * rate_B[1] / rate_B[0])
            assert_true(commit_000004_temp != 0, "commit f2b %d is Zer0" % i)
            assert_true(commit_797d79_temp != 0, "commit d79 %d is Zer0" % i)
            balance_797d79_B.append(balance_797d79_temp)
            balance_000004_B.append(balance_000004_temp)
            commit_797d79_B.append(commit_797d79_temp)
            commit_000004_B.append(commit_000004_temp)
            privatekey_alias.append(self.testData['privateKey'][0][i][-6:])

        share_797d79_B = self.fullnode.get_pdeshares(self.testData['797d79'], self.testData['000004'],
                                                     [self.testData['token_ownerPaymentAddress'][0]] +
                                                     self.testData['paymentAddr'][0] +
                                                     self.testData['paymentAddr'][5] +
                                                     self.testData['paymentAddr'][8])
        share_l0_797d79_B = self.fullnode.get_pdeshares(self.testData['797d79'], self.testData['000004'],
                                                        self.testData['paymentAddr'][0])

        INFO("Private key_alias                 : " + str(privatekey_alias))
        INFO("797d79 amount to commit           : " + str(commit_797d79_B))
        INFO("000004 amount to commit           : " + str(commit_000004_B))
        INFO("797d79 balance                    : " + str(balance_797d79_B))
        INFO("000004 balance                    : " + str(balance_000004_B))
        INFO("797d79 share amount before commit : " + str(share_797d79_B))

        STEP(1, "Contribute 000004")
        for i in range(0, len(self.testData['privateKey'][8])):
            contribute_000004 = self.fullnode.contribute_prv(self.testData['privateKey'][8][i],
                                                             self.testData['paymentAddr'][8][i],
                                                             commit_000004_B[i], privatekey_alias[i])
            INFO(str(i) + "-Contribute 000004 Success, TxID: " + contribute_000004)

        # breakpoint()

        STEP(2, "Verifying contribution 000004")
        WAIT(20)
        for i in range(0, len(self.testData['privateKey'][8])):
            step2_result = False
            for _ in range(0, 10):
                if self.fullnode.get_waitingContribution(self.testData['000004'],
                                                         self.testData['paymentAddr'][8][i]):
                    step2_result = True
                    INFO(str(i) + "-The 000004 found in waiting contribution list")
                    break
                WAIT(20)
            assert_true(step2_result == True, "The 000004 NOT found in waiting contribution list")

        # breakpoint()

        STEP(3, "Contribute 797d79")
        for i in range(0, len(self.testData['privateKey'][8])):
            contribute_797d79 = self.fullnode.contribute_token(self.testData['privateKey'][8][i],
                                                               self.testData['paymentAddr'][8][i],
                                                               self.testData['797d79'],
                                                               commit_797d79_B[i], privatekey_alias[i])
            INFO(str(i) + "-Contribute 797d79 Success, TxID: " + contribute_797d79)

        STEP(4, "Verifying 000004 disappeared in waiting list")
        for i in range(0, len(self.testData['privateKey'][8])):
            step4_result = False
            for _ in range(0, 10):
                if not self.fullnode.get_waitingContribution(self.testData['000004'],
                                                             self.testData['paymentAddr'][8][i]):
                    step4_result = True
                    INFO(str(i) + "-The 000004 NOT found in waiting contribution list")
                    break
                WAIT(15)
            assert_true(step4_result == True, "The 000004 is still found in waiting contribution list")

        STEP(5, "Double check balance after contribution")
        WAIT(30)
        for i in range(0, len(self.testData['privateKey'][8])):
            balance_797d79_A.append(self.fullnode_trx.get_customTokenBalance(self.testData['privateKey'][8][i],
                                                                             self.testData['797d79'])[0])
            balance_000004_A.append(self.fullnode_trx.getBalance(self.testData['privateKey'][8][i]))
        share_797d79_A = self.fullnode.get_pdeshares(self.testData['797d79'], self.testData['000004'],
                                                     [self.testData['token_ownerPaymentAddress'][0]] +
                                                     self.testData['paymentAddr'][0] +
                                                     self.testData['paymentAddr'][5] +
                                                     self.testData['paymentAddr'][8])
        share_l0_797d79_A = self.fullnode.get_pdeshares(self.testData['797d79'], self.testData['000004'],
                                                        self.testData['paymentAddr'][0])
        print("\nSUMMARY:")
        INFO("797d79 balance before contribution: " + str(balance_797d79_B))
        INFO("797d79 amount committing          : " + str(commit_797d79_B))
        INFO("797d79 balance after contribution : " + str(balance_797d79_A))
        INFO("000004 balance before contribution: " + str(balance_000004_B))
        INFO("000004 amount committing          : " + str(commit_000004_B))
        INFO("000004 balance after contribution : " + str(balance_000004_A))
        INFO("797d79 share amount before commit : " + str(share_797d79_B))
        INFO("797d79 share amount after contrib : " + str(share_797d79_A))

        STEP(6, "Check rate 797d79 vs 000004")
        rate_A = self.fullnode.get_latestRate(self.testData["797d79"], self.testData["000004"])
        INFO("rate 797d79 vs 000004" + str(rate_A))

        # expect_f2b = []
        # expect_d79 = []
        contribution_total_d79 = 0
        contribution_total_004 = 0
        for i in range(0, len(self.testData['privateKey'][8])):
            # expect_f2b_temp, expect_d79_temp, refund_f2b, refund_d79 = self.cal_actualContribution(
            # balance_000004_B[i],
            #                                                                                        commit_797d79_B[i],
            #                                                                                        rate_B[1],
            #                                                                                        rate_B[0])
            # print("%d: %d %d %d %d" % (i, expect_d79_temp, expect_f2b_temp, refund_d79, refund_f2b))
            # expect_f2b.append(expect_f2b_temp)
            # expect_f2b.append(expect_d79_temp)
            _, actual1, refund1, _, actual2, refund2 = self.fullnode.get_contributionStatus(privatekey_alias[i])
            print("%d-%s from api: %d %d %d %d" % (i, privatekey_alias[i], actual1, actual2, refund1, refund2))
            contribution_total_d79 += actual1
            contribution_total_004 += actual2

        assert_true(rate_B[0] + contribution_total_d79 == rate_A[0], "Rate 79d after contribution is wrong",
                    "Rate 79d after contribution is correct")
        assert_true(rate_B[1] + contribution_total_004 == rate_A[1], "Rate f2b after contribution is wrong",
                    "Rate f2b after contribution is correct")
        # for i in range(0, len(self.testData['privateKey'][0])):
        #     assert_true(balance_797d79_B[i] - expect_d79[i] == balance_797d79_A[i], "balance d79 of %d is wrong" % i,
        #                 "balance d79 of %d is correct" % i)
        #     assert_true(balance_000004_B[i] - expect_f2b[i] == balance_000004_A[i], "balance f2b of %d is wrong" % i,
        #                 "balance f2b of %d is correct" % i)

    @pytest.mark.run
    def test_DEX18_withdrawalLiquidityPRV(self):
        print("""
                    test_DEX05_withdrawalLiquidity:
                    - withdraw token from a contributor
                    - 70% shares
                    """)
        STEP(1, "Get balance before withdraw")
        balance_797d79_B, _ = self.fullnode_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                       self.testData['797d79'])
        balance_000004_B = self.fullnode_trx.getBalance(self.testData['token_ownerPrivateKey'][0])

        # share_797d79_B = self.fullnode.get_pdeshares(self.testData['797d79'], self.testData['000004'],
        #                                              [self.testData['token_ownerPaymentAddress'][0]])

        share_000004_B = self.fullnode.get_pdeshares(self.testData['000004'], self.testData['797d79'],
                                                     [self.testData['token_ownerPaymentAddress'][0]] +
                                                     self.testData['paymentAddr'][0] +
                                                     self.testData['paymentAddr'][5] +
                                                     self.testData['paymentAddr'][9])
        rate_B = self.fullnode.get_latestRate(self.testData["000004"], self.testData["797d79"])
        STEP(2, "Withdraw 70% from 1st share owner")
        withdraw_share = math.floor(share_000004_B[0] * 0.7)
        INFO("withdrawing: %d share" % withdraw_share)
        txid = self.fullnode.withdrawal_contribution(self.testData['token_ownerPrivateKey'][0],
                                                     self.testData['token_ownerPaymentAddress'][0],
                                                     self.testData['000004'],
                                                     self.testData['797d79'],
                                                     withdraw_share)
        ws_tx = self.fullnode_ws.subcribePendingTransaction(txid)
        tx_fee = ws_tx[2]

        STEP(3, "Wait for Tx to be confirmed")
        step3_result = False
        for i in range(0, 10):
            tx_confirm = self.shard0_trx.get_txbyhash(txid)
            if tx_confirm[0] != "":
                step3_result = True
                DEBUG("the " + txid + " is confirmed")
                break
            else:
                print("shardid: " + str(tx_confirm[1]))
                WAIT(10)
        assert_true(step3_result is True, "The " + txid + " is NOT yet confirmed")

        STEP(4, "Verify balance after withdraw")
        balance_000004_A = False
        for _ in range(0, 10):
            balance_000004_A = self.shard0_trx.getBalance(self.testData['token_ownerPrivateKey'][0])
            if balance_000004_A > balance_000004_B:
                break
            WAIT(10)
        if balance_000004_A is not False:
            balance_797d79_A, _ = self.shard0_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                         self.testData['797d79'])
        else:
            # ERROR("Wait time expired, 000004 did NOT increasse")
            assert_true(balance_000004_A != False, "Wait time expired, 000004 did NOT increase")

        share_000004_A = self.fullnode.get_pdeshares(self.testData['000004'], self.testData['797d79'],
                                                     [self.testData['token_ownerPaymentAddress'][0]] +
                                                     self.testData['paymentAddr'][0] +
                                                     self.testData['paymentAddr'][5] +
                                                     self.testData['paymentAddr'][9])
        rate_A = self.fullnode.get_latestRate(self.testData["000004"], self.testData["797d79"])
        actual_withdrawal = min(withdraw_share, share_000004_B[0])
        d79_withdrawal = math.floor(actual_withdrawal * rate_B[1] / sum(share_000004_B))
        prv_withdrawal = math.floor(actual_withdrawal * rate_B[0] / sum(share_000004_B))

        INFO("SUMMARY:")
        INFO("Balance d79 B: %s" % str(balance_797d79_B))
        INFO("Balance d79 A: %s" % str(balance_797d79_A))
        INFO("Balance prv B: %s" % str(balance_000004_B))
        INFO("Balance prv A: %s" % str(balance_000004_A))
        INFO("Withdrawal amount prv & d79: %d vs %d" % (prv_withdrawal, d79_withdrawal))
        INFO("share prv B: %s" % str(share_000004_B))
        INFO("share prv A: %s" % str(share_000004_A))
        INFO("rate 000004 & 797d79 B: " + str(rate_B))
        INFO("rate 000004 & 797d79 A: " + str(rate_A))

        assert_true(balance_797d79_A == d79_withdrawal + balance_797d79_B,
                    "Balance d79 invalid after withdraw %d != %d + %d " % (
                        balance_797d79_A, d79_withdrawal, balance_797d79_B), "balance 79d is correct")
        assert_true(balance_000004_A + tx_fee == prv_withdrawal + balance_000004_B,
                    "Balance prv invalid after withdraw %d + %d != %d + %d" % (
                        tx_fee, balance_000004_A, prv_withdrawal, balance_000004_B), "balance prv is correct")

    @pytest.mark.run
    def test_DEX19_withdrawalLiquidityPRV(self):
        print("""
                    test_DEX05_withdrawalLiquidity:
                    - withdraw token from a contributor
                    - 70% shares
                    """)
        STEP(1, "Get balance before withdraw")
        shard = 0
        acct = 1
        print (self.testData['paymentAddr'][shard][acct])
        print(self.testData['privateKey'][shard][acct])
        balance_797d79_B, _ = self.fullnode_trx.get_customTokenBalance(self.testData['privateKey'][shard][acct],
                                                                       self.testData['797d79'])
        balance_000004_B = self.fullnode_trx.getBalance(self.testData['privateKey'][shard][acct])

        # share_797d79_B = self.fullnode.get_pdeshares(self.testData['797d79'], self.testData['000004'],
        #                                              [self.testData['token_ownerPaymentAddress'][0]])

        share_000004_B = self.fullnode.get_pdeshares(self.testData['000004'], self.testData['797d79'],
                                                     [self.testData['token_ownerPaymentAddress'][0]] +
                                                     self.testData['paymentAddr'][0] +
                                                     self.testData['paymentAddr'][5] +
                                                     self.testData['paymentAddr'][9])
        print(f"total share 0004: {share_000004_B}")
        rate_B = self.fullnode.get_latestRate(self.testData["000004"], self.testData["797d79"])
        STEP(2, "Withdraw 70% from 1st share owner")
        lone_share_B = self.fullnode.get_pdeshares(self.testData['000004'], self.testData['797d79'],
                                                                  self.testData['paymentAddr'][shard])
        print(f"account share: {lone_share_B[acct]}")
        withdraw_share = math.floor(lone_share_B[acct] * 0.7)
        INFO("withdrawing: %d share" % withdraw_share)
        txid = self.fullnode.withdrawal_contribution(self.testData['privateKey'][shard][acct],
                                                     self.testData['paymentAddr'][shard][acct],
                                                     self.testData['000004'],
                                                     self.testData['797d79'],
                                                     withdraw_share)
        ws_tx = self.fullnode_ws.subcribePendingTransaction(txid)
        tx_fee = ws_tx[2]

        STEP(3, "Wait for Tx to be confirmed")
        step3_result = False
        for i in range(0, 10):
            tx_confirm = self.shard0_trx.get_txbyhash(txid)
            if tx_confirm[0] != "":
                step3_result = True
                DEBUG("the " + txid + " is confirmed")
                break
            else:
                print("shardid: " + str(tx_confirm[1]))
                WAIT(10)
        assert_true(step3_result is True, "The " + txid + " is NOT yet confirmed")

        STEP(4, "Verify balance after withdraw")
        balance_000004_A = False
        for _ in range(0, 10):
            balance_000004_A = self.shard0_trx.getBalance(self.testData['privateKey'][shard][acct])
            if balance_000004_A > balance_000004_B:
                break
            WAIT(10)
        if balance_000004_A is not False:
            balance_797d79_A, _ = self.shard0_trx.get_customTokenBalance(self.testData['privateKey'][shard][acct],
                                                                         self.testData['797d79'])
        else:
            # ERROR("Wait time expired, 000004 did NOT increasse")
            assert_true(balance_000004_A != False, "Wait time expired, 000004 did NOT increase")

        share_000004_A = self.fullnode.get_pdeshares(self.testData['000004'], self.testData['797d79'],
                                                     [self.testData['token_ownerPaymentAddress'][0]] +
                                                     self.testData['paymentAddr'][0] +
                                                     self.testData['paymentAddr'][5] +
                                                     self.testData['paymentAddr'][9])
        lone_share_A = self.fullnode.get_pdeshares(self.testData['000004'], self.testData['797d79'],
                                                                    [self.testData['paymentAddr'][shard][acct]])
        rate_A = self.fullnode.get_latestRate(self.testData["000004"], self.testData["797d79"])
        d79_withdrawal = math.floor(withdraw_share * rate_B[1] / sum(share_000004_B))
        prv_withdrawal = math.floor(withdraw_share * rate_B[0] / sum(share_000004_B))

        INFO("SUMMARY:")
        INFO("Balance d79 B: %s" % str(balance_797d79_B))
        INFO("Balance d79 A: %s" % str(balance_797d79_A))
        INFO("Balance prv B: %s" % str(balance_000004_B))
        INFO("Balance prv A: %s" % str(balance_000004_A))
        INFO("Withdrawal amount prv & d79: %d vs %d" % (prv_withdrawal, d79_withdrawal))
        INFO("list share prv B: %s" % str(share_000004_B))
        INFO("list share prv A: %s" % str(share_000004_A))
        INFO("acct share prv B: %s" % str(lone_share_B))
        INFO("acct share prv A: %s" % str(lone_share_A))
        INFO("rate 000004 & 797d79 B: " + str(rate_B))
        INFO("rate 000004 & 797d79 A: " + str(rate_A))

        assert_true(balance_797d79_A == d79_withdrawal + balance_797d79_B,
                    "Balance d79 invalid after withdraw %d != %d + %d " % (
                        balance_797d79_A, d79_withdrawal, balance_797d79_B), "balance 79d is correct")
        assert_true(balance_000004_A + tx_fee == prv_withdrawal + balance_000004_B,
                    "Balance prv invalid after withdraw %d + %d != %d + %d" % (
                        tx_fee, balance_000004_A, prv_withdrawal, balance_000004_B), "balance prv is correct")
