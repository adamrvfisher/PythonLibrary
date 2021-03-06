# -*- coding: utf-8 -*-
"""

@author: Adam Reinhold Von Fisher - https://www.linkedin.com/in/adamrvfisher/

"""

#This is an Edge Ratio calculator for single issue
#May be deprecated see ERatioSingleIssueDonchianTrendIII.py
#N Period Edge Ratio Computation

#Imports 
from YahooGrabber import YahooGrabber
import numpy as np
import time as t
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
 
#Empty structures
tempdf = pd.DataFrame()
edgelist = []

#Variable assignment
ticker = 'NUGT'
#For ATR + MFE/MFA
atrwindow = 20
#For signal generation
donchianwindow = 10

#How many days to calculate e-ratio for
LengthOfTest = range(2, 19) #(2,3) = 2 day Eratio // assuming fill at "Entry Price"

#Get data
Asset = YahooGrabber(ticker)

#In sample Trimmer
Asset = Asset[-491:-463]

#Make column that represents X axis 
Asset['Index'] = Asset.index

#Format for mpl
Asset['IndexToNumber'] = Asset['Index'].apply(mdates.date2num)

#Format Dataframe to feed candlestick_ohlc()
AssetCopy = Asset[['IndexToNumber', 'Open', 'High', 'Low', 'Close', 'Adj Close']].copy()

#Timer begin
start = t.time()

#log returns
Asset['LogRet'] = np.log(Asset['Adj Close']/Asset['Adj Close'].shift(1)) 
Asset['LogRet'] = Asset['LogRet'].fillna(0)

#Donchian Channel calculation from params
Asset['RollingMax'] = Asset['High'].rolling(window=donchianwindow, center=False).max()
Asset['RollingMin'] = Asset['Low'].rolling(window=donchianwindow, center=False).min()

#Index copies
Asset['Index'] = Asset.index
Asset['RangeIndex'] = range(1, len(Asset.index) + 1)

#ATR calculation
Asset['Method1'] = Asset['High'] - Asset['Low']
Asset['Method2'] = abs((Asset['High'] - Asset['Close'].shift(1)))
Asset['Method3'] = abs((Asset['Low'] - Asset['Close'].shift(1)))
Asset['Method1'] = Asset['Method1'].fillna(0)
Asset['Method2'] = Asset['Method2'].fillna(0)
Asset['Method3'] = Asset['Method3'].fillna(0)
Asset['TrueRange'] = Asset[['Method1','Method2','Method3']].max(axis = 1)

#ATR in points not %
Asset['AverageTrueRangePoints'] = Asset['TrueRange'].rolling(window = atrwindow,
                                center=False).mean()
#ATR in percent
Asset['AverageTrueRangePercent'] = Asset['AverageTrueRangePoints'] / Asset['Close']

#Signal generation; long if new high and no new high on previous period, short 
#if new low and no new low on previous period; if Donchian window or ATR is not calculated stay out of market
Asset['Regime'] = np.where(Asset['High'] > Asset['RollingMax'].shift(1), 1, 0)
Asset['Regime'] = np.where(Asset['Low'] < Asset['RollingMin'].shift(1), -1, Asset['Regime'])

#Stay flat if ATR has not been established // nan > 0 == false
Asset['Regime'] = np.where(Asset['AverageTrueRangePercent'] > 0, Asset['Regime'], 0)

#Find trade date when regime changes
Asset['OriginalTrade'] = 0
Asset['OriginalTrade'].loc[(Asset['Regime'].shift(1) != Asset['Regime']) & (Asset['Regime'] == -1)] = -1  
Asset['OriginalTrade'].loc[(Asset['Regime'].shift(1) != Asset['Regime']) & (Asset['Regime'] == 1)] = 1 

#Organize entry price & check for gap
Asset['EntryPrice'] = np.nan
#For all original trade days
for a in Asset['OriginalTrade'][Asset['OriginalTrade'] != 0].index:
    #If a long trade
    if Asset['OriginalTrade'][a] == 1:
        #Record previous high as entry
        Asset['EntryPrice'].loc[a] = Asset['RollingMax'].shift(1).loc[a]
        #Check for open higher than entry gap and reassign
        if Asset['Open'][a] > Asset['EntryPrice'][a]:
            Asset['EntryPrice'].loc[a] = Asset['Open'][a]
    #If a short trade
    if Asset['OriginalTrade'][a] == -1:
        #Record previous high as entry
        Asset['EntryPrice'].loc[a] = Asset['RollingMin'].shift(1).loc[a]
        #Check for open lower than entry gap and reassign
        if Asset['Open'][a] < Asset['EntryPrice'][a]:
            Asset['EntryPrice'].loc[a] = Asset['Open'][a]
            
Asset['EntryPrice'] = Asset['EntryPrice'].ffill()   
            
#Make list of Original Trade DATES
tradedates = Asset[['OriginalTrade', 'Index', 'RangeIndex', 'Adj Close', 'AverageTrueRangePoints']].loc[(
                               Asset['OriginalTrade'] != 0)]
#Number of signals generated
numsignals = len(tradedates)

#temp variable assignment
MFEpoints = None
MAEpoints = None

#For number of e-ratio days to compute
for z in LengthOfTest:
    print('Calculating ' + str(z) + ' Day e-ratio')
    #For each value of RangeIndex on Tradedate
    for i in tradedates.RangeIndex:
        print('Calculating ' + str(z) + ' Day e-ratio for trade on ' + str(Asset['Index'].loc[Asset['RangeIndex'] == i][0]))
        #Assign computation space
        tempdf = pd.DataFrame()
        #Assign entry price
        entryprice = Asset['EntryPrice'].loc[Asset['RangeIndex'] == i][0]
        #Take H, L, C, sample data for number of days under study post trade        
        tempdf['Close'] = Asset['Close'].loc[Asset.index[i:i+z]] 
        tempdf['High'] = Asset['High'].loc[Asset.index[i:i+z]] 
        tempdf['Low'] = Asset['Low'].loc[Asset.index[i:i+z]] 

        #For long trades 
        if tradedates['OriginalTrade'].loc[tradedates['RangeIndex'] == i][0] == 1:  
            print('Long entry at ', entryprice) 
            #Check status 
