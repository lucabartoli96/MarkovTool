

from MarkovChain import MarkovChain

K = 2

def _state(i, j, line):
    if j < K-1:
        if i == 0:
            s = line[:j+1]
        else:
            s = '#' + line[:j+1]
    else:
        s = line[j-K+1:j+1]

    if s[-1] == '\n':
        s = s[:-1] + '#'

    return s


def read(path):
    file = open(path, 'r')
    builder = MarkovChain.builder()

    states = []
    prec = None

    transitions = {}

    for i, line in enumerate(file):
        for j in range(len(line)):

            s = _state(i, j, line)

            if not s in transitions:
                transitions[s] = {}
                builder.addState(s)

            if i == j == 0:
                builder.setInitial(s, 1)

            if prec :
                if s not in transitions[prec] :
                    transitions[prec][s] = 1
                else:
                    transitions[prec][s] += 1

            prec = s

    for s1 in transitions:

        edges = 0
        cases = 0

        for s2 in transitions[s1]:
            edges += 1
            cases += transitions[s1][s2]

        tot = 0
        for s2 in transitions[s1]:
            if edges > 1:
                p = transitions[s1][s2]/float(cases)
                tot += p
                edges -= 1
            else:
                p = 1.0-tot
            builder.addTransition(s1, s2, p)

    return builder.build()
