# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 13:03:32 2017

@author: AmatVictoriaCuramIII
"""
from pandas_datareader import data
def Age(s):
    s = data.DataReader(s, 'yahoo', start='1/1/1900', end='01/01/2050')
    return len(s['Adj Close'])