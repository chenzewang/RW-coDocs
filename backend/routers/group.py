
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
groupRouter = Blueprint('group',__name__)

####################################
########## Group 操作 ###############
####################################

#创建团队
@groupRouter.route('/api/creategroup/',methods=['POST'])
def creategroup():
   user=get_user_byusername(request.form['username'])
   id=get_newid()
   newGroup=Group(id=id,groupname=request.form['groupname'],leaderid=user.id,createdtime=datetime.datetime.now(),description=request.form['description'])
   newGroupMember=GroupMember(id=id,group_id=id,user_id=user.id)
   db.session.add(newGroup)
   db.session.add(newGroupMember)
   db.session.commit()
   return sendmsg('success')


# 修改团队信息
@groupRouter.route('/api/modify_group_info/',methods=['POST'])
def modify_group_info():
    db.session.query(Group).filter(Group.id==request.form['groupid']).update({"groupname":request.form['groupname'],
    "description":request.form['description']})
    db.session.commit()
    return sendmsg("success")




# 显示我加入的group
# tested
@groupRouter.route('/api/mygroup/',methods=['POST'])
def mygroup():
    user=get_user_byusername(request.form['username'])
    all_groupmember=GroupMember.query.filter(GroupMember.user_id==user.id).all()
    res=[]
    for groupmember in all_groupmember:
        group=Group.query.filter(Group.id==groupmember.group_id).first()
        if(group.leaderid!=user.id):
            res.append(group_to_content(group))
    return jsonify(res)

# 判断这个group是不是当前登录用户所创建的group
# tested
@groupRouter.route('/api/groupiscreatedbyme/',methods=['POST'])
def groupiscreatedbyme():
    user=get_user_byusername(request.form['username'])
    res=Group.query.filter(and_(Group.leaderid==user.id,Group.id==request.form['groupid'])).first()
    if(res):
        return sendmsg('yes')
    return sendmsg('no')

@groupRouter.route('/api/search_group/',methods=['POST'])
def search_group():
    user=User.query.filter(User.username==request.form['username']).first()
    keyword=request.form['keyword']
    res=[]
    all_group=Group.query.filter(Group.groupname.like('%{keyword}%'.format(keyword=keyword))).all()
    for group in all_group:
        gm=GroupMember.query.filter(and_(GroupMember.group_id==group.id,GroupMember.user_id==user.id)).first()
        if(gm):
           continue
        res.append(group_to_content(group))
    return jsonify(res)

@groupRouter.route('/api/group_created_byme/',methods=['POST'])
def group_created_byme():
    user=get_user_byusername(request.form['username'])
    all_group=Group.query.filter(Group.leaderid==user.id).all()
    res=[]
    for group in all_group:
        res.append(group_to_content(group))
    return jsonify(res)


# 作为团队的管理者，添加成员，在被接受端选择接受邀请时加人，给leader发一条消息
# 在我的group中添加用户，这里的用户是前端判断好的不在该group中的user
@groupRouter.route('/api/addgroupmember/',methods=['POST'])
def addgroupmember():
    userid=request.form['userid']
    user=User.query.filter(User.id==userid).first()
    groupid=request.form['groupid']
    group=Group.query.filter(Group.id==groupid).first()
    id=get_newid()
    newGroupMember=GroupMember(id=id,user_id=userid,group_id=groupid)
    db.session.add(newGroupMember)
    db.session.commit()

    # 发送消息
    id=get_newid()
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=user.username+"通过了你的邀请，加入团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=userid,receiver_id=group.leaderid,document_id=0,
        group_id=groupid,send_time=now,content=content,type=1
    )
    db.session.add(new_notice)
    db.session.commit()

    all_document=db.session.query(Document).filter(Document.group_id==groupid).all()
    for document in all_document:
        id=get_newid()
        newDU=DocumentUser(id=id,document_id=document.id,
            user_id=userid,last_watch=0,
            favorited=0,type=1,modified_time=0)
        db.session.add(newDU)
        db.session.commit()
    del_notice(request.form['id'])
    response={
        'message':'success'
    }
    return jsonify(response)

