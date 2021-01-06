# -*- coding: utf-8 -*-
"""

Created on Thu Aug 15 09:16:58 2019
@author: cb13

"""

#%%
# import modules
import numpy as np

#%%     USER CONFIGURATION

###############################################################################
# set linefeed depending on operating system
linefeed_PC = '\n'
###############################################################################

###############################################################################
# set path_facsim for output files
fac_runfile         = 'NOXY.FAC'                                # executable for facsim run (modified by this script, based on fac_file_org)
instrument          = 'CRDS'                                    # amendment for copied files (in modeloutput)
path_facsim         = 'c:/TDCRDS/FACSIM/'                       # need to be defined in dosbox config!!!!
fac_chemistry       = 'NOxy_MCM_subset_PANetc_raw.FAC'          # facsimile file to be modified for run 'NOxy_MCM_subset_PANetc_raw.FAC'
path_output         = 'c:/TDCRDS/FACSIM/output/'                # facsimile file to be modified for run
###############################################################################

###############################################################################
# set model parameters
time_step_facsimile = 0.005                                     # time step for model output
digits_timefac      = 4                                         # number of digits for model input (time in sec)
digits_conc         = 16                                        # number of digits for model input (conc in mixing rato) #16
totalsamplingtime   = 10;                                       # in sec
###############################################################################

###############################################################################
# input parameters for model - max 72 char (limited by facsim), max 13
# needs to match parameter notation in facsim
# in list at least two parameters needed, otherwise strange seperation
param1_list = 'T','p','Treactor[i_noreactor, i_reac]','TCRDS', 'WVOH';   # fixed, need to match facsim
param2_list = 'NO[i_NO]','NO2','H2O','O3','H2O2','HONO','HNO3', 'HO2NO2';
param3_list = 'C4H8','CH3O2NO2','CHEX','PAA','AA', 'N2O5';  

###############################################################################
# choose output variables and their format !!! be aware that one line in facsimile can only have 72 chars
# please do not choose redundant variables for the outputstring or modeloutput2python will crash
outputformat = (13,5)  # changed: problems when negative sign, then no space between two columns and genfromtxt gets a problem (12,6) (size, digits)
outputstring1 = ['TIME','T', 'P', 'M', 'OH', 'HO2', 'O3'] #,'RO2', 'O3', 'CH3CO3' 'HO2' ,'dummy'
outputstring2 = ['TIME', 'NO', 'NO2',  'HO2NO2', 'HONO', 'HNO3'] # 'N2O5' ,'NO3',
outputstring3 = ['TIME','C4H8','CHEX', 'NO3','N2O5'] # , 'Nitrat', 'NitratAN', 'NitratPN','NitratPAN' 'CH3O2NO2', 'IPN',
##############################################################################

##############################################################################
# define output files containing physical parameters
list_time = ['flowspeed_ambient', 'flowspeed_reactor','flowspeed_CRDS', 
             'time_start', 'time_ambient', 'time_reactor', 'time_CRDS','time_tot'] # flow speedreactor is an array             
list_dim = ['length_ambient_20','length_ambient_750','length_reactor', 'length_CRDS_20', 'length_CRDS_750', 
            'flow_sampletube', 'samplelinediameter_ambient', 'samplelinediameter_reactor', 'samplelinediameter_CRDS', 'volumefilter_CRDS']
##############################################################################
            
###############################################################################
# define dimensions of TD Design
flow_sampletube      = 1000.00        # in cm^3 / min, mass flow 

length_20            = 80.00          #  length of 1/8 tubing from cylinder to three way valve
length_750           = length_20      #  length of 1/8 tubing from cylinder to three way valve
length_20_2          = 20.00          #  1/4 tubing from 3 way valve to 20° metal tubing ""virtual reactor""								
length_750_2         = length_20_2    #  1/4 tubing from 3 way valve to 750° quartz tubing reactor
length_ambient_20    = length_20/10  + length_20_2/10     #currently not needed
length_ambient_750   = length_750/10 + length_750_2/10    #currently not needed
length_ambient       = np.array([length_20, length_750])
length_ambient_2     = np.array([length_20_2, length_750_2])

length_reactor       = 50.   # in cm; length of reactor (heated)

length_CRDS_750      =	1500.00 / 10	# in cm	1/4"		length from 700° reactor to instrument						
length_CRDS_20       =	1500.00 / 10	# in cm	1/4"		length from 20° reactor to instrument	

length_CRDS          = np.array([length_CRDS_20, length_CRDS_750])   # in cm; length from reactor to instrument

samplelinediameter_ambient   = 1/8*2.54;                  #in cm 
samplelinediameter_ambient_2 = 1/4*2.54;                  #in cm
samplelinediameter_reactor   = 1/4*2.54;                  #in cm 
samplelinediameter_CRDS      = 1/8*2.54;                  #in cm   
samplelinediameter_filter    = np.sqrt(56000*4/np.pi/100) #Diameter: 26.7mm = np.sqrt(56000*4/np.pi/100) to calculate length of 100mm back to the decired Volume of 56ccm #TBC by NPL										      

volumefilter_CRDS    = 56 # in cm^3     #to be confirmed with Dave
###############################################################################

###############################################################################
# define parameters to run model
T_K        = 273.15       # convert to K; fixed, dont change

p          = 1000.        # ambient pressure in mbar 
preactor   = p            # pressure in reactor in mbar
pCRDS      = p            # pressure in front of instrument in mbar
T          = 20 + T_K                                                     # ambient temperature in K
Treactor   = np.array([[20, np.nan, np.nan, np.nan, np.nan, np.nan],           # ambient channel temperatures -> needs to be same dimension as other channels
                       [600, np.nan, np.nan, np.nan, np.nan, np.nan]],  # heated channel temperatures -> needs to be same dimension as other channels
                            dtype='float64')+T_K                          # reactor temperatures in K as array to be looped #20+T0, 100+T0, 200+T0, 300+T0, 400+T0, 500+T0, 650+T0 #np.array([25+T0,750+T0])
TCRDS      = 43 + T_K                                                     # Temperature in instrument
###############################################################################

###############################################################################
# initial concentrations for facsim run, in mixing ratios (unitless)
H2O        = 0.00
#HO2       = 0.0;
O3         = 0.0e-9                 #10.0e-9
H2O2       = 0.0e-9                 #1.0e-9 
#OH        = 0.0;

NO         = [1.000e-12]             #1.000e-9
NO2        = 9973.9722e-9                 #5.0e-9
HONO       = 0
HNO3       = 980.806e-9                 #1.0e-9 
HO2NO2     = 1.0e-12 
PAN        = 1.0e-12                #500.0e-12
CH3O2NO2   = 0.0
IC3H7NO3   = 1.0e-12                #100.0e-12 
PAA        = 0.0e-9                    #1.0e-9 
AA         = 0.0e-9                 #1.0e-9 
N2O5       = 0.0

WVOH       = 8.0                # wall loss for OH in sec-1

C4H8       = 0.0e-9
CHEX       = 735.6e-9
#C3H6      = 0.0e-8
#HCHO      = 0.0;
#CH3CO3    = 0;
#CH3CO2    = 0;
#CH3O2     = 0;
#HCHO      = 0;
#CH3OOH    = 0;
#CH3CHO    = 0;
#CH3CO     = 0;
#acetone   = 0;
#CH2COOOH  = 0;
#CH2CO2    = 0;
#IPO       = 0;
###############################################################################

###############################################################################
##############    END OF INPUT PARAMETERS   ###################################
###############################################################################
