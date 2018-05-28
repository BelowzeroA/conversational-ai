from brain.brain import Brain
from onto.node import Node


class Connection:

    initial_pulsing_tick = -999

    def __init__(self, source: Node, target: Node, container):
        self.source = source
        self.target = target
        self.weight = Brain.default_primary_connection_weight
        self.sign = 1
        self.container = container
        self.pulsing = False
        self.potential = 0
        self.last_pulsing_tick = Connection.initial_pulsing_tick
        self.secondary = False


    def update(self):
        if self.pulsing:
            self.last_pulsing_tick = self.container.brain.current_tick
            weight_coefficient = Brain.default_secondary_connection_weight if self.secondary else\
                Brain.default_primary_connection_weight
            potentiation = self.weight * weight_coefficient
            if self.potential >= Brain.control_signal_potential:
                potentiation = self.weight * weight_coefficient * self.potential

            self.target.potential += potentiation # self.potential
            self.target.contributors.append('{}: {}'.format(self.source.node_id, potentiation))
        self.pulsing = False
        self.potential = 0


    def reset(self):
        self.potential = 0
        self.pulsing = False
        self.last_pulsing_tick = Connection.initial_pulsing_tick


    def _repr(self):
        return '[{}-{}]'.format(self.source.node_id, self.target.node_id)

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()


    def serialize(self):
        _dict = {
            'source': self.source.node_id,
            'target': self.target.node_id,
            'weight': self.weight
        }
        return _dict
