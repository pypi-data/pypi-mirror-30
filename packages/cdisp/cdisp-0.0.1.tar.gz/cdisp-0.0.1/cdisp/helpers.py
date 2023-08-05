#-*- coding: utf-8 -*-

"""

Helper functions 

"""

import numpy     # module for array manipulation

def Df_fine(x, t):
    """Function for computing first order numerical derivatives using 3rd order derivative calculation (more precise and slower)
     
    Usage
    ------
     
    The function returns y = dx/dt.

    Parameters
    ------
    x: 1-dimensional array
    t: 1-dimensional array preferably with the same length as x
          
    """
#######
    if type(x) <> 'numpy.ndarray': x = numpy.array(x)  # convert to numpy array
    N = x.shape[0]         # length of the original array 
    df = []                # initial derivative empyy list
    for k in range(N):     # loop for calculation 
        if k == 0:         # first point case
            dx = x[k + 1] - x[k]
            dt = t[k + 1] - t[k]
        elif k == N - 1:   # last point case
            dx = x[k] - x[k - 1]
            dt = t[k] - t[k - 1]
        elif k == 1 or k == N - 2: # second and second-to-last cases
            dx = x[k + 1] - x[k - 1]
            dt = t[k + 1] - t[k - 1]             
        else:                    # remaining cases
            dx = -x[k + 2] + 8*x[k + 1] - 8*x[k - 1] + x[k - 2]
            dt = 3*(t[k + 2] - t[k - 2])     
        df.append(Ddata/Dvar)   # add point to the list
    return numpy.array(df)

def Df(x, t):
    """Function for computing first order numerical derivatives
     
    Usage
    ------
     
    The function returns y = dx/dt.

    Parameters
    ------
    x: 1-dimensional array
    t: 1-dimensional array preferably with the same length as x
          
    """
#######
    if type(x) <> 'numpy.ndarray': x = numpy.array(x)  # convert to numpy array
    N = x.shape[0]         # length of the original array 
    df = []                # initial derivative empyy list
    for k in range(N):     # loop for calculation 
        if k == 0:         # first point case
            dx = x[k + 1] - x[k]
            dt = t[k + 1] - t[k]
        elif k == N - 1:   # last point case
            dx = x[k] - x[k - 1]
            dt = t[k] - t[k - 1]
        else:              # remaining cases
            dx = x[k + 1] - x[k - 1]
            dt = t[k + 1] - t[k - 1]     
        df.append(dx/dt)    # add point to the list
    return numpy.array(df)
