

import sys
import os
from flask import Flask, request
from chatterbot import ChatBot
import opencc
path = os.listdir('/home')[0]
sys.path.append('/home/'+ path +'/github')
from FBChatBot import Chatbot2Sql, tem_function, MessageFun
from FBChatBot.taiwan_train import TaiwanTrainChatDesign


#-----------------------------------------
# load chatbot library
# it will create db.sqlite3
#-----------------------------------------
def chat_fun():
    chatbot = ChatBot('Ron Obvious',trainer = 'chatterbot.trainers.ChatterBotCorpusTrainer')
    chatbot.train("chatterbot.corpus.english")# 基於英文的自動學習套件
    chatbot.train("chatterbot.corpus.chinese")# 載入(簡體)中文的基本語言庫
    chatbot.train("chatterbot.corpus.chinese.greetings")# 載入(簡體)中文的問候語言庫
    chatbot.train("chatterbot.corpus.chinese.conversations")# 載入(簡體)中文的對話語言庫
# main                    
main = Flask(__name__)

# test1
ssl_dir = '/etc/letsencrypt/live/linsam.servebeer.com/'
#ssl_dir = '/home/linsam/project/linsam.servebeer.com/'
verify_token = 'access_token'

#--------------------------------------------------------------
@main.route('/', methods=['GET'])
def verify():
    global verify_token
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == verify_token:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    
    return "Hello world", 200
#------------------------------------------------------
# chatbot main
#------------------------------------------------------    
@main.route('/', methods=['POST'])
def webhook():
    #--------------------------------------------------------------
    # chatbot auto response
    data = request.get_json()#
    entry = data["entry"]
    messaging_event = entry[0]['messaging'][0]
    #--------------------------------------------------------------
    def chatbot_tallk(message_text):
        #message_text = 'hi'
        chatbot = ChatBot('Ron Obvious',trainer = 'chatterbot.trainers.ChatterBotCorpusTrainer')
        return_text = chatbot.get_response(message_text)
        return_text = str(return_text)
        
        return_text2 = opencc.convert(return_text, config='mix2zht.ini')
    
        return return_text2
    #----------------------------------------------------------------
    try:
        message_text,sender_id,recipient_id = MessageFun.get_user_message()
        print(message_text)
        print(recipient_id)
        print(sender_id)
        #-----------------------------------------------------------------------------------
        try:
            if len(Chatbot2Sql.get_last_message( sender_id , 1 , 'client',recipient_id)) ==0:
                Chatbot2Sql.update(message_text,sender_id,recipient_id,'client')
            elif message_text != Chatbot2Sql.get_last_message( sender_id , 1 , 'client',recipient_id)[0]:
                #print(123)
                Chatbot2Sql.update(message_text,sender_id,recipient_id,'client')
                
            elif message_text == Chatbot2Sql.get_last_message( sender_id , 1 , 'client',recipient_id)[0]:
                123
                return "ok", 200
            elif '該時段、該車種已訂票額滿' == Chatbot2Sql.get_last_message( sender_id , 1 , 'server',recipient_id)[0]:
                123
                return "ok", 200            
        except:
            print(456)
        #-----------------------------------------------------------------------------------
        #print('go to TaiwanTrainChatDesign')
        end_set = ['退出','離開','quit','end','bye','掰','88']
        if tem_function.set_in_text( end_set , message_text):
            text = "bye bye"
            MessageFun.send_message(sender_id, text)
            Chatbot2Sql.update(text,sender_id,recipient_id,'server')
            
        elif '你是誰' in message_text:
            text = "你好，我是聊天機器人，還在開發中，目前可接受訂票的服務"
            MessageFun.send_message(sender_id, text)
            #Chatbot2Sql.update(text,sender_id,recipient_id,'server')
        # project 1
        elif TaiwanTrainChatDesign.chat(message_text,sender_id,recipient_id):
            print(999)
            print('---------------------------------------------------')
            return "ok", 200
        else:
            print(2)
            try:
                print(3)
                return_text = chatbot_tallk(message_text)
                MessageFun.send_message(sender_id, return_text)
                #Chatbot2Sql.update(return_text,sender_id,recipient_id,'server')
                return "ok", 200
            except:
                print(4)
                return_text = "i don't know"
                MessageFun.send_message(sender_id, return_text)
                #Chatbot2Sql.update(return_text,sender_id,recipient_id,'server')
                return "ok", 200
            
        if messaging_event.get("delivery"):  # delivery confirmation
            print("delivery")
            pass

        if messaging_event.get("optin"):  # optin confirmation
            print("optin")
            pass

        if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
            print("postback")
            pass
        
        return "ok", 200
    except:
        123
        return "ok", 200

ssl_content = (
    ssl_dir + 'fullchain.pem',
    ssl_dir + 'privkey.pem',
)
#main.run(debug = False, host = '0.0.0.0', port = 5442, ssl_context=ssl_content)
# main
main.run(debug = False, host = '0.0.0.0', port = 5443, ssl_context=ssl_content)
#main.run(debug = False, host = '0.0.0.0', port = 5443)
#app.run(debug = False)
# test
# main.run(debug = False, host = '0.0.0.0', port = 5441, ssl_context=ssl_content)


