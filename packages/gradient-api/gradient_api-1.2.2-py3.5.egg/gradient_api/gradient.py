# coding=utf-8
# uliontse

import numpy as np
import pandas as pd
from sympy import Symbol,diff
import matplotlib.pyplot as plt



def generate_1d(expr_or_poly1d,init_x=-0.5,step=0.01,num_iters=1e4,showPlot=False,xlimArr=None,ylimArr=None):
    '''
    :param expr_or_poly1d: str or array1d_like,
    :param init_x: float,
    :param step: float,
    :param num_iters: int or float,
    :param showPlot: boolean,
    :param xlimArr: tuple, affect plot_x:
    :param ylimArr: tuple,
    :return: dict,
    '''
    cur_x = np.array([init_x])[0] # avoid Overflow Error.
    step = np.array([step])[0]
    num_iters = int(num_iters)

    if isinstance(expr_or_poly1d,str):
        expr = expr_or_poly1d
        x = Symbol('x')
        diff_expr = str(diff(eval(expr),x))
        gradient = lambda x: np.array([eval(diff_expr)])[0]
        y = lambda x: np.array([eval(expr)])[0]

    else: # follow np.poly1d Error.
        L = expr_or_poly1d
        y = np.poly1d(L)
        gradient = np.poly1d.deriv(y)

    if xlimArr:
        plot_x = np.linspace(init_x-abs(xlimArr[0]),init_x+abs(xlimArr[1]),201)
    else:
        plot_x = np.linspace(init_x -5, init_x + 5, 201)
    plot_y = y(plot_x)
    # plt.ion()

    cur_num = 0
    for i in range(num_iters):
        cur_num += 1
        prev_x = cur_x
        cur_x -= step * gradient(prev_x)
        if abs(y(cur_x) - y(prev_x)) < np.array([1e-8])[0]:
            break
        if showPlot and i % 2 == 0:
            # plt.cla()
            plt.plot(plot_x, plot_y)
            plt.scatter(cur_x, y(cur_x), color='red')
            if xlimArr: plt.xlim(xlimArr)
            if ylimArr: plt.ylim(ylimArr)
            plt.pause(0.1)
    plt.ioff()
    plt.show()
    return {
        'X': cur_x,
        'Y': y(cur_x),
        'Gradient': gradient(cur_x),
        'Numloop': cur_num
    }



def generate_2d(dataFrame:pd.DataFrame,step=0.1,num_iters=1e4):
    '''
    :param dataFrame: pandas.DataFrame, like train_data with labels.
    :param step: float,
    :param num_iters: int or float,
    :return: dict,
    '''

    arr = np.hstack([np.ones((len(dataFrame),1)),dataFrame])
    X = pd.DataFrame(arr) # 列名未知
    Y = X.pop(X.shape[1]-1)

    init_theta = np.zeros(X.shape[1])
    cur_theta = init_theta
    num_iters = int(num_iters)

    def y(theta):
        try:
            return np.sum((Y - X.dot(theta)) ** 2) / len(Y)
        except:
            return float('inf')

    def gradient(theta):
        try:
            return X.T.dot(X.dot(theta) - Y) * 2 / len(X)
        except:
            return float('inf')


    cur_num = 0
    for i in range(num_iters):
        cur_num += 1
        prev_theta = cur_theta
        cur_theta -= step * gradient(prev_theta)
        if abs(y(cur_theta) - y(prev_theta)) < np.array([1e-8])[0]:
            break

    return {
        'theta': cur_theta.values,
        'Y': y(cur_theta),
        'Gradient': gradient(cur_theta).values,
        'Numloop': cur_num,
        'Linear_Intercept': cur_theta[0],
        'Linear_Coef': cur_theta[1:].values,
    }

