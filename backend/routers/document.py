
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
documentRouter = Blueprint('document',__name__)

####################################
########## document 操作 ###############
####################################


# 创建个人文档 (同时赋予权限)
@documentRouter.route('/api/create_personal_doc/', methods=['POST'])
def create_personal_doc():
    msg=''
    if request.method == 'POST':
        id = get_newid()
        user = User.query.filter(User.username==request.form['username']).first()
        creator_id=user.id
        now=datetime.datetime.now()
        content=request.form['content']
        msg="success"
        newDocument=Document(id=id,title=request.form['title'], 
            creator_id=creator_id,created_time=now,
            modify_right=request.form['modify_right'],
            share_right=request.form['share_right'],
            discuss_right=request.form['discuss_right'],
            others_modify_right=request.form['modify_right'],
            others_share_right=request.form['share_right'],
            others_discuss_right=request.form['discuss_right'],
            content=content,recycled=0,is_occupied=0,
            group_id=0,
            modified_time=0)
        db.session.add(newDocument)
        db.session.commit()

        id=get_newid()
        newDU=DocumentUser(id=id,document_id=newDocument.id,
            user_id=user.id,last_watch=0,
            favorited=0,modified_time=0,type=0)
        db.session.add(newDU)
        db.session.commit()
        # # 赋予创建者以文档的全部权限
        # share_right=1
        # watch_right=1
        # modify_right=1
        # delete_right=1
        # discuss_right=1
        # document=newDocument
        # newDocumentUser=DocumentUser(id=id,document_id=document.id,user_id=user.id,
        #     share_right=share_right,watch_right=watch_right,modify_right=modify_right,
        #     delete_right=delete_right,discuss_right=discuss_right
        # )
        # db.session.add(newDocumentUser)
        # db.session.commit()
    response={
        'message':msg,
        'newDocumentId':id
    }
    return jsonify(response)

# 创建团队文档 (同时赋予权限)
@documentRouter.route('/api/create_group_doc/', methods=['POST'])
def create_group_doc():
    msg=''
    if request.method == 'POST':
        id = get_newid()
        user = User.query.filter(User.username==request.form['username']).first()
        creator_id=user.id
        now=datetime.datetime.now()
        content=request.form['content']
        group_id=request.form['group_id']
        msg="success"
        newDocument=Document(id=id,title=request.form['title'], 
            creator_id=creator_id,created_time=now,
            modify_right=request.form['modify_right'],
            share_right=request.form['share_right'],
            discuss_right=request.form['discuss_right'],
            others_modify_right=request.form['others_modify_right'],
            others_share_right=request.form['others_share_right'],
            others_discuss_right=request.form['others_discuss_right'],
            content=content,recycled=0,is_occupied=0,
            group_id=group_id,modified_time=0)
        db.session.add(newDocument)
        db.session.commit()

        id=get_newid()
        i=1
        all_member=GroupMember.query.filter(GroupMember.group_id==group_id).all()
        for member in all_member:
            newDU=DocumentUser(id=id+i,document_id=newDocument.id,
            user_id=member.user_id,last_watch=0,
            favorited=0,modified_time=0,type=1)
            i=i+1
            db.session.add(newDU)
        db.session.commit()

        # # 赋予创建者以文档的全部权限
        # share_right=1
        # watch_right=1
        # modify_right=1
        # delete_right=1
        # discuss_right=1
        # document=newDocument
        # newDocumentUser=DocumentUser(id=id,document_id=document.id,user_id=user.id,
        #     share_right=share_right,watch_right=watch_right,modify_right=modify_right,
        #     delete_right=delete_right,discuss_right=discuss_right
        # )
        # db.session.add(newDocumentUser)
        # db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

# 查看我拥有的文档(除团队文档外的文档)
@documentRouter.route('/api/my_docs/',methods=['POST'])
def my_docs():
    user=User.query.filter(User.username==request.form['username']).first()
    all_du=DocumentUser.query.filter(DocumentUser.user_id==user.id).all()
    res=[]
    for du in all_du:
        doc=Document.query.filter(du.document_id==Document.id).first()
        if doc.recycled == 0 and du.type != 1:
            res.append(document_to_content(doc))
    return jsonify(res)

# 获取我创建的所有文档的信息
@documentRouter.route('/api/my_created_docs/',methods=['POST'])
def my_created_docs():
    user=User.query.filter(User.username==request.form['username']).first()
    all_document=Document.query.filter(and_(Document.creator_id==user.id,Document.recycled==0)).all()
    res=[]
    for document in all_document:
        if document.recycled == 0:
            res.append(document_to_content(document))
    return jsonify(res)

