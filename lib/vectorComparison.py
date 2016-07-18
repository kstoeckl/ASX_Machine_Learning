"""
A Module containing a number of functions which attempt to quantify error
in different ways.
"""
import numpy as np
from sklearn.metrics import mean_squared_error
import pandas as pd

def compute_rms(Ytest,Yresult):
    """Returns the root mean square error of the two series."""
    return np.sqrt(mean_squared_error(Ytest.values,Yresult["Prediction"].values))

def compute_lad(Ytest,Yresult):
    """Computes the least absolute deviation of the two series."""
    residuals = np.absolute(Ytest.values-Yresult.values)
    return (residuals.sum(axis=0)/len(residuals))[0]

def compute_hmc(Ytest,Yresult,percen_for_alpha=0.6):
    """Computes the Huber M cost,
    percen_for_alpha is a value between (0,1) that determines what value
    of alpha will be obtained. High alpha lowers effect of outliers, low
    alpha increases the effect.
    """
    residuals = np.absolute(Ytest.values-Yresult.values)
    residuals.sort(axis=0)
    alpha = residuals[np.ceil(len(residuals)*percen_for_alpha)][0]
    temp = residuals.copy()
    for val in temp:
        if (val[0]>alpha):
            val[0] = alpha*(val-0.5*alpha)
        else:
            val[0] = 0.5*np.power(val,2)
    hmc = (temp.sum(axis=0)/len(temp))[0]
    
    return hmc

def threshold_pass(Ytest,Yresult,threshold,brokerage):
    """Computes the Precision and number of true positives of the prediction
    of the Learner.
    A true positive when: the prediction exceeds a threshold and 'real' 
    returns are enough to at least cover the brokerage fees.

    TODO: Perhaps introduce a measure that considers the extent to
    which a positive result is greater than brokerage. (As some trials
    with relatively low precision perform well, by occasionally 
    hitting a big swing.)"""
    tp=0
    fp=0
    #not used could be used for other measures eg sensitivity
    tn=0
    fn=0
    pred_mean = Yresult['Prediction'].mean()
    for index, row in Yresult.iterrows():
        if (row['Prediction']+pred_mean>threshold):
            if (Ytest.ix[index][0]>brokerage):
                tp+=1
            else:
                fp+=1
        if (row['Prediction']+pred_mean<-threshold):
            if (Ytest.ix[index][0]<-brokerage):
                tp+=1
            else:
                fp+=1
    #protection against div by zero
    precision=0
    if (fp+tp>0):
        precision = float(tp)/(fp+tp)
    return (precision,tp)

def other_thresh_pass(Ytest,Yresult,brokerage):
    """An alternate measure of precision using a time dependent Error_Measure.
    Not used at the moment.
    """
    tp=0
    fp=0
    #not used could be used for other measures
    tn=0
    fn=0
    for index, row in Yresult.iterrows():
        #can't use abs here in case prediction is opposite to reality
        if (row['Prediction']*row['Error_Measure']>brokerage):
            if (Ytest.ix[index][0]>brokerage):
                tp+=1
            else:
                fp+=1
        if (row['Prediction']*row['Error_Measure']<-brokerage):
            if (Ytest.ix[index][0]<-brokerage):
                tp+=1
            else:
                fp+=1
    #protection against div by zero
    precision= 0
    if (tp>0):
        precision = tp/(fp+tp)
    return (precision,tp)
