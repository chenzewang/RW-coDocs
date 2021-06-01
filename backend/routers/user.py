
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
userRouter = Blueprint('user',__name__)

####################################
########## User 操作 ###############
####################################

#登录
# tested
@userRouter.route('/api/login/', methods=['POST'])
def login():
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            user = get_user_byusername(request.form['username'])
            response=user_to_content(user)
            return jsonify(response)
    return sendmsg('fail')

# 获取当前登录用户
# tested
@userRouter.route('/api/get_user/',methods=['POST'])
def get_user():
    user = get_user_byusername(request.form['username'])
    response=user_to_content(user)
    return jsonify(response)

# tested
@userRouter.route('/api/get_user_byid/',methods=['POST'])
def get_user_byid():
    user=User.query.filter(User.id==request.form['userid']).first()
    return jsonify(user_to_content(user))

# tested
@userRouter.route('/api/logout/',methods=['GET'])
def logout():
    return sendmsg('success')

# 注册
@userRouter.route('/api/regist/', methods=['POST'])
def regist():
    if request.method == 'POST':
        username = User.query.filter(User.username == request.form['username']).first()
        email = User.query.filter(User.email == request.form['email']).first()
        if(username or email):
            return sendmsg('fail')
        else:
            id=get_newid()
            newUser=User(id=id, username=request.form['username'], password=request.form['password'],
                email=request.form['email'])
            db.session.add(newUser)
            db.session.commit()
    return sendmsg('success')

# tested
@userRouter.route('/api/getalluser/',methods=['GET'])
def getalluser():
    all_user=User.query.all()
    res=[]
    for user in all_user:
        res.append(user_to_content(user))
    return jsonify(res)


# 修改User Info
@userRouter.route('/api/modify_user_info/', methods=['POST'])
def modify_user_info():
    if request.method == 'POST':
        user = User.query.filter(User.username==request.form['username']).first()
        username = User.query.filter(User.username == request.form['new_username']).first()
        email = User.query.filter(User.email == request.form['new_email']).first()
        if(username):
            if(username.id!=user.id):
                return sendmsg('fail')
        if(email):
            if(email.id!=user.id):
                return sendmsg('fail')
        db.session.query(User).filter(User.username==request.form['username']).update({"password":request.form['new_password1'],
            "username":request.form['new_username'],
            "email":request.form['new_email'],
            "description":request.form['new_description']})
        # db.session.query(User).filter(User.username==session['username']).update({"username":request.form['new_username']})
        # db.session.query(User).filter(User.username==session['username']).update({"email":request.form['new_email']})
        db.session.commit()
        session['username']=request.form['new_username']
    return sendmsg('success')