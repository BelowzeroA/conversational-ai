import json

from algo.core.op_connection import OperationConnection
from algo.core.op_exit import AlgoOperationExit
from algo.core.op_listener import AlgoOperationListener
from algo.core.op_signaller import AlgoOperationSignaller
from algo.core.op_memory import AlgoOperationMemory
from algo.core.op_call import AlgoOperationCall
from algo.core.op_compare import AlgoOperationCompare
from memory.memory_events import MemoryEvent


class OperationContainer:
    def __init__(self, onto_container, algorithm):
        self.entries = {}
        self.operations = []
        self.connections = []
        self.onto_container = onto_container
        self.algorithm = algorithm
        self.brain = None


    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as data_file:
            self.entries = json.load(data_file)

        for entry in self.entries['nodes']:
            op = None
            if entry['type'] == 'signaller':
                op = AlgoOperationSignaller(id=entry['id'], algorithm=self.algorithm)
                op.signalled_potential = OperationContainer.read_property(entry, 'potential', 1)
                op.num_cells = OperationContainer.read_property(entry, 'num_cells', 0)
                op.source = OperationContainer.read_property(entry, 'source', 'memory')
            elif entry['type'] == 'listener':
                op = AlgoOperationListener(id=entry['id'], algorithm=self.algorithm, num_cells=entry['num_cells'])
                op.filter = OperationContainer.read_property(entry, 'filter', None)
                op.connected_with = OperationContainer.read_property(entry, 'connected_with', None)
                op.is_ = OperationContainer.read_property(entry, 'is', None)
                op.previously_unseen = OperationContainer.read_property(entry, 'previously_unseen', False)
                if entry['num_cells'] == 1:
                    op.event = MemoryEvent.One
                elif entry['num_cells'] == 2:
                    op.event = MemoryEvent.Two
            elif entry['type'] == 'memory':
                op = AlgoOperationMemory(id=entry['id'], algorithm=self.algorithm)
                op.num_cells = OperationContainer.read_property(entry, 'num_cells', 0)
                op.source = OperationContainer.read_property(entry, 'source', 'memory')
                op.operation = OperationContainer.read_property(entry, 'operation', 'write')
            elif entry['type'] == 'compare':
                op = AlgoOperationCompare(id=entry['id'], algorithm=self.algorithm)
            elif entry['type'] == 'exit':
                op = AlgoOperationExit(id=entry['id'], algorithm=self.algorithm)
            elif entry['type'] == 'call':
                op = AlgoOperationCall(id=entry['id'], algorithm=self.algorithm, called_algo=entry['algo'])
            if op:
                self.operations.append(op)

        for entry in self.entries['connections']:
            source_node = self.get_node_by_id(entry['source'])
            target_node = self.get_node_by_id(entry['target'])
            connection = OperationConnection(source=source_node, target=target_node)
            self.connections.append(connection)


    @staticmethod
    def read_property(entry, property_name, default_value):
        if property_name in entry:
            return entry[property_name]
        else:
            return default_value

    def get_node_by_id(self, id):
        ops = [op for op in self.operations if op.node_id == id]
        if ops:
            return ops[0]
        return None


    def get_outgoing_connections(self, node):
        return [conn for conn in self.connections if conn.source == node]


    def get_incoming_connections(self, node):
        return [conn for conn in self.connections if conn.target == node]


    def print_nodes(self):
        repr = ''
        for node in self.nodes:
            firing_symbol = 'F' if node.firing else ' '
            repr += '[{} {}] '.format(firing_symbol, node.node_id)
        return repr

