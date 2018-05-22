from typing import List

from memory.memory_events import MemoryEvent
from memory.working_memory_cell import WorkingMemoryCell
# from onto.node import Node

memory_limit = 20


class WorkingMemory:

    def __init__(self, brain):
        self.brain = brain
        self.listeners = []
        self.subscribers = []
        self.context = None
        self.cells: List[WorkingMemoryCell] = []
        self.stack: List = []
        self.write_counter = {}
        self.support_context = False
        for i in range(memory_limit):
            self.cells.append(WorkingMemoryCell())


    def write(self, node):
        node_found = [cell.node for cell in self.cells if not cell.free and cell.node == node]
        if node_found:
            return
        for cell in self.cells:
            if cell.free:
                cell.write(node)
                self.notify_subscribers(node)
                if node in self.write_counter:
                    self.write_counter[node] += 1
                else:
                    self.write_counter[node] = 1
                break


    def notify_subscribers(self, node):
        for subscriber in self.subscribers:
            subscriber(node)


    def push(self, num_cells=0, source='memory'):
        if source == 'memory':
            cells_to_push = [cell for cell in self.cells if not cell.free and cell.captured]
            num_pushed = 0
            for cell in cells_to_push:
                num_pushed += 1
                self.stack.append(cell.node)
                cell.captured = False
                if num_pushed >= num_cells:
                    break
        elif source == 'context':
            self.stack.append(self.context)


    def attach_subscriber(self, function):
        self.subscribers.append(function)


    def attach_listener(self, operation):
        self.listeners.append({'operation': operation, 'event': operation.event})


    def notify_listeners(self, event, charged_cells, abstract, concrete):
        for listener in self.listeners:
            if listener['event'] == event:
                operation = listener['operation']
                if not operation.algorithm.active:
                    continue
                wm_context = {'context': self.context,
                              'abstract': abstract,
                              'concrete': concrete,
                              'write_counter': self.write_counter,
                              'attention': charged_cells}
                operation.fire_if_conditions(wm_context)


    def broadcast(self, num_cells, source):
        done_cells = 0
        if source == 'stack':
            if len(self.stack) < num_cells:
                return
            for i in range(num_cells):
                self.broadcast_node(self.stack.pop())
        else:
            max_charge = max(self.cells, key=lambda c: c.charge).charge
            cells_to_broadcast = [cell for cell in self.cells if not cell.free and cell.captured]
            for cell in cells_to_broadcast:
                cell.captured = False
                self.broadcast_node(cell.node)
                done_cells += 1
                if done_cells == num_cells:
                    break


    def broadcast_node(self, node):
        node.potential += self.brain.control_signal_potential
        node.fire()
        node.firing_period = self.brain.control_signal_period


    def active_cells_content(self):
        max_charge = max(self.cells, key=lambda c: c.charge).charge
        return [cell.node for cell in self.cells if not cell.free and cell.charge == max_charge]


    def captured_cells_content(self):
        max_charge = max(self.cells, key=lambda c: c.charge).charge
        return [cell.node for cell in self.cells if not cell.free and cell.charge == max_charge and cell.captured]


    def check_listeners(self):
        charged = []
        abstract = True
        concrete = True
        max_potential = 0.0
        for cell in self.cells:
            if not cell.free and cell.charge == WorkingMemoryCell.max_charge:
                if cell.node_potential > max_potential:
                    max_potential = cell.node_potential

        for cell in self.cells:
            # if not cell.free and cell.charge == WorkingMemoryCell.max_charge and cell.node_potential == max_potential:
            if not cell.free and cell.charge == WorkingMemoryCell.max_charge:
                charged.append(cell)
                abstract |= cell.node.abstract
                concrete |= not cell.node.abstract

        if len(charged) > 1:
            self.notify_listeners(MemoryEvent.Two, charged, abstract, concrete)
        for cell in charged:
            self.notify_listeners(MemoryEvent.One, [cell], cell.node.abstract, not cell.node.abstract)


    def update(self):
        self.check_listeners()

        if self.context and self.support_context:
            self.context.fire()

        for cell in self.cells:
            cell.update()


    def __repr__(self):
        repr = ''
        for cell in self.cells:
            if not cell.free:
                repr += '[{} {}] '.format(cell.node.node_id, cell.node.pattern)
        return repr

