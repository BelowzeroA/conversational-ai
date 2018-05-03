

class AlgoBuilder:

    def __init__(self, brain):
        self.brain = brain
        self.queries = {}


    def load_from_file(self, filename):
        current_query = ''
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith('\t'):
                    self.queries[current_query].append(line.strip())
                else:
                    current_query = line
                    self.queries[current_query] = []


    def tokenize_line(self, line):
        translator = str.maketrans('', '', string.punctuation.replace('-', '') + '«»')
        terms = line.translate(translator).split()
        return terms


    def store(self, filename):
        out_val = {'nodes': self.container.nodes, 'connections': self.container.connections}
        with open(filename, mode='wt', encoding='utf-8') as output_file:
            print(self._serialize(out_val), file=output_file)


    def build(self, filename):
        self.load_from_file(filename)
