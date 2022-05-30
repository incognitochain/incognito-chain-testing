from Configs.Configs import ChainConfig
from Helpers.Logging import INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import SUT, STAKER_ACCOUNTS

shard_test = 0
fix_node = ChainConfig.FIX_BLOCK_VALIDATOR
# list_validator_k_shard_test = ["1iYBtWJBANTGhpMrbUkpz2nEk7pjX2vX1NeD6Lp3Tkt2iEbUjK"","
#                                "1AYrcY4H9a6gqzd1P74QKF3AXqVGdYmfcshsYMbTUYDviY2UGQ"","
#                                "1mdmpXwra8MrFjyDmcbgJCBwDPnZ9ByWaXv4GwPmzHgzQTMvZP"","
#                                "12KC1gJDewygCzEuVRwAHXA48cWFjm37JX5FzrK6usE6JWtRZKx"","
#                                "12raNsFjGbJs4g8wMrLTgTDUBhYufxxzY3D2Vr19HrnbHyfsCjD"","
#                                "12ZjnJvXu1Cw4AUEoNw3mK2jj3ZRsmngt2KghpQ6p1FVFpwbgCg"","
#                                "12f46qQhFpyC8MwqgqsgUBohU5YAaDsAynkSYYnqu7mDmP761Lf"","
#                                "1ciAuzjtfZz6AxWzL9eKTNoxzSPRLiz2rnzJjfmPR3e4FWKyZ3"","
#                                "1L9apTE6CvRmbxkocUdMQULGZ3XRqe4hhU7j6aVw6dhhtiX5aF"","
#                                "12XchU2Sy2jmpSrdoVsQiogFEHMcv3vkyRShfzzSPvhQLB3UaHY"","
#                                "1j4Y3DvZufBKNbvA1NrNAoWAuDydYBBMqU7tvfUwUpzV4gMB2Z"","
#                                "12ofT77VZwtzMX3Wi7Kpgt56T8g9NrgZy4gRZv4TJeH3oVpRULM"","
#                                "1WGGEdXWULzvAqVq6YKTrRe5SpmLNRhmGfz5Sv4FVz2rw8uVwc"","
#                                "1R4sF1nrgbRBxmiVXfVDmakbFE5zwUVMs1cgyZuRy5YDhhaHyz"","
#                                "1Z6nB1MSGZSpCUBVfy8RmXJMwQdtuyyb7ekhHvuiakZuaZeVSZ"","
#                                "1wApnU3Qd99MD3TcwzL2Atu5SPGJismpjmYBxkEroGK8jxBRyV"","
#                                "12WmPn5of5wS4cvDp45WwVgxXkDBndzGj1ffk29Mic9naC1Ttqw"","
#                                "1YdPFh6oDngQLcaRfPU1QoEovZgitYDg7YAYmrzbpvkyVo35y6"","
#                                "1U7TKnpvCfVKg8FcWMpVJaoKCJNQuye4hbRDnQ515qvE9p3vZ1"","
#                                "1LBgmVnwrLnAicSw3hJL2Vv332ZwHPhxSG8jyjzZsyasy8bafE"","
#                                "12ttMExhURGwAtBcCo9wE5Dftj4o9Dz3pY6Ja4NUWNd2Z84ZU3x"","
#                                "12bdyr7bvRAU85U89N9XFfALvivjCuaujpzxbiVi2JFsDEY7ieB"","
#                                "128QzuRkdowdnYjXAzPP6Wmq5uS1PCcVhr78vvvyhKx49hC9qfv"","
#                                "12B4GNAHUasfZwv8uqRC9QrLT661S9qmBdeMzUSiu2wELZqWsMz"","
#                                "1H3zZRXpUdi6Qw6AJtUD8qCiDYfQ8puzNnkS6J3QNtyWCLcd7u"","
#                                "1P6USjJBaA15E2d259k835UgZ8zmabWVpYMF7svT6Pzg5C15wq"","
#                                "12EKvwFvHa21ptFHZ2HMU2KF1DMujJ4rgwQ18ivXePJS8uWLbmL"","
#                                "1vTkVgWTzWdar1ktsgwzSrXCa8Xv4fHsUXMr2G4WfrT8RmK2qK"","
#                                ]


