import re

from Helpers.KeyListJson import KeyListJson
from Helpers.Logging import INFO
from Objects.AccountObject import Account

list_key_set = [
    {
        "PaymentAddress": "12RuriZuuoYZxkfhGEKbJsxn94MXiMt9aFW2ucreeFYSsvCUZVWKQPX7DrHABJ8ffh7V76QufqPEXMbkdxEMsZPLuXLS8HKAd8ffBxK",
        "PublicKey": "1eej8x3nSfcmknBrR3jkbv97h7GHrJ7sCNLNUoxHqem4fPMe9V",
        "PrivateKey": "112t8sw2apGTwoVT2M6adwp1fQvH5KzVsns5GFFEHzLxKTYpqmVTJVCUTAzfkQDNKUondiV6MBCSk9MVDao5RRwuhdjkScMBZ42YJ3hZb6Db",
        "ValidatorKey": "12kkr7NxhnekKKBcn9RNgR31gy6LxqiX51eoexvPQpToGdxm28k",
        "Staker": 0
    },
    {
        "PaymentAddress": "12RwroRSY4SBfi7kBS3gECXGtDh9rwbuyLWWi2RcZiwD4yJbnY3342AcRQtwGxinMnCHHSCRMbJGaNX3mvq2wYzuDy18jMo7hWQiHqJ",
        "PublicKey": "1tBTU3xmVjjVxfdSCJGZ6k5XR5AjiV5yAVufeTfhji8pHvAHYF",
        "PrivateKey": "112t8sw37yYFcpGhQnNLsHMbBDDSbW27t3YPMLDSK2q2ZmmZ6iSc1d1K5QkCsdsZ5L3YFaLz2R1KZzJHrAxQNefukYvc5hvKgVBFgatYaDtU",
        "ValidatorKey": "12RpaScwxD4xEC5et5UrkStSjTSTd6djFXT52B8M5U8v23bZ9yK",
        "Staker": 1
    },
    {
        "PaymentAddress": "12RtXqisFdNKY3ka7ywVrMEsmfKmLwVs2Jdb2ZfB4RNLwqq8VAiC5Ky3pxaKCvMFr5ZjJnxftDGuaZDw8xjybGztC9qeqbf4jde2ovK",
        "PublicKey": "1Vh3BfZf2TpfwSnbysVJnb7squWvYE3bmvFLbPDdVqSVyJ4Mr9",
        "PrivateKey": "112t8sw3HuTUHxw9U7agDsiBBzoLcjd3Z4o226QzUYHL9sAdHTo82iJ4TaaKZ5ZJzU6EcquxNjGTpxW5kdfrsx1EeRD7WChepy4y4WeUhvXA",
        "ValidatorKey": "1aJCk2HxULpcBADDZu7BxZBivTqMJB4kSAyVJeuJNaBCxTfJ1A",
        "Staker": 2
    },
    {
        "PaymentAddress": "12RujkGjbtA1LMPcCXK8kUhcuevsY6YC7ZhTbYmhBiBCTKeQV7diRACx1idho56U7pXz2UNrBarZNtCZuyzLsL5KsC7aouPjE2s3Wdp",
        "PublicKey": "1dqc5gcUW3wumvJwbBnW8qvZE9qwcBUqHb38RfZ7pLkCxpWz3e",
        "PrivateKey": "112t8sw3X7XahWjLwAjgBe51nF4AKqubXFMAFeumM5ECDr8RFH1FKoqzjRECkuXbqJDGr3sAM3qREixjtMpMgPrg63XdKBGYikiSaH89A53V",
        "ValidatorKey": "1CvVLnKzeWZWGrijrHBo9b5PPy77scgcGhuyPdz6aWGVU9qkji",
        "Staker": 3
    },
    {
        "PaymentAddress": "12S5MhbK68bPdDQo8e6hJkHphr5mP6DXhwVGN6Ay1KY4jhYrY3dSwpV8ZQHMaQGb8EnD7fbr53hjHJC44ab19sQZ1VT9RkDrz19tfTM",
        "PublicKey": "12ksPk9mQGJ45JSax8qS7g6bMxU8JwCqxAbCVGxDxVEXBtvs9ke",
        "PrivateKey": "112t8sw3swjDhYme56xtqu2Zc1CsodJAekC6FL5Lj7QpV7ZY9WvnyrDQc1W3Vim74dcHFR9QZLcu9LkUpDaziTX4bF39gKMBegWVgBDn6nv4",
        "ValidatorKey": "1e2571JcwDa6nxfW66FSA9NpRpvcMowbU1M7vTXvUR6WJa6AjJ",
        "Staker": 4
    },
    {
        "PaymentAddress": "12RuaBJMMibatpFK3mKCFGjuMCZnb1Gkkoe76rpe7eYvLCd1uE1xndK8nRxvSnV36hEW6FH2Em1GEP1PXotFHsJxBeeiNwZr92K9Aiw",
        "PublicKey": "1civT5YoDMjg6jkiGpyjPmVgjhkeyEspnjTKtsnVMchLiyz2ia",
        "PrivateKey": "112t8sw4G9xiRC151H5MWV4Kb1CfXAugPQuecjrnktU7W3JUVqd8LhCMa4jwiqaqnSSdNQvKRTqibA7W9tSKegn16HveZDJs1UC4GP4LiRTn",
        "ValidatorKey": "1eZt6YvHHhiKYBJrCpNj4KnkVNBn46bk11MgokpWYBaPssdBCU",
        "Staker": 5
    },
    {
        "PaymentAddress": "12Rtmcapak2UPVoaRboux2PBtbh4aRuSQyGxga4RDxnRri2r3CCzoppaipsmLtcmFdgjB5JA9YZkWQaiqjp4jiBuB6ResXRYSgAJdbU",
        "PublicKey": "1XJ9WpjdxMnpfxKxSLur499vaMM8tpqwwXtfGpQX3Emm39Vis9",
        "PrivateKey": "112t8sw4ZAc1wwbKog9NhE6VqpEiPii4reg8Zc5AVGu7BkxtPYv95dXRJtzP9CkepgzfUwTseNzgHXRovo9oDb8XrEpb5EgFhKdZhwjzHTbd",
        "ValidatorKey": "15KssSyWEX3Jw49ktvFFH9rhZfiGhCrqB3KXWFTG2WzSmqD9AS",
        "Staker": 6
    },
    {
        "PaymentAddress": "12RtSvkNArzfrppmR5cx67eDtGLGkDzduVjShWP4S8SpLcuPGhLsQVZcAeDZc4yXTPXYjarkssYYQ74Z4qNUjyqM3NF1ubriNB9jv16",
        "PublicKey": "1V7pkR1uRr6oKutV7Hzz1RRR7w8ENLim7eHjzotW8NuMkVPi2c",
        "PrivateKey": "112t8sw4ijTH6E6gbPhCF6y36zijFfb7T1JnU8GWVSMmWMP85zzmjkoLRH4fF5HkJR8W7uqfnDQ19ARtW9mDmvCUviNNdZ3i39PDhXztjfgM",
        "ValidatorKey": "1cJ6MDSA1mSHezUrgvYDE4F1zvR6V3WviArYJUr8NWQmJzHaQN",
        "Staker": 7
    },
    {
        "PaymentAddress": "12RzrDJUdeVaBd2Mfa3BzHL3DpaA59xr7Pje16s6bJ8zuFewK2QGExx8BW6gB3ZsaitdYdD3UAPfY2CSpeb1cZfcNv8sdGwYgsvkKLX",
        "PublicKey": "12EPj68XYXuBzpfjFfesWK1Pf6ywSuVa4mTKeaDshqVo3P8B5Pv",
        "PrivateKey": "112t8sw4uNsCeamWRqU1QLiquPbBfGB7HE8qyd7YsBUjSWf3nhcRmoMfyptRDAatJNWBopRTigciNHcPVoZG3bhMKUhrvv6LSzq8FwSwNvBD",
        "ValidatorKey": "1tN2rcueWU4xaZJMNvn7XHk1ybSqeDKhzbr1G8c4v8nZLnnqQ2",
        "Staker": 8
    },
    {
        "PaymentAddress": "12S2z9ZkBMJX75W1LEN8SLdmYXz3npUiwxPrW4uMeZ8xQeQ9n4rPDK1PoWvqPyePYNaxgMbCmCJv7VNU47L1PcmFMhy3SEoxrZyDXJL",
        "PublicKey": "12UqY13WDhFqvywRbJhHebVursQfzVSnKysTFqrRY8zr6onqgrr",
        "PrivateKey": "112t8sw5AggHj5K7c2gZFqnuUypfRimgLvoxHK8U6yE33wAeU1bV2DLkRVhVDHycwaM5LFwLeVLyMGBCx97FyBx3NTHimNVb9MwjP2BeSDDd",
        "ValidatorKey": "1qjRfdYhLaZS5SETLiEaEod3D8dwJpTRPQGN87gyUrt1G9PEWM",
        "Staker": 9
    },
    {
        "PaymentAddress": "12RpTuUno1eZauWT4TEMvgLekatCQbXRCDEBLCrUMe5RpYN9Wdx7Tjg9v1wnGNu7uMC2jAJWjxQGM7sA6WY7QF8ABAXr3nPJKuk5rVx",
        "PublicKey": "12C7DsiMkLCTsDRhGNzf2jRfg8FVT7aZH61iCS4N3tFmXCtkbK",
        "PrivateKey": "112t8sw5fAsCpef9kSYwit7deNVmwhLs64R6s2cH49rWna8yhyCybKM85sFmegtVnEarWXuaTjvVaxVEu3rDTrz7dyUQcy5m37o3LekSxAWe",
        "ValidatorKey": "12cyENYgnbvBr8xgR7BayWWoZtVXeHGXhY4vhivzf7MuXxBY465",
        "Staker": 10
    },
    {
        "PaymentAddress": "12RtLbrNqUhb4uMeNysWwMDzvfYQmTNyWwSXazEipTkhxzsLDQ7hb2itq2CJ3TV8pC7XS8ax5pZVePjj1L9Q2UrULfPd6yjXfrAYMKX",
        "PublicKey": "1UP4WwiMMYXYFkNr9RxmeTLf1B2WXFvqQr5FL6GXRyj57dYSyE",
        "PrivateKey": "112t8sw5ne46SFtGAvvhDMj31LdhJcqsTnkiSz439WJc7xtLsRDiA8uq2AYaCPhi3a56soeSBdqRSwyWSBajv89GrPsQk2svLUonNBCSvHX9",
        "ValidatorKey": "1zHp2owSB8DfeUAGxmL1DhVoiuqcbN3ZtPtLrXYSZWqKLNqr38",
        "Staker": 11
    },
    {
        "PaymentAddress": "12S1UGwviwAva472pwqbxDKkhBhLRqMrLMN7SQV2dhaCCewU7oKQ3nVZsDXCL5aeNp2kgZsw2ExQYCwFGzcjJeNZEsDAsvRA3FPuvm6",
        "PublicKey": "12JbWgqYRew5xhQbHLWKCxStxdtLQEeYT4ydnTYGQEyMv3b1JUU",
        "PrivateKey": "112t8sw6FFcmpk5XwvnC1jgQSTPeDcvSVQQZpQbodQABHqt2abNSsjBSFummAFrLxnuZzd7KpFbdWg9WX27ECgyczdWog1HUCuQcUWVsXfeS",
        "ValidatorKey": "1bkdB9KSHEmiEuveSqGDYsdYLW2vkAcAuWSLMFq8o1KYorhx2t",
        "Staker": 12
    },
    {
        "PaymentAddress": "12S3C8MBaTjmu5udx3irwGB8C6J5A9iFtpw1C8M4xKvpoFHzvKfeALkZWMZnARbHDGkgHP9SfBTJL5PKnTcTUGgzp6cvT9aBs9Zo3an",
        "PublicKey": "12WEWm99fS1eBSN2Lo943Mz7PMj7vxDLLVbMbV7oWYCgSSgeoyf",
        "PrivateKey": "112t8sw6XHCn6jmMAfC47kvrhRVG4o1zKBA41wxfb53S3tHXLZNyWKZWSgSHnEPAHKyEvvho3b4oKLxfNka5LJttkmmYpzq2Wccn6ohvjvKN",
        "ValidatorKey": "1297Jr4CNbE54Ayg5p9Yf1JPEL5ynP1MCnTvKg7vREU14XUU9Gg",
        "Staker": 13
    },
    {
        "PaymentAddress": "12S2dDHrXfxvec22ypzCVfLE7vKuqQRqY7SF4u35pHuKfVMfL5SzyZmpsNmvSzWkkpqVdtZRjZLmZUJCTvydU5M2RBgq6LyfF1mLfLN",
        "PublicKey": "12SQ1U2YdQ3Bd9NTqkJy6jJTDHNPSBkAZiLRTq7uS7pWFJS82Aj",
        "PrivateKey": "112t8sw6cetGmM3HhBX3M3Sy69HWbHHa3QMmJXAmVs8QwmDJHoWRgkG2a1SWMjRGZ5xQ8vmFqtUnFXGBUH4zk4jva4NL459GPX9BKzgLZGPL",
        "ValidatorKey": "1uKM7hvNpxeEDiEmWYRhFjbaAEuyj3ZGvSiiSTp82DCHKzPyXT",
        "Staker": 14
    },
    {
        "PaymentAddress": "12S4oUiJDT9RuVdfYrwGcPCUBp5f37jEzofrUisxXQkHKSog81AFfzkKF5h2NReeApm1dh8igV1iEMzeY4WPcTof7FsAA45xKAgXBLL",
        "PublicKey": "12h7a43B1wnrC1Lc32EKvHW3Bv3GYQWSeRonVYUYCcxBHhFq6kz",
        "PrivateKey": "112t8sw6zCUr3AHqEDvEwisiAdvueNXBgxF9FncvX7gvB8AZtgjrrKcimuumszHsv1UdjqrFmfWGwK6wZWKwb3vhcmAkWRjL9t3jj2vZc67W",
        "ValidatorKey": "1ndgCrs2tK2D4nFfG4dWBKfKF2Lrvj5cTj7vxgJ9Sz2yQeLrx5",
        "Staker": 15
    },
    {
        "PaymentAddress": "12RthVhBpERzDcGN9psZSAHFx5ZkwmsNDSdcnCxVAgn9QRyWCs6TzhuvDp474TBF7wR8vfR4UaZV35X7EYVt943suPbdCkcAurGwUPu",
        "PublicKey": "1WpJcFXZkVVpjn5HWkUfGyAyu2xGc98MACZDWsBk1FSQ5tA7Ww",
        "PrivateKey": "112t8sw7CFBzQb33w2uZ9s3aEeKVWYx2LEWQNGDLc6aTNEVoWP2dBihDWYs2gcWfKWUVoeVCKKm6WFz1u5V2VqoXrpSZsqguCN3jSG4nAqTR",
        "ValidatorKey": "12S9ZVPLDncsqYcEbtKGcXV2E9SFr1SsGxJK6nprRzuKfnMjJJK",
        "Staker": 16
    },
    {
        "PaymentAddress": "12S5PYNiYoLPGY8fi6AgJ2t77oLbYQEqhYRW3UD6bPL628mSQFZBC6qYU4ZJTV17bnvS1gtUZ4rrbyULBQqXwKBsXbGBP97HDEiZhAK",
        "PublicKey": "12m5qbnRi4pGEAQy5eBNSxEVBX4uVHfvpwaDoVyuVNLwCWnR9F2",
        "PrivateKey": "112t8sw7hxinJWGLEBuKuQBWgHba9tZJjtpb7knf7LkEmuXKPqx46gtj98ch3haxeyfJxNiXFGYMKSkVYDQ5oqCZxhrtr38aPu6QRusfPY9L",
        "ValidatorKey": "12ik8v4e1eouzsoudBfdGuEu3YgphFzsx78fGH7Sh6Kg5mRjFj6",
        "Staker": 17
    },
    {
        "PaymentAddress": "12Rpg3xPHSVGjAc4qgd5nAucnxEKEdbH4X2rMi8ivysUmh4cHRXg6ny9QzWAEkdBteXRWeFN7m9vPWFcv9nKtjayunf3vh828BAa5EC",
        "PublicKey": "13cDWAvedxRmoAxUZUTeCeZYswW8gPUAQpX76k2KuDTbb1hwq2",
        "PrivateKey": "112t8sw7reJJNyymSE5jnotTebGcyFhffceV69x5U9fdpEVxD2T35J3Y9h1Zwv9Z1K8RcJSjaNwTw3LU8FoxtMaNjmvYjiqNE6xjD6Haun1T",
        "ValidatorKey": "134cB6maRK475Sx9a1pZzoq5x7k3Erx375XP5vLkWV55kjt7k6",
        "Staker": 18
    },
    {
        "PaymentAddress": "12RydJL3ZGKiNpARUsParZiG76QXx8fV299XvMp9dngNv8ueAHRDFc84nLhAJUkvnYMza6kdMRShbFFmRzwzSKV8Gio7xarvVVMoZEc",
        "PublicKey": "1268MFJJCidHmUD7c8FTaCwqZggWkpSxoAcuppiL9DiyFLBSPKQ",
        "PrivateKey": "112t8sw8ALu9XTiMmttzhP6qqrJFuEuN54sdQ4S4u9VKW4oXdjus3BTG4PAa7Lv3NZRjHTFPHSxjLX2NcGQHDmfhmjeda45xq5RayTnHK5op",
        "ValidatorKey": "1tasLT7fLncjGCFHAdctkZfL9igatHj2ALH3r1di1wpK9qKZmi",
        "Staker": 19
    },
    {
        "PaymentAddress": "12RvMxuAEBPYdxPr6s1RZstiGXgnu3ZTTKmHUxWqaMjRVNEX8HcSqocYuo6ZQHDkWmPHw1b6JuCZJryzHfUN6vre7xfAK6TUyqfqrnr",
        "PublicKey": "1i4SQCTtfrRSEmqd1rdhTDWgoodmFxdU5NXy6RXmMHCDA8kW9Z",
        "PrivateKey": "112t8sw8Vy9SjrxbdPP7ZHQW9nWhqTMyGMvytz7F4hLLu3D5JSRNg8estbiYrbUe59R5JsiJ4S16WLZnVH5b4P5nPG9nXXP88jXUcWSzXuEP",
        "ValidatorKey": "12KRGCPcgUwrt85ogG8GZSvS7vbmQUYfA4fh7HyqZZM7Wm4k6yu",
        "Staker": 20
    },
    {
        "PaymentAddress": "12RytpdtWBMJcvG5K7SPqh6v8S7H8nchoSH92LoBNuXzaXxkCTzoZfPFKoxjh2JCwyDHJysFCqL2mjmfTikDtMxcmBNnohzdoN4YiUz",
        "PublicKey": "127wHMm3Sn5zEe2qbiZVhTYwUGic1DbNCYtUVoW2uWcT9859nVx",
        "PrivateKey": "112t8sw8mME38xYsgAqor65zSTGT14m8sdeMP8mFqpwDUns8maskZMYKoct3VrN7qsrpXVU6sJ2qjCQR92xeEeTJjGm4DnxYT9FPWzaV6VWQ",
        "ValidatorKey": "12kcDLgqLNJwxfcUmCkkZCbn234uzhv6G3L33NZ2cQYaRsqPVSh",
        "Staker": 21
    },
    {
        "PaymentAddress": "12RqvczDpxXV6NCWwZbkz6uyu7MipCFF1mWSVSZacQjpMgHU9JED3mYY2vcBtxvypGYLkxExzKhtReTjwepmxD33yFNH8CEyowc8GGk",
        "PublicKey": "1C4nhtqoFW3JZfChDDrtnmrvFaUTKQ2XgGagRSiN7n7iZxRYcy",
        "PrivateKey": "112t8sw99iuF9GBoX97ASjo9mzJMnVMujUqnFtGzZiPsgdH88jJYCDDTZL3ecWAGN45nfrwFBxvxy9A1N7VSmvKrpwnicvnYCFmgVL5tTRrA",
        "ValidatorKey": "12s7cmdeUN2KZXhpBZhZVS7R2kT1Rrt1cHzqoZc2gnukJzZj14q",
        "Staker": 22
    },
    {
        "PaymentAddress": "12RqFBp4rio4HcYUpZNHJkuT2e8TENtbSsZNrQZ2wdTst4RWdq76jUcPywo6Pu3suFbfRb5kaMKHyGijaR4LiqNZF94FnT6v4PfemgV",
        "PublicKey": "17UDKdA7Ky3xpF5iqivnXCMXnckRwPN2TnxbfYcm9oySFNGpWJ",
        "PrivateKey": "112t8sw9NJiGqe7iq74AxYypJoJRQjg4LQLCiXkAmyjFnQnLvPLpVsstAuJM1BkNTFFTwLV3J6kKxFiYXdTikmH9pmp3G8vgFoDVZNFmnGSZ",
        "ValidatorKey": "16eSSkQUvMY7NVi7jDFjkfnuM4UbXxvb251phpUFC4bfpU4xmv",
        "Staker": 23
    },
    {
        "PaymentAddress": "12Rxwhoz3UVEr4ojy9LRpGtTrcaSBjmc7i64TR7y4WmbfjHnmhDoAiTbGPYTwhYEUtwTwU8PvYyNTja2Wt4i1MGobvVvQ1diBATYrpR",
        "PublicKey": "121Wghj2hu62gRk6NgnnkygMyqEs6fwoJYfRoaiN7W3QUn5noqi",
        "PrivateKey": "112t8sw9fKe1JtQXZbJQrccwLwBQkrumgsALATXUKSreTJ8YHJ4WaMrSpHqzGfomJAgdhAyKUnNDAFrVgBT9QNi1e5R6MYexnfLEBL1rrMNj",
        "ValidatorKey": "1Fum3DzWEwSgwfeYo9Yc2MwJsfikBomyPbbk9ryLTExNrrgaR8",
        "Staker": 24
    },
    {
        "PaymentAddress": "12Ruxo7KphsCjde1zU9GNHMQrMfa4ypkca4GpJqpc3Z7cjoEoKes8a8QRn3E2bGQDYCXjHAmFpc5cJRjKxwTnCDQxfsbsTUELEhUDG6",
        "PublicKey": "1fMpLBADxqQE93woHK8XqbEup1sqrbJW4riY1Tpj4JoPzahdDk",
        "PrivateKey": "112t8sw9rQWCNSTy7fvYeWGb629Lr65ZPCCRxnt5BR7SkPcEHhfbjZn6isAeGNCoRHnRWYUrSMn8c1R3MduBnPG2vZ2DMEiaEdLSdVXca45y",
        "ValidatorKey": "1x6mzh4sFxT8mXbNy8AtNeo3ef4HzLbPJL4xoRhzREK66j4sM5",
        "Staker": 25
    },
    {
        "PaymentAddress": "12S4zCcwXMXeR1ozcMZCvBueRVFEwAzKCNBny9HjR6rJq71m7ENnYSoFeAhQzVwM5BqMspsyuB2ojfpW6PTmTSGapiESPP9rg3aaBh6",
        "PublicKey": "12iN4ArYuqsGG9dZXgWtEuPw4Gkjf8xnfyE8L81skHrrqtJo7NN",
        "PrivateKey": "112t8swAHqNEnccAwUcb37ZfQFPToKH1xq9RLqS3ANjJsHFdUsfp9RDQK6UMKJY1zxaQAJjz61UkxCMPFPUsrJQLndTYMsbST2GQPAbptPpV",
        "ValidatorKey": "12a844mVRGKPNekCVi671zjjKZRq7xeHsJKyo4er11Uhm5BNy1r",
        "Staker": 26
    },
    {
        "PaymentAddress": "12S1rLxkkZHVKgpFV2r1WWKHxXgAg2nD7XnUTreQpGiun8N1472HWfSwK8wmTQW5jeM9adNgvgmiJFwVXyHpryJWYQ9qshoqBo3g7CG",
        "PublicKey": "12MAhdSqRiBKimojvebvS6V4am36vMPcWo19Neo2Rr93nnz63t6",
        "PrivateKey": "112t8swAVfgtRZ2b9P7RqMx3e6rVZMTMggR74quRdw7RkNCsTkSB812CatQYRLvNCWjcvYfBMifyVfhY7WcrSsXXDiYsnCEWrrCfoUjVfN1Z",
        "ValidatorKey": "1xSVvgdxqKSTTVERX5VgBcWN31mf1eqo3UF4qNbUagZJScXePK",
        "Staker": 27
    },
    {
        "PaymentAddress": "12S2VxVN7KJLruVU6o4ydKnmSf4y3bb3Ln6aMAgPLTD2Jk65SA5gHs2pKoopi3y6b5SR7oGwRryAPbsHyuwa5ouQL1u23FzZAsKQk37",
        "PublicKey": "12RYxqJAeKXVC4PjEf7qHHroCV7ZFMcYP6aT9UZEHAT9pty4x13",
        "PrivateKey": "112t8swAiegrqgrU9KzzU3YYitbQX982nq5777ChkVADVYpE6YmbUxtZzocU1ohMVoHy3paBf64NDJaqds2Aw4ftkLjt2yG76rr7swwMhro1",
        "ValidatorKey": "12aeXLdwRJzWPHAMDRS7cJBNr4fcW1rrXCd18Xi18WMjasXy6WD",
        "Staker": 28
    },
    {
        "PaymentAddress": "12RpLf4zEwZxwYigjxaKvbyxWLdj9mmniMVy3PCwyh63X3VjT7dhb94YcRuDv6zGLiajDuiW8depXsqmgMVvNUY3n1zjqmeJG1CzjfF",
        "PublicKey": "11M7EWeC4EEinEtZ49b4LpuJDgX6ifdSjDDKAbqp7zFzWDhr2i",
        "PrivateKey": "112t8swB9LSXHp1VdaTWcJGNrvsu6BWL35qCe4KaYwoJ6YdYmcjsd6p5kJmo5iyfopMMdUuaXvCxLurhTHChs6Lv2MsCX71o57kT1757wZ9X",
        "ValidatorKey": "12GMnyGqhx1coEpGroVnzqGdJtRcqqt4bzzzcjSoG9BzjRARGtX",
        "Staker": 29
    },
    {
        "PaymentAddress": "12Rqw9E1aJHbSsdzJr4i4unWtZnaTynmt2yQeV8MBvodtKc6k8KmuAC2NfD45cQwcVgVjF3gzS3s439HEGvdU596X7Jya1s4uva6Tq5",
        "PublicKey": "1C8K7Zumk5pziyuNZyesbkJMwDoRWw1MCpXXaGRLHASibVSrwj",
        "PrivateKey": "112t8swBRGz2bxjASrQoNAU3P6pqRm8tnPfcDpcjqyWm9xNUTudEvBbiD2ChV4MEqKcc3ib6oGz1Bf8UzANkQ815YjSuUW7Kq4PrXJ6XyPFK",
        "ValidatorKey": "1DQtBE7LAnoLgsUTuemaBW8qrz8CtGASQ9p4fFvnKFYMBRttwh",
        "Staker": 30
    },
    {
        "PaymentAddress": "12RupAg6Tdkpc7Upq99rBsprs1LjXgBfZaga6SJueTCCu7L1ocDGTmW9Fup6rbJjEJSj7kCHnHonzxKUn1KK5rSVBcnrnuKCZkczn7m",
        "PublicKey": "1eMVNbd6gotQWb97JfG4UR4ZZmLxUxeVRAJmJXejGQYYrwwxW6",
        "PrivateKey": "112t8swBaZpuEmoW5CHUc5Lh4WJBMne21NEbM5UtCSbm9oJXjzt4oKicHMbEGd37K3N71o5NEETCryXJ53N6jnxgvidg6HH7EMHcpVpAAvSU",
        "ValidatorKey": "12t8QL7pSVFpQjj2mni62gzkVbMAm8RUdY1d1CUTMx4V9v874UM",
        "Staker": 31
    },
    {
        "PaymentAddress": "12Rxz87ShNnZGtuod86LYPgN2buEtiemn9JoxhhMurNMaGG2UVSdZ2LvSuvY3L3mJUFjzUfs7oeNNUSboHj4uz8bA7mquJ18FeVGLLM",
        "PublicKey": "121o39EmLDeTStuqyBZrpBe9gpEkjeNdJbASZqZbuv72rEjGcBi",
        "PrivateKey": "112t8swBqLmEqWSE6S18f8yRSPH8ohSY5dW4vE7VsNpuwa74wanrQRA8pQCaEbFsTRVeXYxFC8VsmuwqkUARg9J93X2Hk7hbXPrnJV3fp2K1",
        "ValidatorKey": "12ZDpFzEa5TNuyjVBqGg1wCSp9oyjWC1sW9dPQpZSgevepG8e5p",
        "Staker": 32
    },
    {
        "PaymentAddress": "12RxNuVw2FN6JVZGBNyXsazedqsVPDMBmenUi9ung7JzCi8jLmrWZfzvbdxo4HJSAgKbJZj3KoyWMsSvCq32X1BtzwSeagjonrWYLW7",
        "PublicKey": "1wgy1er3VWunNWMC3RQLLHvAKVkhPFd3NkmJfcHpvAi6ev84nd",
        "PrivateKey": "112t8swCCLU78Quq6M6ZFU555SQDgBrHiwd5dKTuA6rDvBLuVEzFcwYYndvmkAX7Y2V6hwwv9CKKSKmyb7wZoEzoKTEJaje89iZANjieA164",
        "ValidatorKey": "1UwiyTpuvL2maULyTNhmHnPn7U7NyREWTmHvqQa6WEkE8UiBDV",
        "Staker": 33
    },
    {
        "PaymentAddress": "12Ry4nuDtxYbQ6WJHUcbtKXzKjkfEYyZxFazeYVGDmuG5wBLipD8HE4zcXX1E8NfyU8q2L8Rie69mZh2B53hdddi5AU74tnsHniUpTp",
        "PublicKey": "122LbgrkQ9DSYMneMzNYRfH4Y8wgXo4sapL5RbT6KC6qAtiSui1",
        "PrivateKey": "112t8swCSXZ2JZkkNxmKVdVKVvn5htkuHNsseLnDeRB8UdZGyg1pQBm3grfkbkk212Rv5s8vX5SBCxsh1B4rLiiBB8Eqt82mPPUo5fAnpED4",
        "ValidatorKey": "12XWkn9p2aDXB8jzGkn43JPckGhn6TiyqYYpxdYLq7NmW3ugZ5A",
        "Staker": 34}
]


