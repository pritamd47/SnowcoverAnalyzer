# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from sklearn.datasets import load_boston
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D as ln
import pandas as pd
import numpy as np


def DrawLine(theta):
    theta = np.array(theta)

    b = theta[0][0]
    m = theta[0][1]

    x = np.matrix([-999,999])
    y = m * x + b

    return np.array(x)[0], np.array(y)[0]

def ComputeCost(X, y, theta):
    inner = np.power(((X * theta.T) - y), 2)
    return np.sum(inner) / (2 * len(X))


def gradientDescent(X, y, theta, alpha, iters, line = None):
    temp = np.matrix(np.zeros(theta.shape))
    parameters = int(theta.ravel().shape[1])
    cost = np.zeros(iters)

    for i in range(iters):
        error = (X * theta.T) - y

        for j in range(parameters):
            term = np.multiply(error, X[:, j])
            temp[0, j] = theta[0, j] - ((alpha / len(X)) * np.sum(term))
        theta = temp
        cost[i] = ComputeCost(X, y, theta)
        print i, ":", theta,":", cost[i]


        if line:
            x_plt, y_plt = DrawLine(theta)
            line.set_xdata(x_plt)
            line.set_ydata(y_plt)
            plt.draw()
            plt.pause(0.0001)

    return theta, cost

def main():
    boston = load_boston()
    df = pd.DataFrame(boston.data, index=boston.target)
    for i in range(13):
        for j in range(i, 13):
            data = pd.DataFrame()
            data.insert(0, 'index', np.array(df[i]))
            data.insert(1, 'values', np.array(df[j]))
            data.insert(0, 'Ones', 1)

            alpha = 0.001
            iters = 100000

            cols = data.shape[1]
            X = data.iloc[:, 0:cols - 1]
            y = data.iloc[:, cols - 1:cols]

            X = np.matrix(X.values)
            y = np.matrix(y.values)
            theta = np.matrix(np.array([0, 0]))

            fig = plt.figure()
            ax = plt.axes(xlim=(0,max(np.array(X[:,1:]).flatten())),ylim=(0,max(np.array(y).flatten())+10))
            plt.scatter(X[:,1:],y,marker='.')

            x_plt, y_plt = DrawLine(theta)

            line, = plt.plot(x_plt, y_plt)

            print "Initial cost: ", ComputeCost(X, y, theta)

            # performing linear regression
            Line = None

            g, cost = gradientDescent(X, y, theta, alpha, iters)
            print "Theta: ", g
            print "Final Cost: ", ComputeCost(X, y, g)

            if not line == None:
                x_plt, y_plt = DrawLine(g)
                plt.plot(x_plt, y_plt)
                plt.savefig("x{0}y{1}_c{2}_am{3}.png".format(i,j, cost[-1], g), bbox_inches='tight', dpi=600)
                plt.close()
                plt.plot(range(len(cost)), cost, color='red')
                plt.savefig("x{0}y{1}_costcurve.png".format(i,j), bbox_inches='tight', dpi = 600)
                plt.close()

if __name__ == '__main__':
    main()
