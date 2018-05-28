import ntpath
import os

from algo.core.op_container import OperationContainer
from onto.onto_graph_walker import OntoGraphWalker
from onto.node import Node


class Algorithm:

    def __init__(self, onto_container, filename=None):
        self.container = OperationContainer(onto_container=onto_container, algorithm=self)
        if filename:
            self.container.load(filename)
            self.name = os.path.splitext(ntpath.basename(filename))[0]
        self.onto_container = onto_container
        self.brain = self.onto_container.brain
        self.active = False
        self.finished = False
        self.time_exceeded = False
        self.start_tick = 0
        self.current_tick = 0
        self.wait_ticks = self.read_property('waiting', 0)
        self.reply_type = self.read_property('reply_type', None)
        self.initial_potential_period = self.read_property('initial_potential_period', Node.initial_potential_period)
        self.next = None
        self.switching_to = None
        self.callback = None
        self.awaiting = False
        self.graph_walker = OntoGraphWalker(self.brain, self)


    def read_property(self, property_name, default_value):
        if property_name in self.container.entries:
            return self.container.entries[property_name]
        else:
            return default_value


    def start(self, tick):
        self.start_tick = tick
        self.current_tick = tick
        self.active = True
        self.onto_container.reset()
        self.brain.working_memory.reset_memory()
        self.container.operations[0].fire()


    def update(self, tick):
        if self.active:
            self.current_tick = tick
            if self.current_tick - self.start_tick >= self.wait_ticks and self.wait_ticks:
                self.time_exceeded = True
                self.active = False
                return

            for op in self.container.operations:
                op.update()
            for conn in self.container.connections:
                conn.update()

            if self.switching_to and self.callback:
                self.active = False
                self.callback(self.switching_to)

            if self.awaiting:
                self.graph_walker.make_step(self.current_tick)


    def regain_execution(self):
        self.switching_to = None
        self.active = True


    def init_onto_nodes(self):
        for node in self.onto_container.nodes:
            if node.initial:
                node.initial_potential_period = self.initial_potential_period


    def __repr__(self):
        return self.name

