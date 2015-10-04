#coding:utf-8
from ctypes import *
import time
import sys
import traceback
from requests import put, get
import json
 
l = ["gakuseki","name"]
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
 
    #try:
    print "%s%s_%s_%s"%(URL,API_PASS,gakuseki,name)
    try:
        user = json.loads(get("%s%s_%s_%s"%(URL,API_PASS,gakuseki,name)).json())
    except:
        print u"カードをしっかりタッチするか、ネットワーク認証を受けて下さい。"
        return

    try:
        res = put(URL+"p",data={"key":API_PASS,"gakuseki":gakuseki,"name":name}).json()
    except:
        print u"もう一度トライしてください。"
        return
 
 
    if res == "success":
        if user["attend"] == 0:
            print u"出席が完了しました。"
        else:
            print u"退出が完了しました。"
    else:
        print u"データ送信に失敗しました。"
 
    return
 
f = cdll.felicalib
 
 
f.pasori_open.restype = c_void_p
pasori = f.pasori_open()
 
 
f.pasori_init(pasori)
 
f.felica_read_without_encryption02.restype = c_int
 
while 1:
    f.felica_polling.restype = c_void_p
    felica = f.felica_polling(pasori, 0xFE00, 0, 0)
 
    if not felica:
        print u"カードがありません。カードをタッチして下さい。"
        time.sleep(0.5)
        continue
 
    print "\a"
    post_user_data()
 
    time.sleep(5)
 
f.pasori_close(pasori)