#            print(tempdf)
            #MFE
            maxup = max(tempdf['High'] - entryprice)
            #MAE            
            maxdown = max(entryprice - tempdf['Low']) 
            print('MFE in points = ', maxup)
            print('MAE in points = ', maxdown)
#            print(atrwindow, ' day ATR = ', tradedates['AverageTrueRangePoints'].loc[tradedates['RangeIndex'] == i][0])
            #MFE assignment
            MFEpoints = maxup
            #MFE assignment to trade dates            
            tradedates['MFEpoints'].loc[tradedates['RangeIndex'] == i] = maxup
            #MAE assignment
            MAEpoints = maxdown
            #MAE assignment to trade dates            
            tradedates['MAEpoints'].loc[tradedates['RangeIndex'] == i] = maxdown
        #For short trades
        if tradedates['OriginalTrade'].loc[tradedates['RangeIndex'] == i][0] == -1:
            print('Short entry at ', entryprice)             
            #Check status 
#            print(tempdf)
            #MAE
            maxup = max(tempdf['High'] - entryprice)
            #MFE       
            maxdown = max(entryprice - tempdf['Low'])  
            print('MFE in points = ', maxdown)            
            print('MAE in points = ', maxup)
#            print(atrwindow, ' day ATR = ', tradedates['AverageTrueRangePoints'].loc[tradedates['RangeIndex'] == i][0])
            #MFE assignment
            MFEpoints = maxdown
            #MFE assignment to trade dates                        
            tradedates['MFEpoints'].loc[tradedates['RangeIndex'] == i] = maxdown
            #MAE assignment
            MAEpoints = maxup
            #MAE assignment to trade dates            
            tradedates['MAEpoints'].loc[tradedates['RangeIndex'] == i] = maxup
#        print('--------------------------------------------')    
#        print('--------------------------------------------')    
#        print('--------------------------------------------')    
    #Adjust MFE and MAE for volatility - normalization
    tradedates['VolAdjMFE'] = tradedates['MFEpoints']/tradedates['AverageTrueRangePoints']
    tradedates['VolAdjMAE'] = tradedates['MAEpoints']/tradedates['AverageTrueRangePoints']
    #Add MFE and MAE values
    sumMFE = sum(tradedates['VolAdjMFE'])
    sumMAE = sum(tradedates['VolAdjMAE'])
    #Divide by number of signals
    AvgVolAdjMFE = sumMFE/numsignals
    AvgVolAdjMAE = sumMAE/numsignals 
    #Performance metric
    edgeratio = AvgVolAdjMFE/AvgVolAdjMAE
    #Display results
    print('The ', z, ' day edge ratio is', edgeratio)
    #Add metric to list
    edgelist.append(edgeratio)
#              
#Length = len(Asset1['LogRet'])
#Range = range(0,Length)
#print(MaxDD*100, '% = Max Drawdown')
#
#Make dataframe of performance metrics from iterations
edgeratioframe = pd.DataFrame(index = range(2, len(edgelist) + 2))
edgeratioframe['EdgeRatio'] = edgelist
#Graphical display
edgeratioframe['EdgeRatio'].plot(grid=True, figsize=(8,5))
#End timer
#end = t.time()
#Timer stats
#print((end - start), ' seconds later.')
#Display performance
#print('Max eRatio is', max(edgeratioframe['EdgeRatio']))

#Graphics
#X and Y axis scale figure
figure, axe = plt.subplots(figsize = (10,5))
#Assign axis labels
plt.ylabel(ticker + ' Price')
plt.xlabel('Date') 
#Overlay
axe.plot(AssetCopy['IndexToNumber'], Asset['RollingMax'], color = 'green', label = 'RollingMax')
axe.plot(AssetCopy['IndexToNumber'], Asset['RollingMin'], color = 'red', label = 'RollingMin')
#axe.plot(Asset['IndexToNumber'], Asset['SMA'], color = 'black', label = 'SMA')

#Signal triangles..
axe.scatter(Asset.loc[Asset['OriginalTrade'] == 1, 'IndexToNumber'].values, 
            Asset.loc[Asset['OriginalTrade'] == 1, 'EntryPrice'].values, label='skitscat', color='green', s=75, marker="^")
axe.scatter(Asset.loc[Asset['OriginalTrade'] == -1, 'IndexToNumber'].values, 
            Asset.loc[Asset['OriginalTrade'] == -1, 'EntryPrice'].values, label='skitscat', color='red', s=75, marker="v")

#Plot the DF values with the figure, object
candlestick_ohlc(axe, AssetCopy.values, width=.6, colorup='green', colordown='red')
axe.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

#For ATR
figure2, axe2 = plt.subplots(figsize = (10,2))
#Add labels
plt.ylabel(ticker + ' ATR Percent')
plt.xlabel('Date')
#ATR line graph
axe2.plot(AssetCopy['IndexToNumber'], Asset['AverageTrueRangePercent'], color = 'black', label = '4wkATRPercent')
#axe2.plot(AssetCopy['IndexToNumber'], AssetCopy['ATRRollingMax'], color = 'green', label = 'ATRRollingMax')
#axe2.plot(AssetCopy['IndexToNumber'], AssetCopy['ATRRollingMin'], color = 'red', label = 'ATRRollingMin')
#Date formatting
axe2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
