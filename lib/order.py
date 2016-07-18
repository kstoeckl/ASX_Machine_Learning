"""
A Module for the construction and manipulation of orders
An example of a typical order is,
Date        Symbol  Order   Shares
20/08/2015  AAC     SELL    7722.007722
Orders are stored in dataframes indexed jointly by a timestamp and a symbol.
These can be saved in a .csv for easy later retreival and combination.
"""
import glob
import dataConversion
import pandas as pd
import os

ORDER_PATH = 'orders/'

def combine_order_files(path,comined_orders_name):
    """Combines all order files located in path into a single order file."""
    allFiles = glob.glob(path + "*.csv")
    c_orders = pd.DataFrame()
    orders = []
    for order_file in allFiles:
        print(order_file)
        df = pd.read_csv(order_file,index_col=None, header=0)
        orders.append(df)
    c_orders = pd.concat(orders)
    #chronological order
    c_orders = c_orders.iloc[c_orders['Date'].argsort()]

    c_orders.to_csv(comined_orders_name)

def remove_csv_files(path):
    """Removes all CSV files from path"""
    for order in glob.glob(path + "*.csv"):
        os.remove(order)

def create_orders(prediction_data,error_measure,symbol,period,brokerage,
        purchase_size,file_name):
    """Reads through the prediction data chronologically, making orders
    if it believes the prediction data suggests a favourable trade."""
    trade_df = pd.DataFrame(index =prediction_data.index,
        columns = ['Symbol','Order','Shares'])
    print(prediction_data)
    pred_mean = prediction_data['Prediction'].mean()
    prices = dataConversion.get_company_data(symbol)
    position=0#keeps track of whether in long or short or neither
    tracker=0#keeps track of the number of timesteps a position has been held
    for index,row in prediction_data.iterrows():
        amount = 0
        #enter long
        if ( tracker<=0 and ((row['Prediction']+pred_mean>error_measure+brokerage)
            and position<1)):
            tracker=period
            #from short
            if (position==-1):
                amount = purchase_size/price
            price = prices.ix[index,0]
            trade_df.ix[index] = [symbol,'BUY',amount+purchase_size/price]
            position= 1
        #enter short
        elif (tracker<=0 and ((row['Prediction']+pred_mean<-1*(error_measure+brokerage))
            and position>-1)):
            tracker=period
            #from long
            if (position==1):
                amount = purchase_size/price
            price = prices.ix[index,0]
            trade_df.ix[index] = [symbol,'SELL',amount+purchase_size/price]
            position= -1
        #exit long
        elif (tracker<=0 and position>0 and row['Prediction']+pred_mean<0 ):
            trade_df.ix[index] = [symbol,'SELL',purchase_size/price]
            position=0
        #exit short
        elif (tracker<=0 and position<0 and row['Prediction']+pred_mean>0):
            trade_df.ix[index] = [symbol,'BUY',purchase_size/price]
            position=0
        else:
            trade_df.ix[index] = [symbol,'NOTHING',0]
        tracker-=1
    #stripping nothing orders
    trade_df = trade_df[trade_df['Order']!='NOTHING']

    trade_df.to_csv(file_name)

def create_orders_o1(prediction_data,error_measure,symbol,period,brokerage,purchase_size,file_name):
    trade_df = pd.DataFrame(index =prediction_data.index, columns = ['Symbol','Order','Shares'])
    print(prediction_data)
    prices = dataConversion.get_company_data(symbol)
    print(prices)
    position=0
    for index,row in prediction_data.iterrows():
        amount = 0
        #enter long
        if ( (row['Prediction']>error_measure+brokerage) and position<1):
            #from short
            if (position==-1):
                amount = purchase_size/price
            price = prices.ix[index,0]
            trade_df.ix[index] = [symbol,'BUY',amount+purchase_size/price]
            position= 1
        #enter short
        elif (( row['Prediction']<(-1*(error_measure+brokerage)) ) and position>-1):
            #from long
            if (position==1):
                amount = purchase_size/price
            price = prices.ix[index,0]
            trade_df.ix[index] = [symbol,'SELL',amount+purchase_size/price]
            position= -1
        #exit long
        elif (row['Prediction']<0 and position>0):
            trade_df.ix[index] = [symbol,'SELL',purchase_size/price]
            position=0
        #exit short
        elif (row['Prediction']>0 and position<0):
            trade_df.ix[index] = [symbol,'BUY',purchase_size/price]
            position=0
        else:
            trade_df.ix[index] = [symbol,'NOTHING',0]
    #stripping nothing orders
    trade_df = trade_df[trade_df['Order']!='NOTHING']

    trade_df.to_csv(file_name)

