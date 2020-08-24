from IncognitoChain.Objects.AccountObject import Account

account_list = \
    [
        Account(
            private_key="112t8rnXVMJJZzfF1naXvfE9nkTKwUwFWFeh8cfEyViG1vpA8A9khJk3mhyB1hDuJ4RbreDTsZpgJK4YcSxdEpXJKMEd8Vmp5UqKWwBcYzxv",
            payment_key="12RyJTSL2G8KvjN7SUFuiS9Ek4pvFFze3EMMic31fmXVw8McwYzpKPpxeW6TLsNo1UoPhCHKV3GDRLQwdLF41PED3LQNCLsGNKzmCE5",
            shard=0),
        Account(
            "112t8rnX6USJnBzswUeuuanesuEEUGsxE8Pj3kkxkqvGRedUUPyocmtsqETX2WMBSvfBCwwsmMpxonhfQm2N5wy3SrNk11eYxEyDtwuGxw2E",
            "12RwbexYzKJwGaJDdDE7rgLEkNC1dL5cJf4xNaQ29EmpPN52C6oepWiTtQCpyHAoo6ZTHMx2Nt3A8p5jYqpYvbrVYGpVTen1rVstCpr",
            shard=0),
        Account(
            "112t8rnXoEWG5H8x1odKxSj6sbLXowTBsVVkAxNWr5WnsbSTDkRiVrSdPy8QfMujntKRYBqywKMJCyhMpdr93T3XiUD5QJR1QFtTpYKpjBEx",
            "12RqmK5woGNeBTy16ouYepSw4QEq28gsv2m81ebcPQ82GgS5S8PHEY37NU2aTacLRruFvjTqKCgffTeMDL83snTYz5zDp1MTLwjVhZS",
            shard=1),
        Account(
            "112t8rnZ5UZouZU9nFmYLfpHUp8NrvQkGLPD564mjzNDM8rMp9nc9sXZ6CFxCGEMuvHQpYN7af6KCPJnq9MfEnXQfntbM8hpy9LW8p4qzPxS",
            "12Rw9oesEgd8t5NGrfqxtWTCzh1eDif55miqZ1kFzj5zeQ6UQnNB9JXRn5Vc5QVbBaiFhoYdYPnQZ5tWwcBpse5EJXM3Av6qEV2wspv",
            shard=2),
        Account(
            "112t8rnan3pbXtdvfKSk3kti1tFcFpVSq5wp7c3hhLk7E4jQih2zsv8ynjpP1UQivExGwbMf9Ezp9qmKBJuHhNZPAzheqX4WTV8LfrdZY5Mh",
            "12RxCyrWFCkpzfnMcnN8MuDrXkFAsEAkhyn4zHhy3n6CNZPYJ4cNDesBGycwu62PJn8rQ8uLiC5zSYDiXFa9hXtQMUJvVCMT2uUNn8G",
            shard=2),
        Account(
            "112t8rnZ9qPE7C6RbrK6Ygat1H94kEkYGSd84fAGiU396yQHu8CBHmV1DDHE947d7orfHnDtKA9WCffDk7NS5zUu5CMCUHK8nkRtrv4nw6uu",
            "12Rrk9r3Chmt5Wibkmu2VcFSUffGZbkz2rzMWdmmB3GEu8t8RF4v2wc1gBQtkJFZmPfUP29bSXR4Wn8kDveLQBTBK5Hck9BoGRnuM7n",
            shard=5,
            validator_key='12RqVU3SmFG8NNVhnC6LhTGyfq5Nk4R5w341Z55JmpVx9PGsfbu'),
        Account(
            "112t8rnaK4C17Chu8rEAPXHUaPYNeGz8VsjV7BzdeLA9VBc8oiYwQXNrc6XEABb4uNEfG9LFgvVfi4KQmVpQrwMWph4E1YoVS1m37HwrFDsE",
            "12RtmaJMoRbUCsYxLC4RatP2vWVR3QdZXpbkXR7LwZjVrZfXF46ZNL4QgpCU71SXjz2eCeruA7ZiHM91otTJXzqJiztq5mrdHA35yaf",
            shard=5,
            validator_key='126svgr8EXp2kW6H9iBa9V5ZCxC8zHeD81iJQVwHHAXGamgdPyb')
    ]

