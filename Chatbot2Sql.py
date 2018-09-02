#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 17:56:01 2018

@author: root
"""

import datetime
import re
import sys
import os
path = os.listdir('/home')[0]
sys.path.append('/home/'+ path +'/github')
from FBKey import host, port, user ,password ,database

def connect():
    conn = ( pymysql.connect(host = host,
                             port = port,
                             user = user,
                             password = password,
                             database = database,
                             charset = "utf8") )  
    cursor = conn.cursor() 
    return conn,cursor
#-----------------------------------------
# update message to sql
#-----------------------------------------
def update(message_text,sender_id,recipient_id,user):
    
    conn,cursor = connect()
    
    tem = str( datetime.datetime.now() )
    time = re.split('\.',tem)[0]
    # 將 data 匯入 test file 中, test file 是由 create_ptt_dataset 建立, 作為範例使用
    ( cursor.execute('insert into '+ 'message_data' +
    '(sender_id,recipient_id,user,message_text,datetime)' +
    ' values(%s,%s,%s,%s,%s)', 
              (sender_id,
               recipient_id,
               user,
               message_text,
               time
               ) ) )
    
    conn.commit()
    conn.close()
#--------------------------------------------------------------
# get last message
#--------------------------------------------------------------
def get_last_message(sender_id,amount,user,recipient_id):# sql_var_name = 'recipient_id' ; user = 'server'; amount = 1

    conn,cursor = connect()
    sql_text = "SELECT * FROM `message_data` WHERE `sender_id` LIKE '"+sender_id+"' AND `recipient_id` LIKE '"+recipient_id+"' AND `user` LIKE '"+user+"'"
    cursor.execute(sql_text)

    message_data = cursor.fetchall()
    # close connect
    conn.close()
    
    message_text = []
    for d in message_data:
        message_text.append(  d[3] )

    value = message_text[ (len(message_text)-amount):len(message_text) ]
    
    return value
    
import pymysql

def create_dataset():  
    conn = ( pymysql.connect(host = host,
                             port = port,
                             user = user,
                             password = password,
                             database = database,
                             charset = "utf8") )  
    c=conn.cursor()
    sql_name = 'OrderTaiwanTrainTicketStatus'
    sql_string = ( 'create table ' + sql_name + 
                  '( identity text(100), compute_code text(100), train_no text(100),'+
                  'from_station text(100),start_date text(100),start_time text(100),'  +
                  'to_station text(100),'  +
                  '  sender_id text(100), status text(100), datetime text(100), finaltime text(100))' )
    
    c.execute( sql_string )
    c.execute('ALTER TABLE `'+ sql_name +'` ADD id BIGINT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY;')
    c.close() 
    conn.close()
#--------------------------------------------------------------
    
    
    
    
    
