from algo.algo_container import AlgoContainer
from algo.core.algorithm import Algorithm
from algo.graph_walker import GraphWalker
from algo.train.algo_composer import AlgoComposer
from algo.train.estimator import Estimator
from brain.brain import Brain
from onto.builder import OntoBuilder
from onto.builder2 import OntoBuilder2
from onto.onto_container import OntoContainer


def main():
    builder = OntoBuilder2()
    # builder.build_knowledge_base('data/knowledge_base.txt')
    builder.build_facts('data/fact_base.txt')
    builder.store('data/knowledge_base.json')

    onto_container = OntoContainer()
    onto_container.load("data/knowledge_base.json")
    onto_container.build_secondary_connections()

    algo1 = Algorithm(onto_container=onto_container, filename='algo/patterns/simple_connection.json')

    algo_container = AlgoContainer()
    algo_container.add_algorithm(algo1)

    brain = Brain(onto_container=onto_container, algo_container=algo_container)
    estimator = Estimator(brain)
    algo_composer = AlgoComposer(brain=brain, estimator=estimator)

    # input = 'do people in a slavic speaking country speak english?'
    input = 'do people in a USA speak english?'
    # input = 'does USA have people?'

    graph_walker = GraphWalker(brain=brain)
    graph_walker.train_mode = True
    result = graph_walker.resolve(input)
    print(result)
    exit()

    algorithm = algo_composer.compose(input, 'right')
    if algorithm:
        algorithm.save('algo/patterns/composed.json')


if __name__ == '__main__':
    main()