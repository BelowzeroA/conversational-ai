from algo.core.operation import AlgoOperation


class AlgoOperationWriter(AlgoOperation):

    def __init__(self, id: str, algorithm, num_cells):
        super(AlgoOperationWriter, self).__init__(id, algorithm)
        self.num_cells = num_cells
        self.fired = False


    def update(self):
        super(AlgoOperationWriter, self).update()
        if self.firing:
            self.firing = False
            if not self.fired:
                self.algorithm.brain.working_memory.push(self.num_cells)
            self.fired = True
