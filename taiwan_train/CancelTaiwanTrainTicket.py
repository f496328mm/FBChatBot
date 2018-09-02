#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 00:24:09 2018

@author: root
"""

import sys
import os
from selenium import webdriver
import pymysql
import pandas as pd
from datetime import datetime
path = os.listdir('/home')[0]
sys.path.append('/home/'+ path +'/github')
from FBChatBot import Chatbot2Sql, MessageFun
from FBKey import host, port, user ,password ,database
#sys.path.append('/home/linsam/github/fb_chatbot/taiwan_train')

#def get_success_ticket_info(sender_id):

def connect():
    conn = ( pymysql.connect(host = host,
                             port = port,
                             user = user,
                             password = password,
                             database = database,
                             charset = "utf8") )  
    cursor = conn.cursor() #创建游标
    return conn,cursor

def update(success_ticket_info):
    sender_id = success_ticket_info['sender_id'][0]
    orderCode = success_ticket_info['orderCode'][0]
    
    conn,cursor = connect()

    sql_text = ( "UPDATE `OrderTaiwanTrainTicketStatus` SET "+
                 "`status` = 'cancel' WHERE `sender_id` = '"+str(sender_id)+"' "+
                 "AND `status` = 'success' AND `compute_code` = '"+str(orderCode)+"'; " )
    cursor.execute( sql_text )
    conn.commit()
    conn.close()

def load(sender_id):
    # sender_id = str( 1668007999939769 )
    conn,cursor = connect()
    
    sql_text = ( "SELECT * FROM `OrderTaiwanTrainTicketStatus` WHERE `sender_id` = "+ str( sender_id ) +
                " AND `status` = 'success'" )
    cursor.execute( sql_text )
    # 抓所有的 data
    message_data = cursor.fetchall()
    success_ticket_info = pd.DataFrame()
    if len(message_data)==0:
        123
        return 0,0
    elif len(message_data)==1:
        message_data = pd.DataFrame({
                'user_id' : message_data[0][0],
                'orderCode' : message_data[0][1],
                'train_no' : message_data[0][2],
                'from_station' : message_data[0][3],
                'start_date' : message_data[0][4],
                'start_time' : message_data[0][5],
                'to_station' : message_data[0][6],
                'sender_id' : message_data[0][7],
                'status' : message_data[0][8],
                'datetime' : message_data[0][9],
                'finaltime' : message_data[0][11]
                },index = [0] )
        success_ticket_info = success_ticket_info.append(message_data)        
        
    elif len(message_data)>1:
        
        now = datetime.now()
        tem = []
        for i in range(len(message_data)):# d = message_data[2]
            if now < message_data[i][11]:
                tem = pd.DataFrame({
                'user_id' : message_data[i][0],
                'orderCode' : message_data[i][1],
                'train_no' : message_data[i][2],
                'from_station' : message_data[i][3],
                'start_date' : message_data[i][4],
                'start_time' : message_data[i][5],
                'to_station' : message_data[i][6],
                'sender_id' : message_data[i][7],
                'status' : message_data[i][8],
                'datetime' : message_data[i][9],
                'finaltime' : message_data[i][11]
                },index = [i] )
                success_ticket_info = success_ticket_info.append(tem)
            else:
                
                sql_text = "UPDATE `OrderTaiwanTrainTicketStatus` SET `status` = 'cancel' WHERE `OrderTaiwanTrainTicketStatus`.`id` = "
                sql_text = sql_text+ str( message_data[i][10] ) +';'
                cursor.execute( sql_text )
    else: 
        123
    #print(message_data)
    conn.close()
    
    return success_ticket_info,1
    
def ask_for_which_ticket_to_cancel(success_ticket_info,sender_id,recipient_id):
    text = '請問要取消以下哪張票'
    MessageFun.send_message(sender_id, text)  
    Chatbot2Sql.update(text,sender_id,recipient_id,'server')    
    index = 0
    for i in success_ticket_info.index:# 
        start_date = success_ticket_info.T.loc['start_date'][i]
        start_date = str( start_date.month ) + '/' + str( start_date.day )
        
        start_time = success_ticket_info.T.loc['start_time'][i]
        hour = str( start_time.seconds//3600 )
        minute = str( ( start_time.seconds//60 )%60 )
        if( len(minute) == 1 ):
            minute = '0'+minute
        start_time = hour+':'+minute
        
        from_station = success_ticket_info.T.loc['from_station'][i]
        to_station = success_ticket_info.T.loc['to_station'][i]
        finaltime = success_ticket_info.T.loc['finaltime'][i]
        finaltime = str( finaltime.month ) + '/' + str( finaltime.day ) + ' 24:00'
        
        text = str(index+1)+': '+start_date+' '+start_time+' ' + from_station +' → ' + to_station+', 最後取票時間 : ' + finaltime
        print( text )
        MessageFun.send_message(sender_id, text )
        index = index+1
        

def cancel_main(success_ticket_info,sender_id,recipient_id):
    
    driver = webdriver.Firefox()
    driver.get('http://railway.hinet.net/ccancel.htm')
    driver.find_element_by_id("personId").send_keys(success_ticket_info['user_id'][0])
    driver.find_element_by_id("orderCode").send_keys(success_ticket_info['orderCode'][0])
    # click
    inputs = driver.find_element_by_xpath('/html/body/form/table/tbody/tr[4]/td[2]/button')
    inputs.click()
    try:
    # click
        inputs = driver.find_element_by_xpath('/html/body/form/button')
        inputs.click()
    except:
        123
    update(success_ticket_info)
    text = driver.find_element_by_class_name('orange02').text
    driver.quit()
    
    MessageFun.send_message(sender_id, text)  
    Chatbot2Sql.update(text,sender_id,recipient_id,'server')

def main(sender_id,recipient_id,i):
    # go to index
    success_ticket_info,bo = load(sender_id)
    
    if bo == 0:
        text = '所有訂票已取消'
        MessageFun.send_message(sender_id, text)  
        Chatbot2Sql.update(text,sender_id,recipient_id,'server')
        return 1
    
    # ask for which ticket to cancel 
    if ( len(success_ticket_info)>1 and i != 0 ):
        i=i-1
        
        success_ticket_info = pd.DataFrame( success_ticket_info.iloc[i] ).T
        success_ticket_info.index = [0]
        cancel_main(success_ticket_info,sender_id,recipient_id)
        
    elif ( len(success_ticket_info) ==1 and i == 0 ):
        #type(success_ticket_info)
        # success_ticket_info = pd.DataFrame( success_ticket_info.iloc[0] )
        success_ticket_info.index = [0]
        cancel_main(success_ticket_info,sender_id,recipient_id)
    else:
        
        ask_for_which_ticket_to_cancel(success_ticket_info,sender_id,recipient_id)
        
        #success_ticket_info = ask_for_which_ticket_to_cancel(success_ticket_info,sender_id,recipient_id)
    return 1







