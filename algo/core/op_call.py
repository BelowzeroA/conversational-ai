from algo.core.operation import AlgoOperation


class AlgoOperationCall(AlgoOperation):

    def __init__(self, id: str, algorithm, called_algo):
        self.called_algo = called_algo
        super(AlgoOperationCall, self).__init__(id, algorithm)


    def update(self):
        super(AlgoOperationCall, self).update()
        if self.firing:
            self.firing = False
            self.algorithm.switching_to = self.called_algo
