#!/usr/bin/env python

"""
    File name: mktcap.py
    Author: Jon Lu
    Date created: 6/12/2017
    Date last modified: 6/13/2017
    Python Version: 3.6.1
"""

import pandas as pd
import numpy as np
import pyodbc
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm
import matplotlib.colors as colors
from matplotlib.animation import FuncAnimation, FFMpegWriter


def get_query(datepart, number):
    """

    Parameters
    ----------
    datepart : str
        Part of date that number is added to, ex. yy, m m
    number : int
        Number to add to datepart

    Returns
    -------
    sql : str
        String representation of sql query for market history

    """
    sql = """
    declare @t datetime
    
    select @t = max(TradeDate) from stocks..tblTradeDates where TradeDate < dateadd(""" + datepart + ', ' + str(number) + """, getdate())
    
    select Symbol, TradeDate, MarketCap from stocks..tblStockHistory
    where TradeDate = @t
    and MarketCap is not NULL AND MarketCap != 0
    order by TradeDate, MarketCap desc
    """
    return sql


def get_data(datepart, number):
    """

    Parameters
    ----------
    datepart : str
        Part of date that number is added to, ex. yy, mm
    number : int
        Number to add to datepart

    Returns
    -------
    data : pd.DataFrame
        data returned by query

    """
    sql = get_query(datepart, number)
    cnxn = pyodbc.connect('Driver={SQL Server};Server=[server];Database=SandBox;')
    data = pd.read_sql_query(sql, cnxn)
    return data

df = pd.DataFrame()  # create new dataframe
for i in range(0, -11, -2):  # 0, -2, -4, etc
    df_year = get_data('yy', i)
    df = pd.concat([df, df_year])  # concatenate to full dataframe

df = pd.pivot_table(df, values='MarketCap', index='Symbol', columns='TradeDate')

df = df.applymap(np.log)  # maps ln over market cap values

ax = df.plot.kde()  # density function

for line in ax.lines[:-1]:
    line.set_linestyle('-.')
    line.set_linewidth(1)
ax.lines[-1].set_linewidth(2)  # latest line thicker, not dot-dashed

plt.xlim(-5, 15)  # trims tails
plt.grid(True)

plt.savefig('plot.png')

plt.close()  # close plot before next plot

fig, ax = plt.subplots()  # new plot

cm = plt.get_cmap('gist_rainbow')  # color map
cNorm = colors.Normalize(vmin=0, vmax=len(df.columns)-1)
scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)


def update(i):  # update function as per FuncAnimation spec
    plt.clf()
    plt.title(df.columns[i])
    ax = df.iloc[:, i].plot.kde()
    ax.lines[0].set_c(scalarMap.to_rgba(i))
    plt.grid(True)
    plt.xlim(-5, 15)  # trims tails
    plt.ylim(-.01, .2)  # fixed vertical scale

anim = FuncAnimation(fig, update, len(df.columns))
# plt.show()
writer = FFMpegWriter(fps=1)
anim.save('plots.mp4', writer=writer)
