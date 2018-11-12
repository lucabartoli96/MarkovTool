# coding=utf-8

from MarkovChain import MarkovChain
import MarkovChainIO as mcio
import time
import os, sys, traceback
import re

from latex_helper import *

# Python to latex libs
from pylatex import Document, Section, NoEscape


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

        preamble(doc)

        with doc.create(Section('Markov Chain')):

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
