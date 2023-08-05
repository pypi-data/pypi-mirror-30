import numpy as np

class Gene(object):

    def __init__(self,id,n):
        self.id = id
        self.gene = np.zeros(n)

    def __repr__(self):
        return 'Gene ' + str(id) + ': ' + str(self.gene)

