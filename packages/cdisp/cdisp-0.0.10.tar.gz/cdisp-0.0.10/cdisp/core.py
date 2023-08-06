#-*- coding: utf-8 -*-

"""

Dispersion calculation functions

"""

import numpy      # module for array manipulation
import pandas     # module for general data analysis
import os         # module for general OS manipulation
import scipy      # module for scientific manipulation and analysis
import scipy.constants   # module for with physical constants
from .helpers import *   

## 
def set_transverse_mode(data_frame, order_tag, neff_tag = 'neff', complex_neff = False):
    """ Function for classification of transverse modes
    
        For this function to work, the frequency and polarization must the the same.
        Also the input have to be a Pandas data frame;
    """
    if type(data_frame).__name__ != 'DataFrame': raise(ValueError("The object MUST be a Pandas data frame"))
    ####
    No = len(data_frame)                               # number of modes
    order_list = numpy.array(['%1d' % x for x in numpy.arange(1, No + 1)][::-1])   # list with the transversal order
    neffs = numpy.array(data_frame[neff_tag])               # neffs of the modes
    if complex_neff:
        neffs = numpy.abs(numpy.array([complex(s.replace('i' , 'j ')) for s in neffs]))  # for complex neff    
    inds = neffs.argsort(kind = 'mergesort')             # neff sorting
    inds2 = numpy.array(inds).argsort(kind = 'mergesort')   # index resorting (reverse sorting)
    order_list_sorted = order_list[inds2]                # list with the right (sorted) transversal order
    data_frame[order_tag] = order_list_sorted
    return data_frame
#######

def data_classification(data_frame, wavelength_tag = 'wlength', frequency_tag = 'freq', 
                        input_tags = ['eig', 'Ptm', 'Ppml', 'Pcore', 'Pbus'], 
                        class_tags = ['polarization', 'ring_bus', 'transverse_mode']):
    """ Function for filtering quality factor, losses and classification of polarization and transverse modes
    
       The input have to be a Pandas data frame;
    """
    ## limits setting
    pml_thre = 0.5   # threshold for power in the PMLs
    bus_thre = 1.0   # threshold for power in the bus waveguide relative to the ring
    tm_thre = 1.0   # threshold for power in the TM mode
    ## tags for classification
    [eigenval_tag, TM_tag, pml_tag, ring_tag, bus_tag] = input_tags
    [pol_tag, ring_bus_tag, order_tag] = class_tags
    ## list of columns
    list_col = list(data_frame.columns)  # columns names
    Neig = list_col.index(eigenval_tag)   # index before 
    list_par = list_col[:Neig]    # list of parameters
    ## create wavelength or frequency colunm
    if frequency_tag not in list_col: data_frame[frequency_tag] = scipy.constants.c/data_frame[wavelength_tag]
    if wavelength_tag not in list_col: data_frame[wavelength_tag] = scipy.constants.c/data_frame[frequency_tag]
    ## setting frequency column as the standard for internal use  
    if frequency_tag not in list_par: 
        list_par.remove(wavelength_tag)
        list_par.append(frequency_tag)
    ## PML filtering
    data_frame = data_frame[data_frame[pml_tag] < pml_thre]     # Filter the light that goes to the Pml
    ## TE and TM modes separation
    data_frame[pol_tag] = numpy.array(pandas.cut(numpy.array(data_frame[TM_tag]), [0, tm_thre, data_frame[TM_tag].max()], labels = ['TE', 'TM']))
    list_tag = [pol_tag]
    ## waveguide and bus separation
    if bus_tag in list_col:
        data_frame[ring_bus_tag] = numpy.array(pandas.cut((numpy.array(data_frame[bus_tag])/numpy.array(data_frame[ring_tag]))**(1./4), [0, bus_thre, 1000000], labels = ['ring', 'bus']))
#        data_frame[ring_bus_tag] = numpy.array(pandas.cut(numpy.array(data_frame[ring_tag]), [0, ring_thre, 100000], labels = ['','ring']))
        list_tag = list_tag + [ring_bus_tag]
    ## transverse mode separation
    list_group = list_par + list_tag  # list to filter the first time
    data_frame = data_frame.groupby(list_group, as_index = False).apply(set_transverse_mode, order_tag)  # transverse order
    return data_frame, list_group + [order_tag]

####
def find_idx_nearest_val(array, value):
    '''function to find the nearest index matching to the value given'''
    idx_sorted = numpy.argsort(array)
    sorted_array = numpy.array(array[idx_sorted])
    idx = numpy.searchsorted(sorted_array, value, side="left")
    if idx >= len(array):
        idx_nearest = idx_sorted[len(array)-1]
    elif idx == 0:
        idx_nearest = idx_sorted[0]
    else:
        if abs(value - sorted_array[idx-1]) < abs(value - sorted_array[idx]):
            idx_nearest = idx_sorted[idx-1]
        else:
            idx_nearest = idx_sorted[idx]
    return idx_nearest

