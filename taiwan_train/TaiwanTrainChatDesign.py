#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 20:55:49 2018

@author: root
"""

import re
from fbmq import Attachment, Page
import sys
import os
path = os.listdir('/home')[0]
sys.path.append('/home/'+ path +'/github')
from FBKey import host
from FBChatBot import Chatbot2Sql, MessageFun, tem_function
from FBChatBot.taiwan_train import TaiwanTrainRemainTicketSql_fun, search_remain_ticket
from FBChatBot.taiwan_train import order_ticket, TaiwanTrainRemainTicketSql, CancelTaiwanTrainTicket
from FBChatBot.taiwan_train.search_remain_ticket import station_set
from FBChatBot.taiwan_train.MyTicket import MyTicket

ssl_dir = '/etc/letsencrypt/live/linsam.servebeer.com/'

page_access_token = MessageFun.page_access_token
page = Page(page_access_token)
#--------------------------------------------------------------
 
def chat(message_text,sender_id,recipient_id):
    
    '''if TaiwanTrainRemainTicketSql_fun.bool_sender_id_first(sender_id) != 1:
        print('no first')
    elif TaiwanTrainRemainTicketSql_fun.bool_sender_id_first(sender_id) == 1:
        text = '歡迎使用台鐵訂票機器人，\n以下是訂票範例'
        MessageFun.send_message(sender_id, text)
        Chatbot2Sql.update(text,sender_id,recipient_id,'server')
        
        url = "http://114.34.138.146/train_ticket_png/"
        
        image_url = url + 'train_example.png'
        page.send(sender_id, Attachment.Image(image_url) )          
        
        return 1'''
    
    
    if '取消訂票' in message_text :
        print('cancel')
        MessageFun.send_message(sender_id, '請稍等')
        try:
            # sender_id = '1928838193857487'; recipient_id = '1833003783417644'
            CancelTaiwanTrainTicket.main(sender_id,recipient_id,0)
            return 1
        except:
            return 0    
    elif( tem_function.text_in_set(
            Chatbot2Sql.get_last_message( sender_id , 1 , 'server',recipient_id),
            '請問要取消以下哪張票') ):
        print('cancel mulit ticket')
        if re.search('[0-9]',message_text):
            try:
                message_text = re.search('[0-9]',message_text)[0]
                i = int(message_text)   
                CancelTaiwanTrainTicket.main(sender_id,recipient_id,i)
                
                return 1
            except:
                123
                return 0
    elif '我的車票' in message_text or '我的票' in message_text :
        print('my ticket')
        try:
            MT = MyTicket(sender_id,recipient_id)
            MT.load_data()
            MT.chatdesign()
            
            return 1
        except:
            123
            return 0
    elif '訂火車票' in message_text or '訂票' in message_text :
        TaiwanTrainRemainTicketSql.clear(sender_id)
        text = "歡迎使用訂票服務, "
        MessageFun.send_message(sender_id, text)
        Chatbot2Sql.update(text,sender_id,recipient_id,'server')
        
        if TaiwanTrainRemainTicketSql_fun.load_user_id(sender_id) == 0:
            text = "第一次使用，請先輸入身分證字號\n( 只會在該系統使用，不會進行其他用途 )"
            MessageFun.send_message(sender_id, text)
            Chatbot2Sql.update(text,sender_id,recipient_id,'server')
            return 1
        else:
            text = '請輸入訂票資訊'
            MessageFun.send_message(sender_id, text)
            Chatbot2Sql.update(text,sender_id,recipient_id,'server')
            return 1
    elif tem_function.text_in_set( Chatbot2Sql.get_last_message( sender_id , 1 ,'server', recipient_id),'身分證字號' ):
        # message_text = '我的身分證是u121726696'
        user_id = re.findall("[a-zA-Z][0-9]{9}",message_text)
        if(len(user_id)==1):
            text = '請輸入訂票資訊'
            MessageFun.send_message(sender_id, '請輸入訂票資訊')
            Chatbot2Sql.update(text,sender_id,recipient_id,'server')
            
            TaiwanTrainRemainTicketSql_fun.update_user_id(sender_id,user_id)
            return 1
            
        elif(len(user_id)==0):
            print('error')
            MessageFun.send_message(sender_id,'輸入錯誤,請重新輸入')
            return 1
            
        # sender_id = str( 1668007999939769 );recipient_id = str( 1581238015253059 )
    elif( tem_function.text_in_set( Chatbot2Sql.get_last_message( sender_id , 1 , 'server',recipient_id) , '請輸入訂票資訊') and 
          tem_function.set_in_text( station_set , message_text ) ):
        print('begin to order_ticket_by_remain_ticket')
        MessageFun.send_message(sender_id, '請稍等')
        # message_text = '花蓮到台北 3/4 下午5點'
        tem = MessageFun.message2order_info(message_text)
        #tem = message2order_info(message_text)
        order_info = tem.main()
        user_id = TaiwanTrainRemainTicketSql_fun.load_user_id(sender_id)

        # begin selenium
        text = search_remain_ticket.main(order_info,user_id,sender_id)
        if text == '該時段、該車種已訂票額滿':
            print('out')
            MessageFun.send_message(sender_id, 'sorry, '+text)  
            Chatbot2Sql.update(text,sender_id,recipient_id,'server')
            return 1
        else:
            ticket_info = text
        
        text1 = '以下時段有車'
        MessageFun.send_message(sender_id, text1)  

        for i in range( len(ticket_info.set) ):# 
            from_time = ticket_info.set.T.loc['from_time'][i]
            to_time = ticket_info.set.T.loc['to_time'][i]
            #cost = cost_time(from_time,to_time)
            
            from_time = from_time.split(' ')[1]
            to_time = to_time.split(' ')[1]
            
            kinds = ticket_info.set.T.loc['others'][i]
            text = str(i+1)+':'+from_time +' → '+to_time+' '+ kinds
            print( text )
            MessageFun.send_message(sender_id, text )
            
        text2 = '請問你想要哪個時段：輸入數字(1 or 2 ...)'
        MessageFun.send_message(sender_id, text2)  
        Chatbot2Sql.update(text1+text2,sender_id,recipient_id,'server')
        
        return 1
    # order ticket 
    elif( tem_function.text_in_set(
            Chatbot2Sql.get_last_message( sender_id , 2 , 'server',recipient_id),
            '以下時段有車請問你想要哪個時段：輸入數字(1 or 2 ...)') ):
        #print('final')
        MessageFun.send_message(sender_id, '請稍等')
        if TaiwanTrainRemainTicketSql_fun.check_input_is_train_no(message_text,sender_id) ==1:
            try:
                message_text = re.search('[0-9]',message_text)[0]
                i = str(int(message_text))
                
                png_name = order_ticket.main(sender_id,i)
                url = "http://" + host + "/train_ticket_png/"
                
                image_url = url + png_name
                page.send(sender_id, Attachment.Image(image_url) )  
                
                TaiwanTrainRemainTicketSql.clear(sender_id)
                Chatbot2Sql.update('order ticket success',sender_id,recipient_id,'server')
                Chatbot2Sql.update('order ticket success',sender_id,recipient_id,'server')
                #print('final ok')
                return 1
            except:
                #print('000')
                return 0
        elif( TaiwanTrainRemainTicketSql_fun.check_input_is_train_no(message_text,sender_id) ==0 and
             'order ticket success' not in Chatbot2Sql.get_last_message( sender_id , 1 , 'server',recipient_id) ):
            text = '輸入錯誤, 如再次錯誤, 將跳出訂票系統'
            MessageFun.send_message(sender_id, text)  
            Chatbot2Sql.update(text,sender_id,recipient_id,'server')
            return 1
        

    return 0

