#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 21:00:13 2018

@author: root
"""
from flask import request
import json
import requests
import pandas as pd
import re
import datetime
import sys
import os
path = os.listdir('/home')[0]
sys.path.append('/home/'+ path +'/github')

#page_access_token = 'EAAX3kDNUZCgoBABnGGO8oAvcRCmpMymsTnE15cZC5oJ7x8zsbKaXAewGIeBAX2vUc9fyqSOMKSKnhc92rjCYZCppSKCOZBrsiYVZAlLHAEvMRx8RuoQhS4fII7qP4xegIyAAhdaTCSzlRt2MQZAIDkXxcNGypcZAaZC1dWBe0MPR78ALtOQtYZCoV'
page_access_token = 'EAACflswCTuwBAE5oVZA0waQ9IiywZAaZAZC8PjuEUHCRZCbFLtn05cvv32kR2HaojAuZBkk8xLPAhW31ZAlz2yX3JJmbo8T2siisjmOmZCsN9hkXMvmN3W2JfuUrNSnVQZBu4uX1xA9JmeJ1tvY6W1goVt3YnT198TZAXZAPcAbz8x51hoyx3dwLNNA'

def get_user_message():
    data = request.get_json()#
    log(data,'client')  # you may not want to log every incoming message in production, but it's good for testing
    #print(data)
    entry = data["entry"]
    messaging_event = entry[0]['messaging'][0]
    
    message_text = messaging_event["message"]["text"]  # the message's text
    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    #print(message_text)
    
    return message_text,sender_id,recipient_id    
#------------------------------------------------------
# send message to fb user
#------------------------------------------------------
def send_message(recipient_id, message_text):
    global page_access_token
    log("sending message to " + recipient_id + ": " + message_text,'server')

    params = { "access_token": page_access_token }
    headers = { "Content-Type": "application/json" }
    data = json.dumps({
        "recipient": { "id": recipient_id },
        "message": { "text": message_text }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)    
        

def log(message,user ): 
    def message2dataframe(message):
        text            = message['entry'][0]['messaging'][0]['message']['text']
        recipient_id    = message['entry'][0]['messaging'][0]['recipient']['id']
        sender_id       = message['entry'][0]['messaging'][0]['sender']['id']
        timestamp       = message['entry'][0]['messaging'][0]['timestamp']
    
        data = {'text':text,
                'recipient_id':recipient_id,
                'sender_id':sender_id,
                'timestamp':timestamp
                }
        data = pd.DataFrame(data, index=[0])
        return data
    #----------------------------------------------------------------    
    try:
        if(user == 'client'):
            data = message2dataframe(message)
            print('====================client====================')
            print('client_id = '+ data.sender_id[0] )# user messenger 
            print('client message = '+ data.text[0]  )
            
        elif(user == 'server'):
            print('==================server====================')
            print(str(message))# user messenger 
    except:
        123
    sys.stdout.flush()  
    
#-----------------------------------------------------------------------
'''
message_text = '花蓮到台北 後天 下午5點'
message_text = '花蓮到台北 下禮拜5 下午5點'
self = message2order_info(message_text)
order_info = self.main()
order_info
'''
class message2order_info:
    
    def __init__(self,message_text):
        self.message_text = message_text
        #sys.path.append('/home/linsam/project/fb_chatbot/taiwan_train')
        from FBChatBot.taiwan_train.search_remain_ticket import station_set
        self.station_set = station_set
        
    def take_start_date(self):
        
        def week_fun(text):
            #text = '下星期5'
            weekday_text = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'日':7,'天':7}
            for tem in ['一','二','三','四','五','六','日','天','七']:
                text = text.replace(tem,str(weekday_text.get(tem) ))   
                
            weekday_value = int( re.sub('[下]{0,1}[星期禮拜]','',text) )

            now_week = datetime.datetime.now().weekday() +1# because monday is 0
            if now_week == 0 : now_week = 7
            
            delta = weekday_value - now_week
            
            month = datetime.datetime.now().month
            day = datetime.datetime.now().day+delta
            if '下' in text: day = day+7
            
            date = str(month) +'/'+str(day)
            return date
        #----------------------------------------------------------
        now = datetime.datetime.now()

        if re.search('[0-9]*/[0-9]*',self.message_text):
            date = re.search('[0-9]*/[0-9]*',self.message_text).group(0)
            
        elif  re.search('[0-9]*-[0-9]*',self.message_text):
            date = re.search('[0-9]*-[0-9]*',self.message_text).group(0)
            date = date.replace('-','/')
            
        elif re.search('[下]{0,1}[星期禮拜]+[一二三四五六七日天0-9]{1,}',self.message_text):
            date = re.search('[下]{0,1}[星期禮拜]+[一二三四五六七日天0-9]{1,}',self.message_text).group(0)
            date = week_fun(date)
            
        elif re.search('今天',self.message_text):
            month = datetime.datetime.now().month
            day = datetime.datetime.now().day + 0
            date = str(month) +'/'+str(day) 
            
        elif re.search('明天',self.message_text):
            month = datetime.datetime.now().month
            day = datetime.datetime.now().day + 1
            date = str(month) +'/'+str(day)
            
        elif re.search('後天',self.message_text):
            month = datetime.datetime.now().month
            day = datetime.datetime.now().day + 2
            date = str(month) +'/'+str(day)
            
        elif re.search('大後天',self.message_text):
            month = datetime.datetime.now().month
            day = datetime.datetime.now().day + 3
            date = str(month) +'/'+str(day)
            
        #----------------------------------------------------------
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
    

