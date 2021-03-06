**Overview:**
	An ongoing project to use machine learning to create predictive
	models of the ASX. Then use these models to construct entry and exit 
	signals, which can then be converted into orders. These orders can
	then be subsequently converted into portfolios, whose relative
	performances can be measured.

	The data science platform for Python, Anaconda was used, drawing
	largely on Pandas and Numpy. Currently only a Kth Nearest Neighbour
	Regression Learner has been used, however I fully intended to 
	explore other machine learning algorithms and more general
	trading ideas.

	This project was primarily started for the purpose of learning 
	and has been on an on-going hobby project since early to mid 2016.
	This is the reason for the writing of many of my own modules, 
	however in later versions, I may migrate over to using something
	like pyfolio.

	Once again just re-iterating, this is a hobby project and no actual
	trading is taking place, so in particular the data from Yahoo Finance
	is not being used for commercial purposes.

**Algorithms:**
	**KNNLearner:**
		A Kth Nearest Neighbour Regression Learner.
		Makes use of a Bag Learner.

	For further details about each Algorithm and their performance
	over backtesting see their READMEs located in their directories.

**Installation:**
	If you desire to tinker with the code yourself,

	Install `Anaconda
	<https://www.continuum.io/downloads/>`_ for Python 3.5

	Clone the Repository.

	You have two main options for setting up the environment and path.

	**Option 1:**
		Navigate to the directory and run $ conda env create

		Alter the environment so that /lib is included in path as in 
		this `example
		<http://conda.pydata.org/docs/using/envs.html#saved-environment-variables>`_.

	**Option 2:**
		Modify your environment as you see fit, making sure to include
		/lib in the path.

**Usage:**
	Each Learner at this point as two main scripts, testLearner.py and 
	learnerPerformance.py

	**testLearner.py:**
		When run this script splits the data into two sections an initial 		
		training segment and a testing segment, then runs the Learner with 
		the parameters set as constants at the top of the script. 

	**learnerPerformance.py:** 
		When run this script splits the data into three sections an initial 
		training segment, a testing segment and a validation segment. All 
		symbols in the ASX (excluding some if they don't have a sufficient 
		daily volume traded) are run through the learner with the parameters 
		set as constants at the top of the script.

		'Successes' from the testing data are then selected and then run 
		against the validation data.

	These scripts produce basic performance metrics, order files,
	portfolios and graphics that can be inspected.

	A basic subset of data of the ASX has been attached (Approximately 10 years
	of data for companies with codes in the range of [AAA,CAA) ). To retrieve
	additional ASX data refer to retrieve.py, this script can be used to
	retrieve symbols listed in company_codes.csv from Yahoo Finance.
	You may retrieve a subset of companies by altering company_codes.csv
	and you may alter the time period of the data retrieved by adjusting the
	DAYSPRIOR constant in the python script.
