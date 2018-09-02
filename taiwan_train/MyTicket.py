

import sys
import os
import numpy as np
import pandas as pd
path = os.listdir('/home')[0]
sys.path.append('/home/'+ path +'/github')
from FBChatBot.taiwan_train import TaiwanTrainRemainTicketSql_fun
from FBChatBot import Chatbot2Sql, MessageFun
from FBKey import host, user ,password ,database

'''
sender_id = str( 2033192286715644 )
recipient_id = str( 1833003783417644 )
self = MyTicket(sender_id,recipient_id)
data = self.load_data()

'''

class MyTicket:
    
    def __init__(self,sender_id,recipient_id):
        self.data_name = 'OrderTaiwanTrainTicketStatus'
        self.sender_id = sender_id
        self.recipient_id = recipient_id
   
    def load_data(self):
        
        self.data = pd.DataFrame()
        
        tem_col_name = TaiwanTrainRemainTicketSql_fun.execute_sql2(
                host = host,
                user = user,
                password = password,
                database = database,
                sql_text = 'SHOW columns FROM '+ self.data_name )
        
        col_name = []
        for i in range(len(tem_col_name)):
            col_name.append( tem_col_name[i][0] )
        col_name.remove('id')    
    
        for col in col_name:
            text = 'select ' + col + ' from ' + self.data_name
            text = text + " WHERE `sender_id` =  "+str(self.sender_id)
            text = text + " AND `status` = 'success' " 
            
            tem = TaiwanTrainRemainTicketSql_fun.execute_sql2(
                    host = host,
                    user = user,
                    password = password,
                    database = database,
                    sql_text = text )
            
            tem = np.concatenate(tem, axis=0)
            tem = pd.DataFrame(tem)
            #if len(tem) 
            self.data[col] = tem.T.iloc[0]
        
        #return self.data
        

    def chatdesign(self):
        text = '您的車票如下'
        MessageFun.send_message(self.sender_id, text)  
        Chatbot2Sql.update(text,self.sender_id,self.recipient_id,'server')    
        index = 0
        for i in range(len(self.data)):
            start_date = self.data.T.loc['start_date'][i]
            start_date = str( start_date.month ) + '/' + str( start_date.day )
            
            start_time = self.data.T.loc['start_time'][i]
            hour = str( start_time.seconds//3600 )
            minute = str( ( start_time.seconds//60 )%60 )
            if( len(minute) == 1 ):
                minute = '0'+minute
            start_time = hour+':'+minute
            
            from_station = self.data.T.loc['from_station'][i]
            to_station = self.data.T.loc['to_station'][i]
            finaltime = self.data.T.loc['finaltime'][i]
            finaltime = str( finaltime.month ) + '/' + str( finaltime.day ) + ' 24:00'
            
            text = str(index+1)+': '+start_date+' '+start_time+' ' + from_station +' → ' + to_station+', 最後取票時間 : ' + finaltime
            #print( text )
            
            MessageFun.send_message(self.sender_id, text )
            index = index+1    
            
            
            
            
            
            
            