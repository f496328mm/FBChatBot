# -*- coding: utf-8 -*-
"""
Created on Thu May 10 09:09:33 2018

@author: root
"""

import sys
import os
path = os.listdir('/home')[0]
sys.path.append('/home/'+ path +'/github')
from chatterbot import ChatBot

def retrainchatbot():
    chatbot = ChatBot('Ron Obvious',trainer = 'chatterbot.trainers.ChatterBotCorpusTrainer')
    chatbot.train("chatterbot.corpus.english")# 基於英文的自動學習套件
    chatbot.train("chatterbot.corpus.chinese")# 載入(簡體)中文的基本語言庫
    chatbot.train("chatterbot.corpus.chinese.greetings")# 載入(簡體)中文的問候語言庫
    chatbot.train("chatterbot.corpus.chinese.conversations")# 載入(簡體)中文的對話語言庫
    
    
    
retrainchatbot()
    
    