# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 20:13:42 2017

@author: AmatVictoriaCuramIII
"""

#This is part of a kth fold optimization set of programs
#Test sets are stored in pickles locally

#Divide time series
firsttime = '07/01/1983'
secondtime = '01/01/1995'
thirdtime = '01/01/2006'
fourthtime = '01/01/2010'
lasttime = '01/01/2050'
#Assign tickers
ticker = '^GSPC'
#Import modules
import pandas as pd
from ChaikinAggMaker import ChaikinAggMaker
#Read in test sets
S1TS = pd.read_pickle('SP500NCS1TS')
S2TS = pd.read_pickle('SP500NCS2TS')
S3TS = pd.read_pickle('SP500NCS3TS')
S4TS = pd.read_pickle('SP500NCS4TS')
#Delete duplicate columns
S1TS = S1TS.loc[:,~S1TS.columns.duplicated()]
S2TS = S2TS.loc[:,~S2TS.columns.duplicated()]
S3TS = S3TS.loc[:,~S3TS.columns.duplicated()]
S4TS = S4TS.loc[:,~S4TS.columns.duplicated()]
#Test param sets
testset1winners = ChaikinAggMaker(ticker, S1TS, firsttime, secondtime)
testset2winners = ChaikinAggMaker(ticker, S2TS, secondtime, thirdtime)
testset3winners = ChaikinAggMaker(ticker, S3TS, thirdtime, lasttime)
testset4winners = ChaikinAggMaker(ticker, S4TS, fourthtime, lasttime)
#Empty structure
Aggregate = pd.DataFrame()
#Concatenate param sets
Aggregate = pd.concat([Aggregate, testset1winners, testset2winners,
                    testset3winners, testset4winners],axis = 1)
#Delete duplicate columns.
Aggregate = Aggregate.loc[:,~Aggregate.columns.duplicated()]