committees = [
    Account(
        '112t8rnqijhT2AqiS8NBVgifb86sqjfwQwf4MHLMAxK3gr1mwxMaeUWQtR1MfxHscrKQ2MsyQMvJ3LEu49LEcZzTzoJCkCiewQ9p6wN5SrG1'),
    Account(
        '112t8rnud1R3of9rPkdKHWy8mQ5gMpXuBjLGhVrNurvHC93fF6qfiaEC8Nf7AHRbgrn1KF33akoNMNqUEUdSU7caXYvRL4uT58fhCuDV2Qs8'),
    Account(
        '112t8rnw7XyoehhKAUbNTqtVcda1eki89zrD2PfGMBKoYHvdE94ApWvXDtJvgotQohRot8yV52RZz2JjPtYGh4xsxb3gahn7RRWocEtW2Vei'),
    Account(
        '112t8ro1sHxz5xDkTs9i9VHA4cXVb5iqwCq2H2ffYYbGRh2wUHSHRRbnSQEMSnGiMvZAFLCccNzjZV9bSrphwGxxgtskVcauKNdgTEqA9bsf'),
    Account(
        '112t8ro424gNfJkKqDj25PjgWqCFTgG83TRERX1djUVr2wgJB6Lwk7NFi4pU8KxWSHsb4xK7UwPVYJ48FEGTzrB9jM58WfyvaJGCsT83jfNs'),
    Account(
        '112t8ro719sBgnX2GouVjLEZUvVwaepg8FkG35GtrFiFHeuE3y47PjXBbxHQdX1z87AAtEH5WCMZ8GUbhaZL3DbJuLqj7AAxGoc85damvB4J'),
    Account(
        '112t8rncy1vEiCMxvev5EkUQyfH9HLeManjS4kbcsSiMgp4FEiddsiMunhYL2pa8wciCAWxYtt9USgCv21fe2PkSxfnRkiq4AmDvJe33wtgV'),
    Account(
        '112t8rndMXjgDEGkuUmVedQxVYuZsQK5UvM9ZR1aZximBuNNJKpBn9j93MRqLBS17mHoCdLQNMmoYyuERZ1M3pRMG8SQj3NraHsG9eZPbbRK'),
    Account(
        '112t8rngznzWowvtXKyTnE9avawQGJCVgfJounHDT5nWucoVFv43TYu9PyjiGpPXXXQbCVEzxxCSfDmPNEBknK5B8n5qFiaddStg2M9pCYkZ'),
    Account(
        '112t8rnk4jduDzQGcmzKXr6r1F69TeQtHqDBCehDXPpwQTo7eDkEKFGMDGar46Jy4gmqSZDgwyUwpnxGkCnE2oEXmQ5FQpQJ4iMpDqLkgzwy'),
    Account(
        '112t8rnkSY1EtXtfZNGTKU6CFhfrdQ2YqLbLpfFEUGzVfoQeC6d47M5jWwv542aHJgEdtBKxmr2aikjxibL75rqGXEyKfUPXg1yp3xnCpL7D'),
    Account(
        '112t8rnmCktTnBnX866sSj5BzU33bUNZozJRes9xL7GPqSTQX9gsqG3qkiizsZuzV7BFs7CtpqNhcWfEMUZkkT7JnzknDB49jD2UBUemdnbK')]

beacons = [
    Account(
        '112t8rncBDbGaFrAE7MZz14d2NPVWprXQuHHXCD2TgSV8USaDFZY3MihVWSqKjwy47sTQ6XvBgNYgdKH2iDVZruKQpRSB5JqxDAX6sjMoUT6'),
    Account(
        '112t8rnfXYskvWnHAXKs8dXLtactxRqpPTYJ6PzwkVHnF1begkenMviATTJVM6gVAgSdXsN5DEpTkLFPHtFVnS5RePi6aqTSth6dP4frcJUT'),
    Account(
        '112t8rngZ1rZ3eWHZucwf9vrpD1DNUAmrTTARSsptNDFrEoHv3QsDY3dZe8LXy3GeKXmeso8nUPsNwUM2qmZibQVXxGzstF4vZsYzJ83scFL'),
    Account(
        '112t8rnpXg6CLjvBg2ZiyMDgpgQoZuAjYGzbm6b2eXVSHUKjZUyb2LVJmJDPw4yNaP5M14DomzC514joTH3EVknRwnnGViWuH2HJuN6cpNhz')]