def test_convert_from_list_key_set():
    """
    @return:
    Account("112t8sw2apGTwoVT2M6adwp1fQvH5KzVsns5GFFEHzLxKTYpqmVTJVCUTAzfkQDNKUondiV6MBCSk9MVDao5RRwuhdjkScMBZ42YJ3hZb6Db"),
    Account("112t8sw2apGTwoVT2M6adwp1fQvH5KzVsns5GFFEHzLxKTYpqmVTJVCUTAzfkQDNKUondiV6MBCSk9MVDao5RRwuhdjkScMBZ42YJ3hZb6Db")
    """
    str_list_acc = ''
    for i in list_key_set:
        pr = i["PrivateKey"]
        str_list_acc += f'Account("{pr}"),'
    INFO(str_list_acc)
    return str_list_acc


string = """
20335
Profiling=11131 ./incognito --datadir data/staker_0 --rpclisten 0.0.0.0:10335 --listen 0.0.0.0:10452 --miningkeys "12kkr7NxhnekKKBcn9RNgR31gy6LxqiX51eoexvPQpToGdxm28k" --discoverpeersaddress 0.0.0.0:9330 --externaladdress 0.0.0.0:10452 --loglevel debug --relayshards all --norpcauth &

20336
Profiling=11132 ./incognito --datadir data/staker_1 --rpclisten 0.0.0.0:10336 --listen 0.0.0.0:10453 --miningkeys "12RpaScwxD4xEC5et5UrkStSjTSTd6djFXT52B8M5U8v23bZ9yK" --discoverpeersaddress 0.0.0.0:9330 --externaladdress 0.0.0.0:10453 --loglevel debug --relayshards all --norpcauth &
"""


