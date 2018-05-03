from algo.core.operation import AlgoOperation


class AlgoOperationExit(AlgoOperation):

    def __init__(self, id: str, algorithm):
        # self.num_cells = num_cells
        super(AlgoOperationExit, self).__init__(id, algorithm)


    def update(self):
        super(AlgoOperationExit, self).update()
        if self.firing:
            self.firing = False
            self.algorithm.active = False
            self.algorithm.finished = True
