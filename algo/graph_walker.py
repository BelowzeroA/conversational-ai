from brain.brain import Brain
from helpers.question_parser import QuestionParser
from helpers.reply_composer import ReplyComposer


class GraphWalker:

    def __init__(self, brain):
        self.brain = brain
        self.resolved = False
        self.current_tick = 0
        self.train_mode = False
        self.verbose = True
        self.broadcast_done = False
        self.node_to_signal = None
        self.input_nodes = []


    def resolve(self, input):
        question_parser = QuestionParser(self.brain.onto_container, input)
        self.input_nodes = question_parser.get_initial_nodes()

        self.brain.working_memory.context = question_parser.get_context_entry()
        self.brain.working_memory.support_context = not question_parser.is_yes_no_query()

        if self.train_mode:
            self.brain.working_memory.attach_subscriber(self._on_memory_write)

        self.fire_initial()

        self.brain.algo_container.activate_first()

        self.run_loop()

        reply_composer = ReplyComposer(brain=self.brain)
        return reply_composer.reply_as_string()


    def _on_memory_write(self, node):
        if not self.broadcast_done:
            self.node_to_signal = node
            self.broadcast_done = True


    def run_loop(self):
        self.current_tick = 0
        while not self.brain.algo_container.is_finished() and self.current_tick <= 60:
            self.update_state()
            if self.verbose:
                print(self.brain.algo_container.active_algorithm, self.brain.onto_container)
                print(self.brain.working_memory)


    def update_state(self):
        self.current_tick += 1
        self.brain.current_tick = self.current_tick

        algorithm_switched = self.brain.algo_container.update(self.current_tick)

        if self.brain.algo_container.finished:
            return
        elif algorithm_switched:
            self.reset_state(self.brain.algo_container.active_algorithm)

        self.current_tick += 1
        algorithm_switched = self.brain.algo_container.update(self.current_tick)
        if not self.brain.algo_container.finished:
            if algorithm_switched:
                self.reset_state(self.brain.algo_container.active_algorithm)
            self.brain.onto_container.update()
            self.brain.working_memory.update()

            if self.node_to_signal:
                self.brain.working_memory.broadcast_node(self.node_to_signal)
                self.node_to_signal = None


    def reset_state(self, algorithm):
        for node in self.brain.onto_container.nodes:
            node.potential = 0
        self.fire_initial()
        algorithm.init_onto_nodes()


    def fire_initial(self):
        for node in self.input_nodes:
            if len(self.input_nodes) == 1:
                node.potential = Brain.control_signal_potential
            node.initial = True
            node.fire()
