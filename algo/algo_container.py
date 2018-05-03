from algo.core.algorithm import Algorithm
from algo.core.op_listener import AlgoOperationListener


class AlgoContainer:

    def __init__(self):
        self.active_algorithm = None
        self.active_algorithm_idx = 0
        self.algorithms = []
        self.finished = False
        self.out_of_algorithms = False


    def add_algorithm(self, algo):
        self.algorithms.append(algo)


    def activate_first(self):
        self.active_algorithm = self.algorithms[self.active_algorithm_idx]
        self.active_algorithm.start(1)


    def update(self, tick):
        algorithm_switched = False
        if self.is_finished():
            return True
        if self.active_algorithm.time_exceeded and not self.active_algorithm.finished:
            self.active_algorithm_idx += 1
            if self.active_algorithm_idx >= len(self.algorithms):
                self.out_of_algorithms = True
                return True
            else:
                algorithm_switched = True
                self.active_algorithm = self.algorithms[self.active_algorithm_idx]
                self.active_algorithm.start(tick)

        self.active_algorithm.update(tick)
        if self.active_algorithm.finished:
            self.finished = True
        return algorithm_switched


    def is_finished(self):
        return self.finished or self.out_of_algorithms


    def attach_to_brain(self, brain):
        for algo in self.algorithms:
            algo.brain = brain
            for op in algo.container.operations:
                if isinstance(op, AlgoOperationListener):
                    brain.working_memory.attach_listener(op)