def test_command_find_id_run_node_single():
    INFO()
    epoch_b4 = 0
    while True:
        string_even = '\nEVEN\n'
        string_odd = '\nODD\n'
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
        epoch = beacon_bsd.get_epoch()
        while epoch == epoch_b4:
            WAIT(ChainConfig.BLOCK_TIME)
            beacon_bsd = SUT().get_beacon_best_state_detail_info()
            epoch = beacon_bsd.get_epoch()
        epoch_b4 = epoch
        height = beacon_bsd.get_beacon_height()
        committee_shard = beacon_bsd.get_shard_committees()[str(shard_test)]
        size = (len(committee_shard)) / 2
        p = 0
        q = 0
        for j in range(fix_node):
            if j % 2 == 0:
                p += 1
                string_even += f'pgrep incognito -a | grep shard_{shard_test}_{j}\n'
                # string_even += f'docker stop shard{shard_test}-{j}\n'
                # print(f'{(int(size+0.5) * 2 / 3 - 1)-(fix_node/2)} <= {p} < {(int(size+0.5) * 2 / 3)-(fix_node/2)}')
                if (int(size + 0.5) * 2 / 3) < p <= (int(size + 0.5) * 2 / 3 + 1):
                    string_even += '========================\n'
            else:
                q += 1
                string_odd += f'pgrep incognito -a | grep shard_{shard_test}_{j}\n'
                # string_odd += f'docker stop shard{shard_test}-{j}\n'
                if (int(size) * 2 / 3) < q <= (int(size) * 2 / 3 + 1):
                    string_odd += '========================\n'
        list_staker = []
        # if ChainConfig.ACTIVE_SHARD != 8:
        #     acc_group = STAKER_ACCOUNTS
        # else:
        #     acc_group = []
        #     for key in list_validator_k_shard_test:
        #         acc = STAKER_ACCOUNTS.find_account_by_key(key)
        #         acc_group.append(acc)
        acc_group = STAKER_ACCOUNTS
        for committee in committee_shard[fix_node:]:
            i = 0
            for acc in acc_group:
                if acc.is_this_my_key(committee.get_inc_public_key()):
                    break
                i += 1
            list_staker.append(i)
        for j in range(len(list_staker)):
            if j % 2 == 0:
                p += 1
                string_even += f'pgrep incognito -a | grep staker_{list_staker[j]}\n'
                # string_even += f'docker stop staker1.{list_staker[j]}\n'
                if (int(size + 0.5) * 2 / 3) < p <= (int(size + 0.5) * 2 / 3 + 1):
                    string_even += '========================\n'
            else:
                q += 1
                string_odd += f'pgrep incognito -a | grep staker_{list_staker[j]}\n'
                # string_odd += f'docker stop staker1.{list_staker[j]}\n'
                if (int(size) * 2 / 3) < q <= (int(size) * 2 / 3 + 1):
                    string_odd += '========================\n'
        INFO(string_even)
        INFO(string_odd)
        WAIT(ChainConfig.BLOCK_TIME * (ChainConfig.BLOCK_PER_EPOCH - (height % ChainConfig.BLOCK_PER_EPOCH)))


