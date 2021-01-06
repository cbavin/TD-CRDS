# -*- coding: utf-8 -*-
"""
2017/07/22

@author: dkubisti
Script based on CIMSkOH simulations
Script to loop over facsim runs for CRDS - nitrates with different reactor temperatures -  work in progress!!!
hard coded: works only for three output files, coded in facsim_raw.fac and modeloutput2python
hard coded: works only for three input files, coded in facsim_raw.fac 
"""

# %% comments
# plt.close("all")
# %matplotlib qt #plot figure outside console must be typed in console

# %% import packages
# set path to import self written modules
import sys
sys.path.append("C:/TDCRDS/python")

import numpy as np
import os
#from shutil import copyfile 
#import pandas as pd
import numpy.lib.recfunctions as rfn
import matplotlib.pyplot as plt
#import fileinput
import re

from rmfield import rmfield   # self written module to delete redundant files
from modeloutput import modeloutput
import imp
#modeloutput = imp.load_source('modeloutput', 'c:/TDCRDS/Python/modeloutput.py')
from modeloutput2python import modeloutput2python  # written for three output files, hard coded
from makeplots_CRDS import makeplots_CRDS
from makeplots_mr_CRDS import makeplots_mr_CRDS


#%% LOAD CONFIG FILE AND SETTING  
import config_TDCRDS_NPL as config # config file for NPL

# assign variable names without amendment config
list_config = dir(config)
for i_listconfig in range(0,np.size(list_config)):
    if (list_config[i_listconfig] == 'np') | (list_config[i_listconfig][0] == '_'):
        continue
    cmdstr = list_config[i_listconfig] + ' = config.' + list_config[i_listconfig]
    exec(cmdstr)

# %% PATH

# set path_facsim for output files , set by config_TDCRDS_NPL.py file
fac_file_org        = path_facsim + fac_chemistry               #c:/TDCRDS/FACSIM/NOxy_MCM_subset_PANetc_raw.FAC
fac_file_run        = path_facsim + fac_runfile                 # facsimile file to be modified for run #c:/TDCRDS/FACSIM/NOXY.FAC
# time step for facsim run
time_nostep         = int(np.trunc(totalsamplingtime/time_step_facsimile + 0.0/time_step_facsimile)) 

# output format, set by config.py file
maxVariablesinOneFile = np.int(np.floor((72.-22.)/outputformat[0]))  #22 approx char for write..... command

# fixed paremeters
NA              = 6.022e+23    # molecules in one mol
VA              = 22414        # mol volume in mol/cm^3 @ T=273.15 and p=1013.25 hPa
p0              = 1013.25      # norm pressure in mbar
T0              = 273.15       # norm temperature in K
MA              = NA/VA

#%% calculate Molvolume dependent on pressure and temperature

pTa_corr_fac         = p/p0 * T0/(T)          # correction factor for volume flow under ambient conditions
pTreactor_corr_fac   = p/p0 * T0/(Treactor)   # correction factor for volume flow in reactor
pTCRDS_corr_fac      = p/p0 * T0/(TCRDS)      # correction factor for volume flow in instrument

Mambient        = NA/VA * p/p0 * T0/(T)               # correction factor for mol-1 under ambient conditions
Mreactor        = NA/VA * preactor/p0 *T0/(Treactor)  # correction factor for mol-1 in reactor
Msample         = NA/VA * pCRDS/p0 * T0/(TCRDS);      # correction factor for mol-1 in instrument

# %% 
##########    define structure of OUTPUT FILES  ###############################

#*****************************************************************************
# dimension of system, e.g. lengths, flows to be stored
# structured array for output parameters - ***list_dim***
dim_list =[]
for i_listdim in range (0, np.size(list_dim)):
    dim_list.append(eval(list_dim[i_listdim]))   
formatdim_str = ['f8'  for formatdim_str in range(np.size(list_dim))];   
dim = np.array([tuple(dim_list)], dtype={'names': list_dim, 'formats':formatdim_str})

