
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
noticeRouter = Blueprint('notice',__name__)

####################################
########## 消息 操作 ###############
####################################

# 获取用户未读所有的消息
@noticeRouter.route('/api/get_all_notice/',methods=['POST'])
def get_all_notice():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    all_notice=Notice.query.filter(Notice.receiver_id==receiver.id).all()
    res=[]
    for notice in all_notice:
        res.append(notice_to_content(notice))
    return jsonify(res)

# 未读转已读(直接从数据库中删除)
@noticeRouter.route('/api/del_new_notice/',methods=['POST'])
def del_new_notice():
    new_notice_id=request.form['new_notice_id']
    del_notice(new_notice_id)
    response={
        'message':'success'
    }
    return jsonify(response)

# 查看所有不需要确认的消息(type=0,1,3,4,5,7,8,9)
@noticeRouter.route('/api/view_non_confirm_notice/',methods=['POST'])
def view_non_confirm_notice():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    all_notice=Notice.query.filter(Notice.receiver_id==receiver.id).all()
    res=[]
    for notice in all_notice:
        stat=notice.type
        if(stat==0 or stat==1 or stat==3 or stat==4 or stat==5 or stat==7 or stat==8 or stat==9):
            res.append(notice_to_content(notice))
    return jsonify(res)


# 查看所有需要确认的消息(type=2) 需要有两个button，分别发出type=1、5的消息
@noticeRouter.route('/api/view_confirm_notice/',methods=['POST'])
def view_confirm_notice():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    all_notice=Notice.query.filter(and_(Notice.receiver_id==receiver.id,Notice.type==2)).all()
    res=[]
    for notice in all_notice:
        res.append(notice_to_content(notice))
    print(res)
    return jsonify(res)

# 查看所有需要确认的消息(type=6) 需要有两个button，分别发出type=7、8的消息
@noticeRouter.route('/api/view_confirm_apply_notice/',methods=['POST'])
def view_confirm_apply_notice():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    all_notice=Notice.query.filter(and_(Notice.receiver_id==receiver.id,Notice.type==6)).all()
    res=[]
    for notice in all_notice:
        res.append(notice_to_content(notice))
    print(res)
    return jsonify(res)

# 查看某用户的总未读消息数量
@noticeRouter.route('/api/num_of_notice/',methods=['POST'])
def num_of_notice():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    all_notice=Notice.query.filter(Notice.receiver_id==receiver.id).all()
    cnt=0
    for notice in all_notice:
         cnt+=1
    content={
        'notice_cnt':cnt
    }
    return jsonify(content)

# 查看用户各种消息类型分别的数量
@noticeRouter.route('/api/all_sort_notice/',methods=['POST'])
def all_sort_notice():
    receiver=User.query.filter(User.username==request.form['receiver_username']).first()
    all_notice=Notice.query.filter(Notice.receiver_id==receiver.id).all()
    cnt_normal=0
    cnt_type2=0
    cnt_type6=0
    cnt_total=0
    for notice in all_notice:
        stat=notice.type
        if(stat==2):
            cnt_type2+=1
        elif(stat==6):
            cnt_type6+=1
        else:
            cnt_normal+=1
        cnt_total=cnt_type2+cnt_type6+cnt_normal
    content={
        'cnt_type2':cnt_type2,
        'cnt_type6':cnt_type6,
        'cnt_normal':cnt_normal,
        'cnt_total':cnt_total
    }
    return jsonify(content)
