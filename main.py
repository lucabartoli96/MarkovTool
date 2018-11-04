
from MarkovChain import MarkovChain
from reader import read
import time


import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def main():

    # S = ["A", "B", "C"]
    # sigma = [0.2, 0.2, 0.6]
    # pi = [[0.5, 0.5, 0], [0.1, 0, 0.9], [0, 0, 1]]

    # S = ['A', 'B', 'C', 'D', 'E']
    # sigma = [1, 0, 0, 0, 0]
    # pi = [[0.25, 0.75, 0, 0, 0], [0.5, 0.5, 0, 0, 0],
    #       [0, 0, 1, 0, 0], [0, 0, 0.3, 0.7, 0], [1, 0, 0, 0, 0]]

    # S = ['A', 'B', 'C', 'D']
    # sigma = [1, 0, 0, 0]
    # pi = [[0, 0, 0, 1], [0, 0, 0, 1],
    #       [0.5, 0.5, 0, 0], [0, 0, 1, 0]]

    #mc = MarkovChain(S, sigma, pi)

    mc = read('prova.txt')

    st = mc.states()
    iD = mc.initialDistribution()
    tM = mc.transitionMatrix()
    eL = mc.edgeList()

    print st
    print iD
    print tM
    print eL

    # Test Communication Matrix computation
    # compares it to the faster version
    print mc.comMat()
    print ""


    # Test classes procedure
    print mc.classes()
    print ""

    # Test single state class procedure
    for s in st:
        print s + ': ' + str(mc.getClass(s))
    print ""

    # For each couple of states prints if they
    # communicate or they are equivalent
    # for  s1 in S:
    #     for s2 in S:
    #         print s1 + '<' + s2 + ': ' + str(mc.communicate(s1, s2))
    #         print s1 + '=' + s2 + ': ' + str(mc.equivalent(s1, s2))
    #         print ""

    for state in st:
        print "period(" + state + ")= " + str(mc.period(state))

    G = nx.DiGraph()
    G.add_nodes_from(st)
    G.add_weighted_edges_from(eL)

    # pos = nx.spring_layout(G)
    # nx.draw_networkx_nodes(G, pos, node_size = 500)
    # nx.draw_networkx_edges(G, pos, arrows=True)
    # nx.draw_networkx_labels(G, pos)
    # labels = nx.get_edge_attributes(G,'weight')
    # nx.draw_networkx_edge_labels(G, pos, font_family='sans-serif',
    #     edge_labels=labels)
    G.graph['edge'] = {'arrowsize': '1', 'splines': 'curved'}
    G.graph['graph'] = {'scale': '1000'}

    A = to_agraph(G)
    A.layout('dot')

    # set edge labels
    for triplet in eL:
        e = A.get_edge(triplet[0], triplet[1])
        e.attr['label'] = triplet[2]

    A.draw('image.png')
    # img = mpimg.imread('image.png')
    # plt.imshow(img)
    # plt.show()

    #plt.show()
