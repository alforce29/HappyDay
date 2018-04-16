# -*- coding: utf-8 -*-
# @Time     : 2018/4/12  14:08
# @Author   : Xiang Huang
# @Site     : https://www.shanshu.ai
# @File     : test1.py
# @Software : PyCharm Community Edition
import pandas as pd

df = pd.read_csv('deppon_S_location_matrix.csv')
df = df[['from', 'to', 'distance', 'time']]
distance_arr = pd.pivot_table(df, ['distance'], 'from', 'to').fillna(0).get_values()
time_arr = pd.pivot_table(df, ['time'], 'from', 'to').fillna(0).get_values()

xiaoma_sol = pd.read_excel('xiaoma_solution.xlsx')
ind = pd.pivot_table(df, ['distance'], 'from', 'to').fillna(0).index.tolist()

xiaoma_dict = {}
for i in range(len(xiaoma_sol)):
    xiaoma_dict[xiaoma_sol.iloc[i]['driver_id']] = [122]

for i in range(len(xiaoma_sol)):
    if ind.index(xiaoma_sol.iloc[i]['station_id']) not in xiaoma_dict[xiaoma_sol.iloc[i]['driver_id']]:
        xiaoma_dict[xiaoma_sol.iloc[i]['driver_id']].append(ind.index(xiaoma_sol.iloc[i]['station_id']))

time_cnt = {}
for item in [7451]:
    time_cnt[item] = 0
    for i in range(len(xiaoma_dict[item]) - 1):
        print xiaoma_dict[item][i+1]
        print time_cnt[item]
        time_cnt[item] += 1200
        print time_cnt[item]
        time_cnt[item] += time_arr[xiaoma_dict[item][i+1]][xiaoma_dict[item][i+2]]
