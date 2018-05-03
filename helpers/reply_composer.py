

class ReplyComposer:

    def __init__(self, brain):
        self.brain = brain


    def reply_as_string(self):
        reply_type = self.brain.algo_container.active_algorithm.reply_type
        captured_cells = self.brain.working_memory.captured_cells_content()
        if self.brain.algo_container.finished:
            if reply_type == 'memory':
                return captured_cells[0].pattern
            elif reply_type == 'yes':
                return 'yes'
            elif reply_type == 'ambiguity':
                return 'need to clarify: {} or {}'.format(captured_cells[0], captured_cells[1])
        else:
            return 'answer not found'