def _test_convert_from_string_run_node():
    """
    @return:
    Account("112t8sw2apGTwoVT2M6adwp1fQvH5KzVsns5GFFEHzLxKTYpqmVTJVCUTAzfkQDNKUondiV6MBCSk9MVDao5RRwuhdjkScMBZ42YJ3hZb6Db"),
    Account("112t8sw2apGTwoVT2M6adwp1fQvH5KzVsns5GFFEHzLxKTYpqmVTJVCUTAzfkQDNKUondiV6MBCSk9MVDao5RRwuhdjkScMBZ42YJ3hZb6Db")
    """
    list_raw = string.split('\n')
    list_all = []
    list_validator_key = []
    list_acc = []
    str_list_acc = ''
    for i in list_raw:
        pattern = re.compile(r"--miningkeys \"*(\w+)\"*")
        t = re.findall(pattern, i)
        list_all.append(t)
    for j in list_all:
        if j:
            list_validator_key.append(j[0])
    for key in list_validator_key:
        key_list_file = KeyListJson()
        acc_group = key_list_file.get_staker_accounts()
        acc = acc_group.find_account_by_key(key)
        str_list_acc += f'Account("{acc.private_key}"),'
    INFO(str_list_acc)
    return str_list_acc


private_k_str = """112t8rnXi8eKJ5RYJjyQYcFMThfbXHgaL6pq5AF5bWsDXwfsw8pqQUreDv6qgWyiABoDdphvqE7NFr9K92aomX7Gi5Nm1e4tEoV3qRLVdfSR
112t8rnY42xRqJghQX3zvhgEa2ZJBwSzJ46SXyVQEam1yNpN4bfAqJwh1SsobjHAz8wwRvwnqJBfxrbwUuTxqgEbuEE8yMu6F14QmwtwyM43"""


