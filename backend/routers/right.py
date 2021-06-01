
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
rightRouter = Blueprint('right',__name__)

####################################
########## right 操作 ###############
####################################


# 1：有权限
# 0：无权限
# 创建者直接权限全给
# 只有创建者才有给别人授予权限的权利

# # 授予权限
# @rightRouter.route('/api/grant_right/', methods=['POST'])
# def grant_right():
#     msg=''
#     if request.method=='POST':
#         id=get_newid()
#         document = Document.query.filter(Document.id == request.form['DocumentID']).first()
#         user = User.query.filter(User.username==request.form['username']).first()
#         share_right=request.form['share_right']
#         # watch_right=request.form['watch_right']
#         modify_right=request.form['modify_right']
#         # delete_right=request.form['delete_right']
#         #delete_right=0
#         discuss_right=request.form['discuss_right']
#         newDocumentUser=DocumentUser(id=id,document_id=document.id,user_id=user.id,
#             share_right=share_right,watch_right=watch_right,modify_right=modify_right,
#             delete_right=delete_right,discuss_right=discuss_right
#         )
#         db.session.add(newDocumentUser)
#         db.session.commit()
#         response={
#             'message':'grant right success'
#         }
#         return jsonify(response)

# 个人文档创建者修改权限
@rightRouter.route('/api/modify_personal_doc_right/', methods=['POST'])
def modify_personal_doc_right():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        others_share_right=request.form['others_share_right']
        # watch_right=request.form['watch_right']
        others_modify_right=request.form['others_modify_right']
        # delete_right=request.form['delete_right']
        others_discuss_right=request.form['others_discuss_right']
        db.session.query(Document).filter(Document.id==document.id).update({"others_share_right":others_share_right,
            "others_modify_right":others_modify_right,"others_discuss_right":others_discuss_right})
        msg="success"
        #     "watch_right":watch_right,"modify_right":modify_right,"delete_right":delete_right,"discuss_right":discuss_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"share_right":share_right,
        #     "watch_right":watch_right,"modify_right":modify_right,"delete_right":delete_right,"discuss_right":discuss_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"watch_right":watch_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"modify_right":modify_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"delete_right":delete_right})
        # db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"discuss_right":discuss_right})
        db.session.commit()
        response={
            'message': msg
        }
        return jsonify(response)

# 团队文档创建者修改权限
@rightRouter.route('/api/modify_group_doc_right/', methods=['POST'])
def modify_group_doc_right():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        share_right=request.form['share_right']
        modify_right=request.form['modify_right']
        discuss_right=request.form['discuss_right']
        others_modify_right=request.form['others_modify_right'],
        others_share_right=request.form['others_share_right'],
        others_discuss_right=request.form['others_discuss_right'],
        db.session.query(Document).filter(Document.id==document.id).update({"share_right":share_right,
            "modify_right":modify_right,"discuss_right":discuss_right,
            "others_share_right":others_share_right,"others_modify_right":others_modify_right,
            "others_discuss_right":others_discuss_right})
        msg="success"
        db.session.commit()
        response={
            'message': msg
        }
        return jsonify(response)
