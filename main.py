# coding=utf-8

from MarkovChain import MarkovChain
import MarkovChainIO as mcio
import time
import os, sys, traceback
import re

from latex_helper import *

# Python to latex libs
from pylatex import Document, Section, NoEscape

PDF = 'pdf'
JSON = 'json'


def commands(argv):

    # input file params
    fileName = None
    folder = None
    fileExtension = None

    # output file params
    format = PDF
    name = None
    encoding = None

    if len(argv) == 1 :
        raise ValueError('No file name specified')
    else:
        i = 1
        while argv[i].startswith('-'):
            option = argv[i][1:]

            if i+1 > len(argv)-1:
                raise ValueError('Expected parameter after \'%s\', got nothing' % argv[i])
            elif argv[i+1].startswith('-'):
                raise ValueError('Expected parameter after \'%s\', got command \'%s\'' % (argv[i], argv[i+1]))

            if option == 'f':
                format = argv[i+1].lower()
                if format not in (PDF, JSON):
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



def buildJSON(mc):
    raise ValueError('Not implemented yet')


def main(argv):

    path, fileName, folder, fileExtension, format, name, encoding = commands(argv)

    # print 'Path: ' + path
    # print 'Filename: ' + fileName
    # print 'fileExtension: ' + fileExtension
    # print 'folder: ' + folder
    # print 'format: ' + format
    # print 'name: ' + name
    # print 'encoding: ' + encoding
    # print 'generated: ' + folder + '/' + name

    print 'Processing \'%s\' to build Markov Chain...' % fileName

    try:
        if fileExtension == 'json':
            mc = mcio.jsonToMarkovChain(path, encoding=encoding)
        else:
            mc = mcio.txtToMarkovChain(path, encoding=encoding)

        if format == PDF:
            buildPDF(mc, folder + '/' + name)
        else:
            buildJSON(mc)

    except Exception, e:
        print e

        if format == PDF:
            doc = Document()
            error(doc, "It is impossible to build the pdf file:\\\\", traceback.format_exc())
            doc.generate_pdf(folder + '/' + name, clean_tex=False)
        else:
            pass

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