@documentRouter.route('/api/my_deleted_docs/',methods=['POST'])
def my_deleted_docs():
    user=User.query.filter(User.username==request.form['username']).first()
    all_document=Document.query.filter(and_(Document.creator_id==user.id,Document.recycled==1)).all()
    res=[]
    for document in all_document:
        res.append(document_to_content(document))
    return jsonify(res)

# 传递权限信息
@documentRouter.route('/api/tell_doc_right/',methods=['POST'])
def tell_doc_right():
    document = Document.query.filter(Document.id == request.form['DocumentID']).first()
    user=User.query.filter(User.username==request.form['username']).first()
    DUlink=db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
    if(DUlink==None):
        response={
            'watch_right':False,
            'modify_right':False,
            'share_right':False,
            'discuss_right':False,
            'others_modify_right':False,
            'others_share_right':False,
            'others_discuss_right':False,
            'others_watch_right':False,
            'doctype':-1,
            'usertype':-1,
            'isleader':False
        }
    elif user.id==document.creator_id:
        if document.group_id!=0:
            type=0
        else:
            type=1
        response={
            'watch_right':True,
            'modify_right':True,
            'share_right':True,
            'discuss_right':True,
            'others_modify_right':True,
            'others_share_right':True,
            'others_discuss_right':True,
            'others_watch_right':True,
            'doctype':type,
            'usertype':DUlink.type,
            'isleader':True
        }
    else:
        if document.group_id!=0:
            type=0
        else:
            type=1

        modify_right=toTF(document.modify_right)
        share_right=toTF(document.share_right)
        discuss_right=toTF(document.discuss_right)
        
        others_modify_right=toTF(document.others_modify_right)
        others_share_right=toTF(document.others_share_right)
        others_discuss_right=toTF(document.others_discuss_right)
        response={
            'watch_right':True,
            'modify_right':modify_right,
            'share_right':share_right,
            'discuss_right':discuss_right,
            'others_modify_right':others_modify_right,
            'others_share_right':others_share_right,
            'others_discuss_right':others_discuss_right,
            'others_watch_right':True,
            'doctype':type,
            'usertype':DUlink.type,
            'isleader':False
        }
    return jsonify(response)     

# 告知文档当前权限
@documentRouter.route('/api/tell_current_doc_right/',methods=['POST'])
def tell_current_doc_right():
    document = Document.query.filter(Document.id == request.form['DocumentID']).first()
    response={
        'modify_right':document.modify_right,
        'share_right':document.share_right,
        'discuss_right':document.discuss_right,
        'others_modify_right':document.others_modify_right,
        'others_share_right':document.others_share_right,
        'others_discuss_right':document.others_discuss_right,
    }
    return jsonify(response)

# 获取文档
@documentRouter.route('/api/get_doccontent/', methods=['POST'])
def get_doccontent():
    print(session)
    msg=''
    mcontent=''
    mtime=datetime.datetime.now()
    if request.method == 'POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user=User.query.filter(User.username==request.form['username']).first()
        if (document==None) or (user==None):
            msg="fail"
            mcontent=""
            response={
                'message':msg,
                'content':mcontent
            }
            return jsonify(response)
        DUlink=db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        # mtime=DUlink.last_watch
        # 判断用户是否有权限查看该文档
        # 初步完善
        # TODO: 目前只有创建者能查看文档(已修正)
        # TODO: 目前任何参与者都可以查看文档
        if (document!=None) and (DUlink!=None):
            msg="success"
            mcontent=document.content
            now=datetime.datetime.now()
            mtime=now
            db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"last_watch":now})
            db.session.commit()
            # DUlink=db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        else:
            msg="fail"
            mcontent=""
    response={
        'message':msg,
        'content':mcontent,
        'time':mtime
    }
    return jsonify(response)


#获取文档标题
@documentRouter.route('/api/get_doctitle/',methods=['POST'])
def get_doctitle():
    msg=''
    mtitle=''
    mtime=datetime.datetime.now()
    if request.method == 'POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user=User.query.filter(User.username==request.form['username']).first()
        if (document==None) or (user==None):
            msg="fail"
            mcontent=""
            response={
                'message':msg,
                'title':mtitle
            }
            return jsonify(response)
        DUlink=db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        # mtime=DUlink.last_watch
        # 判断用户是否有权限查看该文档
        # 初步完善
        # TODO: 目前只有创建者能查看文档(已修正)
        # TODO: 目前任何参与者都可以查看文档
        if (document!=None) and (DUlink!=None):
            msg="success"
            mtitle=document.title
            now=datetime.datetime.now()
            mtime=now
            db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"last_watch":now})
            db.session.commit()
            # DUlink=db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        else:
            msg="fail"
            mtitle=""
    response={
        'message':msg,
        'title':mtitle,
        'time':mtime
    }
    return jsonify(response)

