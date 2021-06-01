
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_,not_,func
from models import *
from manage import *
from flask_cors import CORS
import config
import datetime,time

#router
from routers.user import userRouter
from routers.group import groupRouter
from routers.document import documentRouter
from routers.right import rightRouter
from routers.comment import commentRouter
from routers.notice import noticeRouter
from routers.message import messageRouter
#end router


app = Flask(__name__,
            static_folder = "../frontend/dist/static",
            template_folder = "../frontend/dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config.from_object(config)
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'
db = SQLAlchemy(app)

app.register_blueprint(userRouter)
app.register_blueprint(groupRouter)
app.register_blueprint(documentRouter)
app.register_blueprint(rightRouter)
app.register_blueprint(commentRouter)
app.register_blueprint(noticeRouter)
app.register_blueprint(messageRouter)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def home(path):
    return render_template("index.html")


if __name__ == '__main__':
    # from werkzeug.contrib.fixers import ProxyFix
    # app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(debug = True)