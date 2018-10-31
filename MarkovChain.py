
import numpy as np

ERR_MSG = {
    'length_sigma'  : 'states set and Initial distribution have different dimensions',
    'sum_sigma'     : 'Initial distribution sum should be 1',
    'length_pi'     : 'states set and transition matrix have different dimensions',
    'sum_pi'        : 'Matrix row sum should be 1',
    'count_state'   : 'States must have different names',
    'wrong_name'    : 'Given string does not name any state'

}


class MarkovChain:


    # TODO: Si potrebbero migliorare le eccezioni, dicendo dove sta
    #       l'errore, e si potrebbe permettere di non passare sigma
    #       o di passarlo in parte e dare 0 alle altre distribuzioni
    #       iniziali
    def __init__(self, stateSet, initialDist, transMat):

        if len(stateSet) != len(initialDist) :
            raise ValueError(ERR_MSG['length_sigma'])

        if sum(initialDist) != 1 :
            raise ValueError(ERR_MSG['sum_sigma'])

        if len(stateSet) != len(transMat) :
            raise ValueError(ERR_MSG['length_pi'])

        for row in transMat:

            if len(row) != len(stateSet) :
                raise ValueError(ERR_MSG['length_pi'])

            if sum(row) != 1 :
                raise ValueError(ERR_MSG['sum_pi'])

        for state in stateSet:
            if stateSet.count(state) > 1 :
                raise ValueError(ERR_MSG['count_state'])

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


    def comMat(self):

        if not self._C:

            A = np.vectorize(lambda elem: elem != 0)(self.pi)
            C = np.stack(np.stack(i == j for j in range(self.size)) for i in range(self.size))

            for i in range(self.size):
                C += np.matmul(C, A)

            C.flags.writeable = False
            self._C = C

        return self._C

    def _comMat(self, v, visited):

        visited[v] = True

        for u in range(self.size):
            if self.pi[v, u]>0 and not visited[u]:
                self._comMat(u, visited)


    def comMatFast(self):

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

        print circuits
