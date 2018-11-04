
import numpy as np
import sys

INITIAL = 'initial'
TRANSITIONS = 'transitions'

def gcd(arg1, arg2=None):

    if arg2:
        a, b = arg1, arg2
        while b:
            a, b = b, a % b
        return a
    else:
        g = arg1[0]
        for num in arg1[1:]:
            g = gcd(g, num)
        return g


class MarkovChainError(Exception):

    LEN_SIGMA = 'States list and initial ditribution have different dimensions'
    SUM_SIGMA = 'Initial distribution sum should be 1, it is {} instead'
    LEN_PI = 'States list and transition matrix have different dimensions'
    LEN_ROW_PI = 'States list and row number {} of transition matrix have different dimensions'
    SUM_ROW_PI = 'Pi row sum should be 1, row {} sum is {} instead'
    DUP_STATE = 'Identifier {} names two different states'
    NO_STATE = 'Identifier {} does not name any state'
    NEG_SIGMA = 'Initial distribution elements should be non-negative'
    NEG_ROW_PI = 'Pi elements should be non-negative'
    DUP_TRANS = 'Transition to {} already defined'

    def __init__(self, message):
        super(MarkovChainError, self).__init__(message)

class MarkovChain:

    def _structures(self):

        mc = self

        class Sigma:

            # sigma is a dictionary with the structure:
            # {
            #   index_1 : probability_1,
            #   index_2 : probability_2,
            #   ...
            #}
            def __init__(self, sigma):
                self._sigma = tuple( (sigma[i], i) for i in sigma )

            def toArray(self):
                sigma = np.zeros(mc.size)
                for pair in self._sigma:
                    sigma[pair[1]] = pair[0]
                return sigma


        class MarkovChainState:

            def __init__(self, name, transitions):
                self._name = name
                self._transitions  = transitions

            @property
            def name(self):
                return self._name

            @property
            def adj(self):
                return (pair[0] for pair in self._transitions)

            @property
            def transitions(self):
                return self._transitions


        return MarkovChainState, Sigma


    # desc is a dictionary with the structure:
    # {
    #   name_1 : {
    #               ['initial' : sigma_1,]
    #               'transitions': {
    #                   name_i_1 : t_i_1,
    #                   name_i_2 : t_i_2,
    #                   ...
    #   }
    #   name_2 : {
    #               ...
    #   }
    #   ...
    #}
    # so the field 'initial' is optional
    def _initFromDescription(self, desc):

        State, Sigma = self._structures()

        sigma = {}
        map = {}
        tot_sigma = 0

        i = 0

        for s in desc:

            if INITIAL in desc[s] and desc[s][INITIAL]:
                if desc[s][INITIAL] < 0:
                    raise MarkovChainError(MarkovChainError.NEG_SIGMA)
                sigma[i] = desc[s][INITIAL]
                tot_sigma += sigma[i]

            if TRANSITIONS in desc[s]:
                if desc[s][TRANSITIONS]:
                    tot = 0
                    for t in desc[s][TRANSITIONS]:
                        if t not in desc:
                            raise MarkovChainError(MarkovChainError.NO_STATE.format(t))
                        if desc[s][TRANSITIONS][t] < 0:
                            raise MarkovChainError(MarkovChainError.NEG_ROW_PI)
                        tot += desc[s][TRANSITIONS][t]

                    if tot != 1.0:
                        raise MarkovChainError(MarkovChainError.SUM_ROW_PI.format(s, tot))
            else:
                raise MarkovChainError(MarkovChainError.SUM_ROW_PI.format(s, 0))

            map[s] = i
            i += 1

        if tot_sigma != 1.0:
            raise MarkovChainError(MarkovChainError.SUM_SIGMA.format(tot_sigma))

        mc = []

        for s in desc:
            transitions = []
            for t in desc[s][TRANSITIONS]:
                transitions.append((map[t], desc[s][TRANSITIONS][t]))
            transitions = tuple(sorted(transitions, lambda t1, t2: t1[0] < t2[0]))
            mc.append(State(s, transitions))

        return tuple(mc), Sigma(sigma)


    def _initFromArray(self, stateSet, initialDist, transMat):

        State, Sigma = self._structures()

        if len(stateSet) != len(initialDist) :
            raise MarkovChainError(MarkovChainError.LEN_SIGMA)

        if  any(p<0 for p in initialDist):
            raise MarkovChainError(MarkovChainError.NEG_SIGMA)

        if sum(initialDist) != 1.0 :
            raise MarkovChainError(MarkovChainError.SUM_SIGMA.format(sum(initialDist)))

        if len(stateSet) != len(transMat) :
            raise MarkovChainError(MarkovChainError.LEN_PI)

        for i, row in enumerate(transMat):

            if len(row) != len(stateSet) :
                raise MarkovChainError(MarkovChainError.LEN_ROW_PI.format(i))

            if  any(p<0 for p in row):
                raise MarkovChainError(MarkovChainError.NEG_ROW_PI)

            if sum(row) != 1.0 :
                raise MarkovChainError(MarkovChainError.SUM_ROW_PI.format(i, sum(row)))

        for state in stateSet:
            if stateSet.count(state) > 1 :
                raise MarkovChainError(MarkovChainError.DUP_STATE.format(state))

        mc = []
        for i, s in enumerate(stateSet):
            transitions = []
            for j in range(len(stateSet)):
                if transMat[i][j]>0:
                    transitions.append((j, transMat[i][j]))
            mc.append(State(s, tuple(transitions)))

        sigma = {}

        for i, p in enumerate(initialDist):
            sigma[i] = p

        print sigma

        return tuple(mc), Sigma(sigma)


    def __init__(self, arg0, arg1=None, arg2=None):

        if not arg1 and not arg2:
            self._mc, self._sigma = self._initFromDescription(arg0)
        else:
            self._mc, self._sigma = self._initFromArray(arg0, arg1, arg2)

        self._C = None

    @property
    def size(self):
        return len(self._mc)


    def states(self):
        return tuple(s.name for s in self._mc)


    def initialDistribution(self):
        return self._sigma.toArray()

    def transitionMatrix(self):
        pi = np.zeros((self.size, self.size))
        for i, s in enumerate(self._mc):
            for pair in s.transitions:
                j = pair[0]
                p = pair[1]
                pi[i, j] = p
        return pi

    def edgeList(self):
        edges = []
        for s1 in self._mc:
            for pair in s1.transitions:
                s2 = self._mc[pair[0]]
                weight = pair[1]
                edges.append((s1.name, s2.name, weight))
        return tuple(edges)

    def _comMat(self, v, visited):

        visited[v] = True

        for u in self._mc[v].adj:
            if not visited[u]:
                self._comMat(u, visited)


    def comMat(self):

        if not self._C:

            C = []

            self._C = np.zeros((self.size, self.size), dtype=bool)

            for v in range(self.size):
                self._comMat(v, self._C[v])

            self._C.flags.writeable = False

        return self._C


    def _order(self, v, visited, stack):

        visited[v] = True

        for u in self._mc[v].adj:
            if not visited[u]:
                self._order(u, visited, stack)

        stack.append(v)

    def _transposedAdj(self, v):
        adj = []
        for i, s in enumerate(self._mc):
            for j in s.adj:
                if j == v:
                    adj.append(i)
        return adj

    def _cc(self, v, visited, cc):

        visited[v] = True

        for u in self._transposedAdj(v):
            if not visited[u]:
                cc.append(u)
                self._cc(u, visited, cc)


    def _classes(self):

        visited = np.zeros(self.size, dtype=bool)
        stack = []

        for v in range(self.size):
            if not visited[v]:
                self._order(v, visited, stack)

        visited = np.zeros(self.size, dtype=bool)
        classes = {}

        while stack:
            v = stack.pop()
            if not visited[v]:
                classes[v] = [v]
                self._cc(v, visited, classes[v])

        return classes


    def _getClass(self, v):

        classes = self._classes()

        for u in classes:
            if v in classes[u]:
                return classes[u]


    def getClass(self, s):
        return tuple( self._mc[u].name for u in self._getClass(self.index(s)))


    def classes(self):

        classes = self._classes()
        classes_named = {}

        for v in classes:
            classes_named[self._mc[v].name] = tuple(self._mc[u].name for u in classes[v])

        return classes_named


    def _communicate(self, v, visited, dest):

        visited[v] = True

        if v == dest:
            return True

        for u in self._mc[v].adj:
            if not visited[u]:
                if self._communicate(u, visited, dest):
                    return True

        return False


    def index(self, name):
        for i, s in enumerate(self._mc):
            if s.name == name:
                return i


    def communicate(self, s1, s2):

        source = self.index(s1)
        dest   = self.index(s2)

        visited = np.zeros(self.size, dtype=bool)

        return self._communicate(source, visited, dest)


    def equivalent(self, s1, s2):
        return self.communicate(s1, s2) and self.communicate(s2, s1)


    def _period(self, s, v, visited, distance, circuits):

        visited[v] = True

        for u in self._mc[v].adj:

                if u == s:
                    d = distance[v]+1
                    if d not in circuits:
                        circuits.append(d)

                if not visited[u]:
                    distance[u] = distance[v]+1
                    self._period(s, u, visited, distance, circuits)


    def period(self, s):

        C = self._getClass(self.index(s))
        circuits = []

        for source in C:
            visited = np.zeros(self.size, dtype=bool)
            distance = np.zeros(self.size)

            self._period(source, source, visited, distance, circuits)

        if circuits:
            return gcd(circuits)
        else:
            return None

    @staticmethod
    def builder():

        class MarkovChainBuilder:

            def __init__(self):
                self._desc = {}

            def addState(self, s, initial=None, transitions=None):

                if s in self._desc:
                    raise MarkovChainError(MarkovChainError.DUP_STATE.format(s))

                self._desc[s] = {}
                self._desc[s][TRANSITIONS] = {}

            def setInitial(self, s, initial):

                if s not in self._desc:
                    raise MarkovChainError(MarkovChainError.NO_STATE.format(s))

                if initial < 0:
                    raise MarkovChainError(MarkovChainError.NEG_SIGMA)

                self._desc[s][INITIAL] = initial

            def setTransitions(self, s, transitions):

                if s not in self._desc:
                    raise MarkovChainError(MarkovChainError.NO_STATE.format(s))

                for s1 in transitions:
                    if s1 not in self._desc:
                        raise MarkovChainError(MarkovChainError.NO_STATE.format(s))
                    if transitions[s1] < 0:
                        raise MarkovChainError(MarkovChainError.NEG_ROW_PI)

                self._desc[s][TRANSITIONS] = transitions

            def addTransition(self, s1, s2, p):

                if s1 not in self._desc:
                    raise MarkovChainError(MarkovChainError.NO_STATE.format(s1))
                if s2 not in self._desc:
                    raise MarkovChainError(MarkovChainError.NO_STATE.format(s2))

                if s2 in self._desc[s1][TRANSITIONS]:
                    raise MarkovChainError(MarkovChainError.DUP_TRANS.format(s2))
                self._desc[s1][TRANSITIONS][s2] = p

            def build(self):
                return MarkovChain(self._desc)

        return MarkovChainBuilder()


    def path(self):

        class Path:

            def __init__(self):
                self._s = self._first()

            def next(self):
                pass
