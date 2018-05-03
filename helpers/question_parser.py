import string


class QuestionParser:

    def __init__(self, onto_container, text):
        self.onto_container = onto_container
        self.text = text
        translator = str.maketrans('', '', string.punctuation.replace('-', '') + '«»')
        self.terms = self.text.translate(translator).split()


    def get_onto_terms(self):
        entries = []
        for term in self.terms:
            if self.onto_container.get_node_by_pattern(term):
                entries.append(term)
        return entries


    def is_yes_no_query(self):
        return self.terms[0] in ['do', 'does', 'is', 'was']


    def get_context_entry(self):
        nodes = self.onto_container.get_nodes_by_pattern(self.terms)
        if self.is_yes_no_query():
            return nodes[-1:][0]
        else:
            return nodes[0]


    def get_initial_nodes(self):
        nodes = self.onto_container.get_nodes_by_pattern(self.terms)
        if self.is_yes_no_query():
            context_node = self.get_context_entry()
            return [node for node in nodes if node != context_node and node is not None]
        return [node for node in nodes if node is not None]