# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 17:26:30 2016

@author: dkubisti
"""
def makeplots_mr_CRDS(modelrun, figure_id, id, title):
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    # get variables names
    variablelist = modelrun.dtype.names
    
    for i_var in range(0,np.size(variablelist)):
    # make plots        
        plt.subplot(4,4,i_var+1)
        plt.plot(modelrun['TIME_'+id],modelrun[variablelist[i_var]]/modelrun['M_'+id]*1.0e+9,'-b'); #/modelrun['M_' + id]
        plt.ylabel(variablelist[i_var])
        plt.xlabel('time / s')
        plt.grid()    