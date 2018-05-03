import json

from onto.connection import Connection
from onto.node import Node


class OntoContainer:
    def __init__(self):
        self.chat_id = ''
        self.entries = {}
        self.nodes = []
        self.connections = []
        self.brain = None


    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as data_file:
            self.entries = json.load(data_file)

        for entry in self.entries['nodes']:
            node = Node(id=entry['id'], pattern=entry['patterns'][0], container=self)
            if 'abstract' in entry:
                node.abstract = entry['abstract']
            self.nodes.append(node)

        for entry in self.entries['connections']:
            source_node = self.get_node_by_id(entry['source'])
            target_node = self.get_node_by_id(entry['target'])
            connection = Connection(source=source_node, target=target_node, container=self)
            self.connections.append(connection)


    def next_node_id(self):
        if len(self.nodes) == 0:
            return '1'
        return str(max([int(node.node_id) for node in self.nodes]) + 1)


    def _add_bidirect_connections(self, node1, node2, secondary=False):
        if node1 == node2:
            raise BaseException('cannot connect node to itself')
        connection = Connection(source=node1, target=node2, container=self)
        connection.secondary = secondary
        self.connections.append(connection)
        connection = Connection(source=node2, target=node1, container=self)
        connection.secondary = secondary
        self.connections.append(connection)


    def build_secondary_connections(self):
        for node in self.nodes:
            if node.knowledge_center:
                continue
            for common_neighbor in self.nodes:
                if self.are_nodes_connected(node, common_neighbor, primary_only=True):
                    for candidate_node in self.nodes:
                        if candidate_node != node and \
                            self.are_nodes_connected(candidate_node, common_neighbor, primary_only=True)\
                            and not self.are_nodes_connected(node, candidate_node)\
                                and not (node.knowledge_center and candidate_node.knowledge_center):
                            self._add_bidirect_connections(node, candidate_node, secondary=True)


    def update(self):
        for node in self.nodes:
            node.update()

        for conn in self.connections:
            conn.update()


    def attach_to_brain(self, brain):
        self.brain = brain


    def get_node_by_id(self, id):
        nodes = [node for node in self.nodes if node.node_id == id]
        if nodes:
            return nodes[0]
        return None


    def get_nodes_by_pattern(self, patterns):
        return [node for node in [self.get_node_by_pattern(pattern) for pattern in patterns] if node is not None]


    def get_node_by_pattern(self, pattern):
        nodes = [node for node in self.nodes if node.pattern == pattern]
        if nodes:
            return nodes[0]
        return None


    def get_outgoing_connections(self, node):
        return [conn for conn in self.connections if conn.source == node]


    def get_incoming_connections(self, node):
        return [conn for conn in self.connections if conn.target == node]


    def get_connection_between_nodes(self, source, target):
        connections = [conn for conn in self.connections if conn.target == target and conn.source == source]
        if connections:
            return connections[0]
        return None


    def find_node(self, clause_part):
        # for entry in self.entries:
        value = clause_part
        if not isinstance(clause_part, str):
            value = clause_part["text"]
        entries = list(entry for entry in self.entries if ("patterns" in entry and value in entry["patterns"]))
        if len(entries):
            return entries[0]
        return None


    def find_node_by_id(self, _id):
        if isinstance(_id, tuple):
            _id = _id[0]
        entries = list(entry for entry in self.entries if (entry["id"] == _id))
        if len(entries):
            return entries[0]
        return None


    def are_nodes_connected(self, node1, node2, primary_only=False):
        c1 = [conn for conn in self.connections if conn.source == node1 and conn.target == node2 and
                    (not conn.secondary or primary_only == False)]
        c2 = [conn for conn in self.connections if conn.source == node2 and conn.target == node1 and
                    (not conn.secondary or primary_only == False)]
        return len(c1) > 0 or len(c2) > 0


    @staticmethod
    def sum_input_weigths(descendants, target_id):
        weight = 0
        for value in descendants.values():
            weight += sum(conn["weight"] for conn in value if conn["node_id"] == target_id)
        return weight


    def find_common_targets_of_type(self, source_nodes, _type):
        descendants = {}
        for node in source_nodes:
            node_id = node["id"]
            descendants[node_id] = []  # set()
            # weight = 0
            for conn in node["connections"]:
                target_node = self.find_node_by_id(conn["target"])
                if target_node and target_node["type"] == _type:
                    weight = conn["sign"]
                    descendants[node_id].append({"node_id": target_node["id"], "weight": weight})

        target_sets = []
        for target_list in descendants.values():
            target_sets.append([target["node_id"] for target in target_list])

        if len(target_sets) < 2:
            return []

        intersection = set(target_sets[0]).intersection(*target_sets[1:])
        if not intersection:
            return []
        else:
            # return [self.find_node_by_id(node_id) for node_id in intersection]
            result = []
            for target_id in intersection:
                weight = self.sum_input_weigths(descendants, target_id)
                result.append({ "node": target_id, "weight": weight})
            return result


    def sort_nodes_by_id(self):
        for node in self.nodes:
            node.numeric_id = int(node.node_id)
        self.nodes.sort(key=lambda x: x.numeric_id)


    def __repr__(self):
        repr = ''
        for node in self.nodes:
            firing_symbol = 'F' if node.firing else ' '
            if node.potential > 0:
                repr += '[{} p:{}] '.format(node.node_id, node.potential)
        return repr

