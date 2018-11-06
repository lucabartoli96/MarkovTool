
from MarkovChain import MarkovChain
from reader import read
import time
import os

import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from pylatex import Document, Section, Command, Itemize, Subsection, Tabular,\
                    Math, TikZ, Axis, Plot, Figure, Matrix, Alignat, LongTable,\
                    MultiColumn
from pylatex.utils import italic

#TODO far formattare per bene le stringhe a questa funzione
def toLatexSet(elems, beginWith=None, hintLen=None):

    def append(data, elem, canBreak):
        pass


    if beginWith:
        data = beginWith
    else:
        data = []
    data.append('\{')

    i = len(data)
    length = dataLen(0, data)

    if hintLen:
        data.append('&')
    for elem in elems:
        data.append(str(elem))
        if elem != elems[-1]:
            data.append(',')
        if hintLen and length >= hintLen:
            data.append(' \\\\ ')
            data.append('& ')

    data.append('\}')
    return data

def toLatexState(s):
    return s.replace('#', '\#')

def toLatexProb(p):
    p = str(p)
    if '/' in p:
        i = p.index('/')
        p = '\\frac{' + p[:i] + '}{' + p[i+1:] + '}'
    return p

def stateSet(doc, st):
    with doc.create(Subsection('States set')):
        data = toLatexSet(list(toLatexState(s) for s in st),
                          beginWith=['S', '='],
                          hintLen=25)

        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.extend(data)


def initialDistribution(doc, iD):
    with doc.create(Subsection('Initial Disribution')):
        data = []
        for s in iD:
            data.append('\sigma_{%s}=%0.2f' % (s.replace('#', '\#'), iD[s]))
            data.append(',')
        del data[-1]

        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.extend(data)


def transitionMatrix(doc, tM):
    with doc.create(Subsection('Transitions')):
        data = ['\setcounter{MaxMatrixCols}{20}', '\Pi=']
        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.extend(data)
            agn.append(Matrix(tM, mtype='b'))


def transitionList(doc, tL):
    with doc.create(Subsection('Transitions')):
        data = ['\Pi:\\\\']
        outer = []
        i=0
        for s1 in tL:
            inner = []
            for s2 in tL[s1]:
                inner.append('%s: %0.2f' % (toLatexState(s2), tL[s1][s2]))

            innerString = ''.join(toLatexSet(inner,
                        beginWith=[toLatexState(s1), '\\rightarrow']))
            outer.append(innerString)
        data = toLatexSet(outer, hintLen=3)
        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.extend(data)


def edgeList(doc, eL):
    with doc.create(Subsection('Edges')):
        with doc.create(LongTable("l l l")) as data_table:
            data_table.add_hline()
            data_table.add_row( ['$s_i$', '$s_j$', '$p$'], escape=False)
            data_table.add_hline()
            data_table.end_table_header()
            data_table.add_hline()
            data_table.end_table_last_footer()
            for triplet in eL:
                data_table.add_row(['$' +  toLatexState(triplet[0]) + '$',
                                    '$' +  toLatexState(triplet[1]) + '$',
                                    '$' +  toLatexProb(triplet[2]) + '$'],
                                    escape=False)

def main():

    # S = ["A", "B", "C"]
    # sigma = [0.2, 0.2, 0.6]
    # pi = [[0.5, 0.5, 0], [0.1, 0, 0.9], [0, 0, 1]]

    # S = ['A', 'B', 'C', 'D', 'E']
    # sigma = [1, 0, 0, 0, 0]
    # pi = [[0.25, 0.75, 0, 0, 0], [0.5, 0.5, 0, 0, 0],
    #       [0, 0, 1, 0, 0], [0, 0, 0.3, 0.7, 0], [1, 0, 0, 0, 0]]

    S = ['A', 'B', 'C', 'D']
    sigma = [1, 0, 0, 0]
    pi = [[0, 0, 0, 1], [0, 0, 0, 1],
          [0.5, 0.5, 0, 0], [0, 0, 1, 0]]

    mc = MarkovChain(S, sigma, pi)

    mc = read('prova.txt')
    #mc = read('ungaretti.txt')
    #mc = read('reader.py')

    st = mc.states()
    iD = mc.initialDistribution()
    iDA = mc.initialDistributionArray()
    tL = mc.transitionsList()
    tM = mc.transitionMatrix()
    eL = mc.edgeList()
    classes = mc.classes()

    G = nx.DiGraph()

    G.add_nodes_from(st)
    G.add_weighted_edges_from(eL)

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

        stateSet(doc, st)
        initialDistribution(doc, iD)

        if mc.size <= 20:
            transitionMatrix(doc, tM)
        else:
            transitionList(doc, tL)

        edgeList(doc, eL)

        with doc.create(Subsection('Classes')):

            with doc.create(Alignat(numbering=False, escape=False)) as agn:
                for c in classes:
                    agn.append('\\left[%s\\right] =' % c.replace('#', '\#'))
                    elems = []
                    for s in classes[c]:
                        elems.append(s.replace('#', '\#'))
                    agn.extend(toLatexSet(elems, hintLen=15))
                    agn.append('\\\\')

            doc.append('where: ')

            with doc.create(Alignat(numbering=False, escape=False)) as agn:
                first = True
                i=0
                for c in classes:
                    if first:
                        agn.append('&')
                    else:
                        agn.append(',\\ ')
                    if i >= 3:
                        agn.append('\\\\&')
                        i = 0
                    agn.append('period({}) = {}'.format(c.replace('#', '\#'), mc.period(c)))
                    i += 1
                    first = False

        with doc.create(Figure()) as pic:
            pic.add_image(image_filename)

    doc.generate_pdf('full', clean_tex=False)


def dump(mc):
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
    for  s1 in S:
        for s2 in S:
            print s1 + '<' + s2 + ': ' + str(mc.communicate(s1, s2))
            print s1 + '=' + s2 + ': ' + str(mc.equivalent(s1, s2))
            print ""

    for state in st:
        print "period(" + state + ")= " + str(mc.period(state))
