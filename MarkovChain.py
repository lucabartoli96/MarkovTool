
import numpy as np
import sys

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
    SUM_ROW_PI = 'Pi row sum should be 1, row number {} sum is {} instead'
    DUP_STATE = 'Identifier {} names two different states'
    NEG_SIGMA = 'Initial distribution elements should be non-negative'
    NEG_ROW_PI = 'Pi elements should be non-negative'

    def __init__(self, message):
        super(MarkovChainError, self).__init__(message)

class MarkovChain:

    def __init__(self, stateSet, initialDist, transMat):

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

        self._S = tuple(stateSet)

        self._sigma = np.array(initialDist)
        self._sigma.flags.writeable = False

        self._pi = np.matrix( transMat )
        self._pi.flags.writeable = False

        self._C = None


    @property
    def size(self):
        return len(self._S)


    @property
    def S(self):
        return self._S


    @property
    def sigma(self):
        return self._sigma


    @property
    def pi(self):
        return self._pi

    # def comMat(self):
    #
    #     if not self._C:
    #
    #         A = np.vectorize(lambda elem: elem != 0)(self.pi)
    #         C = np.stack(np.stack(i == j for j in range(self.size)) for i in range(self.size))
    #
    #         for i in range(self.size):
    #             C += np.matmul(C, A)
    #
    #         C.flags.writeable = False
    #         self._C = C
    #
    #     return self._C

    def _comMat(self, v, visited):

        visited[v] = True

        for u in range(self.size):
            if self.pi[v, u]>0 and not visited[u]:
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

        for u in range(n):
            if G[v, u]>0 and not visited[u]:
                self._order(G, n, u, visited, stack)

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
            cc = [self.S[v]]
            for u in classes[v]:
                cc.append(self.S[u])
            classes_named[self.S[v]] = tuple(sorted(cc))

        return classes_named


    def _communicate(self, v, visited, dest):

        visited[v] = True

        if v == dest:
            return True

        for u in range(self.size):
            if self.pi[v, u]>0 and not visited[u]:
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

        for u in range(self.size):
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

    def path():

        class Path:            

            def __init__(self):
                self._s = self._first()

            def next():
                pass