#*****************************************************************************              
#  convert to header and format
for outputfileno in range(1,4):         # three output files, starting with one
    cmdstr1 = '\"%' + str(outputformat[0]) + 's\"' + '%'
    cmdstr2 = 'outputheader'    + str(outputfileno) + '= (outputstring' + str(outputfileno) + '[0])'
    cmdstr3 = 'outputparameter' + str(outputfileno) + ' = outputstring' + str(outputfileno) + '[0]' 
    exec(cmdstr2)
    exec(cmdstr3)
    exec('outputfilelength = np.size(outputstring' + str(outputfileno) + ')')
    del cmdstr1, cmdstr2, cmdstr3 
    for i_header in range(1,outputfilelength):
        cmdstr2 = 'outputheader' + str(outputfileno) + ' = outputheader' + str(outputfileno) + ' + \', \' + (outputstring' + str(outputfileno) + '[i_header])'
        exec(cmdstr2)
        cmdstr3 = 'outputparameter' + str(outputfileno) + ' = outputparameter' + str(outputfileno) + ' + \',\' +  outputstring' + str(outputfileno) + '[i_header]'
        exec(cmdstr3)
    del cmdstr2, cmdstr3, outputfilelength    

#*****************************************************************************
#  Reaction times
# ambient conditions  !!! for slm ,  sensitive to msec?
flowspeed_ambient      = flow_sampletube / pTa_corr_fac    
flowspeed_reactor      = flow_sampletube / pTreactor_corr_fac                        # in cm/s
flowspeed_CRDS         = flow_sampletube / pTCRDS_corr_fac

time_start             = 0;
time_ambient           = length_ambient/(flowspeed_ambient/60/((samplelinediameter_ambient/2)**2 * np.pi))
time_ambient_2         = length_ambient_2/(flowspeed_ambient/60/((samplelinediameter_ambient_2/2)**2 * np.pi))
time_reactor           = length_reactor/(flowspeed_reactor/60/((samplelinediameter_reactor/2)**2 * np.pi))
time_CRDS              = length_CRDS/(flowspeed_CRDS/60/((samplelinediameter_CRDS/2)**2 * np.pi)) + \
                         volumefilter_CRDS/(flowspeed_CRDS/60)

time_tot = time_start + \
           np.repeat(np.reshape(time_ambient,(np.size(Treactor,0),1)),np.size(Treactor,1), axis=1) + \
           np.repeat(np.reshape(time_ambient_2,(np.size(Treactor,0),1)),np.size(Treactor,1), axis=1) + \
           time_reactor + \
           np.repeat(np.reshape(time_CRDS,(np.size(Treactor,0),1)),np.size(Treactor,1), axis=1)


# %% 
#################   FACIM simulation   ########################################

ModelResult_strall = []; ModelResult_allarray = []; param_in_allarray = []; dim_allarray = []; times_allarray = [];
i_reac = 0; i_NO = 0; i_noreactor = 0;

