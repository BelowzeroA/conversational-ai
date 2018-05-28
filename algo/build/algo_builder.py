import string
import os
import json

class AlgoBuilder:

    def __init__(self, brain):
        self.brain = brain
        self.queries = {}


    def load_from_file(self, filename):
        current_query = ''
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith(' '):
                    self.queries[current_query].append(line.strip())
                else:
                    current_query = line
                    self.queries[current_query] = []


    def tokenize_line(self, line):
        translator = str.maketrans('', '', string.punctuation.replace('-', '') + '«»')
        terms = line.translate(translator).split()
        return terms


    def _transform_query(self, q):
        ops = []
        for pattern in self.queries[q]:
            terms = self.tokenize_line(pattern)
            first_term = terms[0]
            if first_term == 'store':
                ops.append(self._op_store(terms))
            if first_term == 'what':
                ops.append(self._op_call('switch_context'))
                ops.append(self._op_call('what_question_reply'))
            if first_term == 'compare':
                ops.append(self._op_compare())

        ops.append(self._op_exit())

        for i, op in enumerate(ops):
            op['id'] = str(i + 1)
        return ops


    def _make_op_struct(self, type):
        return {'id': 0, 'type':  type}


    def _op_store(self, terms):
        op = self._make_op_struct('memory')
        op['source'] = terms[1]
        return op


    def _op_call(self, algo_name):
        op = self._make_op_struct('call')
        op['algo'] = algo_name
        return op


    def _op_compare(self):
        op = self._make_op_struct('compare')
        return op


    def _op_exit(self):
        op = self._make_op_struct('exit')
        return op

    @staticmethod
    def _serialize(value):
        return json.dumps(value)


    def _store(self, operations, filename):
        out_val = { 'start_node': 1, 'nodes': operations, 'connections': self._make_connections(operations)}
        with open(filename, mode='wt', encoding='utf-8') as output_file:
            print(self._serialize(out_val), file=output_file)


    def _make_connections(self, ops):
        connections = []
        for i in range(1, len(ops)):
            connections.append({'source': str(i), 'target': str(i + 1)})
        return connections


    def build_from(self, filename, store_path):
        self.load_from_file(filename)
        for q in self.queries:
            ops = self._transform_query(q)
            q_id = q.split(':')[1].strip()
            algo_filename = os.path.join(store_path, q_id + '.json')
            self._store(ops, algo_filename)
