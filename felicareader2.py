#coding:utf-8
from ctypes import *
import time
import sys
import traceback
from requests import put, get
import json

l = ["gakuseki","name"]
user_time = {}
delay = 0.0
API_PASS = "API_PASSWORD"
URL = "attendchecker_URL"

def post_user_data():
    name = ""
    gakuseki = ""

    for val in range(2):
        save = ""
        i = c_uint64()
        f.felica_read_without_encryption02.restype = c_int
        f.felica_read_without_encryption02(felica, 0x1A8B, 0, val, byref(i))
        s = "%016X" % i.value
        w = l[val]
 
        for val in range(0,15,2):
            save += s[0+val:2+val]
            save += " "
 
        data = ""
 
        for v in save.split(" "):
            try:
                data += chr(int(v,16))
            except:
                pass
 
        if w == "name":
            name = data[::-1]
        else:
            gakuseki = data[::-1][2:]

    try:
        user = json.loads(get("%s%s_%s_%s"%(URL,API_PASS,gakuseki,name)).json())
    except:
        print u"カードをしっかりタッチするか、ネットワーク認証を受けて下さい。"
        return -1

    if user["attend"] == 1: #退出はすぐ行う
        put(URL+"p",data={"key":API_PASS,"gakuseki":gakuseki,"name":name}).json()
        print u"退出が完了しました。"
        return 1

    if not user_time.has_key(name): #タッチ完了後から30秒の計測を開始する
        print u"学籍番号:%s  お名前:%s"%(gakuseki,name)
        print u"仮出席が完了しました。30秒以内の再タッチで出席のキャンセルが出来ます。"
        user_time[name] = [0,gakuseki]
        return 1

    if 0 < user_time[name][0] < 60: #30秒経つ前に再タッチした人は出席キャンセル
        del user_time[name]
        print u"出席がキャンセルされました。"

    return 1


f = cdll.felicalib

f.pasori_open.restype = c_void_p
pasori = f.pasori_open()

f.pasori_init(pasori)
f.felica_read_without_encryption02.restype = c_int

while 1:

    for n in user_time.keys():
        if user_time[n][0] >= 60: #タッチ完了後30秒立った人は出席
            print "%s%s_%s_%s"%(URL,API_PASS,gakuseki,name)

            try:
                res = put(URL+"p",data={"key":API_PASS,"gakuseki":user_time[n][1],"name":n}).json()
            except:
                print u"もう一度トライしてください。"

            if res == "success":
                print u"%sさんが出席しました。"%(n)
            else:
                print u"データ送信に失敗しました。"

            del user_time[name]

    f.felica_polling.restype = c_void_p
    felica = f.felica_polling(pasori, 0xFE00, 0, 0)

    if not felica:
        print u"カードがありません。カードをタッチして下さい。"
        time.sleep(0.5)
        for n in user_time.keys():
            user_time[n][0] += 1  #0.5秒毎にインクリメント
        continue

    print "\a"
    res = post_user_data()

    #5秒スリープ
    while res == 1 and delay != 10:
        delay += 1.0
        time.sleep(0.5)
        for n in user_time.keys():
            user_time[n][0] += 1 #0.5秒毎にインクリメント
    delay = 0.0

f.pasori_close(pasori)