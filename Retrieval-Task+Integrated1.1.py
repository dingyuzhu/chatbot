# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 11:51:47 2018

@author: user
"""

from __future__ import unicode_literals
import sys
import itchat
sys.path.append("../")
import jieba.analyse
import jieba
from gensim import corpora, models, similarities
import codecs
import requests
import re
import urllib.request as ul_re
import json
import jsonpath

Train_test = 'data/data.txt'
Traintest = codecs.open(Train_test, 'rb').readlines()
Traintest = [w.strip() for w in Traintest]
# Chinese Word tokenizing with jieba
Traintest_word = []
for word in Traintest:
    words_list = [words for words in jieba.cut(word)]
    Traintest_word.append(words_list)

# Accessing the question part of the corpora
Train_test_Q = 'data/data_Q.txt'
Traintest_Q = codecs.open(Train_test_Q, 'rb').readlines()
Traintest_Q = [word.strip() for word in Traintest_Q]
# Chinese Word tokenizing with jieba
Traintest_Question = []
for Question in Traintest_Q:

    Q_list = [Q for Q in jieba.cut(Question)]
    Traintest_Question.append(Q_list)

# Update dictionary from corpora
dictionary = corpora.Dictionary(Traintest_Question)

# Indexing dictionary
dictionary.keys()

# Convert document into the bag-of-words (BoW) format = list of (token_id, token_count) tuples.
corpus = [dictionary.doc2bow(doc) for doc in Traintest_Question]
# The corpus is now in vector space model

tfidf_model = models.TfidfModel(corpus)
tfidf_model.save('tfidf.model')


# Retrieve response from corpus
def retrieve_response(user_input):
    doc_test = user_input
    doc_test_list = [word for word in jieba.cut(doc_test)]

    doc_test_vec = dictionary.doc2bow(doc_test_list)
    # tfidf[corpus] to get the TF-IDF of each question
    # get the similarities of each question in compare to the user input
    index = similarities.SparseMatrixSimilarity(tfidf_model[corpus], num_features=len(dictionary.keys()))
    sim = index[tfidf_model[doc_test_vec]]
    # Sort each question with their similarities in descending order
    SimilaritiesList = sorted(enumerate(sim), key=lambda item: -item[1])
    num = 0
    Result_tuple = SimilaritiesList[num]  # get tuple, index, similarities获取元组   索引  相似度
    Result_index = Result_tuple[0]  # get index of the question with highest similarity to user_input
    response_list = Traintest_word[Result_index]  # QA response
    Result_score = Result_tuple[1]
    print("Similarity:"+str(Result_score))
    newlist = response_list[response_list.index('\t'):]  # Testing QA response result
    response = ''
    for res in newlist:
        response += res
    response = re.sub('\s', '', response)
    response = response[:-3]
    print("answer:"+response)
    return response
    
    
def get_response(_info):  # invoke turling robot
    print(_info)
    api_url = 'http://www.tuling123.com/openapi/api'  # turling robot url
    data = {
        'key': 'e11501a19c394d05b36d12137ab1d652',  # turling api key
        'info': _info,
        'userid': 'wechat-robot',
    }
    r = requests.post(api_url, data=data).json()
    print(r.get('text'))
    return r


def booking_flights(user_text):
    global flag
    global return_session
    # user_text=msg['Text']
    
    if user_text == '结束':
        flag = 0
        return_session = ''
    else:
        url = 'https://aip.baidubce.com/rpc/2.0/unit/bot/chat?access_token=24.62800c1e0d94478b487ec04859411f5b.2592000.1546348586.282335-14856895'
        post_data = {
            "bot_session": return_session,
            "log_id": "7758521",
            "request": {
                "bernard_level": 0,
                "client_session": "{\"client_results\":\"\", \"candidate_options\":[]}",
                "query": user_text,
                "query_info": {
                    "asr_candidates": [],
                    "source": "KEYBOARD",
                    "type": "TEXT"
                },
                "updates": "",
                "user_id": "88888"
            },
            "bot_id": "17037",
            "version": "2.0"
        }
        encoded_data = json.dumps(post_data).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        request = ul_re.Request(url, data=encoded_data, headers=headers)
        response = ul_re.urlopen(request)
        html = response.read()
        # data=json.loads(html)
        # data["action_list"][0]['say']
        jsonobj = json.loads(html)
        say = jsonpath.jsonpath(jsonobj, '$..say')
        print(say)
        say_convert = ''.join(say)
        if say_convert == '好的，已为您定好票！':
            return_session = ''
            flag = 0
            # itchat.send_msg(say_convert, toUserName=msg['FromUserName'])
        else:
            bot_session = jsonpath.jsonpath(jsonobj, '$..bot_session')
            session_convert = str(bot_session)
            index = session_convert.find('session_id')
            index = index-1
            session_id = session_convert[index:-5]
            return_session = str("{"+session_id+"}")
            # itchat.send_msg(say_convert, toUserName=msg['FromUserName'])
        return say_convert


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):  # AutoReply to User
    global return_session
    print("收到好友消息：" + msg['Text'])  # msg['Text']是好友发送的消息
    # msg['Text'].encode('utf-8')
    check1 = "笑话"
    check2 = "天气"
    check3 = "机票"
    global flag
    # print(type(msg['Text']))
    
    word_list = jieba.cut(msg['Text'])
    for word in word_list:
        if word == str(check2):
            flag = 2
        if word == str(check1):

            return get_response(msg['Text'])['text']
        if word == str(check3):
            flag = 1
            
    if flag == 1:
        user_text = msg['Text']
        
        if user_text == '结束':
            flag = 0
            return_session = ''
        else:
            return booking_flights(user_text)

    elif flag == 2:
        print("收到好友消息：" + msg['Text'])
        if msg['Content'] == '结束':
            flag = 0
        else:
            
            response = get_response(msg['Text'])['text']
            for word in jieba.cut(response):
                if word == '气温':
                    flag = 0
            # return get_response(msg['Text'])['text']
            # return response
            # response=str(datas)
            # response=response[26:-2]
            itchat.send_msg(str(response), toUserName=msg['FromUserName'])

    elif flag == 0:
        user_input = msg['Text']
        return retrieve_response(user_input)


if __name__ == '__main__':
    global return_session
    return_session = ''
    global flag
    flag = 0
    itchat.auto_login()  # hotReload = True, keep online
    itchat.run()
