"""
A Module for the retreival of dataframes from csv files and the 
formating of that data.
"""
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import glob

def get_company_data(symbols, dropping=['Volume','Open','High','Low','Close'],
    store_path ='../CSVData/' ):
    """Retrieves data for each symbol in symbols."""
    if type(symbols) is not str:
        #retrieve first item so there is something to join to
        df = get_company_data(symbols[0],dropping)
        for symbol in symbols[1:]:
            df = df.join(get_company_data(symbol,dropping,store_path),how='outer')  
        df = clean_data(df)
        return df
    else:
        symbol = symbols
        try:
            df = pd.read_csv(store_path+symbol+'.csv',index_col=0)
            for column in dropping:          
                df = df.drop(column,1)
            #data in reverse chronological order, so reverse it
            df = df.ix[::-1]
            date_range = pd.DataFrame()
            start = pd.to_datetime(df.index[0])
            end = pd.to_datetime(df.index[-1])
            #Inserts non-trading days
            date_range['Date'] = pd.date_range(start,end, freq='D')
            date_range.set_index(['Date'],inplace=True) 
            df = df.join(date_range,how="right")
            df = clean_data(df)
            #give columns symbol suffix
            df.rename(columns = lambda x: x+"_"+symbol,inplace=True)
        except:
            print(symbol," not found")
            df="null"
    return df
def get_data_ASX_history(symbols,start,end,dropping=['Volume','Open','High','Low']):
    """Deprecated Function for the retrieval of data from a different format"""
    df = pd.DataFrame()
    if (isinstance(end,str)):
        df['Date'] = pd.date_range(start,end, freq='D')
    else:
        df['Date'] = pd.date_range(start,periods = end, freq='D')
    df = df.set_index(['Date'])

    store_path ='historicalcsvData/'

    for symbol in symbols:
        ext = '_'+symbol
        try:
            current = pd.read_csv(store_path+symbol+'.csv',index_col=0)
            for column in dropping:          
                current = current.drop(column+ext,1)
            df = df.join(current, how='left')
        except:
            path ='historicalData/2014'
            allFiles = glob.glob(path + "/*.txt")
            for file_ in allFiles:
                dfread = pd.read_csv(file_,header=None,index_col=0)
                with open(store_path+symbol+'.csv', 'a') as f:
                    col = dfread.loc[symbol]
                    row = (pd.DataFrame(col).T)
                    row.to_csv(f, header=False, index=False)

            current = pd.read_csv(store_path+symbol+'.csv',header=None)
            current.columns = ['Date','Open'+ext,'High'+ext,'Low'+ext,'Close'+ext,'Volume'+ext]  
            current['Date'] = pd.to_datetime(current['Date'].astype(str),format="%Y%m%d")
            current.set_index(['Date'], inplace=True)
            current.to_csv(store_path+symbol+'.csv')
            for column in dropping:          
                current = current.drop(column+ext,1)
            df = df.join(current, how='left') 
    df = clean_data(df)
    return df

def get_average_daily_value_traded(symbol):
    """Returns the average daily volume traded of a company."""
    df = get_company_data(symbol, dropping=['Open','High','Low','Close'])
    try:
        df['DailyValue'] = df.iloc[:,0]*df.iloc[:,1]
        return  df['DailyValue'].mean(axis=0)
    except:
        return 0
    

def normalize_data(df):
    """Normalizes the data from the values in the first row."""
    #dataframe
    try:
        return df/df.iloc[0,:]
    #series
    except:
        return df/df.iloc[0]
def clean_data(df):
    """Fills Nan values with suitable values."""
    #forward fill if n/a encounterd after data
    df = df.fillna(method = 'ffill')
    #backward fill if n/a encounterd before data
    df = df.fillna(method = 'bfill')
    return df

def normalize_relative_to_max(df):
    """Normalizes the cols of the df off the max of the abs of the col."""
    for col in df:
        maxVal = df[col].abs().max()
        df[col]= df[col]/maxVal;
    return df

def convert_to_returns(df,period=1):
    """Converts a df with a single column of close or adj close to
    returns per period."""
    #print(df)
    if len(df.index)<period:
        return -1
    r = df.copy()
    r.iloc[period:] = (r.iloc[period:].values/r.iloc[:-period].values)-1
    r.iloc[0:period]=0
    r.columns = ['Returns']
    #print(r)
    return r

def add_bollinger_bands(df,graph,name,period=20):
    """Adds Bollinger Bands to the graph."""
    rm = df[name].rolling(center=False,window=period).mean()
    rstd = df[name].rolling(center=False,window=period).std()
    upper = rm+2*rstd
    lower = rm-2*rstd
    upper.plot(label = "Upper Band", ax=graph)
    lower.plot(label = "Lower Band", ax=graph)
    return graph

def plot_data(df,title,x_axis,y_axis,error_measure='N/A'):
    """Plots the data in the df with two optional error measures."""
    pred_mean = df['Prediction'].mean()
    if 'Error_Measure' in df.columns:
        adj = df['Error_Measure'].copy()
        df['Error_Measure_U'] = df['Prediction'].copy()+adj
        df['Error_Measure_L'] = df['Prediction'].copy()-adj
        del df['Error_Measure']
    if (error_measure!='N/A'):
        df['Upper_Error_measure+Brokerage'] = error_measure+pred_mean
        df['Lower_Error_measure+Brokerage'] = -1*error_measure+pred_mean
    ax = df.plot(title=title,fontsize=12)
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    plt.show()