# 获取团队所有没有被删除的文档
@documentRouter.route('/api/get_group_docs/',methods=['POST'])
def get_group_docs():
    all_document=Document.query.filter(and_(Document.group_id==request.form['group_id'],Document.recycled==0)).all()
    res=[]
    for document in all_document:
        res.append(document_to_content(document))
    return jsonify(res)


# 修改文档
@documentRouter.route('/api/modify_doc/', methods=['POST'])
def modify_doc():
    msg=''
    if request.method == 'POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        # TODO: 目前只有创建者能修改文档
        msg="success"
        now=datetime.datetime.now()
        content=request.form['content']
        db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"content":content,
            "modified_time":now
        })
        db.session.query(DocumentUser).filter(and_(DocumentUser.user_id==user.id,
            DocumentUser.document_id==request.form['DocumentID'])).update({"modified_time":now})
        db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

# 文档想要分享给其他用户前，需要先检索用户，根据用户名检索，返回所有不拥有该文档的用户
# tested
@documentRouter.route('/api/query_notindoc_user/',methods=['POST'])
def query_notindoc_user():
    keyword=request.form['keyword']
    document_id=request.form['document_id']
    res=[]
    all_user=get_user_bykeyword(keyword)
    all_document_user=get_user_indocument(document_id)
    for user in all_user:
        if user not in all_document_user:
            content={
                'id':user.id,
                'username':user.username,
                'email':user.email
            }
            res.append(content)
    return jsonify(res)

# 个人文档分享
@documentRouter.route('/api/pernal_doc_share_to/',methods=['POST'])
def personal_share_to():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.id==request.form['user_id']).first()
        target_user=User.query.filter(User.id==request.form['target_user_id']).first()
        id=get_newid()
        newDU=DocumentUser(id=id,document_id=document.id,
            user_id=target_user.id,last_watch=0,
            favorited=0,type=0,modified_time=0)
        
        # 发送消息
        id=get_newid()
        now=datetime.datetime.now()
        send_time=now.strftime('%Y-%m-%d')
        content=user.username+"分享给你了一个文档("+document.title+")"
        new_notice=Notice(id=id,sender_id=user.id,receiver_id=target_user.id,document_id=document.id,
            group_id=0,send_time=now,content=content,type=4
        )
        msg='success'
        db.session.add(new_notice)
        db.session.add(newDU)
        db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

# 团队文档分享
@documentRouter.route('/api/group_doc_share_to/',methods=['POST'])
def group_doc_share_to():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.id==request.form['user_id']).first()
        target_user=User.query.filter(User.id==request.form['target_user_id']).first()
        id=get_newid()
        newDU=DocumentUser(id=id,document_id=document.id,
            user_id=target_user.id,last_watch=0,
            favorited=0,type=2,modified_time=0)
        
        # 发送消息
        id=get_newid()
        now=datetime.datetime.now()
        send_time=now.strftime('%Y-%m-%d')
        content=user.username+"分享给你了一个文档("+document.title+")"
        new_notice=Notice(id=id,sender_id=user.id,receiver_id=target_user.id,document_id=document.id,
            group_id=0,send_time=now,content=content,type=4
        )
        msg='success'
        db.session.add(new_notice)
        db.session.add(newDU)
        db.session.commit()
    response={
        'message':msg
    }
    return jsonify(response)

# 收藏文档
@documentRouter.route('/api/favor_doc/', methods=['POST'])
def favor_doc():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        if document!=None and DUlink.favorited==0:
            msg='success'
            db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"favorited":1})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 取消收藏文档
@documentRouter.route('/api/cancel_favor_doc/', methods=['POST'])
def cancel_favor_doc():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        if document!=None and DUlink.favorited==1:
            msg='success'
            db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).update({"favorited":0})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 查看我收藏的文档
# 收藏的，并且没删除的
@documentRouter.route('/api/my_favor_doc/',methods=['POST'])
def my_favor_doc():
    user=User.query.filter(User.username==request.form['username']).first()
    DUlink=DocumentUser.query.filter(and_(DocumentUser.favorited==1,DocumentUser.user_id==user.id)).all()
    res=[]
    for dulink in DUlink:
        document=Document.query.filter(and_(Document.id==dulink.document_id,Document.recycled==0)).first()
        if(document):
            res.append(document_to_content(document))
    return jsonify(res)

