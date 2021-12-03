from typing import List

from Drivers.Connections import SshSession
from Helpers.Logging import config_logger
from Objects.NodeObject import Node

logger = config_logger(__name__)


def load_test_data(name):
    logger.info(f'Loading: test data {name}')
    try:
        return __import__(f'TestData.{name}', fromlist=['object'])
    except ModuleNotFoundError:
        raise Exception(f"!!! Test data not found: {name}")


def load_test_bed(name):
    logger.info(f'Loading test bed: {name}')
    try:
        return __import__(f'TestBeds.{name}', fromlist=['object'])
    except ModuleNotFoundError:
        raise Exception(f"!!! Test bed not found: {name}")


class TestBed:
    REQUEST_HANDLER: Node = Node()
    SSH_CONNECTIONS = {}

    def __init__(self, test_bed=None):
        if test_bed is not None:
            tb = load_test_bed(test_bed)
            self.full_node: Node = tb.full_node
            try:
                self.beacons: Beacon = tb.beacon
            except AttributeError:
                self.beacons: Beacon = Beacon()
            try:
                self.shards: List[Shard] = tb.shard_list
            except AttributeError:
                self.shards: List[Shard] = []
            try:
                self.stakers: List[Node] = tb.stakers
            except AttributeError:
                self.stakers: List[Node] = []
            try:
                self.highways: List[Node] = tb.highways
            except AttributeError:
                self.highways: List[Node] = []
            TestBed.REQUEST_HANDLER = self.full_node
            self.name = test_bed
        else:
            self.full_node = Node()
            self.beacons = Beacon()
            self.shards: List[Shard] = []
            self.name = ""
            self.stakers: List[Node] = []
            self.highways: List[Node] = []
            TestBed.REQUEST_HANDLER = self.full_node

    @staticmethod
    def ssh_to(node: Node):
        try:
            TestBed.SSH_CONNECTIONS[node._address]
        except KeyError:
            TestBed.SSH_CONNECTIONS[node._address] = SshSession(node._address, node._username, node._password,
                                                                node._ssh_key).ssh_connect()
        node.ssh_attach(TestBed.SSH_CONNECTIONS[node._address])
        return node

    @staticmethod
    def ssh_clean_up():
        for ip, session in TestBed.SSH_CONNECTIONS.items():
            session.disconnect()

    def __call__(self, *args, **kwargs):
        return TestBed.REQUEST_HANDLER

    def __str__(self):
        return f"Test bed name: {self.name} | Full node : {self.full_node} | Current request handler: {self()}"

    def precondition_check(self):
        logger.info(f'Checking test bed')
        return self

    def is_default(self):
        return self.full_node.is_local_host()

    def find_node_by_validator_k(self, validator_k):
        for shard in self.shards:
            for node in shard._node_list:
                TestBed.ssh_to(node)
                key = node.get_mining_key()
                if validator_k == key:
                    return node
        for node in self.stakers + self.beacons._node_list:
            TestBed.ssh_to(node)
            key = node.get_mining_key()
            if validator_k == key:
                return node
        return None


class Shard:
    """
    A shard is just a list of node
    """

    def __init__(self, node_list: list = None):
        self._node_list = node_list

    def __getitem__(self, item):
        return self._node_list[item]

    def __iter__(self):
        self.__current_index = 0
        return iter(self._node_list)

    def __next__(self):
        if self.__current_index >= len(self._node_list):
            raise StopIteration
        else:
            self.__current_index += 1
            return self[self.__current_index]

    def __len__(self):
        return len(self._node_list)

    def add_node(self, node: Node):
        self._node_list.append(node)

    def get_node(self, index_or_name=0) -> Node:
        if type(index_or_name) is int:
            return self._node_list[index_or_name]
        if type(index_or_name) is str:
            return self._node_list[self.__find_index_with_name(index_or_name)]

    def get_representative_node(self) -> Node:
        for node in self._node_list:
            if node._address is not None:
                return node

    def __find_index_with_name(self, node_name_to_find):
        for node in self._node_list:
            if node._node_name == node_name_to_find:
                return self._node_list.index(node)
        return -1


class Beacon(Shard):
    """
    just an alias, technically Beacon and Shard object are the same in this circumstance
    they both consist of a list of nodes
    """
    pass