# 团队管理者向我发送了加入团队邀请，我拒绝了
@groupRouter.route('/api/refuse_groupmember/',methods=['POST'])
def refuse_groupmember():
    userid=request.form['userid']
    user=User.query.filter(User.id==userid).first()
    groupid=request.form['groupid']
    group=Group.query.filter(Group.id==groupid).first()

    # 发送消息
    id=get_newid()
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=user.username+"拒绝了你的邀请，不加入团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=userid,receiver_id=group.leaderid,document_id=0,
        group_id=groupid,send_time=now,content=content,type=5
    )
    db.session.add(new_notice)
    del_notice(request.form['id'])
    db.session.commit()
    
    response={
        'message':'success'
    }
    return jsonify(response)

# 团队创建者想要邀请需要先检索用户，根据用户名检索，返回所有不在该团队中的检索用户
# tested
@groupRouter.route('/api/queryuser/',methods=['POST'])
def queryuser():
    keyword=request.form['keyword']
    groupid=request.form['groupid']
    res=[]
    all_user=get_user_bykeyword(keyword)
    all_group_user=get_user_ingroup(groupid)
    for user in all_user:
        check=1
        for group_user in all_group_user:
            if group_user.id==user.id:
                check=0
                continue
        if check==1:
            content={
                'id':user.id,
                'username':user.username,
                'email':user.email,
                'description':user.description
            }
            res.append(content)
    return jsonify(res)

# 团队的leader邀请加入团队(发送邀请信息)
@groupRouter.route('/api/invite_user/',methods=['POST'])
def invite_user():
    group_id=request.form['group_id']
    group=Group.query.filter(Group.id==group_id).first()
    user_id=request.form['user_id']
    sender=User.query.filter(User.username==request.form['leader_username']).first()
    notice=Notice.query.filter(and_(and_(Notice.group_id==group_id,Notice.sender_id==sender.id),and_(Notice.type==2,Notice.receiver_id==user_id))).first()
    if(notice):
        response={
            'message':'success'
        }
        return jsonify(response)
    id=get_newid()
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=sender.username+"邀请你加入团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=sender.id,receiver_id=user_id,document_id=0,
        group_id=group_id,send_time=now,content=content,type=2
    )
    db.session.add(new_notice)
    db.session.commit()
    response={
        'message':'success'
    }
    return jsonify(response)

# 团队外用户申请加入某团队
@groupRouter.route('/api/apply_in_group/',methods=['POST'])
def apply_in_group():
    user=User.query.filter(User.username==request.form['username']).first()
    group=Group.query.filter(Group.groupname==request.form['groupname']).first()
    notice=Notice.query.filter(and_(and_(Notice.group_id==group.id,Notice.sender_id==user.id),and_(Notice.type==6,Notice.receiver_id==group.leaderid))).first()
    if(notice):
        response={
            'message':'success'
        }
        return jsonify(response)
    id=get_newid()
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=user.username+"申请加入团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=user.id,receiver_id=group.leaderid,document_id=0,
        group_id=group.id,send_time=now,content=content,type=6
    )
    db.session.add(new_notice)
    db.session.commit()
    response={
        'message':'success'
    }
    return jsonify(response)


# 作为团队leader，收到了来自用户的申请，我选择通过他的申请，加人，给申请人发一条消息
# 在我的group中添加用户，这里的用户是前端判断好的不在该group中的user
@groupRouter.route('/api/accept_application_addgroupmember/',methods=['POST'])
def accept_application_addgroupmember():
    userid=request.form['userid']
    user=User.query.filter(User.id==userid).first()
    groupid=request.form['groupid']
    group=Group.query.filter(Group.id==groupid).first()
    leader=User.query.filter(User.id==group.leaderid).first()
    id=get_newid()
    newGroupMember=GroupMember(id=id,user_id=userid,group_id=groupid)
    db.session.add(newGroupMember)
    db.session.commit()

    # 发送消息
    id=id+1
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=leader.username+"通过了你的申请，你已加入团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=leader.id,receiver_id=user.id,document_id=0,
        group_id=groupid,send_time=now,content=content,type=7
    )
    db.session.add(new_notice)
    db.session.commit()
    del_notice(request.form['id'])
    all_document=db.session.query(Document).filter(Document.group_id==groupid).all()
    for document in all_document:
        id=get_newid()
        newDU=DocumentUser(id=id,document_id=document.id,
            user_id=userid,last_watch=0,
            favorited=0,type=1,modified_time=0)
        db.session.add(newDU)
        db.session.commit()
    response={
        'message':'success'
    }
    return jsonify(response)

