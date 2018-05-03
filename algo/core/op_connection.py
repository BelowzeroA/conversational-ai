from algo.core.operation import AlgoOperation


class OperationConnection:

    def __init__(self, source: AlgoOperation, target: AlgoOperation):
        self.source = source
        self.target = target
        self.pulsing = False
        self.weight = 1


    def update(self):
        if self.pulsing:
            self.target.potential += self.weight
            self.pulsing = False