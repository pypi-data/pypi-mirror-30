import numpy as np
import pandas as pd
import matplotlib as mat
import seaborn as sns
def print_ver():
    print(np.__name__, np.__version__)
    print(pd.__name__, pd.__version__)
    print(mat.__name__, mat.__version__)
    print(sns.__name__, sns.__version__)

def run_test():
    x=np.random.randn(10,1)
    y=np.random.randn(10,1)

    mat.pyplot.plot(x,y,'bo')
    mat.pyplot.show()

    df = pd.DataFrame(index=range(0,len(x)))
    df['x']=x
    df['y']=y
    #df.head()

    sns.lmplot('x','y',data=df)
    mat.pyplot.show()

if __name__=='__main__':
    print_ver()
    run_test()
	
