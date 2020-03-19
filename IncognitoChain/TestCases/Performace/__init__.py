from threading import Thread
from typing import List

from IncognitoChain.Drivers.Response import Response
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Objects.AccountObject import Account

account_list = [
    Account(  # 1
        payment_key='12S4qeDokLzJZPGUJ7PmjFG3ZmgQKFCvXvYntffgXMf2biba9SLzQi1r5hbdZsxY9BARL5cYoXZHSKv1B888s9hjqqMpXD4ths2mgZy',
        private_key='112t8rnfYRHi14QZKZbjFQwkm4r4AQvuMu4Yc7P5QKzj18na5DBhpmPdiBLx3s5E2e1y2kDDa7bfEMfaohCM4rpukchZB5psQ5vw5FwogT6D',
        shard=0),
    Account(  # 2
        payment_key='12RzVJYrqghXKozKzLfeRLFKS1oSwPSE3scbTkGesfzW79HFhP62WUpTo49HEcx3QzjUYxfPEF5dn66Qe9quRUPSRz2toLmXCaaHFy9',
        private_key='112t8rnhMV3bGYuNxCQT1USyKdZ5x71jktfn7oFLJimZBQYz9VxZLREZgPbZfnPgnkrFvgapY6yw1avfWpDqv4JZCiBQKKQRQocD3H8UiCvQ',
        shard=0),
    Account(  # 3
        payment_key='12RvqLk1sGyy6oKAhDc9aPvxTjVpczLEcXwNyuGSSjYnZxZw6bWzonjTraGJmK4yf6JM2oU7tvk6hDxEwZxYaLc4YgbuYqNHfyHKdF7',
        private_key='112t8rnhjRNrUCLvw8bWdCGSofMPRGKto5QCrgzkP5mbwjmRKmvLC8vzfgPXmF9gGsZ9mfw11Qx86PjXJWx9dNtr3PRgkh3rLnUYZp1hSA7b',
        shard=0),
    Account(  # 4
        payment_key='12RyMcrrpAcwTooEpxvpVxMGXzHUnmkdvCEBf6Ua7P19vEFC2UUcBhU8Bj5A9JdLocijgt11Ht5x4vjfv2Q2WeAc5xvrhSTy3S3rxoH',
        private_key='112t8rnjCBRWvRUqN6fhu6bjAnonpcke1GRZigyUcR9oy9f3iSG12xHirjBKCsAr3ENgrykYKh8KWQgpFEZxH5hzEicEjMdotZzNeecucVsh',
        shard=0),
    Account(  # 5
        payment_key='12RpYrHcTMHCf8mnfguWesDQBftEz2NDBfj8jEXdai86nDphHgwdguqv98H2jR8j6Mvsx4QK6AaVSvGkjiN2hcZ38aeTk1o4J2v5vC3',
        private_key='112t8rnmWDAmwjCY9ex28Wq8ep3SMtfCrTWgjBzbKnQmq2ALfjr4jjvHVfUtk6Ane6NrpkHCpZVMj7YyYA7wpiCMbLYxiyCfDa3v58bSqaYL',
        shard=0),
    Account(  # 6
        payment_key='12RsBZY2QXRpyqQN7oMcQMmEZBhFUoU9cH6rtYw8Sbciynh3FMsRAaH2CmJPm6Fgtch8gCaA63eaLXhCPeLi6vo6n39ZULupkJ3F61H',
        private_key='112t8rnmuSXmqmu5ATaiNNNgYoLdG9EAvLdp1dMiHhAXEgjmcPthCe1mp5fh2gSu9t8PBnyE8HAAFFNqxPzNEeYwLzLDt4fhV2NH1dkZeXBW',
        shard=0),
    Account(
        payment_key='12S1g14GRAeJV9cTpwGUz8KiTHTqG2KwaUARwLxxqXUszukam7XyDEpCgyc1vtq4VnsD9VQJkrUGa4eov1BJCdWcXEqoPycx6Ar4nf5',
        private_key='112t8rnop8d3zyVmM8zfTCDqnVJ26taQ3WDysSKcsknjMz1uXV5yDahX35TPnDPwYeiBLc8xj1RmHjkzzUZ5n7NoFsNBo6f5AHHgb3JS2UED',
        shard=0),
    Account(  # 7
        payment_key='12Rszs7noz38mUcVpPRzCXxzBLSKceEFo8NaQBiWKR4zUBdLF1Uk2H41YFHowZeTE9xDfafzgokcVs9LyWd3yuwRm9FKfSRGvowC6Hi',
        private_key='112t8rnpHhh7YWz8s8MKWmrZUpd9RfrQ7W7jA7SxBh9Up2RXanpDvqqm3dgB5PzYTxTUc3eBRr4gEECKiFMA2rweMNCTechUBZ1qksmV5WDu',
        shard=0),
    Account(  # 8
        payment_key='12Rvq9pDHBLpwYQpYtHaUTtVRa2rXLqTSoAcF7t4X4Zbv4R28ETEAV7H77goDbhyjLKTnxBiNadMy8GAZf1wkACmbG4w1sMYEHqB49n',
        private_key='112t8rnsYpzkpHxJ34a4YoxEfFvXfLweHuXazSdG8SDk8ajPGeTJEtYDzeEWT4qkR4FApvdNUZ3fU7gCkKry8mFfYfaP411S2s6D7AdA9NYX',
        shard=0),
    Account(  # 9
        payment_key='12S4p6RwrARw31JNm2iBje4u38NRzPfuyqxmssDNh8Sf14ZwfWQm1AppYMHrHwwuXA475GDaQKUDESbF7epP2rbBnKze3Ys1iD51cN8',
        private_key='112t8rntZvYwz2rDeU2TCUxKZukNmbq6C45hfQsSoLfJ2TB1vQw4L64QvMFsufAkpmDjSbNvhByVNUpiy3zhCncdgmHwMRLd6Ln9cG8ALfrQ',
        shard=0),
    Account(  # 10
        payment_key='12S1eGzebMLssZYprc2qmxY5U5HPcAebEadn8XSafC6P2Td8LwFcFmrWAHBzPQrwhqQM6e9p8vy13VEJnWyjB8mR1nRNZerTBHjbCHx',
        private_key='112t8rntk9PuRLqQCJPJz8jTKTsssbx6gg2fPAWBBJMXKcfQHuYBhxxEApNegMkQPCABiUKzM5mtPyXEoaUdKe7Ms7wTvvUuqzavJC4CveTR',
        shard=0),
    Account(  # 11
        payment_key='12RsqocXu2MhTCzGqQ7UwARmgDFgqrJKT7u4WgCTY1PTfcNnuhj9PuBHh6wMFdu3FFoYNYFeNuL9NUKsrwXoTYDwKhgpSNW7h9afvg4',
        private_key='112t8rnwvUwj1czD2eheG4NNjqu15ktz81X8EHAKaypNzHeCpHsMvdzPsjK8QM62aEKaHfnRrNersiN6e5Edq94FBsKDhyYew8D6qTGrTFS8',
        shard=0),
    Account(  # 12
        payment_key='12S66iXzvLxzbfFdoY7jrwz4ovaLc1Vc1WGKvr7Eq2emuv9ad3oMJqC8hheRDXbJSq6dpcct7mymwDPE1beAWGAAL5sWmJMWn6jvVQv',
        private_key='112t8rnx4BqeRqhXe1Hq7FsEm5v4rMMppf5oNfENENgbXyWrLfymMJrLiQQQJAn1v3MLo7vrUkGC4kJHzQqZ6dWabpQiNn7KhmJgwKiR5VaY',
        shard=0),
    Account(  # 13
        payment_key='12RsDQiz69ApBvGTHmsZpFzXPiu1NZqKjfzp13bkY5nk2r65H2jpLWvERDvLSHiLDyzU5BMELzNEvKixajqEZi83PfSgJ9R7dX1kKtK',
        private_key='112t8rnxaWQ9WQX42rbAv7vtSeZeZ2oxvkhsynAFCMP8JCpSXWUEjaBg1znBZE7Z2LCNnifrh59ic33Jt6W24XjrPe9cXRH6dpWZgSwoN1Cd',
        shard=0),
    Account(  # 14
        payment_key='12S6ejYfHyDVdDPvSGmP8HkXWtozZ9b9HbWm5swj8e1ze79PdzKAy65Vd3iDaPtNu1eXswuZEDdpJRYN3S5SZ4bfAkag5g9eLPZ2HvD',
        private_key='112t8rnyBnaN2qzn6r7UL17LgxM2TUkYd79iXLvStbhofrNeTLcVTWSKjiwyWJQiVE5hKcnaQdVWN6dUxYuTktYXZMbmufQ9PGb29JTDogAX',
        shard=0),
    Account(  # 15
        payment_key='12RtEhrfz2WkvzZvJArx3XkAbs4iaE7G5rUJarp845yq3CkyhbLq8Yg8uCCNJuatvSj3qZKf1aYetEuDuom481ng1kGP8eAvRKS7gbe',
        private_key='112t8rnysEYgFy6jye4kkrmrnMY9wtkcr1qpUE5f8YVQt2vL1NxnkbD57YjV3efCmqnsXWCMFet5hqayCfbNAc7tb8QsgNZ5WJAftdkPZroW',
        shard=0),
    Account(  # 16
        payment_key='12Ru5o4EBtu2RXsLa3Ji63XYELDrGXSUeqhuLNVcoLuDXS1PdY8cqYK7dUWbxVvts7S9Ht1EHYHd6PMpV9LmxWKVJkANkKMi5woj7ZN',
        private_key='112t8ro1T3KRfhGji9UHutV8QMdFvjGAXki4kjcqDrPLr8RaHwZzFBhvrhnCZXwhgB9UFnJ4X1sP3em8zKx6Ezy2oMfs1j7vKyjWrRPKi4vG',
        shard=0),
    Account(  # 17
        payment_key='12RqLCpp3VAeAEeNYkWH4VLnDdZDJ2Arx5ZJMpiYAZAWs5w8UR3t5ASA88pUivecgjibTHhp3DTsoZ7XivCWD7Zmcqut2Mn6Vdpe8rc',
        private_key='112t8ro64Yh49P8sfQ633oaekisGf2XMBX79obzqYrqkMFMVdfyrQxwn8WN7HUzXgoc9A2HoAwtzEQ9vx8XpBVMYj1Ja546oZ4YbL49gydV1',
        shard=0),
    Account(  # 18
        payment_key='12Rryh5UMoedKHZU9CHjX1hJDsRNJJ9JSR7uZzgKgH9neDM3YnhCUwD8FHx6Zjy4KxoPGTyT4sA3DsCvFxEgUBuWpiFTJkzd7MSwyyn',
        private_key='112t8ro9u9vd1FFhsvymSaKhzzm7mpbMGQa4X9oG3Z6ykJDiXVkRkyCRtjDLFN6b58RryaJhgzXXpymVUmKWc74Fvm77m9BDebsa2cwf2q3g',
        shard=0),
    Account(  # 19
        payment_key='12S4XL1rVFQXA5CZtEzekwNNget4MQ6qYxEGgbbApDxbnFhGZB5mHoaPqfsh8VT3KBoSVSPAT4kebSrWwM7YyTceEYZvBPNCdoNBUAQ',
        private_key='112t8roGh7k9oDg7fXBWCYMchLtaQ5GfpwrCL9YnGSSsJfBmadxHJgn4GiiTQU855hLzUYFE4pVGhpBUj9RTV9inUqEcEvkXp7qanR84bEqh',
        shard=0),
    Account(  # 20
        payment_key='12Ry8scwynx77bPPMJEpKEVDeSxkpbU1ubPxiZfGTkepnNXqi6Dk9NFfewstodUdhgcjnKCqKNQ6ve3XSo9Zy6izJ2HsjkLPHjozyht',
        private_key='112t8rnZvDJy8nRuK5QPgAVbFrJehDNtn4u6czfCfzdVCExWw4rkS9yWL71JkffraTowNAzau1CufWHrUEV82c9o7furDmZ8xZxJuQXoSL8Q',
        shard=1)
]
data_length = 12
account_list_len = len(account_list) - 1
accounts_send = account_list[0:data_length]
accounts_receive = account_list[account_list_len - data_length:account_list_len]

