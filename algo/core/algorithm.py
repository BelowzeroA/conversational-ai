import ntpath
import os

from algo.core.op_container import OperationContainer
from onto.node import Node


class Algorithm:

    def __init__(self, onto_container, filename=None):
        self.algo_id = id
        self.container = OperationContainer(onto_container=onto_container, algorithm=self)
        if filename:
            self.container.load(filename)
            self.name = os.path.splitext(ntpath.basename(filename))[0]
        self.onto_container = onto_container
        self.active = False
        self.finished = False
        self.time_exceeded = False
        self.start_tick = 0
        self.current_tick = 0
        self.wait_ticks = self.container.entries['waiting']
        self.reply_type = self.container.entries['reply_type']
        self.initial_potential_period = self.container.entries['initial_potential_period'] \
            if 'initial_potential_period' in self.container.entries else Node.initial_potential_period
        self.next = None


    def start(self, tick):
        self.start_tick = tick
        self.current_tick = tick
        self.active = True


    def update(self, tick):
        if self.active:
            self.current_tick = tick
            if self.current_tick - self.start_tick >= self.wait_ticks:
                self.time_exceeded = True
                self.active = False
                return

            for op in self.container.operations:
                op.update()
            for conn in self.container.connections:
                conn.update()


    def init_onto_nodes(self):
        for node in self.onto_container.nodes:
            if node.initial:
                node.initial_potential_period = self.initial_potential_period


    def __repr__(self):
        return self.name

