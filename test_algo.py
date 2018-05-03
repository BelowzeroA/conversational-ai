from algo.algo_container import AlgoContainer
from algo.core.algorithm import Algorithm
from algo.graph_walker import GraphWalker
from brain.brain import Brain
from onto.builder import OntoBuilder
from onto.onto_container import OntoContainer


def main():

    builder = OntoBuilder()
    builder.build_knowledge_base('data/knowledge_base.txt')
    builder.build_facts('data/fact_base.txt')
    # builder.store('data/knowledge_base.json')

    onto_container = OntoContainer()
    # onto_container.load("data/sample1.json")
    onto_container.load("data/knowledge_base.json")
    onto_container.build_secondary_connections()

    algo1 = Algorithm(onto_container=onto_container, filename='algo/patterns/because_i_know.json')
    algo2 = Algorithm(onto_container=onto_container, filename='algo/patterns/inference_bridge.json')
    algo3 = Algorithm(onto_container=onto_container, filename='algo/patterns/resolve_ambiguity.json')


    algo_container = AlgoContainer()
    algo_container.add_algorithm(algo1)
    algo_container.add_algorithm(algo2)
    algo_container.add_algorithm(algo3)

    brain = Brain(onto_container=onto_container, algo_container=algo_container)

    input = 'what language do people speak in english speaking country?'
    # input = 'what language people speak in Russia?'
    # input = ['country', 'check', 'side', 'left', 'cross', 'street']
    graph_walker = GraphWalker(brain=brain)
    result = graph_walker.resolve(input)
    print(result)


if __name__ == '__main__':
    main()