
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
commentRouter = Blueprint('comment',__name__)


####################################
########## 评论 操作 ###############
####################################

# 创建评论
@commentRouter.route('/api/create_comment/', methods=['POST'])
def create_comment():
    msg=''
    if request.method == 'POST':
        id=get_newid()
        user = User.query.filter(User.username==request.form['username']).first()
        creator_id=user.id
        document_id=request.form['DocumentID']
        document=Document.query.filter(Document.id==document_id).first()
        now=datetime.datetime.now()
        content=request.form['content']
        msg="success"
        newComment=Comment(id=id,document_id=document_id,creator_id=creator_id,content=content,created_time=now)
        db.session.add(newComment)
        db.session.commit()

        # 发送消息
        id=get_newid()
        send_time=now.strftime('%Y-%m-%d')
        content=user.username+"给你的文档("+document.title+")发了一条评论"
        new_notice=Notice(id=id,sender_id=user.id,receiver_id=document.creator_id,document_id=document_id,
            group_id=0,send_time=now,content=content,type=3
        )
        db.session.add(new_notice)
        db.session.commit()

    response={
        'message': msg
    }
    return jsonify(response)

# 获取文档的所有评论
@commentRouter.route('/api/get_all_comment/', methods=['POST'])
def get_all_comment():
    all_comment=Comment.query.filter(Comment.document_id==request.form['DocumentID']).all()
    res=[]
    for comment in all_comment:
        user=User.query.filter(User.id==comment.creator_id).first()
        res.append(comment_to_content(comment,user))
    res.reverse()
    return jsonify(res)

# 获取文档所有修改记录
@commentRouter.route('/api/get_all_modified_time/',methods=['POST'])
def get_all_modified_time():
    res=[]
    all_modified_time=db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==request.form['DocumentID'],DocumentUser.modified_time!=0)).order_by(-DocumentUser.modified_time)
    for tmp in all_modified_time:
        user=User.query.filter(User.id==tmp.user_id).first()
        res.append(modifiedtime_to_content(tmp,user))
    document=Document.query.filter(Document.id==request.form['DocumentID']).first()
    user=User.query.filter(User.id==document.creator_id).first()
    res.append(created_info(document,user))
    return jsonify(res)