# LOOP over reactor number:
for i_noreactor in range (0,np.size(Treactor,0)):
    #LOOP over reactor temperatures
    for i_reac in range(0,np.size(Treactor,1)): #test # all range(0,np.size(Treactor)):
    
        if np.isnan(Treactor[i_noreactor,i_reac]):
            continue
        
        # structured array for output parameters  - ***list_time***
        time_list =[]
        for i_listtime in range (0, np.size(list_time)):
            try:
                (eval(list_time[i_listtime])[i_noreactor, i_reac])    # flowspeed_reactor is an array
            except:
                try: 
                    (eval(list_time[i_listtime])[i_noreactor])  
                except:
                    time_list.append(eval(list_time[i_listtime]))   
                else:
                    time_list.append(eval(list_time[i_listtime])[i_noreactor])
            else:
                time_list.append(eval(list_time[i_listtime])[i_noreactor,i_reac])   
         
        formattime_str = ['f8'  for formattime_str in range(np.size(list_time))]   
        times = np.array([tuple(time_list)], dtype={'names': list_time, 'formats':formattime_str})
        
    
    # ****************************************************************************    
    # *******         create .fac with times determined above     ****************
    # ****************************************************************************
    # replace placeholder with definitions below to create the run version of .fac
    
        file_handle = open(fac_file_org, 'r') # open the source file and read it
        file_string = file_handle.read()
        file_handle.close()
        
        # create the pattern object. Note the "r". In case you're unfamiliar with Python
        # this is to set the string as raw so we don't have to escape our escape characters
        result  = file_string
        
        # define number of parameters in .fac
        for i_paramfile in range (0,3):
            pattern = re.compile(r'\bloadparam'+ str(i_paramfile+1))  # \b exact match
            x       = np.size(eval('param' + str(i_paramfile+1) + '_list'))
            result  = pattern.sub('PARAMETER <' + str(x) + '> INPARAM'+ str(i_paramfile+1)+';', result)  # do the replace
    
        # initilise concentrations in facsim.fac,
        for i_paramfile in range (0,3):
            if i_paramfile == 0:
                f_M = '';
            else:
                f_M = '*M';
                
            pattern = re.compile(r'\binitilize_concentrations_param'+ str(i_paramfile+1))  # \b exact match 
            cmdstr = ''
            for i_param in range(0,np.size(eval('param' + str(i_paramfile+1) + '_list'))):
                 s = eval('param' + str(i_paramfile+1) +'_list[i_param]')      # remove brackets
                 s = re.sub("[\(\[].*?[\)\]]", "", s)
                 cmdstr = cmdstr + s + ' = INPARAM' + str(i_paramfile+1) + '<' + str(i_param) + '>' + f_M + ';'+"\n" # NO CONCENTRATIONS (not multiplied by M) when paramfile1 (physical parameters, e.g. T, p)
                 del s;
            result  = pattern.sub(cmdstr,result)  # do the replace  
    
        
        # set fac simulation times
        pattern = re.compile(r'\btime_step')  # \b exact match
        x       = time_step_facsimile
        result  = pattern.sub(str(round(x,digits_timefac)), result)  # do the replace
        
        pattern = re.compile(r'\btime_nostep')
        x       = time_nostep  + np.int(0.5/time_step_facsimile) # 1/2 sec extra
        result  = pattern.sub(str(round(x,digits_timefac)), result) 
        # sample tube chemistry started
        pattern = re.compile(r'\btime_start')
        x       = time_start
        result  = pattern.sub(str(round(x,digits_timefac)), result) 
        # reactor (heating)
        pattern = re.compile(r'\btime_reactor')
        x       = time_start + time_ambient[i_noreactor]
        result  = pattern.sub(str(round(x,digits_timefac)), result) 
        # cooling, sample to CRDS 
        pattern = re.compile(r'\btime_CRDS')
        x       = time_start + time_ambient[i_noreactor] + time_reactor[i_noreactor,i_reac]
        result  = pattern.sub(str(round(x,digits_timefac)), result) 
        
        # output parameters incl. header
        pattern = re.compile(r'\bwriteoutputheader1')
        result  = pattern.sub('write 1=7, \"' + outputheader1 + '\" %', result)  
        pattern = re.compile(r'\bwriteoutputparameter1')
        result  = pattern.sub('write 1=7,((E' + str(outputformat[0]) + ',' + str(outputformat[1]) + ')),' + outputparameter1 + ' %', result)   # future automated format   # number 7 is output file
        # output parameters incl. header
        pattern = re.compile(r'\bwriteoutputheader2')
        result  = pattern.sub('write 1=8, \"' + outputheader2 + '\" %', result)  
        pattern = re.compile(r'\bwriteoutputparameter2')
        result  = pattern.sub('write 1=8,((E' + str(outputformat[0]) + ',' + str(outputformat[1]) + ')),' + outputparameter2 + ' %', result)   # future automated format   # number 7 is output file
        # output parameters incl. header
        pattern = re.compile(r'\bwriteoutputheader3')
        result  = pattern.sub('write 1=9, \"' + outputheader3 + '\" %', result)  
        pattern = re.compile(r'\bwriteoutputparameter3')
        result  = pattern.sub('write 1=9,((E' + str(outputformat[0]) + ',' + str(outputformat[1]) + ')),' + outputparameter3 + ' %', result)   # future automated format   # number 7 is output file
        
        # temperatures
        pattern = re.compile(r'\bTemperature_ambient')
        result  = pattern.sub('T =  '   + str(round(T,digits_conc)) + ';' , result)     
        pattern = re.compile(r'\bPressure_ambient')
        result  = pattern.sub('P =  '   + str(round(p,digits_conc)) + ';' , result)  
        pattern = re.compile(r'\bTemperature_reactor')
        result  = pattern.sub('T =  '   + str(round(Treactor[i_noreactor,i_reac],digits_conc)) + ';' , result)     
        pattern = re.compile(r'\bPressure_reactor')
        result  = pattern.sub('P =  '   + str(round(preactor,digits_conc)) + ';' , result)   
        pattern = re.compile(r'\bTemperature_CRDS')
        result  = pattern.sub('T =  '   + str(round(TCRDS,digits_conc)) + ';' , result)     
        pattern = re.compile(r'\bPressure_CRDS')
        result  = pattern.sub('P =  '   + str(round(pCRDS,digits_conc)) + ';' , result)  
        
        f_out = open(fac_file_run, 'w') # write the file
        f_out.write(result)
        f_out.close()
        del result 
     
    # ****************************************************************************    
    # *******         create input files for fac run              ****************
    # ****************************************************************************
        # plt.figure()
        print('Modelrun for Treactor ' + str(i_noreactor+1) +':', Treactor[i_noreactor,i_reac])
        cmdstr_file = 'ModelNitrates_Treactor_' + str(i_noreactor+1) + '_' +str(int(Treactor[i_noreactor, i_reac]))+  'K'
        cmdstr    = path_facsim + cmdstr_file ;
        
        # create input files - written for three inputfiles!!! - could be more generalised in the future, but max 3
        param1_str = (','.join(param1_list)); param2_str = (','.join(param2_list)); param3_str = (','.join(param3_list))   # convert to one string, so that eval command works
        param1 = eval(param1_str); 
        param2 = eval(param2_str); 
        param3 = eval(param3_str);                                    # list for input file
        format1_str = ['f8'  for format1_str in range(np.size(param1_list))] 
        format2_str = ['f8'  for format2_str in range(np.size(param2_list))]    # create format matrix, 64-bit floating point number  
        format3_str = ['f8'  for format3_str in range(np.size(param3_list))] 
        param1_in = np.array([eval(param1_str)], dtype={'names':param1_list,'formats':format1_str})  # create structured array for npy format 
        param2_in = np.array([eval(param2_str)], dtype={'names':param2_list,'formats':format2_str})  
        param3_in = np.array([eval(param3_str)], dtype={'names':param3_list,'formats':format3_str})  
        # create input parameter file for model !!!!!!!!!!!!! check precision in pythpon / numpy !!!! - maximum signs in facsim for input parameters!!!!!
        np.savetxt(path_facsim + "CRDSIn1.asc", np.transpose(param1), fmt="%3.4e",newline=linefeed_PC) #write and save an ascii file with the concentrations #, delimiter="\t") , need to be ascii for facsim
        np.savetxt(path_facsim + "CRDSIn2.asc", np.transpose(param2), fmt="%3.4e",newline=linefeed_PC) #write and save an ascii file with the concentrations #, delimiter="\t")  , need to be ascii for facsim
        np.savetxt(path_facsim + "CRDSIn3.asc", np.transpose(param3), fmt="%3.4e",newline=linefeed_PC) #write and save an ascii file with the concentrations #, delimiter="\t")  , need to be ascii for facsim            
        # save time factors    
        np.savetxt(path_output + cmdstr_file + '_' +'dim.dat', \
                   [length_ambient[i_noreactor],length_reactor,length_CRDS[i_noreactor],flow_sampletube,\
                    flowspeed_ambient, flowspeed_reactor[i_noreactor,i_reac], flowspeed_CRDS,\
                    time_start,time_ambient[i_noreactor], time_reactor[i_noreactor,i_reac], \
                    time_CRDS[i_noreactor], time_tot[i_noreactor,i_reac]], fmt="%3.4e")        
        # in python format
        param_in  = rfn.merge_arrays((param1_in,param2_in, param3_in), flatten = True, usemask = False);  # merge to one structured array	 
        cmdstr_paramin = 'param_in_'  + str(i_noreactor+1) + '_' + str(int(Treactor[i_noreactor,i_reac])) + ' = param_in '
        exec(cmdstr_paramin)
    #    np.save(path_output + cmdstr_file + '_paramin.npy' ,param_in,times);      #  save
        np.save(path_output + cmdstr_file + '_paramin.npy' ,param_in); 
       
    #################### start model run ##########################################
        os.system('"C:\Program Files (x86)\DOSBox-0.74\DOSBox.exe"')     #start model (it reads the ascii file)
    ###############################################################################
    
        # save facsim file for housekeeping, para1 files, result files and times
        modeloutput(cmdstr_file,'', path_facsim, path_output, instrument, fac_runfile) #str(int(Treactor[i_reac]))
        # save in python format
        cmdstr_result = 'ModelResult_' + str(i_noreactor+1) + '_' + str(int(Treactor[i_noreactor,i_reac])) + '=modeloutput2python(cmdstr_file, str(i_noreactor+1),str(int(Treactor[i_noreactor,i_reac])), path_facsim, path_output, instrument )  '
        exec(cmdstr_result)    
           
        plt.figure()
        x= eval('ModelResult_'  + str(i_noreactor+1) + '_' + str(int(Treactor[i_noreactor,i_reac])))
        makeplots_CRDS(x, 1, str(i_noreactor+1),str(int(Treactor[i_noreactor,i_reac])), cmdstr)
       # makeplots_mr_CRDS(x, 1, str(int(Treactor[i_reac])), cmdstr)
        plt.title(cmdstr)
       
        # create one matrix, including parameter in
        cmdstr_dim = 'dim_'  + str(i_noreactor+1) + '_' + str(int(Treactor[i_noreactor,i_reac])) + ' = dim '
        exec(cmdstr_dim)   
        # attach temperature to times, total time dependent on temperature
        x = np.shape(times.dtype.names)
        novar = x[0] # total number of variables
        for i_novar in range(0,novar):
            times = rfn.rename_fields(times, {times.dtype.names[i_novar]:times.dtype.names[i_novar]+'_' + str(i_noreactor+1) + '_' +str(int(Treactor[i_noreactor,i_reac]))}) 
      
        ModelResult_strall.append('ModelResult_'  + str(i_noreactor+1) + '_' + str(int(Treactor[i_noreactor,i_reac])))# list Variables Modelresult
        ModelResult_allarray.append(eval('ModelResult_'  + str(i_noreactor+1) + '_' + str(int(Treactor[i_noreactor,i_reac]))))
        times_allarray.append(times)  
         
    
# %% ###################    save data      ####################################

# in one .npy file
ModelResult_all = rfn.merge_arrays(ModelResult_allarray, flatten = True, usemask = False);  # merge to one structured array
times_all       = rfn.merge_arrays(times_allarray, flatten = True, usemask = False); 

#  save input and output values  
cmdstr_file = 'ModelNitrates_Treactor_total'
np.savez(path_output + cmdstr_file + '_all' ,ModelResult_all = ModelResult_all, param_in = param_in, dim = dim,  times=times_all, Treactor = Treactor, modelstep=time_step_facsimile);    
       
del ModelResult_all
del times_all