def test_convert_to_list_key_set():
    """
    @return:
    [
    {
     'PaymentAddress': '12Rqib6qtSrFPhPcDXsnVaEGKHo5e1skP9xkzPe3ScxzAw5oLQRo9APXGGnukysopE1VJauYCWoLbLwtEFpX8mucUushPP1sYMpbpPR',
     'PublicKey': '1AfSyPovFkLVqVqarTudLJf5mTfYiPywRaC2aABNEWdYnXsCru',
     'PrivateKey': '112t8rnXi8eKJ5RYJjyQYcFMThfbXHgaL6pq5AF5bWsDXwfsw8pqQUreDv6qgWyiABoDdphvqE7NFr9K92aomX7Gi5Nm1e4tEoV3qRLVdfSR',
     'ValidatorKey': '1Vgz5qoz2Qkj462ApBhY3Q7NNQK6V8Q3oSTizaD52tSwTzDqwM'},
    {
     'PaymentAddress': '12S3Cm7ZyzzheDNLrke2V4fpPuSvRZnMpWA1X99aXhKXa3VLNqAiQkNBWGTs6549JUrCSA9LjzsMmueqAWfcYQWqsC9WLoVgJ8fhEsL',
     'PublicKey': '12WJoJ9XHV1sSqx6pGibcNHaL5R8ZvazxWrKdnVmb19YvzG2HhK',
     'PrivateKey': '112t8rnY42xRqJghQX3zvhgEa2ZJBwSzJ46SXyVQEam1yNpN4bfAqJwh1SsobjHAz8wwRvwnqJBfxrbwUuTxqgEbuEE8yMu6F14QmwtwyM43',
     'ValidatorKey': '1vGPif7nGLCdkS5Mvz3WF5LrhfAg7DQEiPDejUbPDjp1PN1iqG'}
    ]
    """
    list_key_set = []
    list_private_k = private_k_str.split('\n')
    for key in list_private_k:
        acc = Account(private_key=key)
        key_set = {"PaymentAddress": acc.payment_key, "PublicKey": acc.public_key, "PrivateKey": acc.private_key,
                   "ValidatorKey": acc.validator_key}
        list_key_set.append(key_set)
    INFO(list_key_set)
    return list_key_set
