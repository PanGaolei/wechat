#coding:utf-8
import itchat, time
import datetime
import json
import logging
import os
import io, sys
from itchat.content import *
import requests

#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
#@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING], isGroupChat=True)
#@itchat.msg_register(TEXT, isGroupChat=True)

KEY = '9d4c8c5c0bb5403f923209dfae21ac8e'

def set_logger(message, filename, mode='a+', encoding='utf-8'):
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(filename, mode, encoding)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info(message)
    logger.removeHandler(fh)
    return logger

def get_response(msg):
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {'key': KEY, 'info': msg, 'userid': 'wechat-robot'}
    try:
        r = requests.post(apiUrl, data=data).json()
        return r.get('text')
    except:
        return

def group_reply(msg, kwords=[]):
    for kword in kwords:
        if kword in msg['Text']:
            img = 'picture/QR.png'
            msg.User.send('你好，欢迎加入本群，发照，给群主请安')
            msg.User.send("@img@%s" %img)


def friend_reply(msg, kwords=[]):
    defaultReply = '工作中，下班之后联系'
    reply = get_response(msg['Text'])
    # return reply or defaultReply
    # for kword in kwords:
    #     if kword in msg['Text']:
    #         img = 'picture/QR.png'
    #msg.User.send('你好，欢迎加入本群，请扫描以下二维码')
    #msg.User.send("@img@%s" %img)
    if reply:
        msg.User.send(reply)
    else:
        msg.User.send(defaultReply)


def delete_chatroom_member(msg, kwords=[]):
    for kword in kwords:
        if kword in msg['Text']:
            del_memberList = []
            for member in msg['User']['MemberList']:
                if member['UserName'] == msg['ActualUserName']:
                    del_memberList.append(member)
                    itchat.delete_member_from_chatroom(msg['User']['UserName'], del_memberList)


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isGroupChat=True)
def download_group_files(msg):
    abs_path = os.path.abspath(os.curdir)
    group_folder = msg['User']['NickName'] + '/' + msg['Type']
    folder_url = os.path.join(abs_path, group_folder)
    if not os.path.exists(folder_url):
        os.makedirs(folder_url)
    file_url = os.path.join(folder_url, msg.fileName)
    print('start download ******')
    msg.download(file_url)
    print('download finish******')
    msg['Text'] = file_url
    for key in msg.keys():
        if msg[key] == '':
            msg[key] = '-'
    CreateTime = time.localtime(msg['CreateTime'])
    msg['CreateTime'] = time.strftime("%Y-%m-%d %H:%M:%S", CreateTime)
    sender = {}
    if len(msg['User']['MemberList']) > 0:
        for member in msg['User']['MemberList']:
            if member['UserName'] == msg['ActualUserName']:
                sender['NickName'] = member['NickName'] if member['NickName'] != '' else '-'
                sender['DisplayName'] = member['DisplayName'] if member['DisplayName'] != '' else '-'
    message = '"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"\n' %(msg['CreateTime'], \
        msg['User']['UserName'], msg['User']['NickName'], msg['ActualUserName'], sender.get('NickName', '-'), \
        sender.get('DisplayName', '-'), msg['Content'], msg['ActualNickName'], msg['FileName'], msg['Url'], msg['Type'], msg['Text'])
    set_logger(message, filename='test.log')
    print('%s: %s' %(msg['ActualNickName'], msg['Text']))


@itchat.msg_register(FRIENDS)
def add_friend(msg):
    itchat.add_friend(**msg['Text']) # 该操作会自动将新好友的消息录入，不需要重载通讯录
    itchat.send_msg('Nice to meet you!', msg['RecommendInfo']['UserName'])


