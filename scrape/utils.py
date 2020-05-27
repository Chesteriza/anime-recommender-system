# -*- coding: utf-8 -*-
"""
Created on Thu May 14 00:11:31 2020

@author: chest
"""

def flatlist(li):
    '''
    To flatten list into a string 
    li: refers to a list (Output of Selector Function)
    '''
    flatten = ", ".join(li)
    return flatten

def checklist(li, ind):
    '''
    li: refers to a list (Output of Selector Function)
    ind: refers to the index of the output
    Some results could be empty, to indicate such value with "None"
    '''
    if len(li) == 0:
        return('None')
    else:
        return(li[ind])

def removeNew(stri):
    output = re.sub(r"\n", "", stri)
    output = re.sub(r'\s+', ' ', output)
    output = output.strip()
    return output

def convertNumber(stri):
    output = re.sub(r",", "", stri)
    return int(output)