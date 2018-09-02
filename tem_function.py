#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 20:50:46 2018

@author: root
"""



def set_in_text(myset,text):
    # myset = ['第一次使用，請先輸入身分證字號'] 
    # text = '身分證字號'
    for i in range(len(myset)):
        if( myset[i] in text ): 
            return 1
    return 0

def text_in_set(myset,text):
    # myset = ['第一次使用，請先輸入身分證字號'] 
    # text = '身分證字號'
    for i in range(len(myset)):
        if( text in myset[i] ): 
            return 1
    return 0
    









