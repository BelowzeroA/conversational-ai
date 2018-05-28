from algo.core.operation import AlgoOperation


class AlgoOperationMemory(AlgoOperation):

    def __init__(self, id: str, algorithm, num_cells=0):
        super(AlgoOperationMemory, self).__init__(id, algorithm)
        self.num_cells = num_cells
        self.fired = False
        self.source = 'memory'
        self.operation = 'write'


    def update(self):
        super(AlgoOperationMemory, self).update()
        if self.firing:
            self.firing = False
            if not self.fired:
                self.perform()
            self.fired = True


    def perform(self):
        if self.operation == 'write':
            self.algorithm.brain.working_memory.push(self.num_cells, source=self.source)
        elif self.operation == 'exchange_context':
            self.algorithm.brain.working_memory.exchange_context()


