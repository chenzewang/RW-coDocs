
from functools import wraps
from flask import Flask, request, session,jsonify,Blueprint
from flask_sqlalchemy import SQLAlchemy
from manage import *
from sqlalchemy import and_, or_,not_,func
import datetime,time
import config

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)
messageRouter = Blueprint('message',__name__)


####################################
########## 私信 操作 ###############
####################################
@messageRouter.route('/api/sayhi/',methods=['POST'])
def sayhi():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    sender=User.query.filter(User.username==request.form['sender_username']).first()
    id=get_newid()
    now=datetime.datetime.now()
    new_msg=Message(id=id,sender_id=sender.id,receiver_id=receiver.id,send_time=now,content='hi')
    db.session.add(new_msg)
    db.session.commit()
    response={
        'message':'success'
    }
    return jsonify(response)

@messageRouter.route('/api/send_msg_to_sb/',methods=['POST'])
def send_msg_to_sb():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    sender=User.query.filter(User.username==request.form['sender_username']).first()
    id=get_newid()
    now=datetime.datetime.now()
    content=request.form['content']
    new_msg=Message(id=id,sender_id=sender.id,receiver_id=receiver.id,send_time=now,content=content)
    db.session.add(new_msg)
    db.session.commit()
    response={
        'id':id,
        'receiver_name':receiver.username,
        'sender_name':sender.username,
        'send_time':now,
        'content':content
    }
    return jsonify(response)

@messageRouter.route('/api/who_send_msg/',methods=['POST'])
def who_send_msg():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    all_my_msg=Message.query.filter(Message.receiver_id==receiver.id).all()
    res=[]
    for msg in all_my_msg:
        sender=User.query.filter(msg.sender_id==User.id).first()
        res.append(msg_to_content(sender,receiver,msg))
    return jsonify(res)

@messageRouter.route('/api/our_msg/',methods=['POST'])
def our_msg():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    sender=User.query.filter(request.form['sender_username']==User.username).first()
    all_our_msg=Message.query.filter(or_(and_(Message.receiver_id==receiver.id,Message.sender_id==sender.id),
        and_(Message.receiver_id==sender.id,Message.sender_id==receiver.id))).order_by(Message.send_time).all()
    res=[]
    for msg in all_our_msg:
        sender=User.query.filter(User.id==msg.sender_id).first()
        receiver=User.query.filter(User.id==msg.receiver_id).first()
        content={
            'id':msg.id,
            'sender_name':sender.username,
            'receiver_name':receiver.username,
            'content':msg.content,
            'send_time':msg.send_time
        }
        res.append(content)
    return jsonify(res)

@messageRouter.route('/api/send_msg_people/',methods=['POST'])
def send_msg_people():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    all_my_msg=Message.query.filter(or_(Message.receiver_id==receiver.id,Message.sender_id==receiver.id)).all()
    res=[]
    userlist=[]
    for msg in all_my_msg:
        if(msg.sender_id==receiver.id):
            sender=User.query.filter(msg.receiver_id==User.id).first()
            if sender.id not in userlist:
                userlist.append(sender.id)
                res.append(msg_to_content(sender,receiver,msg))
        else:
            sender=User.query.filter(msg.sender_id==User.id).first()
            if sender.id not in userlist:
                userlist.append(sender.id)
                res.append(msg_to_content(sender,receiver,msg))
    return jsonify(res)
