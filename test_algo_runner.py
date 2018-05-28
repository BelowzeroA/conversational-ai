from algo.algo_container import AlgoContainer
from algo.core.algorithm import Algorithm
from algo.algo_runner import AlgoRunner
from algo.train.algo_composer import AlgoComposer
from algo.train.estimator import Estimator
from algo.build.algo_builder import AlgoBuilder
from brain.brain import Brain
from onto.builder import OntoBuilder
from onto.builder2 import OntoBuilder2
from onto.onto_container import OntoContainer


def main():
    builder = OntoBuilder2()
    builder.build_facts('data/fact_base.txt')
    builder.store('data/knowledge_base.json')

    onto_container = OntoContainer()
    onto_container.load("data/knowledge_base.json")
    onto_container.build_secondary_connections()

    algo_container = AlgoContainer()

    brain = Brain(onto_container=onto_container, algo_container=algo_container)
    estimator = Estimator(brain)

    algo_builder = AlgoBuilder(brain)
    algo_builder.build_from('data/algo_base.txt', './algo/patterns')

    algo_container.add_algorithm(
        Algorithm(onto_container=onto_container, filename='algo/patterns/closed_q_reply.json'))
    algo_container.add_algorithm(
        Algorithm(onto_container=onto_container, filename='algo/patterns/what_question_reply.json'))
    algo_container.add_algorithm(
        Algorithm(onto_container=onto_container, filename='algo/patterns/switch_context.json'))
    algo_container.add_algorithm(
        Algorithm(onto_container=onto_container, filename='algo/patterns/get_closest.json'))
    algo_container.attach_to_brain(brain)

    # input = 'do people in a slavic speaking country speak english?'
    input = 'do people in a USA speak english?'
    # input = 'does USA have people?'
    print('query:', input)
    algo_runner = AlgoRunner(brain=brain)
    result = algo_runner.run(input, verbose=False)
    print('result:', result)


if __name__ == '__main__':
    main()