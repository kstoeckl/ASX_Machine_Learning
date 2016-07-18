"""
A python script for measuring the performance of the learner.
Makes use of the python multiprocessing library for speed. 
"""
import pandas as pd
import os
import testLearner
import multiprocessing as mp
import dataConversion
import KNNLearner
import BagLearner
import order
import portfolio

NUM_PROCESSES=4
SYMBOL_PATH = "../refined_symbols.csv"
#Parameters
BROKERAGE=0.002
PURCHASESIZE=10000
CASH=30000
MODIFIER=0.7
K=15
BAGS=30
DAILY_VOLUME_VALUE=50000
FORECAST=1

def test_symbol(symbol,kwargs,output):
    """Passed to each process."""
    print(symbol)
    (corr,error_measure,precision,tp)=testLearner.test_symbol(symbol,**kwargs)
    #Output of each process which will be collected
    output.put((symbol,corr,error_measure,precision,tp))

def performance_analysis(processes,output,performance):
    """Starts each process. Waits for their Completion and records
    their results."""
    for p in processes:
        p.start()
    for p in processes:
        #waits for the completion of all process
        p.join()
    results = [output.get() for p in processes]
    for r in results:
        index = r[0]
        #DailyValueTraded was previously calculated and it is the last value
        #on each row of performance. Hence the setting of a slice of the row. 
        performance.ix[index][:-1] = r[1:]
    return performance

def performance_test(symbols,perf_name,kwargs):
    """Iterates through symbols spawning processes to run tests on companies.
    Saves the results of the tests to perf_name."""
    columns = ["Correlation","Error_measure","Precision","tp","DailyValueTraded"]
    performance = pd.DataFrame(index =symbols.index,columns = columns)
    #-1.1 as a flag for missing and to set float data type
    performance[::]=-1.1
    processes=[]
    output = mp.Queue()
    process_count=0
    count=0
    for index, row in symbols.iterrows():
        count+=1
        p = mp.Process(target=test_symbol,args=(index,kwargs,output))

        #Faster to preclude on volume here
        vol = dataConversion.get_average_daily_value_traded(index)
        performance.set_value(index,'DailyValueTraded',vol)
        if (vol>=DAILY_VOLUME_VALUE):
            processes.append(p)
            process_count+=1
        else:
            continue

        if (process_count%NUM_PROCESSES==0):
            print(count,' out of ',len(symbols.index))
            performance = performance_analysis(processes,output,performance)
            #lets you eyeball first trials
            if (count<30):
                print(performance)
            performance.to_csv(perf_name)
            processes=[]
            output = mp.Queue()
            process_count=0
    #wrap up if len(symbols)%NUM_PROCESSES!=0
    performance = performance_analysis(processes,output,performance)
    print(performance)
    performance.to_csv(perf_name)

def refine_symbols(perf_name):
    """Refines the symbols based off their performance on the testing data.
    If a symbol had high correlation between the predicted returns of the 
    stock and the actual returns of the stock then it typically had higher
    precision.
    In addition high correlation in test data had a correlation with high
    correlation in the validation data.
    So this function chooses the 'successes' from the initial trial to run
    on the validation data.
    """
    df = pd.read_csv(perf_name,index_col=0)
    for index,row in df.iterrows():
        if (row['DailyValueTraded']>=DAILY_VOLUME_VALUE):
            if (row['Correlation']>0.3):
                print(index)
                continue
        df.drop(index,inplace=True)
    print(df)
    return df

if __name__=="__main__":
    perf_name = "forecast="+str(FORECAST)
    perf_csv = "performance/"+perf_name+".csv"

    order_path=order.ORDER_PATH+perf_name
    try:
        os.mkdir(order_path)
    except Exception as e:
        print(e)
    order_path = order_path+'/'

    #Nested kwargs for passing down to inner functions
    #Not the prettiest but it does allow all parameters to be set here.
    kwargs = {"t_data":1/2,"v_data":3/4,"forecast":FORECAST,
        "store_path":"../CSVData/","create_orders":False,
        "order_path":order_path,"brokerage":BROKERAGE,
        "purchase_size":PURCHASESIZE,"cash":CASH,
        "kwargs":{"alg":BagLearner.BagLearner,
            "kwargs":{"alg":KNNLearner.KNNLearner,'bags':BAGS,
                "kwargs":{'k':K}}}}

    symbols = pd.read_csv(SYMBOL_PATH,header=None,index_col=0)
    performance_test(symbols,perf_csv,kwargs)

    #Switch to using validation data
    kwargs["t_data"]=kwargs["v_data"]
    kwargs["v_data"]=1
    kwargs['create_orders']=True

    #remove any pre-existing orders from the path
    order.remove_csv_files(order_path)

    #Select 'sucesses' from inital run then trade
    symbols = refine_symbols(perf_csv)
    print(symbols)

    final_perf_csv = "performance/final"+perf_name+".csv"
    performance_test(symbols,final_perf_csv,kwargs)

    print("combining")
    combined_order_file_name = order.ORDER_PATH+perf_name+".csv"
    order.combine_order_files(order_path,combined_order_file_name)

    portfolio_file_name = portfolio.PORTFOLIO_PATH+perf_name+".csv"
    p = portfolio.portfolio(portfolio_file_name,combined_order_file_name,CASH,BROKERAGE)
    p.performanceAnalysis()