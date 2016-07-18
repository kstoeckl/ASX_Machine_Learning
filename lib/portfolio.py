"""
A class for the analysis of the performance of positions over time.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dataConversion
import calculations as calc

PORTFOLIO_PATH = "portfolios/"

class portfolio:
	ASX_200="XJO"
	
	def __init__(self,portfolioPath,orderPath=None,cash=None,brokerage=None):
		if orderPath==None:
			self.df = pd.read_csv(portfolioPath)
		else:
			#order file
			orders = pd.read_csv(orderPath)
			#retrieves stocks actively traded
			symbols = orders.Symbol.unique()
			cols=[symbol for symbol in symbols]
			cols.append("Cash")
			cols.append("TotalValue")
			#creates a skeleton df indexed by the period of trading
			if len(orders.index>0):
				end_date = orders['Date'].iloc[-1]
				date_range = pd.date_range(orders['Date'].iloc[0],
					orders['Date'].iloc[-1], freq='D')
				self.df = pd.DataFrame(index=date_range,columns = cols)
				self.df.ix[:,:] = 0
				self.create_portfolio_record(orders, symbols,cash,brokerage)
				self.df.to_csv(portfolioPath)
			else:
				print("No Orders from which to construct Portfolio")
		self.benchmark = dataConversion.get_company_data(self.ASX_200)

	def create_portfolio_record(self, orders, symbols, cash,brokerage):
		"""Constructs a dataframe representing the position of a portfolio
		from the date of the first order to that of the last."""
		close_data = dataConversion.get_company_data(symbols)
		self.df = self.df.join(close_data,how='left')
		
		print("here")
		#Code below is relatively slow
		#TODO: Improve Speed, through apply
		for index, row in orders.iterrows():
			share_change=row['Shares']
			if (row['Order']=='SELL'):
				share_change*=-1
			self.df[row['Symbol']].ix[row['Date']] = share_change

		#Allocates initial cash then alters it from buying and selling
		self.df["Cash"].ix[0]=cash
		for symbol in symbols:
			#As selling is marked negative, will result in cash gain.
			self.df["Cash"]-=self.df[symbol]*self.df["Adj Close_"+symbol]
			self.df["Cash"]-=abs(self.df[symbol]*self.df["Adj Close_"+symbol])*brokerage
		#rolling total of cash and shares
		self.df["Cash"] = self.df["Cash"].cumsum()
		for symbol in symbols:
			self.df[symbol] = self.df[symbol].cumsum()
		#calculate total value
		for symbol in symbols:
			self.df["TotalValue"]+=self.df[symbol]*self.df["Adj Close_"+symbol]
		self.df["TotalValue"]+=self.df["Cash"]
	
	def displayPerformance(self, companies=False):
		"""Plots the performance of the portfolio. If companies==True
		displays the normalized prices of the stocks held."""
		temp = self.df.join(self.benchmark,how='left')
		for col in temp.columns:
			if 'Close' not in col and 'Total' not in col:
				del temp[col]
		temp = dataConversion.normalize_data(temp)
		if (companies==True):
			ax = temp.plot(title="PortfolioValue",fontsize=12)
		else:
			ax = temp[['TotalValue','Adj Close_'+self.ASX_200]].plot(
				title="PortfolioValue",fontsize=12)
		ax.set_xlabel('Date')
		ax.set_ylabel('NormalizedValue')
		plt.show()
	def display_return_metrics(self,period,benchmark=False):
		"""Displays some performance metrics for the return of the portfolio
		over the time of investment."""
		#risk free return
		rfr=np.power(1.02,period/365)-1

		if benchmark==True:
			print("Benchmark")
			df = self.benchmark.ix[:,0].copy()
		else:
			print("Portfolio")
			df = self.df['TotalValue'].copy()

		avg_return = calc.average_return_arithmetic(df,period)
		std = calc.deviation_of_returns(df,period)
		dd = calc.deviation_of_returns(df,period,downwards=True)

		sharpe = (avg_return-rfr)/std
		sortino = (avg_return-rfr)/dd
		print("AVG Return = ",avg_return,", Sharpe Ratio = ",sharpe)
		print("Sortino Ratio = ",sortino)

	def performanceAnalysis(self,period=7):
		"""Generates performance metrics for the portfolio relative to 
		the ASX200."""
		print("For period = ",period)
		self.display_return_metrics(period)
		self.display_return_metrics(period,benchmark=True)
		
		temp1 = pd.merge(self.df,self.benchmark,how = 'inner',left_index=True,
			right_index=True)

		temp2 = dataConversion.normalize_data(temp1['TotalValue'])
		temp1 = dataConversion.normalize_data(temp1['Adj Close_'+self.ASX_200])
		
		#corrcoef returns matrix so indicies to get pertinent value
		corr = np.corrcoef(temp1.astype(float),temp2.astype(float))[0][1]

		print("Correlation between portfolio and ASX200, ",corr)
		self.displayPerformance(companies=False)