import matplotlib.pyplot as plt
import numpy as np

def huatu(x,y):
    z1=np.polyfit(x,y,3)
    p1=np.poly1d(z1)
    yvals=p1(x)
    plt.plot(x,y,'b*',label='original values')
    plt.plot(x,y,'r',label='original')
    plt.plot(x,yvals,'g',label='ployfit values')
    plt.xlabel('AppYear')
    plt.ylabel('AppNum')
    plt.title('ployfit')
    plt.legend()
    plt.show()
    return
