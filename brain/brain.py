from memory.working_memory import WorkingMemory


class Brain:
    # hyperparameters
    control_signal_potential = 2
    control_signal_period = 4
    default_primary_connection_weight = 1
    default_secondary_connection_weight = 0.5
    potential_decay_rate = 1
    default_node_threshold = 2

    def __init__(self, onto_container, algo_container):
        self.onto_container = onto_container
        self.algo_container = algo_container
        self.working_memory = WorkingMemory(self)

        self.onto_container.attach_to_brain(self)
        self.algo_container.attach_to_brain(self)
        self.current_tick = 0

