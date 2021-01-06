# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 15:40:06 2020

@author: cb13
"""

import allantools as allan
import numpy as np
57
import tkinter as tk
from tk import 
ledialog
#Imports packages required for code to run. AllanTools is required to calculate the Allanvariance. Numpy is required for reading the source 
le and storing the data in arrays.Tkinter is required for the 
le prompt.
gui window = tk.Tk()
gui window.withdraw()
#This part of the code disables the blank Tkinter window that loads when an instanceof it is called, preventing a blank window from being present for as long as the code isrunning.
class Allanasis:
def init (self, compound, location, column):
self.compound = compound #The name of the compound that's being analysed
self.location = location #The location of the 
le that the data resides in
self.column = int(column) #The column within the 
le your required data is in.
def dataset load(self):

le for analysis = open(self.location)
#Loads the required 
le. This is at the start of the code to minimise time wasted
if the 
le fails to load.
start cell=int(input('Start of range (row number) for '+self.compound+'?'))-3
end cell=int(input('End of range (row number) for '+self.compound+'?'))-3
#This locates the range of the data that is to be analysed. The -3 is present as
the 
rst two rows are skipped as they contain the header and column titles which aren't
necessary, and the 
rst value is value 0.
column data=np.loadtxt(
le for analysis, '
oat', '#', None, None, 2, self.column,
False, 0)
#Loads the designated column. The variables mean the following: (File to be
analysed, type of variable in output, ignored values being with this character, notrrequired,
not required, number of rows to skip, which column to use, not required, not required)
58
column data = column data[start cell:end cell]
#Shortens data to the range speci
ed by start cell and end cell
dataset to analyse = allan.Dataset(column data, rate=1/38, data type='freq')
#Converts data from a numpy array to a dataset that is recognised by AllanTools
return dataset to analyse
#Returns the AllanTools dataset as a variable when this function is called
def dataset allanvariance(self):
dataset = self.dataset load()
#Loads the dataset determined by the function above
dataset.compute("adev")
#Analyses the dataset with one of several possible function (See AllanTools documentation
for details on each)
allan plot = allan.Plot()
#Converts the analysed dataset into a plottable format
allan plot.plot(dataset, errorbars=True, grid=True)
#Plots the data
allan plot.show()
#Shows the plot

le location = 
ledialog.askopen
lename(title="Select File")
#Opens a prompt to choose the required 
le
compound name = input('What compound are you analysing?')
#Asks the name of the compound your analysing is
desired column = input('What column is the required data in?:')
#Asks what column the data you want is in
No2 = Allanasis(compound name, 
le location, desired column)
#De
nes the compound, 
le location and column location of a desired analysis
No2.dataset allanvariance()
#calls the previously de
ned analysis