import string


class AlgoDetector:

    def __init__(self):
        pass


    def tokenize_line(self, line):
        translator = str.maketrans('', '', string.punctuation.replace('-', '') + '«»')
        terms = line.translate(translator).split()
        return terms


    def get_algo_id(self, query):
        terms = self.tokenize_line(query)
        if terms[0] == 'do':
            return 'closed_question_reply'
        if terms[0] == 'what':
            return 'what_question_reply'
