# -*- coding: utf-8 -*-
# @Time     : 2018/4/11  14:47
# @Author   : Xiang Huang
# @Site     : https://www.shanshu.ai
# @File     : solver.py
# @Software : PyCharm Community Edition

import pandas as pd
from gurobipy import *
import pickle
#
#
#

if __name__ == '__main__':
    unit_info = pd.read_csv('unit_info.csv')
    weight_info = unit_info.groupby(['departure', 'arrival']).sum().reset_index()['weight'].tolist()
    unit_info = unit_info.groupby(['departure', 'arrival']).sum().reset_index()['volumn'].tolist()
    df = pd.read_csv('deppon_S_location_matrix.csv')
    df = df[['from', 'to', 'distance', 'time']]
    distance_arr = pd.pivot_table(df, ['distance'], 'from', 'to').fillna(0).get_values()
    time_arr = pd.pivot_table(df, ['time'], 'from', 'to').fillna(0).get_values()
    ind = pd.pivot_table(df, ['distance'], 'from', 'to').fillna(0).index.tolist()

    variable_length = len(unit_info)
    print variable_length
    length = len(distance_arr)
    width = len(distance_arr[0])

    M = Model('VRP')
    x = {}
    u = {}
    t_a, t_d = {}, {}
    c = {}
    # Declare variables
    for i in range(length):
        for j in range(width):
            x[i, j] = M.addVar(vtype=GRB.BINARY, name="x_{}_{}".format(i, j))

    for i in range(variable_length):
        u[i] = M.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=14, name="u_{}".format(i))
        t_a[i] = M.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=21000, name="ta_{}".format(i))
        t_d[i] = M.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=22200, name="td_{}".format(i))
        c[i] = M.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=3001, name="c_{}".format(i))

    u[122] = M.addVar(vtype=GRB.CONTINUOUS, lb=0, name="u_{}".format(i))
    t_d[122] = M.addVar(vtype=GRB.CONTINUOUS, name="t_{}".format(i))
    c[122] = M.addVar(vtype=GRB.CONTINUOUS, lb=0, name="c_{}".format(i))

    M.update()

    # Declare constraints
    # Constraints on degree of nodes
    for i in range(length):
        M.addConstr(x[i,i] == 0)

    for i in [122]:
        M.addConstr(quicksum(x[i,j] for j in range(variable_length)) <= 30)

    for i in [122]:
        M.addConstr(quicksum(x[j, i] for j in range(variable_length)) <= 30)

    for j in range(width):
        M.addConstr(quicksum(x[i, j] for i in range(length)) == quicksum(x[j, k] for k in range(length)))

    for i in range(variable_length):
        M.addConstr(quicksum(x[j, i] for j in range(length)) == 1)

    for i in range(variable_length):
        M.addConstr(quicksum(x[i, j] for j in range(length)) == 1)

    # Constraints on product flow
    for i in range(variable_length):
        for j in range(variable_length):
            M.addConstr(t_d[i] + time_arr[i][j] * x[i, j] - 50000 * (1 - x[i, j]) <= t_a[j])
            M.addConstr(u[i] + unit_info[j] * x[i, j] - 15 * (1 - x[i, j]) <= u[j])
            M.addConstr(c[i] + weight_info[j] * x[i, j] - 4000 * (1 - x[i, j]) <= c[j])

    for i in range(variable_length):
        M.addConstr(t_a[i] + 1200 == t_d[i])

    for i in [122]:
        M.addConstr(u[i] == 0)
        M.addConstr(c[i] == 0)

    # # Add xiaoma test solution into model
    #
    # xiaoma_sol = pd.read_excel('xiaoma_solution.xlsx')
    # xiaoma_dict = {}
    # for i in range(len(xiaoma_sol)):
    #     xiaoma_dict[xiaoma_sol.iloc[i]['driver_id']] = [122]
    # for i in range(len(xiaoma_sol)):
    #     if ind.index(xiaoma_sol.iloc[i]['station_id']) not in xiaoma_dict[xiaoma_sol.iloc[i]['driver_id']]:
    #         xiaoma_dict[xiaoma_sol.iloc[i]['driver_id']].append(ind.index(xiaoma_sol.iloc[i]['station_id']))
    #
    # for item in xiaoma_dict:
    #     for i in range(len(xiaoma_dict[item])-1):
    #         M.addConstr(x[xiaoma_dict[item][i], xiaoma_dict[item][i+1]] == 1)

    # time_cnt = {}
    # for item in [7451]:
    #     time_cnt[item] = 0
    #     for i in range(len(xiaoma_dict[item]) - 2):
    #         print time_cnt[item]
    #         time_cnt[item] += time_arr[xiaoma_dict[item][i+1]][xiaoma_dict[item][i+2]]

    M.update()
    M.setParam(GRB.Param.TimeLimit, 7200)
    M.setObjective(quicksum(distance_arr[i][j] * x[i,j] for i in range(length) for j in range(variable_length)), GRB.MINIMIZE)
    M.optimize()

    x_sol = {}
    u_sol = {}
    t_sol = {}
    sol = {}
    for i in range(length):
        for j in range(width):
            if x[i, j].x > 0.5:
                x_sol[i, j] = 1
                # print i, j, x[i, j].x, '\n'

    for item in u:
        if u[item].x > 0.01:
            u_sol = u[item].x

    for item in t_a:
        if t_a[item].x > 0.001:
            t_sol = t_a[item].x
            print t_a[item].x

    sol['x_sol'] = x_sol
    sol['t_sol'] = t_sol
    sol['u_sol'] = u_sol
    with open('solution.pkl', 'wb') as fout:
        pickle.dump(sol, fout)

    cnt = 0
    for i in range(variable_length):
        if x[i, 122].x > 0.5:
            cnt += 1
    print cnt