def create_orders_02(prediction_data,error_measure,symbol,period,brokerage,
        purchase_size,file_name):
    trade_df = pd.DataFrame(index =prediction_data.index,
        columns = ['Symbol','Order','Shares'])
    print(prediction_data)
    prices = dataConversion.get_company_data(symbol)
    position=0  
    tracker=0
    for index,row in prediction_data.iterrows():
        amount = 0
        #enter long
        if ( tracker<=0 and ((row['Prediction']>error_measure+brokerage)
            and position<1)):
            tracker=period
            #from short
            if (position==-1):
                amount = purchase_size/price
            price = prices.ix[index,0]
            trade_df.ix[index] = [symbol,'BUY',amount+purchase_size/price]
            position= 1
        #enter short
        elif (tracker<=0 and ((row['Prediction']<-1*(error_measure+brokerage))
            and position>-1)):
            tracker=period
            #from long
            if (position==1):
                amount = purchase_size/price
            price = prices.ix[index,0]
            trade_df.ix[index] = [symbol,'SELL',amount+purchase_size/price]
            position= -1
        #exit long
        elif (tracker<=0 and position>0 and row['Prediction']<0 ):
            trade_df.ix[index] = [symbol,'SELL',purchase_size/price]
            position=0
        #exit short
        elif (tracker<=0 and position<0 and row['Prediction']>0):
            trade_df.ix[index] = [symbol,'BUY',purchase_size/price]
            position=0
        else:
            trade_df.ix[index] = [symbol,'NOTHING',0]
        tracker-=1
    #stripping nothing orders
    trade_df = trade_df[trade_df['Order']!='NOTHING']

    trade_df.to_csv(file_name)

def create_orders_o3(prediction_data,error_measure,symbol,period,brokerage,purchase_size,file_name):
    trade_df = pd.DataFrame(index =prediction_data.index, columns = ['Symbol','Order','Shares'])
    prices = dataConversion.get_company_data(symbol)
    position=0  
    tracker=0
    sig_strength=0
    for index,row in prediction_data.iterrows():
        amount = 0
        #enter long
        if (row['Prediction']>error_measure+brokerage and abs(row['Prediction'])>sig_strength):
            #refresh position
            if (position==1):
                tracker=period
                sig_strength= abs(row['Prediction'])
                trade_df.ix[index] = [symbol,'NOTHING',0]
                continue
            #from short
            if (position==-1):
                tracker=period
                sig_strength=abs(row['Prediction'])
                amount=purchase_size/price

            price = prices.ix[index,0]
            trade_df.ix[index] = [symbol,'BUY',amount+purchase_size/price]
            position= 1
        #enter short
        elif (row['Prediction']<-1*(error_measure+brokerage) and abs(row['Prediction'])>sig_strength):
            #refresh position
            if (position==-1):
                tracker=period
                sig_strength= abs(row['Prediction'])
                trade_df.ix[index] = [symbol,'NOTHING',0]
                continue
            #from long
            if (position==1):
                tracker=period
                sig_strength=abs(row['Prediction'])
                amount=purchase_size/price

            price = prices.ix[index,0]
            trade_df.ix[index] = [symbol,'SELL',amount+purchase_size/price]
            position= -1
        #exit long
        elif (tracker<=0 and position>0 and row['Prediction']<0 ):
            trade_df.ix[index] = [symbol,'SELL',purchase_size/price]
            position=0
            sig_strength=0
        #exit short
        elif (tracker<=0 and position<0 and row['Prediction']>0):
            trade_df.ix[index] = [symbol,'BUY',purchase_size/price]
            position=0
            sig_strength=0
        else:
            trade_df.ix[index] = [symbol,'NOTHING',0]
        tracker-=1
    #stripping nothing orders
    trade_df = trade_df[trade_df['Order']!='NOTHING']
    print(trade_df)

    trade_df.to_csv(file_name)
