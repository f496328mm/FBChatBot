#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 20:33:01 2018

"""

import sys
import os
import time
import pymysql
import re
import datetime
path = os.listdir('/home')[0]
sys.path.append('/home/'+ path +'/github')
from FBChatBot.taiwan_train import search_remain_ticket
from VerificationCode2Text import verification_code2text
from FBKey import host, port, user ,password ,database
# order_ticket
#===================================================================================
class KeyInfo(search_remain_ticket.KeyInfo):
    # train_num = 222
    '''def __init__(self,order_info,user_id,driver):
        self.order_info = order_info
        self.user_id = user_id
        self.driver = driver'''
        
    def load_user_id(sender_id):

        conn = ( pymysql.connect(host = host,
                             port = port,
                             user = user,
                             password = password,
                             database = database,
                             charset = "utf8") )  
        cursor = conn.cursor()                         
        cursor.execute("SELECT * FROM `identity` WHERE `sender_id` LIKE '"+sender_id+"'")
        # 抓所有的 data
        message_data = cursor.fetchone()
        # close connect
        conn.close()
        
        try:
            user_id = message_data[2]
            return user_id
        except:
            return 0  
        
    def key_train_num(self):#start_time = 0
        train_num = self.order_info['train_no'][0]
        id_text = self.driver.find_element_by_name("train_no")
        id_text.send_keys(train_num)        
        
    def run(self):
        self.driver.find_element_by_name("person_id").send_keys(self.user_id)# key user id
        self.sel_start_date()
        self.sel_info_botton('from_station','from_station')
        self.sel_info_botton('to_station','to_station')
        self.key_train_num()
        # some time, it is 一般座
        # but some time it is 一般座 and 桌型座, 需點選才會出現, 以下進行點選動作
        try:
            self.sel_info_botton('ticket_amount','to_station')
            self.sel_info_botton('to_station','to_station')
            self.sel_info_botton('ticket_amount','n_order_qty_str')
        except:
            self.sel_info_botton('ticket_amount','to_station')
            self.sel_info_botton('to_station','to_station')
            self.sel_info_botton('ticket_amount','order_qty_str')
        
        inputs = self.driver.find_element_by_xpath('/html/body/div/div[3]/div/form/div/div[14]/button')    
        inputs.submit()# *********        
#===================================================================================
class KeyVcode(search_remain_ticket.KeyVcode):
    
    def keys_verification_code(self):
        image_text = verification_code2text.main(self.image)

        inputElement = self.driver.find_element_by_id('randInput')
        inputElement.send_keys(image_text)

        inputs = self.driver.find_element_by_xpath('//*[@id="sbutton"]')
        inputs.click()
        #inputs.submit()# *********
        
    def rekeys_ver_code(self):
        try:
            text = self.driver.find_element_by_class_name('alert-danger')
        except:
            self.bo_verification = 1
            return 0
        if( '亂數驗證失敗' in text.text ):
            bottom = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/form/button')
            bottom.click()
        else:
            self.save_success_vcode_image()
            self.bo_verification = 1
#===================================================================================
def save_success_image(sender_id,keyvcode):
    
    png_name = str(sender_id) + '_' + str(time.time()) + '.png'
    output_image_name = '/var/www/html/train_ticket_png/' + png_name
    keyvcode.driver.save_screenshot(output_image_name)
    keyvcode.driver.quit()
    
    return png_name

def update_remain_ticket_info(keyvcode,order_info):
    driver = keyvcode.driver
    compute_code = driver.find_element_by_id('spanOrderCode').text
    tem = str( datetime.datetime.now() )
    time = re.split('\.',tem)[0]
    identity = KeyInfo.load_user_id(order_info['sender_id'][0])
    
    
    tem = time.split(' ')[0]
    tem = tem.replace('-','/')
    # if start date == today
    if order_info['start_date'][0] == tem:
        final_take_ticket_time = time.split(' ')[0]+' 23:59'
    #if time
    else:
        tem = driver.find_elements_by_class_name('text-danger')
        final_take_ticket_time = tem[len(tem)-1].text
        final_take_ticket_time = final_take_ticket_time.split(' ')[0]+' 23:59'
    
    #datetime.strptime('23:59','%H:%M')

    conn = ( pymysql.connect(host = host,
                             port = port,
                             user = user,
                             password = password,
                             database = database,
                             charset = "utf8") )  
    cursor = conn.cursor() 
    
    
    ( cursor.execute('insert into '+ 'OrderTaiwanTrainTicketStatus' +
                     '(identity, compute_code,train_no,from_station,to_station,start_date,start_time,sender_id,status,datetime,finaltime)' +
                     ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
              (identity,
               compute_code,
               order_info['train_no'][0],
               order_info['from_station'][0],
               order_info['to_station'][0],
               order_info['start_date'][0],
               order_info['start_time'][0],
               order_info['sender_id'][0],
               'success',
               time,
               final_take_ticket_time) ) )
    
    conn.commit()
    conn.close()
#-------------------------------------------------------------  
# sender_id = str( 1668007999939769 );i=1
def main(sender_id,i):
    
    #print('go2index')
    index = search_remain_ticket.go2index()
    index.go('http://railway.hinet.net/Foreign/TW/etno1.html')
    #print('loadsql')
    order_info = search_remain_ticket.sql()
    order_info = order_info.load(sender_id,i)
    #print('keyinfo')
    keyinfo = KeyInfo(order_info,
                      KeyInfo.load_user_id(sender_id),
                      index.driver)
    keyinfo.run()
    #print('keyvcode')
    keyvcode = KeyVcode(keyinfo.driver)
    keyvcode.main()
    update_remain_ticket_info(keyvcode,order_info)
    #print('returnimage')
    png_name = save_success_image(sender_id,keyvcode)
    
    return png_name







