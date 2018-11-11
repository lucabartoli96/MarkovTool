# coding=utf-8

from MarkovChain import MarkovChain
import MarkovChainIO as mcio
import time
import os, sys, traceback
import re

# Graph visualization libs
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import dot2tex

# Python to latex libs
from pylatex import Document, Section, Command, Itemize, Subsection, Tabular,\
                    Math, TikZ, Axis, Plot, Figure, Matrix, Alignat, LongTable,\
                    MultiColumn, NewPage, Package, NoEscape, LineBreak
from pylatex.utils import italic, bold


def toLatexSet(elems, beginWith=None, hintLen=None, size=''):

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
        length = append(length, data, size + '\{ ', False)

    if hintLen:
        append(length, data, '&', False)
    for elem in elems:
        length = append(length, data, elem, False)

        if elem != elems[-1]:
            length = append(length, data, ',\ ', True)

    if not hintLen:
        append(length, data, '\\right\}', False)
    else:
        length = append(length, data, size + '\}', False)
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
                        size = '\\Bigg',
                        hintLen=120,
                        beginWith=[toLatexState(s1), '\\rightarrow']))
            with doc.create(Alignat(numbering=False, escape=False)) as agn:
                agn.extend([innerString])


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


def createGraphTikz(st, eL):

    def replaceChars(s):
        return (s.replace('#', '\#')
        .replace('#', '\\#')
        .replace(u'è', 'e\'')
        .replace(u'é', 'e\'')
        .replace(u'ù', 'u\'')
        .replace(u'ì', 'i\'')
        .replace(u'à', 'a\'')
        .replace(u'ò', 'o\'')
        .replace(u'’', '\''))

    G = nx.DiGraph()

    nodes = list( i for i in range(len(st)))
    edges = list( (st.index(t[0]), st.index(t[1]), t[2]) for t in eL)

    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edges)
    G.graph['edge'] = {'arrowsize': '1', 'splines': 'curved'}
    G.graph['graph'] = {'scale': '1000000'}
    A = to_agraph(G)
    A.layout('dot')
    for i, s in enumerate(st):
        n = A.get_node(i)
        n.attr['label']= replaceChars(s)
    for triplet in edges:
        e = A.get_edge(triplet[0], triplet[1])
        e.attr['label'] = toLatexProb(triplet[2])
    A.draw('image.png')
    texcode = dot2tex.dot2tex(A.to_string(), format='tikz', crop=True)
    regEx = re.compile(r'(\\begin\{tikzpicture\})(.*?)(\\end\{tikzpicture\})', re.M|re.DOTALL)
    return ''.join(regEx.findall(texcode)[0])


def communicationMatrix(doc, cM):
    with doc.create(Subsection('Communication Matrix')):
        data = ['\setcounter{MaxMatrixCols}{20}', 'C=']
        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.extend(data)
            agn.append(Matrix(cM, mtype='b'))


def graphVisualization(doc, tikzcode):
    doc.append(NewPage())
    doc.append(NoEscape('\\begin{figure}[h]'))
    doc.append(NoEscape('\\centering'))
    doc.append(NoEscape('\\resizebox {!} {\\textheight} {'))
    doc.append(NoEscape(tikzcode))
    doc.append(NoEscape('}'))
    doc.append(NoEscape('\\end{figure}'))


def error(doc, msg, err):
    doc.append(NoEscape("\\vspace*{\\fill}"))
    doc.append(NoEscape(msg))
    doc.append(bold(err))
    doc.append(NoEscape("\\vspace*{\\fill}"))


def main(argv):

    if len(argv) == 1 :
        raise ValueError('No file name specified')

    fileName = argv[1]
    path, fileExtension = os.path.splitext(fileName)
    fileExtension = fileExtension[1:]

    doc = Document()

    print 'Processing \'%s\' to build Markov Chain...' % fileName

    try:
        if fileExtension.lower() == 'json':
            mc = mcio.jsonToMarkovChain(fileName)
        else:
            if len(argv) > 2:
                encoding = argv[2]
                mc = mcio.txtToMarkovChain(fileName, encoding=encoding)
            else:
                mc = mcio.txtToMarkovChain(fileName)

        print 'Computing Markov Chain stuff...'
        print 'States set...'

        print 'Initial distribution...'

        image_filename = os.path.join(os.path.dirname(__file__), 'image.png')

        doc.preamble.append(Package('inputenc', options = ['utf8']))
        doc.preamble.append(NoEscape('\\usepackage{tikz}'))
        doc.preamble.append(NoEscape('\\usetikzlibrary{shapes.geometric}'))
        doc.preamble.append(NoEscape('\\usetikzlibrary{arrows.meta,arrows}'))
        doc.preamble.append(NoEscape('\\usepackage{pgfplots}'))
        doc.preamble.append(NoEscape('\\pgfplotsset{compat=1.11}'))


        with doc.create(Section('Markov Chain')):

            doc.append(NoEscape('\\allowdisplaybreaks'))

            print 'Computing states set...'
            st = mc.states()
            print 'Creating latex code...'
            stateSet(doc, st)

            print 'Computing initial distribution...'
            iD = mc.initialDistribution()
            print 'Creating latex code...'
            initialDistribution(doc, iD)

            print 'Computing Transitions...'
            if mc.size <= 20:
                tM = mc.transitionMatrix()
                print 'Creating latex code...'
                transitionMatrix(doc, tM)
            else:
                tL = mc.transitionsList()
                print 'Creating latex code...'
                transitionList(doc, tL)

            print 'Computing edges...'
            eL = mc.edgeList()
            print 'Creating latex code...'
            edgeList(doc, eL)

            print 'Classes...'
            classes = mc.classes()
            print 'Creating latex code...'
            classesSection(doc, classes)

            print 'Periodicity and Recurrence...'
            recursive = mc.recursiveClasses()
            print 'Creating latex code...'
            periodAndRecur(doc, classes, recursive, mc)


            if mc.size <= 20:
                print 'Computing Communication Matrix...'
                cM = mc.communicationMatrix()
                print 'Creating latex code...'
                communicationMatrix(doc, cM)

        if len(st) < 500:
            print 'Creating graph...'
            tikzcode = createGraphTikz(st, eL)
            print 'Creating latex code...'
            graphVisualization(doc, tikzcode)

        print 'Generating pdf...'
        doc.generate_pdf(path, clean_tex=False)
    except Exception, e:
        print e
        doc = Document()
        error(doc, "It is impossible to build the pdf file:\\\\", traceback.format_exc())
        doc.generate_pdf(path, clean_tex=False)
        sys.exit(1)


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
