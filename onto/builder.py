import re
import json
import string
from json import JSONEncoder

from onto.connection import Connection
from onto.node import Node
from onto.onto_container import OntoContainer


class OntoEncoder(JSONEncoder):
    def default(self, o):
        return o.serialize()


class OntoBuilder:

    def __init__(self):
        self.nodes = set()
        self.id_counter = 0
        self.fact_counter = 0
        self.direction_counter = 0
        self.container = OntoContainer()


    def load_list_from_file(filename):
        lines = []
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                lines.append(line.strip())
        return lines


    def build_knowledge_base(self, filename):
        lines = OntoBuilder.load_list_from_file(filename)
        for line in lines:
            self._build_kb_item(line)

        self.container.nodes = list(self.nodes)
        self.container.sort_nodes_by_id()


    def build_facts(self, filename):
        lines = OntoBuilder.load_list_from_file(filename)
        direction_nodes = []
        fact_nodes = []
        for line in lines:
            if line.startswith('#'):
                continue
            node = self._build_fact(line)
            if node:
                if line[:2].lower() == 'to':
                    self.direction_counter += 1
                    node.pattern = 'direction {}'.format(self.direction_counter)
                    direction_nodes.append(node)
                else:
                    self.fact_counter += 1
                    node.pattern = 'fact {}'.format(self.fact_counter)
                    fact_nodes.append(node)

        if len(direction_nodes) > 1:
            self.id_counter += 1
            pattern = 'direction'
            abstract_direction_node = Node(id=str(self.id_counter), pattern=pattern, container=self.container, abstract=True)
            self.container.nodes.append(abstract_direction_node)
            for node in direction_nodes:
                self._add_bidirect_connections(abstract_direction_node, node)


    def store(self, filename):
        out_val = {'nodes': self.container.nodes, 'connections': self.container.connections}
        with open(filename, mode='wt', encoding='utf-8') as output_file:
            print(self._serialize(out_val), file=output_file)


    @staticmethod
    def _serialize(value):
        return json.dumps(value, cls=OntoEncoder)


    def _find_node_by_pattern(self, pattern):
        nodes = [node for node in self.nodes if node.pattern == pattern]
        if nodes:
            return nodes[0]
        return None


    def _build_kb_item(self, line):
        matches = re.findall("(\[[\w\d\s-]+\])", line)
        make_abstract_node = '+' in line
        make_connection = '*' in line
        nodes = []
        for m in matches:
            pattern = m.strip('[').strip(']')
            node = self._find_node_by_pattern(pattern)
            if not node:
                self.id_counter += 1
                node = Node(id=str(self.id_counter), pattern=pattern, container=self.container, abstract=False)
            nodes.append(node)

        if make_connection:
            self._add_bidirect_connections(nodes[0], nodes[1])

        if make_abstract_node:
            self.id_counter += 1
            pattern = ' '.join([node.pattern for node in nodes])
            abstract_node = Node(id=str(self.id_counter), pattern=pattern, container=self.container, abstract=True)
            for node in nodes:
                self._add_bidirect_connections(node, abstract_node)

            nodes.append(abstract_node)

        self.nodes.update(nodes)


    def _add_bidirect_connections(self, node1, node2):
        if node1 == node2:
            raise BaseException('cannot connect node to itself')
        connection = Connection(source=node1, target=node2, container=self.container)
        self.container.connections.append(connection)
        connection = Connection(source=node2, target=node1, container=self.container)
        self.container.connections.append(connection)


    def _build_fact(self, line):
        translator = str.maketrans('', '', string.punctuation.replace('-', '') + '«»')
        terms = line.translate(translator).split()
        nodes_to_connect = set()
        nodes = []
        # collect nodes for patterns
        for term in terms:
            node = self.container.get_node_by_pattern(term)
            if node:
                nodes.append(node)

        # find upmost abstract node for each
        eliminated = []
        for node in nodes:
            most_abstract_node = self._get_most_abstract_node(node, nodes, eliminated)
            if most_abstract_node:
                nodes_to_connect.add(most_abstract_node)
        nodes_to_connect = [node for node in nodes_to_connect if node not in eliminated]

        # connect em all somehow
        if len(nodes_to_connect) < 2:
            return
        if len(nodes_to_connect) == 2:
            self._add_bidirect_connections(nodes_to_connect[0], nodes_to_connect[1])
        else:
            self.id_counter += 1
            # self.fact_counter += 1
            # pattern = 'direction {}'.format(self.fact_counter)
            fact_node = Node(id=str(self.id_counter), pattern='', container=self.container, abstract=True)
            fact_node.knowledge_center = True
            self.container.nodes.append(fact_node)
            for node in nodes_to_connect:
                self._add_bidirect_connections(fact_node, node)
            return fact_node


    def _get_upper_abstract_nodes(self, node):
        return [conn.target for conn in self.container.connections if conn.source == node and conn.target.abstract]


    def _get_most_abstract_node(self, src_node, nodes, eliminated):
        current_node = src_node
        while True:
            abstract_node = self._get_most_abstract_node_step(current_node, nodes, eliminated)
            if abstract_node == current_node or abstract_node in eliminated:
                return abstract_node
            eliminated.append(current_node)
            current_node = abstract_node


    def _get_most_abstract_node_step(self, src_node, nodes, eliminated):
        upper_abstract = self._get_upper_abstract_nodes(src_node)
        upper_abstract = [node for node in upper_abstract if node not in eliminated]
        if len(upper_abstract) == 0:
            return src_node

        candidate_abstracts = set()
        for abstract_node in upper_abstract:
            for node in nodes:
                if node == src_node:
                    continue
                if self.container.are_nodes_connected(node, abstract_node):
                    candidate_abstracts.add(abstract_node)
                    eliminated.append(node)
        if len(candidate_abstracts) > 1:
            raise BaseException('donna what to do with 2 parallel abstracts')
        if len(candidate_abstracts) == 1:
            return candidate_abstracts.pop()
        else:
            return src_node

