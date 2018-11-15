# coding=utf-8

import time, os, sys, traceback, re

import MarkovChainIO as mcio

from latex_helper import *
from pylatex import Document, Section, NoEscape

PDF, JSON, DUMP = 'pdf', 'json', 'dump'


def commands(argv):

    # input file params
    fileName = None
    folder = None
    fileExtension = None

    # output file params
    format = PDF
    name = None
    encoding = None

    if len(argv) == 2 :
        raise ValueError('No file name specified')
    else:
        i = 2
        while argv[i].startswith('-'):
            option = argv[i][1:]

            if i+1 > len(argv)-1:
                raise ValueError('Expected parameter after \'%s\', got nothing' % argv[i])
            elif argv[i+1].startswith('-'):
                raise ValueError('Expected parameter after \'%s\', got command \'%s\'' % (argv[i], argv[i+1]))

            if option == 'f':
                format = argv[i+1].lower()
                if format not in (PDF, JSON, DUMP):
                    raise ValueError('Unsupported format %s' % format)
            elif option == 'n':
                name = argv[i+1]
            elif option == 'enc':
                encoding = argv[i+1]
            else:
                raise ValueError('Unknwn command %s' % argv[i])

            i += 2

        path = argv[i]
        folder, fileName = os.path.split(path)
        fileName = fileName[:fileName.rfind('.')]
        fileExtension = os.path.splitext(path)[1][1:]

        if not name:
            name = fileName

        return path, fileName, folder, fileExtension, format, name, encoding


def dump(mc):

    print 'State set: '
    st = mc.states()
    print st

    print 'Initial distribution: '
    iD = mc.initialDistribution()
    print iD

    print 'Initial distribution array: '
    iDA = mc.initialDistributionArray()
    print iDA

    print 'Transitions list: '
    tL = mc.transitionsList()
    print tL

    print 'Transition matrix: '
    tM = mc.transitionMatrix()
    print tM

    print 'Edges list: '
    eL = mc.edgeList()
    print eL

    print 'Communication Matrix: '
    cM = mc.communicationMatrix()
    print cM

    print 'Classes: '
    classes = mc.classes()
    print classes

    print 'Periodicity: '
    for state in classes:
        print "period(" + state + ")= " + str(mc.period(state))

    print 'Recursive classes: '
    recursive = mc.recursiveClasses()
    print recursive


def errorDUMP(outputPath):
    print traceback.format_exc()


def buildPDF(mc, outputPath):
    doc = Document()

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
            graphVisualization(doc, mc.size, tikzcode)

    print 'Generating pdf...'
    doc.generate_pdf(outputPath, clean_tex=False)


def errorPDF(outputPath):
    doc = Document()
    error(doc, "It is impossible to build the pdf file:\\\\", traceback.format_exc())
    doc.generate_pdf(outputPath, clean_tex=False)


def buildJSON(mc):
    raise ValueError('Not implemented yet')

def errorJSON(outputPath):
    raise ValueError('Not implemented yet')



def run(argv):

    path, fileName, folder, fileExtension, format, name, encoding = commands(argv)

    print 'Processing \'%s\' to build Markov Chain...' % fileName

    try:
        if fileExtension == 'json':
            mc = mcio.jsonToMarkovChain(path, encoding=encoding)
        else:
            mc = mcio.txtToMarkovChain(path, encoding=encoding)

        if format == PDF:
            buildPDF(mc, folder + '/' + name)
        elif format == JSON:
            buildJSON(mc)
        else:
            dump(mc)

    except Exception, e:

        if format == PDF:
            errorPDF(folder + '/' + name);
        elif format == JSON:
            errorJSON(folder + '/' + name)
        else:
            errorDUMP()

        sys.exit(1)
