
from MarkovChain import MarkovChain
import time

def main():

    # S = ["A", "B", "C"]
    # sigma = [0.2, 0.2, 0.6]
    # pi = [[0.5, 0.5, 0], [0.1, 0, 0.9], [0, 0, 1]]

    S = ['A', 'B', 'C', 'D', 'E']
    sigma = [1, 0, 0, 0, 0]
    pi = [[0.25, 0.75, 0, 0, 0], [0.5, 0.5, 0, 0, 0],
          [0, 0, 1, 0, 0], [0, 0, 0.3, 0.7, 0], [1, 0, 0, 0, 0]]

    mc = MarkovChain(S, sigma, pi)

    print mc.S
    print mc.sigma
    print mc.pi
    print ""

    # Test Communication Matrix computation
    # compares it to the faster version
    time_start = time.clock()
    C1 = mc.comMat();
    time_elapsed = (time.clock() - time_start)
    print C1
    print ""
    print time_elapsed
    print ""

    time_start = time.clock()
    C2 = mc.comMatFast();
    time_elapsed = (time.clock() - time_start)
    print C2
    print ""
    print time_elapsed
    print ""

    equal = True
    n = len(C1)
    for i in range(n):
        for j in range(n):
            equal = equal and C1[i, j] == C2[i, j]

    print equal
    print ""



    # Test classes procedure
    print mc.classes()
    print ""


    # For each couple of states prints if they
    # communicate or they are equivalent
    for  s1 in S:
        for s2 in S:
            print s1 + '<' + s2 + ': ' + str(mc.communicate(s1, s2))
            print s1 + '=' + s2 + ': ' + str(mc.equivalent(s1, s2))
            print ""

    mc.period('A')
