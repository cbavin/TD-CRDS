# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 17:08:28 2016

@author: dkubisti
"""
# %% functions
def modeloutput(file, id, modelpath, modeloutput, instrumenttype, facsheet):
    import numpy as np
    from shutil import copyfile 
    print('save output')
    print(modeloutput + file  + id + '_Input1.dat') #+ '_'
    copyfile(modelpath + instrumenttype + 'In1.asc',  modeloutput + file  + id + '_Input1.dat')
    copyfile(modelpath + instrumenttype + 'In2.asc',  modeloutput + file  + id + '_Input2.dat')
    copyfile(modelpath + instrumenttype + 'In3.asc',  modeloutput + file  + id + '_Input3.dat')
    copyfile(modelpath + instrumenttype + 'OUT1.dat',  modeloutput + file + id + '_Output1.dat')
    copyfile(modelpath + instrumenttype + 'OUT2.dat',  modeloutput + file + id + '_Output2.dat')
    copyfile(modelpath + instrumenttype + 'OUT3.dat',  modeloutput + file + id + '_Output3.dat')
    copyfile(modelpath + facsheet,  modeloutput + file + id + '_' + facsheet)

 
    
