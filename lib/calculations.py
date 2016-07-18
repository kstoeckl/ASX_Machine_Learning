"""
A collection of functions for returning information on time series data.
"""
import numpy as np
import pandas as pd
import dataConversion

def average_return_geometric(data,period=7):
    """Calculates the average returns using geometric mean."""
    return np.power(data.iloc[-1]/data.iloc[0],period/len(data.index))-1

def average_return_arithmetic(data,period=7):
    """Calculates the average returns using arithmetic mean."""
    if len(data.index)<period:
        return 0
    returns = dataConversion.convert_to_returns(data,period)
    #every period'th' value
    return np.mean(returns.iloc[::period])

def deviation_of_returns(data,period=7,downwards=False):
    """Calculates the deviation of a returns time series at each period.
    downwards is a flag to only consider downwards deviation."""
    if len(data.index)<period:
        return 0
    returns = dataConversion.convert_to_returns(data,period)
    #every period'th' value
    temp = returns.iloc[::period]
    if (downwards==True):
        temp = temp.apply(remove_upwards)
            
    return np.std(temp)

def remove_upwards(row):
    if (row>0):
        return 0
    else:
        return row