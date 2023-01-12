# -*- coding: utf-8 -*-

#版本1.0
import os
import requests
import json
import re

import botpy
from botpy import logging

from botpy.message import DirectMessage
from botpy.message import Message
from botpy.ext.cog_yaml import read

#---------配置---------

url = "https://yuanshen.mihoyogames.top:22102/opencommand/api" #此地址需要带端口和结尾的/opencommand/api

console_token = "aOPf!in*R5N!1#ZbNz8+O@6NZq+WO=c&"#填写控制台的token，可在opencommand处看到教程

console_token_mode = 2 #使用控制台执行命令的身份组权限 1-全体成员 2-管理员 4-频道创建者 5-子频道管理员

console_token_use = True #允许频道主等身份组使用控制台执行命令，默认开启

#----------------------



usertoken = {"null":"null"}

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")


    async def on_at_message_create(self, message: Message):
        message.content = message.content[23:]
        #/帮助命令
        if("/帮助" in message.content ):
                    backw = "本机器人由啊这.制作\n服务端需要先安装opencommand插件\n以下是本机器人的使用帮助\n1.先进入游戏\n使用/绑定 uid 命令\n2.进入游戏，查看机器人发送的验证码\n3.使用/验证 验证码 命令绑定uid\n4.使用! 以玩家身份执行gc的命令 使用# 以控制台身份执行gc的命令"


        #/状态命令
        elif("/状态" in message.content ):
                    data = {"action": "online"}
                    x = requests.post(url, json=data,verify=False)
                    online = json.loads(x.text)
                    online_data = online["data"]
                    player_list = online_data["playerList"]
                    backw = "当前服务器在线人数为" + str(online_data["count"] )
                    if(online_data["count"] > 0):
                        if(online_data["count"] <= 20):
                            backw = backw +"\n在线玩家为：" + " ｜ ".join(player_list)
                        else:
                            backw = backw + "\n在线玩家过多，不进行展示"
                    else:
                        backw = backw +""

        #绑定uid
        elif("/绑定 " in message.content):
            #提取uid
            player_uid = message.content.replace('/绑定','')
            player_uid = player_uid.replace(' ','')
            if(player_uid == ""):
                player_uid ="null"
            if(player_uid.isdecimal() == True):
                #请求验证码
                player_uid = int(player_uid)
                data = {"action": "sendCode","data" : player_uid}
                x = requests.post(url, json=data,verify=False)
                print(x.text)
                uid_back = json.loads(x.text)
                uid_check = uid_back["message"]

                if(uid_check == "Player Not Found."):
                    backw = "绑定失败，uid为" + str(player_uid) +"的玩家不在线或不存在"                        
                
                elif(uid_check =="Success"):
                    usertoken[message.author.id] = uid_back["data"]
                    backw = "请查看发送至游戏内的验证码并使用\n/验证 验证码 进行验证操作"

                else:
                    backw = "出现错误，请寻找管理员获取帮助\n" + x.text


            else:
                backw = "错误，uid：" + player_uid + "中含有非数字内容"



        #验证码
        elif("/验证 " in message.content ):
            #提取验证码
            player_check_input = message.content.replace('/验证 ','')
            player_check_input = player_check_input.replace(' ','')
            #列表player_cheak的第0项为验证码 第1项为token
            print(player_check_input)
            if(player_check_input == ""):
                player_check_input ="傻逼填的空的"

            if(player_check_input.isdecimal() == True):

                #验证验证码
                if(usertoken.get(message.author.id, "null") != "null"):
                    data = { "action" : "verify" , "data" : int(player_check_input) , "token" : usertoken.get(message.author.id, "null") }
                    x = requests.post(url, json=data,verify=False)
                    print(x.text)

                    uid_check_feedback = (json.loads(x.text))["retcode"]
                    print(player_check_input)
                    #失败了（
                    if(int(uid_check_feedback) == 400):
                        backw = "绑定失败，验证码错误"
                    
                    #成功了）
                    elif(int(uid_check_feedback) == 200):
                        backw = "绑定成功！您现在可以执行命令了" 

                    #不知道是什么的傻逼报错
                    else:
                        backw = "错误，请寻找管理获取帮助" + x.text

                #没绑定就用的傻逼
                else:
                    backw = "错误，请先使用/绑定 命令"

            #验证码非数字
            else:
                backw = "错误，验证码中含有非数字内容"


        #执行命令
        elif(message.content[1] == "#"):
            #提取命令
            player_command = message.content.replace('#','')
            if(player_command == ""):
                player_command ="null"


            #使用控制台权限执行命令
            if(str(console_token_mode) in str(message.member.roles) or "4" in str(message.member.roles)):
                if(console_token_use == True):
                    data = {"action":"command","data":str(player_command),"server":"","token":str(console_token)}
                    x = requests.post(url, json=data,verify=False)
                    print(x.text)
                    command_run_feedback = (json.loads(x.text))["data"]
                    backw = str(message.author.username) + "使用控制台权限执行了命令" + str(player_command) + "\n以下是控制台反馈的结果:\n" + str(command_run_feedback)
                else:
                    backw = "当前机器人未开启使用控制台功能"
            else:
                backw = "执行控制台命令的权限是" +str(console_token_mode)+"您拥有的权限为" + str(message.member.roles) + "1-全体成员 2-管理员 4-频道创建者 5-子频道管理员"


        elif(message.content[1] == "!" or message.content[1] == "！"):
            #提取命令
            player_command = message.content.replace('!','')
            if(player_command == ""):
                player_command ="null"
            #使用玩家个人权限执行命令
            if(usertoken.get(message.author.id, "null") != "null"):
                data = {"action":"command","data":str(player_command),"token":str(usertoken.get(message.author.id, "null"))}
                x = requests.post(url, json=data,verify=False)
                print(x.text)
                command_run_feedback = (json.loads(x.text))["data"]
                backw = str(message.author.username) + "使用玩家权限执行了命令" + str(player_command) + "\n以下是控制台反馈的结果:\n" + str(command_run_feedback)
                print(backw)

            else:
                backw = "您还没有验证您的验证码，请先使用/验证 命令绑定您的uid"


        #其它的情况？
        else:
            backw = "未知命令，请使用/帮助 获取帮助"

        #反馈
        _message = await message.reply(content="[GCbot]" + str(backw))
















if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道 
    # intents = botpy.Intents.none()
    # intents.public_guild_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], token=test_config["token"])
