from IncognitoChain.Objects.NodeObject import Node


class Shard:
    def __init__(self, node_list: list = None):
        self._node_list = node_list

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
    pass