# 作为团队leader，收到了来自用户的申请，我选择拒绝他的申请，不加人，给申请人发一条消息
@groupRouter.route('/api/refuse_application_addgroupmember/',methods=['POST'])
def refuse_application_addgroupmember():
    userid=request.form['userid']
    user=User.query.filter(User.id==userid).first()
    groupid=request.form['groupid']
    group=Group.query.filter(Group.id==groupid).first()
    leader=User.query.filter(User.id==group.leaderid).first()
    id=get_newid()
    # 发送消息
    id=id+1
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=leader.username+"拒绝了你的申请，加入团队("+group.groupname+")失败"
    new_notice=Notice(id=id,sender_id=leader.id,receiver_id=user.id,document_id=0,
        group_id=groupid,send_time=now,content=content,type=8
    )
    db.session.add(new_notice)
    db.session.commit()
    del_notice(request.form['id'])
    response={
        'message':'success'
    }
    return jsonify(response)

# 显示该团队下的成员
# tested
@groupRouter.route('/api/get_user_bygroup/',methods=['POST'])
def get_user_bygroup():
    all_group_user=get_user_ingroup(request.form['groupid'])
    res=[]
    for user in all_group_user:
        content={
            'id':user.id,
            'username':user.username,
            'email':user.email
        }
        res.append(content)
    return jsonify(res)

# 删除团队成员
@groupRouter.route('/api/delete_user/',methods=['POST'])
def delete_user():
    groupid=request.form['groupid']
    group=Group.query.filter(Group.id==groupid).first()
    userid=request.form['userid']
    db.session.query(GroupMember).filter(and_(GroupMember.user_id==userid,GroupMember.group_id==groupid)).delete()
    db.session.commit()

    # 发送消息
    sender_id=request.form['leaderid']
    sender=User.query.filter(User.id==sender_id).first()
    id=get_newid()
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=sender.username+"将你踢出了团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=sender_id,receiver_id=userid,document_id=0,
        group_id=groupid,send_time=now,content=content,type=0
    )
    db.session.add(new_notice)
    db.session.commit()

    # 删除成员对应文档权限
    all_document=db.session.query(Document).filter(Document.group_id==groupid).all()
    for document in all_document:
        db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==userid)).delete()
        db.session.commit()
    return jsonify({'message':'success'})

# 团队成员主动退出团队
@groupRouter.route('/api/quit_group/',methods=['POST'])
def quit_group():
    groupid=request.form['groupid']
    group=Group.query.filter(Group.id==groupid).first()
    userid=request.form['userid']
    user=User.query.filter(User.id==userid).first()
    db.session.query(GroupMember).filter(and_(GroupMember.user_id==request.form['userid'],GroupMember.group_id==request.form['groupid'])).delete()
    db.session.commit()

    # 发送消息
    receiver_id=group.leaderid
    receiver=User.query.filter(User.id==receiver_id).first()
    id=get_newid()
    now=datetime.datetime.now()
    send_time=now.strftime('%Y-%m-%d')
    content=user.username+"退出了团队("+group.groupname+")"
    new_notice=Notice(id=id,sender_id=userid,receiver_id=receiver_id,document_id=0,
        group_id=groupid,send_time=now,content=content,type=9)
    db.session.add(new_notice)
    db.session.commit()

    # 删除成员对应文档权限
    all_document=db.session.query(Document).filter(Document.group_id==groupid).all()
    for document in all_document:
        db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==userid)).delete()
        db.session.commit()
    return jsonify({'message':'success'})

# 解散团队
@groupRouter.route('/api/delete_group/',methods=['POST'])
def delete_group():
    groupid=request.form['groupid']
    db.session.query(GroupMember).filter(GroupMember.group_id==request.form['groupid']).delete()
    db.session.query(Group).filter(Group.id==request.form['groupid']).delete()
    # 删除成员对应文档
    # 删除团队文档
    db.session.commit()
    all_document=db.session.query(Document).filter(Document.group_id==groupid).all()

    for document in all_document:
        db.session.query(DocumentUser).filter(DocumentUser.document_id==document.id).delete()
        
        db.session.commit()
    db.session.query(Document).filter(Document.group_id==groupid).delete()
    db.session.commit()
    return jsonify({'message':'success'})