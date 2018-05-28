from algo.core.operation import AlgoOperation


class AlgoOperationCompare(AlgoOperation):

    def __init__(self, id: str, algorithm):
        super(AlgoOperationCompare, self).__init__(id, algorithm)
        self.fired = False
        self.source = 'memory'


    def update(self):
        super(AlgoOperationCompare, self).update()
        if self.firing:
            self.firing = False
            if not self.fired:
                self.algorithm.brain.working_memory.compare_stack_with_captured()
            self.fired = True