shard = accounts_send[0].shard

transactions_save_fullnode: List[Response] = []
transactions_save_shard: List[Response] = []

all_thread_list = list()

custom_fee = 100
# 2 random pair of account to send transaction in shard
random_i = [0, 1]
i_to_check_latest = data_length - 1
for i in range(data_length - 1, -1, -1):
    if i not in random_i:
        i_to_check_latest = i
        break
i_to_check_soonest = 0
for i in range(0, data_length):
    if i not in random_i:
        i_to_check_soonest = i
        break
for i in random_i:
    accounts_send[i].defragment_account()

ptoken_id = '57f634b0d50e0ca8fb11c2d2f2989953e313b6b6c5c3393984adf13b26562f2b'


def sending_prv_thread(sender: Account, receiver: Account, amount, shard_id, fee, results_list):
    """
    sending prv in a thread

    shard_id: shard id to send rpc request to, if =-1, send to full node
    """
    tx = sender.send_prv_to(receiver, amount, shard_id=shard_id, fee=fee)
    if type(results_list) is list:
        results_list.append(tx)
    if type(results_list) is dict:
        results_list[sender] = tx


def sending_ptoken_thread(sender: Account, receiver: Account, token_id, amount, token_privacy, results_list):
    """
    sending ptoken in a thread

    """
    tx = sender.send_token_to(receiver, token_id, amount, prv_fee=-1, token_privacy=token_privacy)
    if type(results_list) is list:
        results_list.append(tx)
    if type(results_list) is dict:
        results_list[sender] = tx


def everyone_send_prv_simultaneously(shard_id):
    INFO(f"Creating {data_length} transactions ")
    for index in range(0, data_length):
        thread = Thread(target=sending_prv_thread,
                        args=(
                            accounts_send[index], accounts_receive[index], 234, shard_id, -1,
                            transactions_save_fullnode,))
        thread.start()
        all_thread_list.append(thread)
