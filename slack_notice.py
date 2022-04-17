#!/usr/bin/python
# coding: utf-8

# In[1]:


import slackweb
import requests
import os, json
from bs4 import BeautifulSoup


# In[2]:


# APIURL下記リンクにて取得
# https://my.slack.com/services/new/incoming-webhook/
slack = slackweb.Slack(url = "https://hooks.slack.com/services/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")
# スクレイピング対象URL
url_list = ["https://www.meti.go.jp/policy/anpo/law09.html",
           "https://www.meti.go.jp/policy/consumer/seian/denan/act_history.html"]


# In[3]:


# Slackにメッセージを送信する関数
def throw_slack_msg(msg, url, opt_msg = "改正情報のページが更新されました", color = "#2eb886"):
    attachments = []
    attachment = {
        "title":msg, 
        "color": color,
        "pretext": opt_msg,
        "title_link":url,
    }
    attachments.append(attachment)
    slack.notify(attachments = attachments)


# In[4]:


# BeautifulSoupオブジェクト取得まで
def get_soup_obj(url):
    # レスオブジェクト生成
    response = requests.get(url)
    # 文字化け制御
    response.encoding = response.apparent_encoding
    return BeautifulSoup(response.text, "html.parser")


# In[5]:


# それぞれのページのスクレイピング用関数のリスト
func_list = []
# URL1の取得関数
def get_msg_1(url):
    # BeautifulSoupオブジェクト取得
    soup =  get_soup_obj(url)
    # 改正内容のタイトルをかこっていた古いタグｗ
    strong_ele = soup.find_all('strong')
    #チェックワード
    dumy_ele = soup.find_all('strong')
    return strong_ele[0].find_all('span')[1].get_text(), dumy_ele[0].find_all('span')[1].get_text()
func_list.append(get_msg_1)


# In[6]:


# 電気用品安全法の取得関数
def get_msg_2(url):
    # BeautifulSoupオブジェクト取得
    soup =  get_soup_obj(url)
    #メッセージ
    ul_ele = soup.find_all("ul", id = "history_top")
    #チェックワード class属性を条件に要素を取得
    class_ele = soup.select('.update2011')
    return "電気用品安全法のページが改正されました", class_ele[0].get_text()
func_list.append(get_msg_2)


# In[7]:


# URL3の取得関数
def get_msg_3(url):
    soup =  get_soup_obj(url)
    return "作成中…"
func_list.append(get_msg_3)


# In[8]:


# JSONファイル確認
log_json = []
log_file_path = "/home/jupyter/jupyterlab/slack_notice/slack_notice_log.json"
if(not os.path.isfile(log_file_path)):
    for i in range(len(url_list)):
        log_json.append({})
else:
    # JSON読み込み
    with open(log_file_path) as f:
        log_json = json.load(f)
    if(len(log_json) != len(url_list)):
        for i in range(len(url_list) - len(log_json)):
            log_json.append({})


# In[9]:


for i, url in enumerate(url_list):
    # 改正内容のタイトル取得
    try:
#        msg, check = func_list[i](url)[msg_Ary_Val]
        msg, check_word = func_list[i](url)
        print("{}周目\nURL:{}\nMSG:{}".format(i + 1, url, msg))
#        if("msg" in log_json[i]):
#            if(msg != log_json[i]["msg"]):
        if("check_word" in log_json[i]):
            if(check_word != log_json[i]["check_word"]):
                print("結果:更新あり、通知します")
                throw_slack_msg(msg, url)
                log_json[i]["msg"] = msg
                log_json[i]["check_word"] = check_word
            else:
                print("結果:更新無し")
        else:
            print("結果:新規作成")
            throw_slack_msg(msg, url)
            log_json[i]["msg"] = msg
            log_json[i]["err"] = 0
            log_json[i]["check_word"] = check_word
    except:
        print("結果:エラー")
        if("err" in log_json[i]):
            if(0 == log_json[i]["err"]):
                throw_slack_msg("該当ページを開く", url, opt_msg = "情報を取得できませんでしたリンクをご確認いただくか、管理者にご連絡ください。", color = "#ff0000")
                log_json[i]["err"] = 1
        else:
            throw_slack_msg("該当ページを開く", url, opt_msg = "情報を取得できませんでしたリンクをご確認いただくか、管理者にご連絡ください。", color = "#ff0000")
            log_json[i]["err"] = 1


# In[10]:


# JSONに保存
with open(log_file_path, "w") as f:
    json.dump(log_json , f, ensure_ascii=False)


# In[ ]:





# In[ ]:




