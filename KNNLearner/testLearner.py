"""
A module for testing the Learner with various parameters on different symbols.

When run allows you to test a single symbol with the parameters set
"""
import pandas as pd
import numpy as np
import KNNLearner
import BagLearner
import dataConversion as dc
import portfolio
import vectorComparison
import order

#Parameters
BROKERAGE=0.002
PURCHASESIZE=10000
CASH=30000
MODIFIER=0.7
K=15
BAGS=30
FORECAST=3
SYMBOL = "ANZ"

def predict_for_test(symbol,Xtrain,Ytrain,Xtest,Ytest,alg,kwargs):
    """Trains the machine learning algorithm on the Training data,
    Then queries the algorithm with the test data."""
    learner = alg(**kwargs)

    learner.train(Xtrain, Ytrain) # training step
    Yresult = learner.query(Xtest) # query  
    Yresult.index = Ytest.index
    Yresult.columns = ['Prediction','Error_Measure']
    return Yresult

def test_symbol(symbol,kwargs,brokerage,purchase_size,cash,
    t_data=1/2,v_data=1,forecast=7,display=False,
    create_orders=False,store_path ='../CSVData/', order_path=order.ORDER_PATH):
    """
    Extracts and formats the testing and training data. Retrieves
    the prediction of the learner for the test data. Runs tests 
    and simulates trading based off the prediction.

    t_data: the fraction of data to be used for training
    v_data: t_data<v_data<=1, if v_data==1 then no validation to be performed
    forecast: the forecast period in timesteps(days)
    """
    assert(v_data>t_data and v_data<=1)
    #Data retrieval and Training
    df = dc.get_company_data(symbol,store_path=store_path)
    length = len(df.index)

    df1 = df.ix[0:(int(length*t_data-forecast))].copy()
    df2 = df.ix[forecast:int(length*t_data)].copy() 
    (Xtrain,Ytrain) = prep_for_learner(df1,df2,period=2*forecast,
        forecast=forecast)
    
    df1 = df.ix[int(length*t_data):int(length*v_data)-forecast].copy()
    df2 = df.ix[int(length*t_data+forecast):int(length*v_data)].copy()
    (Xtest,Ytest) = prep_for_learner(df1,df2,period=2*forecast,
        forecast=forecast)

    Yresult = predict_for_test(symbol,Xtrain,Ytrain,Xtest,Ytest,**kwargs)
    
    #Correlation is returned in matrix form, so indices to retrieve value
    corr = np.corrcoef(Ytest.ix[:,0].values,Yresult.ix[:,0].values)[0][1]

    #using root mean square error as an error measure and discarding 
    #the std error measure
    error_measure = MODIFIER*vectorComparison.compute_rms(Ytest,Yresult)
    Yresult = Yresult.drop('Error_Measure',1) 

    threshold = brokerage+error_measure

    (precision,tp) = vectorComparison.threshold_pass(Ytest,Yresult,threshold,brokerage)

    if (create_orders==True or display==True):
        order_file_name = order_path+symbol+".csv"
        order.create_orders(Yresult,error_measure,symbol,forecast,brokerage,
            purchase_size,order_file_name)
    if (display==True):
        df = Ytest.join(Yresult)
        print(symbol,' Performance Metrics')
        print(corr,error_measure,precision)

        portfolio_file_name = portfolio.PORTFOLIO_PATH+symbol+'.csv'
        p = portfolio.portfolio(portfolio_file_name,order_file_name,cash,brokerage)
        p.performanceAnalysis()
        print('ASX200 Performance Metrics')
        print(corr,error_measure,precision,tp)     

        dc.plot_data(df,"LearnerPerformance","Date","DailyReturns",error_measure=threshold)

    return (corr,error_measure,precision,tp)

def prep_for_learner(x,y,period=20,forecast=5):
    """Formats dataframes x and y for input into machine learner.
    Each x coor will consist of the price of the stock at the timestep minus
    the moving average price of the stock and the moving std of the stock.
    y will a single scalar value, the return of the stock over the forecast."""
    y = dc.convert_to_returns(y,forecast)

    x["Rolling_Std"] = x.ix[:,0].rolling(center=False,window=period).std()
    x.ix[:,0] = x.ix[:,0] - x.ix[:,0].rolling(center=False,window=period).mean()
    
    #adjust indices
    x.index = y.index
    y.columns = ['y']
    #discard vals which won't have moving vals
    return (x.ix[period-1:],y.ix[period-1:])

if __name__=="__main__":
    #nested kwargs being passed down
    kwargs = {"alg":BagLearner.BagLearner,
        "kwargs":{"alg":KNNLearner.KNNLearner,'bags':BAGS,
            "kwargs":{'k':K}}}

    test_symbol(SYMBOL,kwargs=kwargs,brokerage=BROKERAGE,
        purchase_size=PURCHASESIZE,cash=CASH,
        t_data=2/3,forecast=FORECAST,display=True)

