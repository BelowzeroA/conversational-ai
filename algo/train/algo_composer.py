from algo.core.algorithm import Algorithm
from algo.graph_walker import GraphWalker


class AlgoComposer:

    def __init__(self, brain, estimator):
        self.brain = brain
        self.estimator = estimator
        self.graph_walker = GraphWalker(brain=brain)


    def compose(self, question, answer):
        result = self.graph_walker.resolve(question)
        if result:
            correct = self.estimator.estimate(question, answer)
            if not correct:
                return self._compose_algorithm(question, answer)


    def _compose_algorithm(self, question, answer):
        if len(self.brain.algo_container.algorithms) != 1:
            raise Exception('unexpected number of algorithms')

        base_algo = self.brain.algo_container.algorithms[0]
        for node in self.brain.onto_container.nodes:
            if node.abstract:
                attempted_algo = Algorithm(onto_container=self.brain.onto_container)
                attempted_algo.copy_from(base_algo)
                self.brain.algo_container.add_algorithm(attempted_algo)
                result = self.graph_walker.resolve(question)
                if result:
                    correct = self.estimator.estimate(question, result)
                    if correct:
                        return attempted_algo


