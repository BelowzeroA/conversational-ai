from algo.core.operation import AlgoOperation


class AlgoOperationSignaller(AlgoOperation):

    def __init__(self, id: str, algorithm, num_cells):
        super(AlgoOperationSignaller, self).__init__(id, algorithm)
        self.num_cells = num_cells
        self.fired = False
        self.source = 'memory'


    def update(self):
        super(AlgoOperationSignaller, self).update()
        if self.firing:
            self.firing = False
            if not self.fired:
                self.algorithm.brain.working_memory.broadcast(self.num_cells, source=self.source)
                print('signaller {} fired'.format(self.node_id))
            self.fired = True
