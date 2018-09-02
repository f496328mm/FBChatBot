#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 16:45:14 2018

@author: linsam
"""


import sys
import pandas as pd
import numpy as np
import pymysql
import re
import datetime 
import os
path = os.listdir('/home')[0]
sys.path.append('/home/'+ path +'/github')
from FBKey import host, port, user ,password ,database
from FBChatBot.taiwan_train import TaiwanTrainRemainTicketSql

def execute_sql2(host,user,password,database,sql_text):
    
    conn = ( pymysql.connect(host = host,# SQL IP
                     port = port,
                     user = user,
                     password = password,
                     database = database,  
                     charset="utf8") )  
                             
    cursor = conn.cursor()    
    # sql_text = "SELECT * FROM `_0050_TW` ORDER BY `Date` DESC LIMIT 1"
    try:   
        cursor.execute(sql_text)
        data = cursor.fetchall()
        conn.close()
        return data
    except:
        conn.close()
        return ''
    
#--------------------------------------------------------------
def update_user_id(sender_id,user_id):# user_id='123'
    conn = ( pymysql.connect(host = host,# SQL IP
                     port = port,
                     user = user,
                     password = password,
                     database = database,  
                     charset="utf8") )  
    cursor = conn.cursor() 
    ( cursor.execute('insert into '+ 'identity' +'(sender_id,identity)' +' values(%s,%s)', 
              (sender_id,user_id
               ) ) )
    
    conn.commit()
    conn.close()
    
#--------------------------------------------------------------
#--------------------------------------------------------------
def load_user_id(sender_id):
    conn = ( pymysql.connect(host = host,# SQL IP
                     port = port,
                     user = user,
                     password = password,
                     database = database,  
                     charset="utf8") )  
    cursor = conn.cursor()                         
    cursor.execute("SELECT * FROM `identity` WHERE `sender_id` LIKE '"+sender_id+"'")
    message_data = cursor.fetchone()
    # close connect
    conn.close()
    
    try:
        user_id = message_data[2]
        return user_id
    except:
        return 0

#---------------------------------------
class message2order_info:
    
    def __init__(self,message_text):
        self.message_text = message_text
        from FBChatBot.search_remain_ticket import station_set
        self.station_set = station_set
        
    def take_start_date(self):

        now = datetime.datetime.now()
        date = re.search('[0-9]*/[0-9]*',self.message_text).group(0)
        if len(date)!=0:
            123
        elif len(date)==0:
            date = re.search('[0-9]*-[0-9]*',self.message_text).group(0)
        date = str(now.year)+'/'+date
        
        return date
#---------------------------------------------------------------
    def take_start_time(self):
        # 早上 下午 晚上 凌晨 半夜 中午
        time_text = ['早上','中午','下午','晚上',
                     '[a,A].[m,M]',
                     '[a,A][m,M]',
                     '[p,P][m,M]',
                     '[p,P].[m,M]']
        add_time_set = [0,12,12,12,0,0,12,12]
        bo = 1
        i=0
        while(bo):
            if re.search( time_text[i] ,self.message_text):
                self.message_text = self.message_text.replace( time_text[i] ,'')
                add_time = add_time_set[i]
                bo = 0
            i = i+1
   
        if re.search('[0-9]*:[0-9]*',self.message_text):
            start_time = re.search('[0-9]*:[0-9]*',self.message_text).group(0)
        elif re.search('[0-9]*點',self.message_text):
            start_time = re.search('[0-9]*點',self.message_text).group(0)
            start_time = int( start_time.replace('點','') )
            
        start_time = start_time+add_time

        return start_time
#---------------------------------------------------------------
    def take_from_to_station(self):

        bo1 = 1
        bo2 = 1
        i = 0
        while(bo1+bo2):
            if self.station_set[i] + '到' in self.message_text:
                #print(station_set[i])
                from_station = self.station_set[i]
                bo1 = 0
            if '到' + self.station_set[i] in self.message_text:
                #print(station_set[i])
                to_station = self.station_set[i]
                bo2 = 0
            i = i + 1
        return from_station,to_station
#---------------------------------------------------------------
    def main(self):
        date = self.take_start_date()
        self.message_text = self.message_text.replace(date,'')
        
        start_time = self.take_start_time()
        from_station,to_station = self.take_from_to_station()
        
        order_info = {'to_station':to_station,
                      'start_date':date,
                      'from_station':from_station,
                      'start_time':start_time,
                      'ticket_amount':1}
        order_info = pd.DataFrame(order_info,index = [0])
        
        return order_info
    
#-------------------------------------------------------------
def check_input_is_train_no(message_text,sender_id):
    try:
        # message_text = '5'
        message_text = re.search('[0-9]',message_text)[0]
        index = str(int(message_text))
        #order_ticket_info = TaiwanTrainRemainTicketInfo.load(sender_id,index)
        TaiwanTrainRemainTicketSql.load(sender_id,index)
        return 1
    except:
        return 0
    
def cost_time(from_time,to_time):
    f = datetime.datetime.strptime(from_time,"%Y/%m/%d %H:%M")
    t = datetime.datetime.strptime(to_time,"%Y/%m/%d %H:%M")
    cost = (t-f).seconds
    hour = int(cost/3600)
    minute = int( (cost-hour*3600)/60 )
    cost = str(hour)+'小時'+str(minute)+'分'
    
    return cost

def bool_sender_id_first(sender_id):
    
    conn = ( pymysql.connect(host = host,# SQL IP
                     port = 3306,
                     user = user,
                     password = password,
                     database = database,  
                     charset="utf8") )  
    cursor = conn.cursor()                         
    cursor.execute("SELECT DISTINCT `sender_id` FROM `message_data`  ")
    tem = cursor.fetchall()
    # close connect
    conn.close()
    
    sender_id_class = []
    for d in tem:
        sender_id_class.append( d[0] )

    sender_id_class = {'sender_id_class' : sender_id_class}
        
    sender_id_class = pd.DataFrame(sender_id_class)
    
    value = np.sum( sender_id == sender_id_class )[0]
    
    return value
    
    
    


