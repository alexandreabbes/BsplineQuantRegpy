import numpy as np
from BsplineQuantRegpy import SplineCubicQuant
import matplotlib.pyplot as plt

def quick_start2():
    print('''##CODE:
    import numpy as np
    from BsplineQuantRegpy import SplineCubicQuant
    import matplotlib.pyplot as plt
    
    print("test_basic_fit")
    x = np.linspace(0, 1, 30)
    #y = x + 0.5*np.sin(10*np.pi*x) + 0.05*np.random.randn(30)
    y = x*(1-x) + 0.05*np.random.randn(30)

    x_eval = np.linspace(0, 1, 100)

    knots = np.quantile(x, np.linspace(0, 1, 6))
    result = SplineCubicQuant(x, y, knots, tau=0.5)
    y_eval = result(x_eval)


    print(" test_monotonicity")

    knots = np.quantile(x, np.linspace(0, 1, 6))
    result_m = SplineCubicQuant(x, y, knots, tau=0.5, monot=1)

    y_eval_m = result_m(x_eval)


    plt.plot(x,y,"*r")
    plt.plot(x_eval,y_eval,color='grey')
    plt.plot(x_eval,y_eval_m,color='black')
    plt.show()
    ''')
    
    print("test_basic_fit")
    x = np.linspace(0, 1, 30)
    #y = x + 0.5*np.sin(10*np.pi*x) + 0.05*np.random.randn(30)
    y = x*(1-x) + 0.05*np.random.randn(30)

    x_eval = np.linspace(0, 1, 100)

    knots = np.quantile(x, np.linspace(0, 1, 6))
    result = SplineCubicQuant(x, y, knots, tau=0.5)
    y_eval = result(x_eval)


    print(" test_monotonicity")

    knots = np.quantile(x, np.linspace(0, 1, 6))
    result_m = SplineCubicQuant(x, y, knots, tau=0.5, monot=1)

    y_eval_m = result_m(x_eval)


    plt.plot(x,y,"*r")
    plt.plot(x_eval,y_eval,color='grey')
    plt.plot(x_eval,y_eval_m,color='black')
    plt.show()



def main():
    quick_start2()

if __name__=="__main__":
  main()
