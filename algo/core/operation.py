

class AlgoOperation:

    def __init__(self, id: str, algorithm):
        self.node_id = id
        self.threshold = 0.5
        self.algorithm = algorithm
        self.potential = 0
        self.firing = False


    def fire(self):
        self.firing = True
        print('operation {} firing'.format(self.node_id))


    def update(self):
        if self.potential > self.threshold:
            self.fire()
            self.potential = 0

        if self.firing:
            connections = self.algorithm.container.get_outgoing_connections(self)
            for connection in connections:
                connection.pulsing = True