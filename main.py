
from MarkovChain import MarkovChain
from reader import read
import time

def main():

    #S, sigma, pi = read('prova.txt')

    S = ["A", "B", "C"]
    sigma = [0.2, 0.2, 0.6]
    pi = [[0.5, 0.5, 0], [0.1, 0, 0.9], [0, 0, 1]]

    # S = ['A', 'B', 'C', 'D', 'E']
    # sigma = [1, 0, 0, 0, 0]
    # pi = [[0.25, 0.75, 0, 0, 0], [0.5, 0.5, 0, 0, 0],
    #       [0, 0, 1, 0, 0], [0, 0, 0.3, 0.7, 0], [1, 0, 0, 0, 0]]

    # S = ['A', 'B', 'C', 'D']
    # sigma = [1, 0, 0, 0]
    # pi = [[0, 0, 0, 1], [0, 0, 0, 1],
    #       [0.5, 0.5, 0, 0], [0, 0, 1, 0]]

    mc = MarkovChain(S, sigma, pi)

    # print mc.S
    # print mc.sigma
    # print mc.pi
    # print ""

    # Test Communication Matrix computation
    # compares it to the faster version
    print mc.comMat()
    print ""


    # Test classes procedure
    print mc.classes()
    print ""

    # Test single state class procedure
    for s in S:
        print s + ': ' + str(mc.getClass(s))
    print ""

    # For each couple of states prints if they
    # communicate or they are equivalent
    for  s1 in S:
        for s2 in S:
            print s1 + '<' + s2 + ': ' + str(mc.communicate(s1, s2))
            print s1 + '=' + s2 + ': ' + str(mc.equivalent(s1, s2))
            print ""

    for state in S:
        print "period(" + state + ")= " + str(mc.period(state))
