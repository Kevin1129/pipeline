#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: kai Liu
@contact:liukai26@hotmail.com
@version: Python 3.10
@license: Apache Licence
@file: visual.py
@time: 4/3/23 3:25 PM
@Description: 
"""


import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

file_name = "nansha_data.csv"
data = pd.read_csv(file_name)
# organize data
data['times'] = pd.to_datetime(data['times'])
df = data.pivot_table(index="times", columns="code", values="value", aggfunc="mean")
# rename columns
df.rename(columns={"C021028010006701": "P1", "C021028010002001": "P2", "C021028010006301": "P3",
                            "C021028001ZGEA0CA03": "pressure", "C021028001ZGEA0DA03": "flow"}, inplace=True)

df.to_excel("nansha_data2.xlsx")
# plot
# fig_name = '灵新路十六涌压力（MPa）'
# fig = px.line(df, x=df.index, y='P1', title='灵新路十六涌压力（MPa）')
# # fig.update_xaxes(rangeslider_visible=True)
# fig.update_layout(
#     xaxis=dict(
#         rangeselector=dict(
#             buttons=list([
#                 dict(count=1,
#                      label="1m",
#                      step="month",
#                      stepmode="backward"),
#                 dict(count=6,
#                      label="6m",
#                      step="month",
#                      stepmode="backward"),
#                 dict(count=1,
#                      label="YTD",
#                      step="year",
#                      stepmode="todate"),
#                 dict(count=1,
#                      label="1y",
#                      step="year",
#                      stepmode="backward"),
#                 dict(step="all")
#             ])
#         ),
#         rangeslider=dict(
#             visible=True
#         ),
#         type="date"
#     ))
#
# fig.write_html(fig_name + ".html")

