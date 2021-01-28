from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.NodeObject import Node
from IncognitoChain.Objects.TestBedObject import TestBed

node1 = Node(url="http://51.79.76.38:9352")
node2 = Node(url="http://51.79.76.38:9340")

beacon = Node(url="http://51.79.76.38:9335")
nodes = [node1, node2]


def restart_at_beacon_height(stop_height, start_height, node_list: List[Node], check_interval):
    height = beacon.help_get_beacon_height()
    for n in node_list:
        TestBed.ssh_to(n)

    while True:
        INFO(f"current height = {height}")
        if height == stop_height:
            INFO(f'Height = {height}, stop the nodes')
            with ThreadPoolExecutor() as e:
                for n in node_list:
                    e.submit(n.kill_node)
            break
        WAIT(check_interval)
        height = beacon.help_get_beacon_height()

    while True:
        INFO(f"current height = {height}")
        if height == start_height:
            INFO(f'Height = {height}, start the nodes')
            with ThreadPoolExecutor() as e:
                for n in node_list:
                    e.submit(n.start_node)
            break
        WAIT(check_interval)
        height = beacon.help_get_beacon_height()


stop_height = 109835
start_height = stop_height + 20
restart_at_beacon_height(stop_height, start_height, nodes, 10)
