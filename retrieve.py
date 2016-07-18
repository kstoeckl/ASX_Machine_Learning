"""
When run retrieves the latest data for all companies stored in companies.csv
from yahoo finance. https://policies.yahoo.com/us/en/yahoo/terms/utos/index.htm

*I don't believe I am breaching any terms by sharing this on github,
given this projects non-commerical nature, however let me know if this
is not the case and I shall ammend my actions.

TODO:
    Some questions as to the accuracy of the data from yahoo finance

    Data was found to occasionally be inaccurate on public holidays.
    (Instead of the day being skipped due to not being a market day.)
    For instance DJW on good friday.

    Altering the algorithm so that it only trades on Market Days and when 
    there is a sufficient volume to support the trade would be a good
    step to eliminate/reduce this.

    Perhaps could also seek a different source of data.
"""
import pandas as pd
import dataConversion as dc
import urllib.request
import datetime
import time

DAYSPRIOR=10*365# The number of days prior to now to retrieve data to.
SYMBOL_PATH = "company_codes.csv"
REFINED_SYMBOL_PATH = "refined_symbols.csv"
CSV_PATH = "CSVData/"


def retrieve_company_data(companies,days,store_path):
    """Retrieves from yahoo finance historical per day data and saves to csv.
    Could be multi threaded for performance.
    The waiting time and attempt number might seem excessive, however dealing
    with relatively poor internet.
    """
    failed_to_get=[]    
    for index, row in companies.iterrows():
        print(index," out of ",len(companies.index))
        found=0
        count=0
        #makes 5 attempts to retrieve item,
        while (found==0 and count<5):
            try:
                if count>0:
                    urllib.request.urlretrieve(req, store_path+symbol+".csv")
                else:
                    symbol = row.ix[0]
                    now = datetime.datetime.now().date()
                    ytd = (datetime.datetime.now()-datetime.timedelta(days=days)).date()
                    req = "http://real-chart.finance.yahoo.com/table.csv?s="
                    req+= symbol+".AX"
                    req+= "&d="+str(now.month)+"&e="+str(now.day)+"&f="+str(now.year)
                    req+= "&g=d&a="+str(ytd.month)+"&b="+str(ytd.day)+"&c="+str(ytd.year)
                    req+= "&ignore=.csv"        
                    print(req)
                    urllib.request.urlretrieve(req, store_path+symbol+".csv")
                    found=1
            except:
                count+=1
                time.sleep(3)
        if (found==0):
            print("failed for ",symbol)
            failed_to_get.append(index)

    return failed_to_get

def refine(companies,failed_to_get,refined_symbol_path):
    """Produces a csv that lists the files that were actually retreived."""
    df = companies.copy()
    for index in failed_to_get:        
        df = df.drop([index])
    df.to_csv(REFINED_SYMBOL_PATH,header=None,index=None)

if __name__=="__main__":
    companies = pd.read_csv(SYMBOL_PATH,header=None)
    failed_to_get=retrieve_company_data(companies,DAYSPRIOR,CSV_PATH)

    refine(companies,failed_to_get,REFINED_SYMBOL_PATH)