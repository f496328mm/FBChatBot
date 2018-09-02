#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 21:13:52 2018

@author: root
"""
import pymysql
import pandas as pd
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
    cursor = conn.cursor() #创建游标
    return conn,cursor

def update(ticket_info_set,sender_id,ticket_amount):
    
    conn,cursor = connect()
    
    ticket_amount = str(ticket_amount)
    for i in range(len(ticket_info_set)):
        print(ticket_info_set)
        train_no = ticket_info_set['train_number'][i]
        from_station = ticket_info_set['from_station'][i]
        to_station = ticket_info_set['to_station'][i]
        
        tem = ticket_info_set['from_time'][i]
        start_date = re.search('[0-9]*/[0-9]*/[0-9]*',tem)[0]
        start_time = re.search('[0-9]*:[0-9]*',tem)[0]

        ( cursor.execute('insert into '+ 'remain_train_ticket_info' +
                         '(i,train_no,from_station,to_station,start_date,start_time,ticket_amount,sender_id)' +
                         ' values(%s,%s,%s,%s,%s,%s,%s,%s)', 
                  (i+1,train_no,from_station,to_station,start_date,start_time,ticket_amount,sender_id
                   ) ) )
    
    conn.commit()
    conn.close()

def clear(sender_id):
    
    conn,cursor = connect()
    cursor.execute("DELETE FROM `remain_train_ticket_info` WHERE `sender_id` LIKE '"+sender_id+"'")
    
    conn.commit()
    conn.close()

def load(sender_id,index):
    
    conn,cursor = connect()
    sql_text = ( "SELECT * FROM `remain_train_ticket_info` WHERE `i` = "+ index +
                " AND `sender_id` LIKE '"+sender_id+"'" )
    cursor.execute( sql_text )
    # 抓所有的 data
    message_data = cursor.fetchone()
    #print(message_data)
    conn.close()
        
    order_ticket_info = {
        'train_no' : message_data[1],
        'from_station' : message_data[2],
        'start_date' : message_data[3],
        'start_time' : message_data[4],
        'ticket_amount' : message_data[5],
        'to_station' : message_data[6],
        'sender_id' : message_data[7]
        }
    
    order_ticket_info = pd.DataFrame(order_ticket_info,index = [0])
    
    return order_ticket_info 



    