def test_create_command_run_node_multikey():
    INFO()
    epoch_b4 = 0
    while True:
        string_cm = "Profiling=11149 ./incognito.dev.instant-finality-bridge --datadir data/mstaker_0 --rpclisten 0.0.0.0:11335 --listen 0.0.0.0:11452 --miningkeys 12Lbru8LTRzXXK9zprvJcG3Y2VjFgUx2wdPWaPJCBnB34A8BBa1,129VqpkctEKf7WNTZ3sJmZR3svBqhJTpGCzFb7dvvM8n3RZGuUy,1sns5tYzDJZQ6YSdSnU47j1E53ujSckW7iJRsY6YJ6GbCMfXXy,14wTPAo74B5bVywVuvysxTBnLgbP7KvFEEYfXfTRpUZo5JS82J,12TE5ou9NnzAtxVjUFa7xXzqk2SWssN45M2YsTk2FTteyv5M8SH,1rjVBSV3r1QB7evhHRHKh9wHrUd932rE8GLJ6LLjas8tNXSSMw,1zDcURDc9ZH1P5rezFkw7RajJGNsCNhoL9Mp2aNTaBBMNiuvzn,12eeeZC8qfnQbRt8uVQFMbogDTiju7RuGgPAdbJHoZ8SNc7DiPW,1YdPFh6oDngQLcaRfPU1QoEovZgitYDg7YAYmrzbpvkyVo35y6,1pkJyghz5tdNy6GFC5P121X2XuGGhG4ic8fYnZZFvJusQrDcGj,1SYxBgkqtCerfuA1DnPvg3N62ZpLyr5kPYzAHEiTfY2yHyN6eW,1kqV4GiWCgrWHWcV36uktZURF6Wobu6jBEAfdPEmV9M4fwdSTN,12eF3CzLUZ1UQKoFntoetgAYWVpD1XGDTAJWJBwjc7kS2sfkz4V,1uyzn9gh8kqht5jzc3iLXfAmPqhZQc4zKX63XWT8phHjHw3Hhw,12XFRxMsccU225s36WcZXD3DUgW5MrMUWNfHU4cQPUJXBR4hk7J,1ZgPfbcWihGH44x9JUWvJ28HEJZFQ4FyLviT5CzKLXdFksA953,125HaAcZEESYWE6reQSERMKeVQmoxMS1KUxyW4gdYgYt8RbXvRx,1V3rEA2zrJNMzv9Lv4KYRo26tHw7v8APLm2LEBd9jmTkBga1gZ,1SFa2qdf5pz7HvT6SjcFofXYfSL3JKoRuDKFoesbTJDU8env6P,12QQS3g7CBGPHrTeYU2KVtGH2woy5avBNeGAnyyGhixfTW2Weko,12oMxLanrrozGfsiP34PS815pyoHVyGcoeS8B1f7vgr6sarXYPT,1BTefnCRW3C9k9ihrSmtd6d23Pty6NKaDQVvQ5eFm2B6UuPPQZ,1qbp1zkQV84Axe2QR2jN9mS1K89s7TiCNLRfM17ftKx7egMky8,1Pgo94DEkbsx7FTqb9gz5qmgnWrJ2ZHNssudZnzvxQKRr4ByUg,1KWiZkpGbyoeUo7ZHaSSGXBE3jtx6Y9ArKSWYV7cKKcC3WUwRR,1XtTRoxQNgJKyJTWH3LWuaFrmsPrZFBUCo9SMqtPPb2S2iatmC,12KXKn7gtuh9f3Hr1J5jL8nXkSaYDyWb3avmCAbCcqze4wdckpo,12V4xNojJpRnk7p3QFej3Fzujq4yshs1M4rGNBCByWy99WQRnYn,1d4SHRBtnV82mJUqRCmyGxC17zs83ZhQAK3pXcE7xV9ChCXQ7r,12fwvbEQfK4ZhQ8BzHk4ZiabeZMi8kgcZ7NQyvdPVHfQpPG7MNn,12HkxWXoc2EQmoTV71njstFzR6EtY66fVoUx9LgHfvY6GRyEwhE,1uDPbbGR8iawqh2ev3gpb8bVFa38SzxUrujiTmiUyrHkUyz8eX,12aX9oy49tzsU7yTPBoj6R1AXkKKNy1CqTo9PoWJyNGHDaT4w7C,1NbtFdrUuRgAjoabnHnLAY4MMXSCUj66UQT4q3V1nnMobeJkww,121WQY7M4QfQeKWMNHE1waJnPhww62uZocRaMUrdBfseWfT3bVD,1pQq52KVX4CA8yer1TLdbLEocusNbN4QhGXus3gaTre4A9sE5m,121Ysxm8t6sHsDyZxApCAJYQJMnWDL5WaiQzJtQm54YhttRgsba,1EME7KihkHDMfBRu8Eaf56epKT3cTMc3okHZgEByN1gkqQ5ZbK,1Pm7LsAteFaTnDRf7xEfEbJW2Lu3ErFYiGRn6ktpTCCB6GxusR,12tkkPfHtsCJbTPCfwkwyd9Ko4qTk78JWSN6FAqLKjajKNjcRsc,1uKDy6JtRLmGXss9TB9eyjuEPT59JEFMqiLbLPN8NJ9ha3TFUE,12wfLXxnp1KR4g74P6uVEjFwD9yYiQwYxXEN58RBHvZzeS3yXcr,16ZLWviRBj3npqZuwHJ9DXMsua7fyfnrDv1n5RqrUKjq7eYAhL,1GycLpANBC7dCico77oyAVKiQeq6isoLc5GEtJRxukqVt3siPj,1Tau7GgcwR42TkyqoM9Jv433df3s7RzYq4gTSUhmYTUeeAzrZP,12ZtUMWt1YnCjNDW5FUgCMYEa81qwg2dhdCe1WfvUX8v9zBARwk,1WfMvgQXEs4rp8ihT3iAL9V5LrdhDLC4uDHd1dhCN4PY6NRGeA,1wApnU3Qd99MD3TcwzL2Atu5SPGJismpjmYBxkEroGK8jxBRyV,12H8oBJUWmkPQUb7ApQ8a1ut5Zzn4tVroy4HPCQrvfPCq8Fzwjo,1r5TBsNRZZ2mUVj7jreTVJ3UrmCsCku82uG1NAbBwkdmPK77C6,1c5Wk53d3JaideyG9vM3LgnHk6uvAvrZ5tfZutw5hCjuFNXGT5,18x7LHRTonQ17e7QxGbc1EdKBQAtgEE8P8nD3EN4pcLrcyNneJ,12g1XMqDpELNtxtB6fEvagXdqVgdYFN6jCzKddqPVD6ppczN4jM,12wYRhWehecPqUH2TTNGt4yLhw8aFKcGduhr5MNQR4R2ojWjy4M,1kHzBxGfkaBzDMk15JZ2pwYHR5ncijqwCywVtFyyiyzKihKy4c,19d3GfREp5bUoi6fesEWJsKLz7mcmCnaXWBk6Zh8USVc6z2ZU8,1tyeoxAvxFvq11eBYfXX9xM4z4MjrcGxj9VgYCep5KFCSwYSNG,1hGrceSakQubESo6WDZtxeKWqLcUpXqjGCKg5DmGVz9Rpvamhh,12MHjTtZXmYuucx1dncC7FGHxjXhGLMTnEKJABDuYdFoKHSUMpu,1q7BxoziKAxW1Dx7SjVa2vasjiwHSCoUCaRKvtfPNjFvnp25is,13LM6uKEXYUi7cwQErSN1AZ9supKc2n7h8faKfL7hK5KQAmXGF,12t6UXZ6SdoHxCX6a7yjBS7Uzs3MJxzKK6fD6xSjiaRZRHEo8RF,122FGorRRZcicm2YgtMznb2puKfZ29ULtVRRtNdkTydAL7VyQzM,12Xkk38cvhqvxQKWMAU46r7vbk2Q5CZsaAV433xTjsUfBQ3oYdw,1hA1X4WJLLyNRakFcQVDqwUJvg7v66VEWx5p4bheLrUPqYVcQg,12HxGTM4f5sBWWiM4PZwPoHzxPnceqB5x5CREBjWbbds2HSitfD,1sjRpoSb6E9CLBcoUW23n7uiMkh9QDvswcU2d4kHk6hmf5AMGy,123nLcb48ukAagcVxzvx3TrmWaGiZNqJvxBT6RiM28Twz73J9UD,12WSpbbEvYTS26HpeL4UgqRaLPvcxnBg3b4om6wxmpCr13bevnM,12uyCkDEDzzK5QmCqiw99P7Qk3eX2XX96T8i19UzXom6SayyxPt,1cmWpecigzJNeuMUtU6L8Bnxjccrp1WEN3eHfXjNE4oD3bdvLS,1B6byQEjtNsntNeHeNqjbeXua7ujrVpWKEpYKGXdjrPu1uYhqr,12dv6DYa4poVT3ad37GPBQZVYoY4iVNu6VjqYnR74szbDU6WNvD,12Eiu36MnFfDbZU939Tp6FCsNSe8DLq9jvHjhAMzaEnr9Qb9hYP,1ywCYv2e67UEw9bS833UGViXrQqMut5h3YbNZCVDkZMQLJZ9fE,12Jk91FMjqexJL5bnfb9hWE9Ym5bEXgTXX8BKYFE6DBbe8MtJbw,12HsgKXFssY47wtubkmc8vcyw9VeshZppCMQyhMgQSyx7hG6qDb,1WvyHX5YVRVduWcUSyF9jP2dheb98gCgL5jGrfnq3k2ioWG6dg,1xtDT7CW4C9T5paAtEZ4CBad42dzQpx5vKhbAJZUMk7q5mwdZZ,1ky5qqwrTdmXUsx1MeadVAXjCxnoSQ4VF1N6bPBLhkD8AZt6VA,12emfFBYfxMJgMHy5jS7VLKfnAGBhQG3CjD1TrZ274X8WiZNpDE,1tRsT14iEjXshVLvSwtxwbeaeov3RqTx6yDHxeAFdjp5iz6aY1,1j4VdUJwbrPH1mQdXDLJShikJ6FgD4K4CwyqAQmbgUTTJF4rYQ,12B6K7AUdymjUyfAAdckxpthFDsHTrJLErAkyy16ff81XZd2SwR,12fdUQp9NLsnfyKJUVi6vXtRpYyWQub6BxkBmG7bccPgZkDxCVL,1XA8QaN1ieenJiEWZiMLwtMgcMKGk3ktHntreezX86MxtAoDvP,1QFVPb5WSWvUeLxaeBjEi5jWLw9nt3dm465YDp6YopSV27zwyH,1HtcXUiYeKk4pa3VD2hk7bxjKwGudRcSCXXu9Fq9V5wL3XhYx6,12kGi39bh7oiKoms7SwahnMyMW4jGpZ8FSKJBoVgzYrS2rrFEGK,1oU4XeuNtjNJ2PM86nRojQ96zRcLCZVK8TG56mBELU1L5xFna7,12X91W8PxiM2VodAwpoVDu4HtrraYXHifRV2NdDHkhQ7uZEkdDU,1nAFUqjSoQDhYDUXxAQAijQeB56jznjJE7J1y862bUF6EDYCKv,12WutaHgtZbZDcGXXm7sPKJ46S2ayRh7wvocizC9XKyW5gf3Xsg,12byVqhcHoibyecCLQNrpLjdHmGxjtorjX2784cGWapKYzBf11F,12cVXKBV21ZA4jFrG8pa7B2fMhH6ZL7EK3tjc6pkqYXqQBorRbu,1266YXgDxVuU4VVbByftXdrLPXXqXrQ4mNpg8XGETk1Szjw7AcV,12mMfk3KvTcDwzQf8DNrULg77TgPsNzuHKkCpWNZ3y2WCedk6hM,123aWYG5Fga5EAgmhgCPBmNkuVJjvep7Lg1ia4ajUmpfgMCB3hF,12317LsQDHtmRgc2imke4MLGRivRHFG2mDCsoussEZazDhP12yj,12E2758bsi7xFZg4kfy9d8bJip3WxUqTcvLx3bR5vMcLD9s6gYY,12dZ34VKnRG6mFLgqAfrcNfPfxmqpZ2k95h2vrUsHFPJpP9S7LY,1x7khU3vymf8ZhrjumHcFTvDHkoiRThuK8DXLCYwEXotocKLUk,1T99yhAh3psNxEZno51CJ3tG3Jk9u1FV69aLduCahr3c5cj2S5,1R4sF1nrgbRBxmiVXfVDmakbFE5zwUVMs1cgyZuRy5YDhhaHyz,12GuC6G3dVeVUKeyTKP1wd3EdfnEWcVyYDN6nqq9QkcWjcdDru3,1vSTyjLDpiZr5LYQ4mLRWKdeEtFETuLn7kREzapnKSXhbHEHMb,12QyBwZYRQAwNqBwkeCXeXbVSxpYYED2Uo2yyWLoYokm4gND2Yo,12SERy8XaCE6f9PTxHJqAhaVcrJpTXjch1BtRcEun9XequuTt3p,125evkpjMPEPfHjB1WSWv2pRH1phJ26WoUZXbNvQZXVsXhdEvD5,16dZyZN7maNLxFwLcLqZDwvDfwhcC9SUuCKqBceweSzZ4K5MCn,1xb7Cqk93gqjLMirnyjQ6PXK3tA4asjm4RGDaRrAde2RZnwQHN,12BpY5E2qmoLZnC6owhjcGiJD5xVutWFBMtYbyVPTPd5K2GjsNh,1s2yTtB83CndEEQoXgshxe3VyftYfUj947UB2xfALKozJ42e7v,1xWcZEyvmALAHWis4KVRtUKDGiYLu6j9ZhU1uYC7disiRVSrqL,1BpSfCrqByrqUsuaDVM34zVtequkboE8TddiTooPx1aUxdYg22,1JtTznPQAEijoM988yw86NXNQn4GeR7vfU86vPUc7gXu9qHJEm,12tEq16EwS1eZsArhP4nvSrEVdXhCxGTC1uL7wz627ZoXn7VsUU,12Z4EYMtLgBZRCx2VatZ1AssVoA9NJ8qz4wdTnEANGAnhDkLr9i,12Gc7i745mEn6EzXPnRLc74967PgwDNPkv48RENJLVS9wZdmu5T,127RMMYC1hyhrLceZLFHaPbeNgnE8apT2bTNJsLxHrzsqAbKctH,1WaZNPaNLCQYB9Kxuf4ApmwCg8rqu2YzMxX22neXid2CPSKDfd,1vqG24UUTE9gJw5Txxn7Rdj7vp9Sexh5hk4mYtas4WiEqpV9YH,12L6i7gWiRc3hKAMjMeBeeMcVcZvXkjTzzJ65XqTexwkyvcgL4E,17PiwsLBBpftbhBw92Dq46m18M3oouQtkNcZ7LYaAP19WSJmmV,123c8KK1rdLoBZUf1MWfF64tXgGCXENMFRCTGJRiSP8teBPfNxn,12bdyr7bvRAU85U89N9XFfALvivjCuaujpzxbiVi2JFsDEY7ieB,1MzDpKojnurctLdHWZm5gwvbajpHyZPStb3ozSzKtfKjMK37UN --discoverpeersaddress 0.0.0.0:9330 --externaladdress 0.0.0.0:11452 --loglevel debug --norpcauth 2> logs/1499_0527_0803/mstaker_0.error | cronolog logs/1499_0527_0803/mstaker_0-%Y-%m-%d.log &"
        beacon_bsd = SUT().get_beacon_best_state_detail_info()
        epoch = beacon_bsd.get_epoch()
        while epoch == epoch_b4:
            WAIT(ChainConfig.BLOCK_TIME)
            beacon_bsd = SUT().get_beacon_best_state_detail_info()
            epoch = beacon_bsd.get_epoch()
        epoch_b4 = epoch
        height = beacon_bsd.get_beacon_height()
        committee_shard = beacon_bsd.get_shard_committees()[str(shard_test)][fix_node:]
        acc_group = STAKER_ACCOUNTS
        for j in range(len(committee_shard)):
            if j % 2 == 0:  # remove key of even subset - shard test
                key = committee_shard[j].get_inc_public_key()
                acc = acc_group.find_account_by_key(key)
                validator_k = acc.validator_key
                string_cm = string_cm.replace(f"{validator_k},", "")
        print("export INCOGNITO_NETWORK_KEY=local")
        print("ulimit -n 10240")
        print(string_cm)
        WAIT(ChainConfig.BLOCK_TIME * (ChainConfig.BLOCK_PER_EPOCH - (height % ChainConfig.BLOCK_PER_EPOCH)))
