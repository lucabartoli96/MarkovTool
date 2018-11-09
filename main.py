
from MarkovChain import MarkovChain
import reader as mcr
import time
import os

import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from pylatex import Document, Section, Command, Itemize, Subsection, Tabular,\
                    Math, TikZ, Axis, Plot, Figure, Matrix, Alignat, LongTable,\
                    MultiColumn, NewPage
from pylatex.utils import italic


def toLatexSet(elems, beginWith=None, hintLen=None):

    def append(length, data, elem, canBreak):
        data.append(elem)
        length += len(elem)
        if hintLen and length >= hintLen and canBreak:
            data.append(' \\\\ ')
            data.append('& ')
            length = 0
        return length

    data = []
    length = 0

    if beginWith:
        for elem in beginWith:
            append(length, data, elem, False)

    if not hintLen:
        length = append(length, data, '\left\{ ', False)-6
    else:
        length = append(length, data, '\{ ', False)

    if hintLen:
        append(length, data, '&', False)
    for elem in elems:
        length = append(length, data, unicode(elem), False)

        if elem != elems[-1]:
            length = append(length, data, ',\ ', True)

    if not hintLen:
        append(length, data, '\\right\}', False)
    else:
        append(length, data, '\}', False)

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
                          hintLen=60)

        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.extend(data)


def initialDistribution(doc, iD):
    with doc.create(Subsection('Initial Distribution')):
        data = []
        for s in iD:
            data.append('\sigma_{%s}=%0.2f' % (toLatexState(s), iD[s]))
            data.append(',\ ')
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
        i=0
        for s1 in tL:
            inner = []
            for s2 in tL[s1]:
                inner.append('%s: %s' % (toLatexState(s2), toLatexProb(tL[s1][s2])))

            innerString = ''.join(toLatexSet(inner,
                        beginWith=[toLatexState(s1), '\\rightarrow']))
            doc.append(Math(data=innerString, escape=False))


def edgeList(doc, eL):
    doc.append(NewPage())
    with doc.create(Subsection('Edges')):
        with doc.create(LongTable("l l l l l l l l l l l l l")) as data_table:
            data_table.add_hline()
            data_table.add_row( ['$s$', '$s\'$', '$p$', ' ', ' ']*2 + ['$s$', '$s\'$', '$p$'], escape=False)
            data_table.add_hline()
            data_table.end_table_header()
            data_table.add_hline()
            data_table.end_table_last_footer()
            for i in range(0, len(eL), 3):
                row = []

                triplet = eL[i]
                row += ['$' +  toLatexState(triplet[0]) + '$',
                        '$' +  toLatexState(triplet[1]) + '$',
                        '$' +  toLatexProb(triplet[2]) + '$',
                        ' ', ' ']
                if i+1 < len(eL):
                    triplet = eL[i+1]
                    row += ['$' +  toLatexState(triplet[0]) + '$',
                            '$' +  toLatexState(triplet[1]) + '$',
                            '$' +  toLatexProb(triplet[2]) + '$',
                            ' ', ' ']
                    if i+2 < len(eL):
                        triplet = eL[i+2]
                        row += ['$' +  toLatexState(triplet[0]) + '$',
                                '$' +  toLatexState(triplet[1]) + '$',
                                '$' +  toLatexProb(triplet[2]) + '$']
                    else:
                        row += [' ',]*3
                else:
                    row += [' ',]*8

                data_table.add_row(row, escape=False)


def classesSection(doc, classes):
    with doc.create(Subsection('Classes')):
        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            for c in classes:
                elems = []
                for s in classes[c]:
                    elems.append(toLatexState(s))
                bW = '\\left[%s\\right] =' % toLatexState(c)
                agn.extend(toLatexSet(elems, beginWith=[bW],hintLen=60))
                agn.append('\\\\')


def periods(doc, classes, mc):
    with doc.create(Subsection('Periodicity')):
        with doc.create(LongTable("l l")) as data_table:
            data_table.add_hline()
            data_table.add_row( ['$s$', '$period(s)$'], escape=False)
            data_table.add_hline()
            data_table.end_table_header()
            data_table.add_hline()
            data_table.end_table_last_footer()
            for c in classes:
                row = ['$' + toLatexState(c) + '$',
                       '$' + str(mc.period(c)) + '$']

                data_table.add_row(row, escape=False)


def periodAndRecur(doc, classes, recursive, mc):
    with doc.create(Subsection('Periodicity and Recurrence')):
        with doc.create(LongTable("l l l")) as data_table:
            data_table.add_hline()
            data_table.add_row( ['$s$', '$period(s)$', '$Recurrence$'], escape=False)
            data_table.add_hline()
            data_table.end_table_header()
            data_table.add_hline()
            data_table.end_table_last_footer()
            for c in classes:
                row = ['$' + toLatexState(c) + '$',
                       '$' + str(mc.period(c)) + '$',
                       str(c in recursive)]

                data_table.add_row(row, escape=False)


def createGraphImage(st, eL):
    G = nx.DiGraph()
    G.add_nodes_from(st)
    G.add_weighted_edges_from(eL)
    G.graph['edge'] = {'arrowsize': '1', 'splines': 'curved'}
    G.graph['graph'] = {'scale': '1000000'}
    A = to_agraph(G)
    A.layout('dot')
    for triplet in eL:
        e = A.get_edge(triplet[0], triplet[1])
        e.attr['label'] = triplet[2]
    A.draw('image.png')

def communicationMatrix(doc, cM):
    with doc.create(Subsection('Communication Matrix')):
        data = ['\setcounter{MaxMatrixCols}{20}', 'C=']
        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.extend(data)
            agn.append(Matrix(cM, mtype='b'))


def main(argv):

    if len(argv) == 1 :
        raise ValueError('No file name specified')

    fileName = argv[1]
    path, fileExtension = os.path.splitext(fileName)
    fileExtension = fileExtension[1:]

    if fileExtension.lower() == 'json':
        mc = mcr.jsonToMarkovChain(fileName)
    else:
        if len(argv) > 2:
            mc = mcr.txtToMarkovChain(fileName, encoding=argv[2])
        else:
            mc = mcr.txtToMarkovChain(fileName)


    # S = ['A', 'B', 'C', 'D']
    # sigma =
    # pi = 

    # mc = MarkovChain(S, sigma, pi)

    #mc = read('prova.txt')
    #mc = read('dante.txt')

    st = mc.states()
    iD = mc.initialDistribution()
    iDA = mc.initialDistributionArray()
    tL = mc.transitionsList()
    tM = mc.transitionMatrix()
    eL = mc.edgeList()
    cM = mc.communicationMatrix()
    classes = mc.classes()
    recursive = mc.recursiveClasses()

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
        classesSection(doc, classes)
        periodAndRecur(doc, classes, recursive, mc)

        if mc.size <= 20:
            communicationMatrix(doc, cM)

        createGraphImage(st, eL)
        with doc.create(Figure()) as pic:
            pic.add_image(image_filename)

    doc.generate_pdf(path, clean_tex=False)


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