@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING], isGroupChat=True)
def output_group_content(msg):
    # keywords = ['加入了群聊', '加入群聊']
    # group_reply(msg, keywords)

    CreateTime = time.localtime(msg['CreateTime'])
    msg['CreateTime'] = time.strftime("%Y-%m-%d %H:%M:%S", CreateTime)
    for key in msg.keys():
        if msg[key] == '':
            msg[key] = '-'
    sender = {}
    if len(msg['User']['MemberList']) > 0:
        for member in msg['User']['MemberList']:
            if member['UserName'] == msg['ActualUserName']:
                sender['NickName'] = member['NickName'] if member['NickName'] != '' else '-'
                sender['DisplayName'] = member['DisplayName'] if member['DisplayName'] != '' else '-'
    message = '"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"|-|"%s"\n' %(msg['CreateTime'], \
        msg['User']['UserName'], msg['User']['NickName'], msg['ActualUserName'], sender.get('NickName', '-'), \
        sender.get('DisplayName', '-'), msg['Content'], msg['ActualNickName'], msg['FileName'], msg['Url'], msg['Type'], msg['Text'])
    set_logger(message, filename='test.log')
    
    sensitive_words = ['fuck', 'pig']
    delete_chatroom_member(msg, sensitive_words)
    print('%s: %s' %(msg['ActualNickName'], msg['Text']))


@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING], isFriendChat=True)
def out_friend_content(msg):
    CreateTime = time.localtime(msg['CreateTime'])
    msg['CreateTime'] = time.strftime("%Y-%m-%d %H:%M:%S", CreateTime)
    msg_file = msg['User']['NickName'] + '.log'
    for key in msg.keys():
        if msg[key] == '':
            msg[key] = '-'
    if msg['FromUserName'] == msg['User']['UserName']:
        message = '"%s" "%s" "%s" "%s" "%s" "%s"\n' %(msg['CreateTime'], msg['User']['NickName'], \
            msg['FileName'], msg['Url'], msg['Type'], msg['Text'])
    else:
        msg['User']['NickName'] = '我'
        message = '"%s" "%s" "%s" "%s" "%s" "%s"\n' %(msg['CreateTime'], msg['User']['NickName'], \
            msg['FileName'], msg['Url'], msg['Type'], msg['Text'])
    
    set_logger(message, filename=msg_file)
    print('%s %s: %s' %(msg['CreateTime'], msg['User']['NickName'], msg['Text']))
    # friend_reply(msg)


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO], isFriendChat=True)
def download_friend_files(msg):
    abs_path = os.path.abspath(os.curdir)
    group_folder = msg['User']['NickName'] + '/' + msg['Type']
    folder_url = os.path.join(abs_path, group_folder)
    if not os.path.exists(folder_url):
        os.makedirs(folder_url)
    file_url = os.path.join(folder_url, msg.fileName)
    print('start download ******')
    msg.download(file_url)
    print('download finish******')
    msg['Text'] = file_url
    for key in msg.keys():
        if msg[key] == '':
            msg[key] = '-'
    CreateTime = time.localtime(msg['CreateTime'])
    msg['CreateTime'] = time.strftime("%Y-%m-%d %H:%M:%S", CreateTime)
    msg_file = msg['User']['NickName'] + '.log'
    if msg['FromUserName'] == msg['User']['UserName']:
        message = '"%s" "%s" "%s" "%s" "%s" "%s"\n' %(msg['CreateTime'], msg['User']['NickName'], \
            msg['FileName'], msg['Url'], msg['Type'], msg['Text'])
    else:
        msg['User']['NickName'] = '我'
        message = '"%s" "%s" "%s" "%s" "%s" "%s"\n' %(msg['CreateTime'], msg['User']['NickName'], \
            msg['FileName'], msg['Url'], msg['Type'], msg['Text'])
    set_logger(message, filename=msg_file)
    print('%s %s: %s' %(msg['CreateTime'], msg['User']['NickName'], msg['Text']))


def get_friends_list():
    friend_lists = itchat.get_friends(update=False)
    for friend in friend_lists:
        friend_json = json.dumps(dict(friend), ensure_ascii=False, indent=4)
        with open('friend.json', 'w', encoding='utf-8') as f:
            f.write(friend_json)
            f.close()


def get_chatrooms_list():
    chatroom_lists = itchat.get_chatrooms(update=False)
    for chatroom in chatroom_lists:
        chatroom_json = json.dumps(dict(chatroom), ensure_ascii=False, indent=4)
        with open('chatroom.json', 'w', encoding='utf-8') as f:
            f.write(chatroom_json)
            f.close()


itchat.auto_login(True)
get_friends_list()
get_chatrooms_list()
itchat.run()
