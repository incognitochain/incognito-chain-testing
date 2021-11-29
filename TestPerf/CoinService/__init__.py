import os

from Objects.AccountObject import AccountGroup

file_name = "accounts"
file_path = os.path.dirname(os.path.realpath(__file__))
file_path = "TestPerf/CoinService"

file = open(f"{file_path}/{file_name}", "r")
keys = []
line = file.readline()
while line:
    keys.append(line.strip("\n"))
    line = file.readline()
file.close()
ACC_LIST = AccountGroup(*keys)
