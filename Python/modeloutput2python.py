# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 17:20:14 2016

@author: dkubisti
"""
# %% functions
def modeloutput2python(modelrun, id_reactor, id, pathmodel, pathoutput, instrumenttype):
    import numpy as np
    from rmfield import rmfield     # self written module
    import numpy.lib.recfunctions as rfn
    
    ModelResult_main1 = np.genfromtxt(pathmodel + instrumenttype + "OUT1.DAT", names=True, skip_header = 0) #skip_header = 1 for PSTREAM
    ModelResult_main2 = np.genfromtxt(pathmodel + instrumenttype + "OUT2.DAT", names=True, skip_header = 0)
    ModelResult_main3 = np.genfromtxt(pathmodel + instrumenttype + "OUT3.DAT", names=True, skip_header = 0)  
    
#    ModelResult_main4 = np.genfromtxt(pathmodel + "CRDSOUT4.DAT", names=True, skip_header = 0)
    
    # merge output data in one struct =>    remove Time column , should be the same for all facsim outputs   
    ModelResult_main2b = rmfield(ModelResult_main2,'TIME')  
    ModelResult_main3b = rmfield(ModelResult_main3,'TIME')
    
    #    ModelResult_main4b = rmfield(ModelResult_main4,'TIME')
    ModelResult_main   = [ModelResult_main1, ModelResult_main2b, ModelResult_main3b];    # 
    
    ModelResult = rfn.merge_arrays(ModelResult_main, flatten = True, usemask = False);  # merge to one structured array
    # rename fields depending on titration id
    x = np.shape(ModelResult.dtype.names)
    novar = x[0] # total number of variables
    for i_novar in range(0,novar):
        ModelResult = rfn.rename_fields(ModelResult, {ModelResult.dtype.names[i_novar]:ModelResult.dtype.names[i_novar]+'_'+id_reactor + '_' + id})   
  
    np.save(pathoutput + modelrun + '_' + id + '.npy' ,ModelResult);      #  save
    
    return ModelResult
        