# 修改文档基本信息
@documentRouter.route('/api/modify_doc_basic/',methods=['POST'])
def modify_doc_basic():
    document = Document.query.filter(Document.id == request.form['DocumentID']).first()
    user = User.query.filter(User.username==request.form['username']).first()
    if(user.id == document.creator_id):
        db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"title":request.form['title']})
        db.session.commit()
        return sendmsg("success")
    return sendmsg("fail")

# 个人文档创建者将文档设置为私密文档（在点击该按钮时，显示提示信息，其他协作者将看不到该文档）
@documentRouter.route('/api/set_document_private/',methods=['POST'])
def set_document_private():
    document = Document.query.filter(Document.id == request.form['DocumentID']).first()
    user = User.query.filter(User.username==request.form['username']).first()
    if(user.id == document.creator_id):
        db.session.query(DocumentUser).filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id!=user.id)).delete()
        db.session.commit()
        return sendmsg("success")
    return sendmsg("fail")

# 团队中的文档，文档创建者将其设置为私密文档（组内将删除该团队文档，转为该创建者的个人文档）
@documentRouter.route('/api/group_doc_to_personal/',methods=['POST'])
def group_doc_to_personal():
    document = Document.query.filter(Document.id == request.form['DocumentID']).first()
    user = User.query.filter(User.username==request.form['username']).first()
    if(user.id == document.creator_id):
        DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id!=user.id)).delete()
        Document.query.filter(Document.id==document.id).update({"group_id":0})
        db.session.commit()
        return sendmsg("success")
    return sendmsg("fail")

# 文档删除到回收站中
@documentRouter.route('/api/recycle_doc/', methods=['POST'])
def recycle_doc():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        # if (document!=None) and (DUlink.delete_right==1)and (document.recycled==0):
        if (document!=None) and (document.recycled==0) and (document.creator_id==user.id):
            msg='success'
            db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"recycled":1})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

@documentRouter.route('/api/recycle_doc_2/', methods=['POST'])
def recycle_doc_2():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        if (document!=None) and (document.recycled==0):
            msg='success'
            db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"recycled":1})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 文件从回收站中删除变成二级删除状态
@documentRouter.route('/api/del_doc/', methods=['POST'])
def del_doc():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        # if (document!=None) and (DUlink.delete_right==1) and (document.recycled==1):
        if (document!=None) and (document.recycled==1) and (document.creator_id==user.id):
            msg='success'
            db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"recycled":2})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 文档从回收站中恢复
@documentRouter.route('/api/recover_doc/', methods=['POST'])
def recover_doc():
    msg=''
    if request.method=='POST':
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        # if (document!=None) and (DUlink.delete_right==1)and (document.recycled==0):
        if (document!=None) and (document.recycled==1) and (document.creator_id==user.id):
            msg='success'
            db.session.query(Document).filter(Document.id==request.form['DocumentID']).update({"recycled":0})
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 文档彻底删除操作
@documentRouter.route('/api/del_complete_doc/', methods=['POST'])
def del_complete_doc():
    msg=''
    if request.method=='POST':
        id=get_newid()
        document = Document.query.filter(Document.id == request.form['DocumentID']).first()
        user = User.query.filter(User.username==request.form['username']).first()
        DUlink=DocumentUser.query.filter(and_(DocumentUser.document_id==document.id,DocumentUser.user_id==user.id)).first()
        print(document!=None)
        print(document.recycled)
        print(DUlink.delete_right)
        #if (document!=None) and (document.recycled==1) and (DUlink.delete_right==1):
        if (document!=None) and (document.recycled==1) and (document.creator_id==user.id):
            msg='success'
            db.session.query(DocumentUser).filter(DocumentUser.document_id==document.id).delete()
            db.session.query(Comment).filter(Comment.document_id==document.id).delete()
            db.session.query(Document).filter(Document.id==document.id).delete()
            db.session.commit()
        else:
            msg='fail'
    response={
        'message':msg
    }
    return jsonify(response)

# 显示最近使用文档
@documentRouter.route('/api/show_recent_doc/', methods=['POST'])
def show_recent_doc():
    res=[]
    user = get_user_byusername(request.form['username'])
    all_documentuser=db.session.query(DocumentUser).filter(and_(DocumentUser.user_id==user.id,DocumentUser.last_watch!=0)).order_by(-DocumentUser.last_watch).all()
    for DU in all_documentuser:
        document=db.session.query(Document).filter(Document.id==DU.document_id).first()
        if(document==None):
            continue
        if document.recycled == 0:
            res.append(document_to_content(document))
    return jsonify(res)
