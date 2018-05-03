import json
import string
from collections import Counter

from onto.builder import OntoEncoder
from onto.connection import Connection
from onto.node import Node
from onto.onto_container import OntoContainer

minimal_weight = 0.25


class OntoBuilder2:

    def __init__(self):
        self.nodes = []
        self.stop_words = ['a', 'is', 'in']
        self.container = OntoContainer()
        self.line_nodes = {}


    def load_list_from_file(filename):
        lines = []
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                lines.append(line.strip())
        return lines


    def tokenize_line(self, line):
        translator = str.maketrans('', '', string.punctuation.replace('-', '') + '«»')
        terms = line.translate(translator).split()
        return terms


    def build_facts(self, filename):
        lines = OntoBuilder2.load_list_from_file(filename)

        self._make_connections(lines)

        direction_nodes = []
        fact_nodes = []
        fact_counter = 0
        direction_counter = 0
        for line in self.line_nodes:
            nodes = self.line_nodes[line]
            if not self._is_fact(nodes):
                continue

            fact_node = self._build_fact(nodes)
            if fact_node:
                if line[:2].lower() == 'to':
                    direction_counter += 1
                    fact_node.pattern = 'direction {}'.format(direction_counter)
                    direction_nodes.append(fact_node)
                else:
                    fact_counter += 1
                    fact_node.pattern = 'fact {}'.format(fact_counter)
                    fact_nodes.append(fact_node)


    def store(self, filename):
        out_val = {'nodes': self.container.nodes, 'connections': self.container.connections}
        with open(filename, mode='wt', encoding='utf-8') as output_file:
            print(self._serialize(out_val), file=output_file)


    @staticmethod
    def _serialize(value):
        return json.dumps(value, cls=OntoEncoder)


    def _make_connections(self, lines):
        for line in lines:
            if not line.startswith('#'):
                self.line_nodes[line] = self._build_nodes(line)

        self._make_simple_connections(lines)
        self._make_knowledge_connections(lines)


    def _make_knowledge_connections(self, lines):
        while True:
            if not self._make_knowledge_connections_1pass(lines):
                break


    def _make_knowledge_connections_1pass(self, lines):
        fact_nodes = []
        for line in lines:
            if line not in self.line_nodes:
                continue

            nodes = self.line_nodes[line]
            if len(nodes) > 2:
                fact_nodes.append(nodes)

        bigrams = []
        for f_nodes in fact_nodes:
            bigrams.extend(self._get_possible_bigrams(f_nodes))

        counter = Counter(bigrams)
        top_frequent = counter.most_common(1)[0]
        num_times = top_frequent[1]
        if num_times < 2:
            return False

        bigram_repr = top_frequent[0]
        nodes_repr = bigram_repr.split('-')
        node1 = self.container.get_node_by_id(nodes_repr[0])
        node2 = self.container.get_node_by_id(nodes_repr[1])

        # create combined node
        combined_node = Node(self.container.next_node_id(), node1.pattern + ' ' + node2.pattern, self.container)
        combined_node.abstract = True
        self.container.nodes.append(combined_node)

        # replace the two nodes in every fact with a newly created abstract node
        for line in self.line_nodes:
            nodes = self.line_nodes[line]
            if node1 in nodes and node2 in nodes:
                pos1 = nodes.index(node1)
                nodes[pos1] = combined_node
                nodes.remove(node2)

        # connect source nodes to a newly created abstract node
        weight = min(1.0, num_times * minimal_weight)

        self._add_bidirect_connections(node1, combined_node, weight)
        self._add_bidirect_connections(node2, combined_node, weight)
        return True


    def _make_simple_connections(self, lines):
        for line in lines:
            if line not in self.line_nodes:
                continue
            terms = self.tokenize_line(line)
            if len(terms) < 6 and 'is' in terms:
                self._build_simple_connection(line)


    def _get_possible_bigrams(self, nodes):
        bigrams = []
        for i in range(len(nodes) - 1):
            node1 = nodes[i]
            node2 = nodes[i + 1]
            bigram = self._get_bigram_repr(node1, node2)
            if bigram not in bigrams:
                bigrams.append(bigram)
            if i < len(nodes) - 2:
                node2 = nodes[i + 2]
                bigram = self._get_bigram_repr(node1, node2)
                if bigram not in bigrams:
                    bigrams.append(bigram)
        return bigrams


    def _get_bigram_repr(self, node1, node2):
        id1 = int(node1.node_id)
        id2 = int(node2.node_id)
        min_id = min(id1, id2)
        max_id = max(id1, id2)
        return '{}-{}'.format(min_id, max_id)


    def _build_nodes(self, line):
        terms = self.tokenize_line(line)
        nodes = []
        for term in terms:
            if term in self.stop_words:
                continue
            node = self.container.get_node_by_pattern(term)
            if node is None:
                node = Node(self.container.next_node_id(), term, self.container)
                self.container.nodes.append(node)
            nodes.append(node)

        return nodes


    def _is_fact(self, nodes):
        there_are_abstract_nodes = sum([1 for node in nodes if node.abstract])
        return there_are_abstract_nodes or len(nodes) > 2


    def _build_simple_connection(self, line):
        nodes = self.line_nodes[line]
        if len(nodes) > 2:
            raise Exception('cannot handle more than 2 nodes in _build_simple_connection()')

        self._add_bidirect_connections(nodes[0], nodes[1], minimal_weight)


    def _build_fact(self, nodes):
        fact_node = Node(self.container.next_node_id(), pattern='', container=self.container, abstract=True)
        fact_node.knowledge_center = True
        self.container.nodes.append(fact_node)
        for node in nodes:
            self._add_bidirect_connections(fact_node, node, minimal_weight)
        return fact_node


    def _add_bidirect_connections(self, node1, node2, weight):
        if node1 == node2:
            raise BaseException('cannot connect node to itself')
        connection = Connection(source=node1, target=node2, container=self.container)
        connection.weight = weight
        self.container.connections.append(connection)
        connection = Connection(source=node2, target=node1, container=self.container)
        connection.weight = weight
        self.container.connections.append(connection)