###
def dispersion_calculation(data_frame, frequency_tag = 'freq', wavelength_tag = 'wlength', 
                           neff_tag = 'neff', wlength0 = None):
    """ functions for dispersion calculation """
    ## initial definitions
    wlength = numpy.array(data_frame[wavelength_tag]) # wavelength
    omega = 2*numpy.pi*numpy.array(data_frame[frequency_tag])  # angular frequency
    beta = numpy.array(data_frame[neff_tag])*omega/scipy.constants.c   # propagation constant
    ## dialing with circular waveguides 
    if 'r0' in data_frame.columns: 
        rad0 = numpy.array(data_frame['r0'])
        beta = beta/rad0
    else: rad0 = 1.0
    ## dispersion calculations
    beta1 = Df(beta*rad0, omega)/rad0     # beta 1
    beta2 = Df(beta1*rad0, omega)/rad0    # beta 2
    beta3 = Df(beta2*rad0, omega)/rad0    # beta 3
    beta4 = Df(beta3*rad0, omega)/rad0    # beta 4
    D = -2*numpy.pi*scipy.constants.c/wlength*beta2   # D parameter
    ## set up the wlength for phase matching
    wlength0 = 0.9e-6
    if wlength0 == None: wlength0 = wlength[int(wlength.shape[0]/2)]
    elif wlength0 < min(wlength): wlength0 = min(wlength)
    elif wlength0 > max(wlength): wlength0 = max(wlength)
    omega0 = 2*numpy.pi*scipy.constants.c/wlength0
    ## phase matching calculation
    idx0 = find_idx_nearest_val(omega, omega0)
    Dbeta = calculate_Dbeta(beta, idx0)     # propagation constant in 
    Dbeta2 = beta2[idx0]*(omega - omega[idx0])**2 + beta4[idx0]/12*(omega - omega[idx0])**4
    norm_gain = calculate_gain(Dbeta, 1.0e4)
    ## outputs
    n_clad, n_core = 1.0, 3.5
    output_tags = ['beta', 'beta1', 'beta2', 'beta3', 'beta4', 'D', 'Dbeta', 'Dbeta_approx', 'beta_norm', 'beta_clad', 'beta_core',
                  'n_clad', 'n_core', 'gain', 'ng', 'fsr']
    outputs = [beta, beta1, beta2, beta3, beta4, D, Dbeta, Dbeta2, beta/scipy.constants.c, n_clad*omega/scipy.constants.c, n_core*omega/scipy.constants.c,
              n_clad, n_core, norm_gain, beta1*scipy.constants.c, 1/(2*numpy.pi*rad0*beta1)]
    for m, output in enumerate(outputs):
        data_frame[output_tags[m]] = output
    return data_frame
###
def dispersion_analysis(data_frame, list0, frequency_tag = 'freq'):
    ## list of columns
    list0.remove(frequency_tag)
    ## remove short data_frames
    Lmin = 3
    data_frame = data_frame.groupby(list0, as_index = False).filter(lambda x: len(x) >= Lmin)
    ## calculate dispersion
    data_frame = data_frame.groupby(list0, as_index = False).apply(dispersion_calculation)
    return data_frame
##
def calculate_Dbeta(x, idx0):
    '''calculate Dbeta for a set of date with equally spaced frequencies'''
    d = x.shape[0]  # array dimension
    Dx = numpy.full(d, numpy.nan)
    idxm = max(-idx0, idx0 - d + 1)  # minimum index
    idxp = min(idx0 + 1, d - idx0)  # maximum index    
    for idx in range(idxm, idxp):
        xm, xp = numpy.roll(x, idx), numpy.roll(x, -idx)
        Dx[idx0 + idx] = xm[idx0] +  xp[idx0] - 2*x[idx0]
    return Dx
##
def calculate_gain(Dbeta, Pn):
    '''calculate the gain of the 4 wave mixing 
    ** here Pn is normalized such as Pn = gamma*P0'''
    return numpy.sqrt(Pn**2 - (Dbeta/2 + Pn)**2)

def create_data_frame(file_list, dict_sub, Nhline = 5, sep = ','):
    """Create a full dataframe with many accumulated probe tables
    """
    data_frame = pandas.DataFrame()
    for filename in file_list:
        with open(filename) as myfile:
            head = list(it.islice(myfile, Nhline))  # read only the first Nhline lines
        full_header = ''.join(head)  # join all in a single string
        ## extrating relevant info from the header
        dict_prop = {}
        sep = ','
        for line in head:
            output = [s.strip() for s in line.split(sep) if s]
            dict_prop[output[0]] = output[1]
        ## creating the header
        header = head[-1].replace('"', '').split('%')[1].strip()   # data header line
        for word, suma in dict_sub.items():
            header = header.replace(word, suma)
        header = [s.strip() for s in header.split(sep) if s]  # clean the whitespaces
        #### dataframe reading and accumulation
        data_frame = pandas.concat([data_frame, pandas.read_csv(filename, skiprows = Nhline, 
                                      sep = sep, header = 0, names = header)], ignore_index = True)
    return data_frame
