
from MarkovChain import MarkovChain
from reader import read
import time
import os

import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from pylatex import Document, Section, Command, Itemize, Subsection, Tabular,\
                    Math, TikZ, Axis, Plot, Figure, Matrix, Alignat
from pylatex.utils import italic

def toLatexSet(elems, hintLen=None):
    data = ['\{']
    if hintLen:
        data.append('&')
    i = 0
    for elem in elems:
        data.append(elem)
        if elem != elems[-1]:
            data.append(',')
        if hintLen and i >= hintLen:
            data.append(' \\\\ ')
            data.append('& ')
            i=0
        i += 1
    data.append('\}')
    return data

def main():

    # S = ["A", "B", "C"]
    # sigma = [0.2, 0.2, 0.6]
    # pi = [[0.5, 0.5, 0], [0.1, 0, 0.9], [0, 0, 1]]

    # S = ['A', 'B', 'C', 'D', 'E']
    # sigma = [1, 0, 0, 0, 0]
    # pi = [[0.25, 0.75, 0, 0, 0], [0.5, 0.5, 0, 0, 0],
    #       [0, 0, 1, 0, 0], [0, 0, 0.3, 0.7, 0], [1, 0, 0, 0, 0]]
    #
    # S = ['A', 'B', 'C', 'D']
    # sigma = [1, 0, 0, 0]
    # pi = [[0, 0, 0, 1], [0, 0, 0, 1],
    #       [0.5, 0.5, 0, 0], [0, 0, 1, 0]]

    # mc = MarkovChain(S, sigma, pi)

    #mc = read('prova.txt')

    mc = read('altraprova.txt')

    st = mc.states()
    iD = mc.initialDistribution()
    iDA = mc.initialDistributionArray()
    tL = mc.transitionsList()
    tM = mc.transitionMatrix()
    eL = mc.edgeList()

    print st
    print iDA
    print tL
    print tM
    print eL

    # Test Communication Matrix computation
    C = mc.comMat()
    print C
    print ""


    # Test classes procedure
    classes = mc.classes()
    print classes
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

    image_filename = os.path.join(os.path.dirname(__file__), 'image.png')
    doc = Document()

    with doc.create(Section('Markov Chain')):
        doc.append('States set:')

        data = ['S', '='] + toLatexSet(list(s.replace('#', '\#') for s in st), 25)

        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.extend(data)

        doc.append('Initial distribution: ')

        data = []
        for s in iD:
            data.append('\sigma_{%s}=%0.2f' % (s.replace('#', '\#'), iD[s]))
            data.append(',')
        del data[-1]

        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.extend(data)

        doc.append('Transition matrix: ')

        if mc.size <= 20:
            data = ['\setcounter{MaxMatrixCols}{20}', '\Pi=']
            with doc.create(Alignat(numbering=False, escape=False)) as agn:
                agn.extend(data)
                agn.append(Matrix(tM, mtype='b'))
        else:
            data = ['\Pi:\\\\']
            outer = []
            i=0
            for s1 in tL:
                inner = []
                for s2 in tL[s1]:
                    inner.append('%s: %0.2f' % (s2.replace('#', '\#'), tL[s1][s2]))

                innerString = ''.join([s1.replace('#', '\#'), '\\rightarrow'] + toLatexSet(inner))
                outer.append(innerString)
            data = toLatexSet(outer, 3)

            with doc.create(Alignat(numbering=False, escape=False)) as agn:
                agn.extend(data)

        doc.append('Edges list: ')

        elems = []
        for triplet in eL:
            s1 = triplet[0].replace('#', '\#')
            s2 = triplet[1].replace('#', '\#')
            p  = triplet[2]
            elems.append('(%s, %s, %0.2f)' % (s1, s2, p))
        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.extend(toLatexSet(elems, 5))

        with doc.create(Subsection('Classes')):

            with doc.create(Alignat(numbering=False, escape=False)) as agn:
                for c in classes:
                    agn.append('\\left[%s\\right] =' % c.replace('#', '\#'))
                    elems = []
                    for s in classes[c]:
                        elems.append(s.replace('#', '\#'))
                    agn.extend(toLatexSet(elems, 15))
                    agn.append('\\\\')

            doc.append('where: ')

            with doc.create(Alignat(numbering=False, escape=False)) as agn:
                first = True
                for c in classes:
                    if not first:
                        agn.append(',\\ ')
                    agn.append('period({}) = {}'.format(c.replace('#', '\#'), mc.period(c)))
                    first = False

        with doc.create(Figure(width="\\textwidth",height="\textheight",keepaspectratio=True)) as pic:
            pic.add_image(image_filename)

    doc.generate_pdf('full', clean_tex=False)
