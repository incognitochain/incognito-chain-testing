from Objects.PdexV3Objects import PdeV3State
      # sell   buy
o1 = [1000, 1900]
        # sell      buy
pool = [10000, 20000]
       # 850
o2 = [1000, 1950]
o3 = [950, 2000]
o4 = [900, 1950]
o5 = [1000, 2050]
o6 = [1000, 2000]
o7 = [950, 1805]


data = {
    "pair1": {
        "State": {
            "Token0ID": "0000000000000000000000000000000000000000000000000000000000000004",
            "Token1ID": "92f9e5aa0683568d041af306d8b029f919bb1cd432241fd751b6f0a8ac0ccc98",
            "Token0RealAmount": 5000,
            "Token1RealAmount": 10000,
            "Token0VirtualAmount": 10000,
            "Token1VirtualAmount": 20000,
            "Amplifier": 20000,
            "ShareAmount": 1000000000,
            "LPFeesPerShare": {
                "0000000000000000000000000000000000000000000000000000000000000004": 190000000000
            },
            "ProtocolFees": {
                "0000000000000000000000000000000000000000000000000000000000000004": 0
            },
            "StakingPoolFees": {}
        },
        "Shares": {
            "1d307f116c6374a246345dac7d9c09c1481d93243bcc388da8861603579336c1": {
                "Amount": 1000000000,
                "TradingFees": {},
                "LastLPFeesPerShare": {}
            }
        },
        "Orderbook": {
            "orders": [
                {
                    "Id": "b832a5dbc0dad6fb8d36d56e4754f9a1b8e05ba2ae90e8b149f468cd200d390c",
                    "NftID": "ef72a79eaa139376068e2e6ac949ded22ee6aa1262794802ea59d2402e635961",
                    "Token0Rate": 1000,
                    "Token1Rate": 1900,
                    "Token0Balance": 0,
                    "Token1Balance": 1900,
                    "TradeDirection": 1,
                    "Fee": 0
                },
                {
                    "Id": "a36943bb6aa3a5f6a7bd73e775a7cef07d29d9051797b39d48e9c7ea794c2ffd",
                    "NftID": "ef72a79eaa139376068e2e6ac949ded22ee6aa1262794802ea59d2402e635961",
                    "Token0Rate": 1000,
                    "Token1Rate": 1950,
                    "Token0Balance": 0,
                    "Token1Balance": 1950,
                    "TradeDirection": 1,
                    "Fee": 0
                },
                {
                    "Id": "o3",
                    "NftID": "ef72a79eaa139376068e2e6ac949ded22ee6aa1262794802ea59d2402e635961",
                    "Token0Rate": 950,
                    "Token1Rate": 2000,
                    "Token0Balance": 0,
                    "Token1Balance": 2000,
                    "TradeDirection": 1,
                    "Fee": 0
                },
                {
                    "Id": "o4",
                    "NftID": "ef72a79eaa139376068e2e6ac949ded22ee6aa1262794802ea59d2402e635961",
                    "Token0Rate": 900,
                    "Token1Rate": 1950,
                    "Token0Balance": 0,
                    "Token1Balance": 1950,
                    "TradeDirection": 1,
                    "Fee": 0
                },
                {
                    "Id": "o5",
                    "NftID": "ef72a79eaa139376068e2e6ac949ded22ee6aa1262794802ea59d2402e635961",
                    "Token0Rate": 1000,
                    "Token1Rate": 2050,
                    "Token0Balance": 0,
                    "Token1Balance": 2050,
                    "TradeDirection": 1,
                    "Fee": 0
                },
                {
                    "Id": "o6",
                    "NftID": "ef72a79eaa139376068e2e6ac949ded22ee6aa1262794802ea59d2402e635961",
                    "Token0Rate": 1000,
                    "Token1Rate": 2000,
                    "Token0Balance": 0,
                    "Token1Balance": 2000,
                    "TradeDirection": 1,
                    "Fee": 0
                },
                {
                    "Id": "o7",
                    "NftID": "ef72a79eaa139376068e2e6ac949ded22ee6aa1262794802ea59d2402e635961",
                    "Token0Rate": 950,
                    "Token1Rate": 1805,
                    "Token0Balance": 0,
                    "Token1Balance": 1805,
                    "TradeDirection": 1,
                    "Fee": 0
                }
            ]
        }
    }
}

token_x = "0000000000000000000000000000000000000000000000000000000000000004"
token_y = "92f9e5aa0683568d041af306d8b029f919bb1cd432241fd751b6f0a8ac0ccc98"

pool_b4 = PdeV3State.PoolPairData(data)
print("AMM RATE ", pool_b4.get_pool_rate(token_x))
receive, pool_predict = pool_b4.predict_pool_after_trade(3977, token_x)
print(receive)