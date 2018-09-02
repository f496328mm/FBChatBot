#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 18:01:24 2018

"""

from selenium import webdriver
import cv2
import pandas as pd
import re
import time
from PIL import Image
import pymysql
import sys
import os
path = os.listdir('/home')[0]
sys.path.append('/home/'+ path +'/github')
from VerificationCode2Text import verification_code2text
from FBKey import host, port, user ,password ,database

station_set = ['台東','鹿野','瑞源','關山','池上','富里','東竹','東里','玉里',
 '瑞穗','富源','光復','萬榮','鳳林','南平','豐田','壽豐','志學','吉安','花蓮',
 '北埔','新城','崇德','和仁','和平','南澳','東澳','蘇澳','蘇澳新','冬山','羅東',
 '二結','宜蘭','四城','礁溪','頭城','龜山','大溪','大里','褔隆','貢寮','雙溪' '牡丹',
 '三貂嶺','猴硐','瑞芳','四腳亭','基隆','八堵','七堵','汐止','南港','松山','台北',
 '萬華','板橋','樹林','山佳','鶯歌','桃園','內壢','中壢','埔心','楊梅','富岡',
 '湖口','新豐','竹北','新竹','竹南','談文','大山','後龍','白沙屯','新埔','通霄',
 '苑裡','日南','大甲','台中港','清水','沙鹿','龍井', '大肚','追分','造橋','苗栗',
 '銅鑼','三義','泰安','后里','豐原','潭子','台中','烏日','新烏日','成功','彰化',
 '花壇','員林','社頭','田中','二水','林內','斗六','斗南','大林','民雄','嘉義',
 '水上','後壁','新營','林鳳營','隆田','拔林','善化','南科','新市', '永康','台南',
 '保安','中洲','大湖','路竹','岡山','橋頭','楠梓','新左營','左營','高雄','鳳山',
 '後庄','九曲堂','屏東','西勢','竹田','潮州','南州','林邊','佳冬','枋寮','加祿',
 '大武','瀧溪','金崙','太麻里','知本','康樂','大慶','十分','平溪','內灣','車埕']

#============================================================================================================
# self = go2index()
# self.go(url)
class go2index:
    
    def __init__(self):
        
        #self.driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver')
        self.driver = webdriver.Firefox()
        # webdriver.Firefox()
        #webdriver.Chrome()

    def go(self,url):# url = 'http://railway1.hinet.net/csearch.htm'
        self.driver.get(url)
#============================================================================================================
# self = keyinfo
class KeyInfo:
    
    def __init__(self,order_info,user_id,driver):
        self.order_info = order_info
        self.user_id = user_id
        self.driver = driver

    def get_start_time(self):
        start_time = self.order_info['start_time'][0]
        if(start_time <= 4): 
            start_time = 1; 
        else: 
            start_time = start_time-4
        
        self.start_time = start_time
    #------------------------------------------------------------------------------
    # select tostation, fromstation ...etc
    #------------------------------------------------------------------------------
    def sel_info_botton(self,var_text,botton_text):
        # get select botton
        sel_botton = webdriver.support.ui.Select(
                    self.driver.find_element_by_name(botton_text))                    
        tem_text = str( self.order_info[var_text][0] )
        
        for sel in sel_botton.options: 
            if tem_text in sel.get_attribute('text') :
                sel_botton.select_by_visible_text((sel.get_attribute('text')))
                break
    def sel_start_date(self):
        # change 1/1 to 01/01
        tem = self.order_info['start_date'][0]
        try:
            tem_date = time.strptime(tem, "%Y-%m-%d")
        except:
            tem_date = time.strptime(tem, "%Y/%m/%d")
        
        year    = str( tem_date.tm_year )
        month   = str( tem_date.tm_mon )
        if(int(month)<10):month = '0'+month
        day     = str( tem_date.tm_mday )
        if(int(day)<10):day = '0'+day
        
        self.order_info['start_date'][0] = str(year)+'/'+month+'/'+day
        self.sel_info_botton('start_date','getin_date')
        
    def sel_start_time(self):#start_time = 0
        self.get_start_time()
        
        start_time_text = str(self.start_time)+':00'
        if self.start_time+8<24 :
            end_time_text = str(self.start_time+8)+':00'
        else:
            end_time_text = str(23)+':59'
        
        self.input_var_to_select(start_time_text,'getin_start_dtime')
        self.input_var_to_select(end_time_text,'getin_end_dtime')
         
    def input_var_to_select(self,var,botton_text):
        sel_botton = webdriver.support.ui.Select(
                    self.driver.find_element_by_name(botton_text))                    
        # loop select, if select.text == keyword, break 
        for sel in sel_botton.options: 
            bo = re.search(var,sel.get_attribute('text'))
            if( bo ):         
                sel_botton.select_by_visible_text((sel.get_attribute('text')))
                break        
        
    def run(self):
        self.driver.find_element_by_name("person_id").send_keys(self.user_id)# key user id
        self.sel_start_date()# select start date
        # 特定車次有 一般座 and 桌型座, 需點選才會出現, 以下進行點選動作
        self.sel_info_botton('from_station','from_station')# select from station
        self.sel_info_botton('to_station','to_station')
        
        self.sel_start_time()# select start time
        self.sel_info_botton('ticket_amount','order_qty_str')# select ticket amount
        self.sel_info_botton('to_station','order_qty_str')# select to station
        
        inputs = self.driver.find_element_by_xpath('/html/body/form/table/tbody/tr[8]/td[2]/button')# get bottom
        inputs.submit()# submit bottom
#============================================================================================================
# driver = keyinfo.driver
# self = keyvcode
class KeyVcode:
    
    def __init__(self,driver):    
        self.driver = driver

    def save_driver_screen(self):
        
        bo=1
        while(bo):
            try:
                im = self.driver.find_element_by_id('idRandomPic')
                if( im.size['width']==200 and im.size['height']==60 ):
                    self.driver.save_screenshot(self.output_image_name)                
                    bo=0
                elif( im.size['width']==210 and im.size['height']==70 ):
                    self.driver.save_screenshot(self.output_image_name)                
                    bo=0
                else:
                    print(im.size)
            except:
                123
        #----------------------------------------------------
        def take_vcode_image(im,output_image_name):
            # get vcode obj l,r,t,d
            
            left = im.location['x']
            right = int( left + im.size['width'] )
            top = im.location['y']
            down = int( top + im.size['height'] )
            
            image = Image.open(output_image_name)
            image = image.crop((left,top,right,down))
            
            return image
        #----------------------------------------------------
        image = take_vcode_image(im,self.output_image_name)
        image = image.resize((200,60))
        image.save(self.output_image_name)
    
        self.image = cv2.imread(self.output_image_name, cv2.IMREAD_COLOR)
        #plt.imshow(self.image)

    def keys_verification_code(self):
        image_text = verification_code2text.main(self.image)
        #print(image_text)
        inputElement = self.driver.find_element_by_id('randInput')
        inputElement.send_keys(image_text)
        self.image_text = image_text
        
        inputs = self.driver.find_element_by_xpath('/html/body/form/table/tbody/tr[3]/td[2]/div/button')
        inputs.click()
        '''
    def save_success_vcode_image(self):

        image = Image.open(self.output_image_name)
        
        tem = '/home/linsam/project/fb_chatbot/verification_code2text'
        tem = '/home/'+ path +'/github/'
        success_image_name = tem + '/success_vcode/'+str(self.image_text)+'.png'
        
        image.save(success_image_name)
        # img id="idRandomPic" alt="驗證碼"
        '''
    def rekeys_ver_code(self):
        bo=1
        while(bo):
            try:
                text = self.driver.find_element_by_class_name('orange02')
                bo=0
            except:
                123        
        if( text.text == '亂數驗證失敗' ):
            bottom = self.driver.find_element_by_xpath('/html/body/form/p[3]/input')
            bottom.click()
        elif len(self.driver.find_elements_by_class_name('orange02'))>1:
            if( '該時段、該車種已訂票額滿' in self.driver.find_elements_by_class_name('orange02')[1].text ):
                self.bo_verification = 1
                self.bo_remain = 0
                print(0)
        else:
            #self.save_success_vcode_image()
            self.bo_verification = 1
            self.bo_remain = 1
            print(1)

                
    def main(self):
        self.bo_verification = 0
        #index = 0
        while( self.bo_verification == 0 ):
            # save screen image
            #tem = '/home/linsam/project/fb_chatbot/verification_code2text'
            tem = '/home/'+ path +'/github/VerificationCode2Text'
            self.output_image_name = tem + '/vcode_image/'+str( time.time() )+'.png'
            #if index==0: time.sleep(2)
            #else: time.sleep(1)
            self.save_driver_screen()
            
            # key verification code
            self.keys_verification_code()
            self.rekeys_ver_code()
            #index = 1
#============================================================================================================
class GetRemainInfo:
    
    def __init__(self,driver):    
        self.driver = driver
    
    def get_ticket_set(self):
    
        def split_ticket_info(text):
            info_set = text.split(' ')
            
            from_time = re.findall(r'[[0-9]*/[0-9]*/[0-9]* [0-9]*:[0-9]*]*',text)[0]
            to_time = re.findall(r'[[0-9]*/[0-9]*/[0-9]* [0-9]*:[0-9]*]*',text)[1]
           
            train_number    = info_set[0]
            train_kinds     = info_set[1]
            from_station    = info_set[4]
            to_station      = info_set[5]
            if( len(info_set)==9 ):
                others          = info_set[8]
            elif( len(info_set)<9 ):
                others          = ''
    
            ticket_info = pd.DataFrame(
                        {'train_number':train_number,
                         'train_kinds':train_kinds,
                         'from_time':from_time,
                         'from_station':from_station,
                         'to_station':to_station,
                         'to_time':to_time,
                         'others':others}, 
                         index=[0])
            return ticket_info
    #-----------------------------------------------------------------------------
    # craw ticket info
        tem = self.driver.find_elements_by_class_name('text_10p') 
        
        # init
        ticket_info_set = pd.DataFrame()
        # split ticket info
        for i in range(len(tem)):
            #print(i)
            text = tem[i].text
            ticket_info = split_ticket_info(text)
            ticket_info_set = ticket_info_set.append(ticket_info) 
        
        ticket_info_set.index = range(0,ticket_info_set.shape[0],1)
        self.set = ticket_info_set
#============================================================================================================
#============================================================================================================        
class sql:
    
    def connect(self):
        conn = ( pymysql.connect(host = host,
                             port = port,
                             user = user,
                             password = password,
                             database = database,
                             charset = "utf8") )  
        cursor = conn.cursor()
        return conn,cursor
    
    def update(self,ticket_info_set,sender_id,ticket_amount):
        
        conn,cursor = self.connect()
        ticket_amount = str(ticket_amount)
        
        for i in range(len(ticket_info_set)):
            #print(ticket_info_set)
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
    
    def clear(self,sender_id):
        
        conn,cursor = self.connect()
        cursor.execute("DELETE FROM `remain_train_ticket_info` WHERE `sender_id` LIKE '"+sender_id+"'")
        
        conn.commit()
        conn.close()
    
    def load(self,sender_id,i):
        
        conn,cursor = self.connect()
        sql_text = ( "SELECT * FROM `remain_train_ticket_info` WHERE `i` = "+ str( i ) +
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
#============================================================================================================
def main(order_info,user_id,sender_id):
    index = go2index()
    index.go('http://railway1.hinet.net/csearch.htm')
    keyinfo = KeyInfo(order_info,user_id,index.driver)
    keyinfo.run()

    keyvcode = KeyVcode(keyinfo.driver)
    keyvcode.main()

    if keyvcode.bo_remain == 1:
        ticket_info = GetRemainInfo(keyvcode.driver)
        ticket_info.get_ticket_set()

        upload2sql = sql()
        upload2sql.update(ticket_info_set = ticket_info.set,
                          sender_id = sender_id,
                          ticket_amount = order_info['ticket_amount'][0])
        keyvcode.driver.quit()
        return ticket_info
    elif keyvcode.bo_remain == 0:
        keyvcode.driver.quit()
        text = '該時段、該車種已訂票額滿'
        return text




