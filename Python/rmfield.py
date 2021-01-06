# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 19:24:04 2018

@author: dkubisti
"""

# %% functions
def rmfield ( a, *fieldnames_to_remove ):
    return a[ [ name for name in a.dtype.names if name not in fieldnames_to_remove ] ]