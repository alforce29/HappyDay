# -*- coding: utf-8 -*-
# @Time     : 2018/4/11  17:58
# @Author   : Xiang Huang
# @Site     : https://www.shanshu.ai
# @File     : test.py
# @Software : PyCharm Community Edition
import pickle
import pandas as pd

df = pd.read_csv('deppon_S_location_matrix.csv')
df = df[['from', 'to', 'distance', 'time']]
distance_arr = pd.pivot_table(df, ['distance'], 'from', 'to').fillna(0).get_values()
time_arr = pd.pivot_table(df, ['time'], 'from', 'to').fillna(0).get_values()
ind = pd.pivot_table(df, ['distance'], 'from', 'to').fillna(0).index.tolist()

def suc(i,x_sol,temp):
    for j in range(0, 122):
        if (i, j) in x_sol:
            temp.append(j)
            return suc(j, x_sol, temp)
    return temp

with open('solution.pkl','rb') as fin:
    sol = pickle.load(fin)

x_list = []
for i in range(0, 123):
    if (122, i) in sol['x_sol']:
        x_list.append(i)

x_sol_list = {}
for i in x_list:
    x_sol_list[i] = suc(i, sol['x_sol'], [i])

temp = []
for item in x_sol_list:
    for i in x_sol_list[item]:
        temp.append([item, ind[i]])

df = pd.DataFrame(temp, columns=['driver_id', 'station_id'])

time_cnt = {}
for item in x_sol_list:
    print x_sol_list[item]
    time_cnt[item] = 0
    for i in range(len(x_sol_list[item])-1):
        time_cnt[item] += 1200
        time_cnt[item] += time_arr[x_sol_list[item][i]][x_sol_list[item][i + 1]]
print time_cnt

obj = 0
for item in sol['x_sol']:
    if item[1] != 122:
        obj += distance_arr[item[0]][item[1]]

print 'obj:',obj