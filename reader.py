

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

    states = []
    prec = None
    transitions = {}
    initial = {}

    for i, line in enumerate(file):
        for j in range(len(line)):

            s = _state(i, j, line)

            if i == j == 0:
                initial[s] = 1

            if s not in transitions:
                transitions[s] = {}

            if s not in states:
                states.append(s)

            if prec :
                if s not in transitions[prec] :
                    transitions[prec][s] = 1
                else:
                    transitions[prec][s] += 1

            prec = s

    states = sorted(states)

    pi = []

    for s1 in states:
        row = []
        edges = 0
        cases = 0

        for s2 in transitions[s1]:
            edges += 1
            cases += transitions[s1][s2]

        tot = 0
        for s2 in states:
            if s2 in transitions[s1]:
                if edges > 1:
                    p = transitions[s1][s2]/float(cases)
                    tot += p
                    edges -= 1
                else:
                    p = 1.0-tot
            else:
                p = 0
            row.append(p)
        pi.append(row)

    sigma = []

    for s in states:
        if s in initial:
            sigma.append(1)
        else:
            sigma.append(0)

    return states, sigma, pi
