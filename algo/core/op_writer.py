from algo.core.operation import AlgoOperation


class AlgoOperationWriter(AlgoOperation):

    def __init__(self, id: str, algorithm, num_cells=0):
        super(AlgoOperationWriter, self).__init__(id, algorithm)
        self.num_cells = num_cells
        self.fired = False
        self.source = 'memory'


    def update(self):
        super(AlgoOperationWriter, self).update()
        if self.firing:
            self.firing = False
            if not self.fired:
                self.algorithm.brain.working_memory.push(self.num_cells, source=self.source)
            self.fired = True
