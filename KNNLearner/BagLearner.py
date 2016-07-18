"""
An Aggregate Learner Class. Takes different samples of the training data to 
to train each individual learner and queries the learners in mass. 
"""
import pandas as pd
import numpy as np

class BagLearner:
    def __init__(self,alg,bags,kwargs):
        self.bags = bags        
        self.learners = []
        for i in range(0,self.bags):
            self.learners.append(alg(**kwargs))

    def train(self,x,y):
        """Performs sampling with replacement on the training data, to 
        train each of the #bags inner learners."""
        #faster to join sample then resplit, then sample and match
        temp = x.join(y,how='inner')
        for i in range(0,self.bags):
            temp_subset = temp.sample(n=int(len(temp.index)/2),replace=True)
            x_subset = pd.DataFrame(temp_subset.ix[:,:len(x.columns)])  
            y_subset = pd.DataFrame(temp_subset.ix[:,-1])
            self.learners[i].train(x_subset,y_subset) 

    def query(self,x):
        """Queries each of the inner learners and aggregates their results.
        Aggregate std of their results is also returned, gives an indication
        of consensus amongst learners, potentially valuable as an error
        measure."""
        Yresult = pd.DataFrame(index = x.index)
        Yresult.index.name = 'x'

        print("Querying BagLearner")
        for i in range(0,self.bags):
            Yresult = Yresult.join(self.learners[i].query(x),how='inner',
                rsuffix='Learner'+str(i))

        mean_cols=[]
        std_cols=[]
        for col in Yresult.columns:
            if 'y_mean' in col:
                mean_cols.append(col)
            if 'y_std' in col:
                std_cols.append(col)

        Yresult['CombinationAlg'] = Yresult[mean_cols].mean(axis=1)
        Yresult['STD'] = Yresult[std_cols].mean(axis=1)
        #in effect drops all other columns
        Yresult = pd.DataFrame(Yresult[['CombinationAlg','STD']],index=Yresult.index)
        
        return Yresult

