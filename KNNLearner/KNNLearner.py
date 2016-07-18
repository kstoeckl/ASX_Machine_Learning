"""
A Kth Nearest Neighbour Machine Learner, with standard train and query methods
"""

import pandas as pd
import numpy as np
from sklearn.neighbors import KDTree

class KNNLearner:
    def __init__(self,k=10):
        self.K=k    

    def train(self,x,y):
        """Simply stores paired x(vector or scalar) and y(scalar) values."""
        self.known_values = x.join(y, how='inner')
        self.known_values = self.known_values.reset_index(drop=True)
        #An alternate structure, using a multi-index
        #self.known_values = x.join(y, how='inner').set_index(list(x.columns.values),drop=True)

    def query(self,x):
        """Finds the K nearest neighbours and return the mean and std of their
        paired y values. Use of apply results in faster computation."""
        y_result = pd.DataFrame(index = x.index)  
        y_result.index.name = 'x'
        y_result = x.apply(self.predict_for_point,axis=1)
        y_result.columns=['y_mean','y_std']
        y_result.index.name = 'x'
        return y_result

    def predict_for_point(self,row):
        """Finds the mean and the std of the y values of the nearest 
        neighbours of a point."""
        index = row.name
        #retrieves all x coordinates
        array = self.known_values.ix[:,0:-1].as_matrix()
        x_val = row.as_matrix()
        #Find the 2-Norm for the xs
        array = np.linalg.norm(array-x_val,axis=1)
        array = np.column_stack((array,self.known_values.ix[:,-1].as_matrix()))
        #array[:,0].argsort() returns the indicies that sort the first column
        array =array[array[:,0].argsort()[0:self.K]]

        #Not weighting closer neighbours more.
        return [np.mean(array[:,1]),np.std(array[:,1])]

    def query_KDTree(self,x):
        """A version of query that makes use of a KDTree data structure.
        At 2-Dim x values and 10 years of data traded daily (< 2720 points of
        data) the query function above still outperformed this method, likely
        due to the set up cost of the tree. If querying multiple times
        or more data/dims might be worth due to O(log(n)).
        Perhaps a KD bag tree learner could be directly implemented, ie where
        the sampling for the bags could be done on a pre existing tree.
        Not sure if this is possible, or if performance gain would be worth the
        time, not a priority.
        """
        #1 indicates column
        tree = KDTree(self.known_values.reset_index().drop('y',1).as_matrix(),
            leaf_size=40)
        dist,neighbours = tree.query(x,self.K)

        y_result = pd.DataFrame(index = x.index)
        y_result['y_mean'] = np.apply_along_axis(self.y_mean,1,neighbours)
        y_result['y_std'] = np.apply_along_axis(self.y_std,1,neighbours)
        return y_result

    def y_mean(self, row):
        """Returns the mean of the y value of the neighbours in the row."""
        return self.known_values.iloc[row].mean().values[0]

    def y_std(self,row):
        """Returns the std of the y value of the neighbours in the row."""
        return self.known_values.iloc[row].std().values[0]

    def query_old(self,x):
        """Scrapped version of query, signficantly slower than current."""
        y_result = pd.DataFrame(index = x.index,columns=['y_mean','y_std'])  
        y_result.index.name = 'x'
        for index_outer,row_outer in x.iterrows():
            y_list = np.zeros([len(self.known_values),2])
            for index,row in self.known_values.iterrows():
                #self written function in another module.
                dist = op.e_dist(row_outer,row)
                y_list[index] = [dist,row['y']]
                
            y_list = y_list[y_list[:,0].argsort()]
            y_est = np.mean(y_list[0:self.K][:,1], axis = 0)
            y_std = np.std(y_list[0:self.K][:,1], axis = 0)
            
            y_result.ix[index_outer]['y_mean']=y_est
            y_result.ix[index_outer]['y_std']=y_std
        
        return y_result