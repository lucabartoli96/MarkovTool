
import numpy as np
import sys

INITIAL = INITIAL
TRANSITIONS = TRANSISIONS

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

            # sigma is a dictionary of the type:
            # {
            #   index_1 : probability_1,
            #   index_2 : probability_2,
            #   ...
            #}
            def __init__(self, sigma):
                self._sigma = tuple( (p, i) for i, p in sigma )

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
                tot_sigma += sigma[s]

            if TRANSISIONS in desc[s]:
                if desc[S][TRANSISIONS]:
                    tot = 0
                    for t in desc[s][TRANSISIONS]:
                        if t not in desc:
                            raise MarkovChainError(MarkovChainError.NO_STATE.format(t))
                        if desc[s][TRANSISIONS][t] < 0:
                            raise MarkovChainError(MarkovChainError.NEG_ROW_PI)
                        tot += desc[s][TRANSISIONS][t]

                    if tot != 1.0:
                        raise MarkovChainError(MarkovChainError.SUM_ROW_PI.format(s, tot))
            else:
                raise MarkovChainError(MarkovChainError.SUM_ROW_PI.format(s, 0))

            map[s] = i
            i++

        if tot_sigma != 1.0:
            raise MarkovChainError(MarkovChainError.SUM_SIGMA.format(tot_sigma))

        mc = []

        for s in desc:
            transitions = []
            for t in desc[s][TRANSISIONS]:
                transitions.append((map[t], desc[s][TRANSISIONS][t]))
            transitions = tuple(sorted(transitions, lambda t: t[0]))
            self._mc.append(State(s, transitions))

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
            for j in transMat[i]:
                transitions.append((j, transMat[i][j]))
            mc.append(State(s, tuple(transitions)))

        for i, p in enumerate(initialDist):
            sigma[i] = p

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

    @property
    def S(self):
        return tuple(s.name for s in self._mc)

    @property
    def sigma(self):
        return self._sigma.toArray()

    @property
    def pi(self):
        pi = np.zeros((self.size, self.size))
        for i, s in enumerate(self._mc):
            for pair in s.transition:
                j = pair[0]
                p = pair[1]
                pi[i, j] = p
        return pi

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


    def _order(self, G, n, v, visited, stack):

        visited[v] = True

        for u in self._mc[v].adj:
            if not visited[u]:
                self._order(n, u, visited, stack)

        stack.append(v)


    def _cc(self, Gt, n, v, visited, cc):

        visited[v] = True

        for u in range(n):
            if Gt[v, u]>0 and not visited[u]:
                cc.append(u)
                self._cc(Gt, n, u, visited, cc)


    def classes(self):

        visited = np.zeros(self.size, dtype=bool)
        stack = []

        for v in range(self.size):
            if not visited[v]:
                self._order(self.pi, self.size, v, visited, stack)

        visited = np.zeros(self.size, dtype=bool)
        classes = {}
        Gt = np.transpose(self.pi)

        while stack:
            v = stack.pop()
            if not visited[v]:
                classes[v] = []
                self._cc(Gt, self.size, v, visited, classes[v])

        classes_named = {}

        for v in classes:
            cc = [self._mc[v].name]
            for u in classes[v]:
                cc.append(self._mc[u].name)
            classes_named[self._mc[v].name] = tuple(sorted(cc))

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


    def communicate(self, s1, s2):

        source = self.S.index(s1)
        dest   = self.S.index(s2)

        visited = np.zeros(self.size, dtype=bool)

        return self._communicate(source, visited, dest)


    def equivalent(self, s1, s2):
        return self.communicate(s1, s2) and self.communicate(s2, s1)


    def _period(self, s, v, visited, distance, circuits):

        visited[v] = True

        for u in self._mc[v].adj:
            if self.pi[v, u]>0:
                if u == s:
                    circuits.append(distance[v]+1)

                if not visited[u]:
                    distance[u] = distance[v]+1
                    self._period(s, u, visited, distance, circuits)


    def period(self, s):
        source = self.S.index(s)

        visited = np.zeros(self.size, dtype=bool)
        distance = np.zeros(self.size)
        circuits = []

        self._period(source, source, visited, distance, circuits)

        if circuits:
            return gcd(circuits)
        else:
            return None

    def builder(self):

        class MarkovChainBuilder:

            def __init__():
                self._desc = {}

            def addState(self, s, initial=0, transitions={}):

                if s in self._desc:
                    raise MarkovChainError(MarkovChainError.DUP_STATE.format(s))

                self._desc[s] = {
                    INITIAL    : intial,
                    TRANSISIONS: transitions
                }

            def setInitial(self, s, intial):

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

                self._desc[s][TRANSISIONS] = transitions

            def addTransition(self, s1, s2, p):

                if s1 not in self._desc:
                    raise MarkovChainError(MarkovChainError.NO_STATE.format(s1))
                if s2 not in self._desc:
                    raise MarkovChainError(MarkovChainError.NO_STATE.format(s2))

                if s2 in self._desc[s1][TRANSISIONS]:
                    raise MarkovChainError(MarkovChainError.DUP_TRANS.format(s2))
                self._desc[s1][TRANSISIONS][s2] = p

            def build(self):
                return MarkovChain(self._desc)

        return MarkovChainBuilder()


    def path(self):

        class Path:

            def __init__(self):
                self._s = self._first()

            def next():
                pass
