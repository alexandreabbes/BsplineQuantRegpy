#!/usr/bin/env python
from BsplineQuantRegpy import SplineCubicQuant
import numpy as np
import matplotlib.pyplot as plt

def quick_start():
    print('''code :
    def quick_start():
    # Generate data
    x = np.linspace(0, 1, 100)
    y = 3*x + 0.2*np.sin(10*np.pi*x) + 0.2*np.random.randn(100)
    knots = np.quantile(x, np.linspace(0, 1, 11))

    # Fit with monotonicity constraint
    result = SplineCubicQuant(x, y, knots, tau=0.5, monot=1)
    # Fit without monotonicity constraint (uncomment to test)
    #result = SplineCubicQuant(x, y, knots, tau=0.5, monot=0)
    # Evaluate
    x_eval = np.linspace(0, 1, 200)
    y_eval = result(x_eval)

    plt.plot(x,y,"*r")
    plt.plot(x_eval,y_eval,color='black')
    plt.show()''')
    
    # Generate data
    x = np.linspace(0, 1, 100)
    y = 3*x + 0.2*np.sin(10*np.pi*x) + 0.2*np.random.randn(100)
    knots = np.quantile(x, np.linspace(0, 1, 11))

    # Fit with monotonicity constraint
    result = SplineCubicQuant(x, y, knots, tau=0.5, monot=1)
    # Fit without monotonicity constraint (uncomment to test)
    #result = SplineCubicQuant(x, y, knots, tau=0.5, monot=0)
    # Evaluate
    x_eval = np.linspace(0, 1, 200)
    y_eval = result(x_eval)

    plt.plot(x,y,"*r")
    plt.plot(x_eval,y_eval,color='black')
    plt.show()

def main():
    quick_start()

if __name__=="__main__":
  main()
