# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 10:38:04 2016

@author: dkubisti


"""

import numpy as np
import os
from shutil import copyfile 
import pandas as pd
import numpy.lib.recfunctions as rfn
import matplotlib.pyplot as plt
import fileinput
# import the modules that we need. (re is for regex)
import re
import glob


#plt.close("all")
#%matplotlib qt #plot figure outside console must be typed in console

# %% chose simulation

# one file containing all information
file =  'C:\\TDCRDS\\FACSIM\\output\\ModelNitrates_Treactor_total_all.npz'

run_x   = np.load(file)
times_all        = run_x['times']
ModelResult_all  = run_x['ModelResult_all']
parameter        = run_x['param_in']
dim              = run_x['dim']
Treactor         = run_x['Treactor']
modelstep        = run_x['modelstep']
#%% plot for all channels, search for different Temperature runs (clumsy coding)

# specify species to be plotted (max 8, otherwise number of subplots needs to be adjusted)
#######################################################################
vartoplot1 = ['NO2','HNO3','C4H8','CHEX','OH','NO','NO3']
vartoplot2 = ['HONO','HO2', 'O3', 'N2O5'] #,'N2O5'
vartoplot  = vartoplot1, vartoplot2
#######################################################################


for ivarlist in range (0, np.size(vartoplot)):
    plt.figure()
    # initialise subplots 
    for ivar in range(0,np.size(vartoplot[ivarlist])):
        if ivar == 0:
            cmdstr = 'ax' + str(ivar+1) + ' = plt.subplot(4,2,' + str(ivar+1) + ')'; exec(cmdstr)
        else:
            cmdstr = 'ax' + str(ivar+1) + ' = plt.subplot(4,2,' + str(ivar+1) + ',sharex = ax1)'; exec(cmdstr)
        plt.grid();  plt.ylabel(vartoplot[ivarlist][ivar]); 
    
    for i in range(0,np.size(ModelResult_all.dtype.names)):
        temperature = (re.findall(r'T_.*',ModelResult_all.dtype.names[i]))
        if temperature == []:   # skip, if variable is not a temperature
            continue
        temperature_K = temperature[0][2:] # get temperature in K   
        
        for ivar in range(0,np.size(vartoplot[ivarlist])):
            cmdstr = 'ax' + str(ivar+1) + '.plot(ModelResult_all[\'TIME_' + temperature_K + '\'], \
                                                 ModelResult_all[\'' + str(vartoplot[ivarlist][ivar]) + '_' + temperature_K + '\']/ModelResult_all[\'M_' + temperature_K +'\']*' + str(1.e+9) + \
                                                 ',\'-\', label = ModelResult_all.dtype.names[i])'''
            eval(cmdstr)
            # plot total time
            cmdstr = 'ax' + str(ivar+1) + '.plot([times_all[\'time_tot_' + temperature_K + '\'], times_all[\'time_tot_' + temperature_K + '\']], \
                                                 [min(ModelResult_all[\'' + str(vartoplot[ivarlist][ivar]) + '_' + temperature_K + '\']/ModelResult_all[\'M_' + temperature_K +'\']*' + str(1.e+9) + '), \
                                                  max(ModelResult_all[\'' + str(vartoplot[ivarlist][ivar]) + '_' + temperature_K + '\']/ModelResult_all[\'M_' + temperature_K +'\']*' + str(1.e+9) + ')], \
                                                  \':\', linewidth=3)'
            eval(cmdstr)
    plt.legend()     
    plt.show()   

#%% delta based to 298 K
# molvolume fixed to 293 K

# ***********************
base_temperature = 293.15
# ***********************

plt.figure()
for i in range(0,np.size(ModelResult_all.dtype.names)):
    temperature = (re.findall(r'T_.*',ModelResult_all.dtype.names[i]))
    if temperature == []:   # skip, if variable is not a temperature
        continue
    temperature_K = temperature[0][2:] # get temperature in K   
    cmdstr = 'plt.plot(ModelResult_all[\'TIME_'  + temperature_K + '\'], \
                                             (ModelResult_all[\'NO2_'  + temperature_K + '\']/ ModelResult_all[\'M_' +temperature_K + '\'] - \
                                              ModelResult_all[\'NO2_'  + str(base_temperature) + '\'] / \
                                              ModelResult_all[\'M_' + str(base_temperature) + '\'])*' + str(1.e+9) + \
                                             ',\'-\', label = ModelResult_all.dtype.names[i])'''  
    eval(cmdstr)
    
plt.legend()    
plt.grid()
plt.ylabel('diff to '+ str(base_temperature)) 
plt.show()  

#%% delta based to precedent temperature, assuming its sorted

# start temperature
# ***********************
base_temperature = 293
# ***********************

plt.figure()
# difference
ax1 = plt.subplot(2,1,1);               plt.ylabel('diff '); ax1.grid()
ax2 = plt.subplot(2,1,2, sharex = ax1); plt.ylabel('ratio'); ax2.grid()
for i in range(0,np.size(ModelResult_all.dtype.names)):
    temperature = (re.findall(r'T_.*',ModelResult_all.dtype.names[i]))
    if temperature == []:   # skip, if variable is not a temperature
        continue
    temperature_K = temperature[0][2:] # get temperature in K   
    # difference
    cmdstr = 'ax1.plot(ModelResult_all[\'TIME_'  + temperature_K + '\'], (ModelResult_all[\'NO2_'  + temperature_K + '\']/ ModelResult_all[\'M_'  + temperature_K + '\']- \
                                              ModelResult_all[\'NO2_'  + str(base_temperature) + '\'] / \
                                              ModelResult_all[\'M_'  + str(base_temperature) + '\'])*' + str(1.e+9) + ',\'-\', label = \'diff:' + str(temperature_K) + 'K - ' + str(base_temperature) + 'K\')'''  
    exec(cmdstr)
    # ratio
    cmdstr = 'ax2.plot(ModelResult_all[\'TIME_'  + temperature_K + '\'], (ModelResult_all[\'NO2_'  + temperature_K + '\']/ ModelResult_all[\'M_'  + temperature_K + '\']) / \
                                                                         (ModelResult_all[\'NO2_'  + str(base_temperature) + '\']/ModelResult_all[\'M_'  + str(base_temperature) + '\'])  \
                                              ,\'-\', label = \'ratio:' + str(temperature_K) + 'K / ' + str(base_temperature) + 'K\')'''
    exec(cmdstr)
    base_temperature = temperature_K
ax1.legend(); ax2.legend()
plt.show()  

#%% calculate differences taking total time into account
test = np.array([])
for itemperature in range(0,np.size(Treactor)):
    #np.where((ModelResult_all['TIME_293']<times_all['time_tot_293']+modelstep) & (ModelResult_all['TIME_293']>times_all['time_tot_293']-modelstep) )
    cmdstr = 'timeindex = np.where((ModelResult_all[\'TIME_'+str(int(Treactor[itemperature]))+'\'] < times_all[\'time_tot_'+str(int(Treactor[itemperature])) + '\']+modelstep) & \
                                   (ModelResult_all[\'TIME_'+str(int(Treactor[itemperature]))+'\'] > times_all[\'time_tot_'+str(int(Treactor[itemperature])) + '\']))'      #-modelstep
    exec(cmdstr)    
    cmdstr = 'x = ModelResult_all[\'NO2_' + str(int(Treactor[itemperature])) + '\'][timeindex]/ \
                  ModelResult_all[\'M_' + str(int(Treactor[itemperature])) + '\'][timeindex] * 1.0e+9'
    exec(cmdstr)
    print('Reactor Temperature:',str((Treactor[itemperature])),'K, NO2: ',round(x[0],3),' ppb')
    test = np.append(test,x)
    

print('Reactor temp diff to one step lower temp: ',np.round(np.diff(test),3),' ppb')
print('Reactor temp diff to one step lower temp as percentage: ',np.round(np.diff(test)/test[1:]*100,1),' %')
print('Input concentration: ',
      'NO2: ', round((ModelResult_all['NO2_293'][0]/ModelResult_all['M_293'][0])*1.0e+9,3), ' ppb , \
       PAN: ', round((ModelResult_all['PAN_293'][0]/ModelResult_all['M_293'][0])*1.0e+9,3), ' ppb , \
       IPN: ', round((ModelResult_all['IC3H7NO3_293'][0]/ModelResult_all['M_293'][0])*1.0e+9,3), ' ppb , \
       HNO3:', round((ModelResult_all['HNO3_293'][0]/ModelResult_all['M_293'][0])*1.0e+9,3), ' ppb ')
       
# quick and dirty

# %% delta, not automated yet

#plt.figure()
#plt.plot(ModelResult_all['TIME_293'],(ModelResult_all['NO2_293'])/ModelResult_all['M_293']*1.e+9,'-b'); #/modelrun['M_' + id]
#plt.plot(ModelResult_all['TIME_473'],(ModelResult_all['NO2_473']-ModelResult_all['NO2_293'])/ModelResult_all['M_293']*1.e+9,'-g'); #/modelrun['M_' + id]
#plt.plot(ModelResult_all['TIME_673'],(ModelResult_all['NO2_673']-ModelResult_all['NO2_473'])/ModelResult_all['M_293']*1.e+9,'-c'); #/modelrun['M_' + id]
#plt.plot(ModelResult_all['TIME_923'],(ModelResult_all['NO2_923']-ModelResult_all['NO2_673'])/ModelResult_all['M_293']*1.e+9,'-r'); #/modelrun['M_' + id]
#plt.plot(ModelResult_all['TIME_923'],(ModelResult_all['HNO3_923'])/ModelResult_all['M_293']*1.e+9,':r'); #/modelrun['M_' + id]
#plt.ylabel('NO2');
#plt.legend(['Delta293K','Delta473K', 'Delta673', 'Delta923', 'HNO3', 'ANs','PN+PANs','Nitrat923'], loc=1)

# mixing rations
#plt.figure()
#plt.plot(ModelResult_all['TIME_293'],1/ModelResult_all['M_293'] * 1.0e+9 * (ModelResult_all['NO2_293']),'-b'); #/modelrun['M_' + id]
#plt.plot(ModelResult_all['TIME_473'],1/ModelResult_all['M_473'] * 1.0e+9 * (ModelResult_all['NO2_473']-ModelResult_all['NO2_293']),'-g'); #/modelrun['M_' + id]
#plt.plot(ModelResult_all['TIME_673'],1/ModelResult_all['M_673'] * 1.0e+9 * (ModelResult_all['NO2_673']-ModelResult_all['NO2_473']),'-c'); #/modelrun['M_' + id]
#plt.plot(ModelResult_all['TIME_923'],1/ModelResult_all['M_923'] * 1.0e+9 * (ModelResult_all['NO2_923']-ModelResult_all['NO2_673']),'-r'); #/modelrun['M_' + id]
#plt.ylabel('NO2');
#plt.legend(['Delta293K','Delta473K', 'Delta673', 'Delta923'], loc=2)
#plt.grid()

#plt.figure()
#plt.plot(ModelResult_all['TIME_293'], (ModelResult_all['NO2_293']/ModelResult_all['NO2_293']),'-b'); #/modelrun['M_' + id]
#plt.plot(ModelResult_all['TIME_473'], (ModelResult_all['NO2_473']/ModelResult_all['NO2_293']),'-g'); #/modelrun['M_' + id]
#plt.plot(ModelResult_all['TIME_673'], (ModelResult_all['NO2_673']/ModelResult_all['NO2_473']),'-c'); #/modelrun['M_' + id]
#plt.plot(ModelResult_all['TIME_923'], (ModelResult_all['NO2_923']/ModelResult_all['NO2_673']),'-r'); #/modelrun['M_' + id]
#plt.ylabel('NO2');
#plt.legend(['Ratio293K','Ratio473K', 'Ratio673', 'Ratio923'], loc=2)
