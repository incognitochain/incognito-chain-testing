from IncognitoChain.Objects.NodeObject import Node


class Shard:
    def __init__(self, node_list: list = None):
        self.node_list = node_list

    def add_node(self, node: Node):
        self.node_list.append(node)

    def get_node(self, index_or_name) -> Node:
        if index_or_name is int:
            return self.node_list[index_or_name]
        if index_or_name is str:
            return self.node_list[self.__find_index_with_name(index_or_name)]

    def __find_index_with_name(self, node_name_to_find):
        for node in self.node_list:
            if node.node_name == node_name_to_find:
                return self.node_list.index(node)
        return -1


def load_shard(shard) -> Shard:
    return shard
