#!/usr/bin/python3
# -*- coding: utf8 -*-
from flask import Flask,request
import json
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from geventwebsocket.websocket import WebSocket   #这条做语法提示用
import sys

app = Flask(__name__)


users = set()
@app.route('/conn')
def index():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock.closed:
        users.add(wsock)
        while True:
            message = wsock.receive()
            if message:
                obj=json.loads(message)
                username=obj['username']
                content=obj['content']
                res="{\"username\":\""+username+"\",\"content\":\""+content+"\"}"
                for user in users.copy():
                    if user!=wsock:
                        try:
                            # print(res)
                            # print(user)
                            print("新用户加入")
                            user.send(res)
                        except:
                            # print("用户断开连接")
                            # print("出错")
                            print("Unexpected error:", sys.exc_info()[0])
                            users.remove(wsock)




if __name__ == '__main__':
    # app.run()
    #在APP外封装websocket
    http_serv = WSGIServer(("0.0.0.0",8888),app,handler_class=WebSocketHandler)
    # 启动服务
    http_serv.serve_forever()