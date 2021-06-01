const url = require('url')
const querystring = require("querystring")
const requestPromise = require('request-promise')
const ShareDB = require('sharedb')
const WebSocketJSONStream = require('@teamwork/websocket-json-stream')
const uuidv3 = require('uuid/v3')
const userApi = require('../dao/api/user')
const Doc = require('./doc')
const {
  log
} = require('console')

class Client {
  constructor() {
    this.docs = []
    const sharedb = new ShareDB()
    this.sharedb = sharedb
    this.sharedbConnection = sharedb.connect()
  }

  getDoc(id) {
    return this.docs.find(
      doc => doc.id === id
    )
  }

  getParams(request) {
    return querystring.parse(url.parse(request.url).query)
  }

  /**
   * 添加一篇正在协作编辑的文档
   * @param {*} conection 新建的ws connection
   * @param {*} request 
   * @returns 
   */
  addDocV2(conection, request) {
    const params = this.getParams(request)
    const {
      documentId,
      token,
      userId
    } = params
    if (!documentId || !userId) {
      conection.close()
      return
    }

    userApi.getUserInfo(userId).then(userInfo => {
      // console.log(params);
      console.log('userinfo', userInfo);
      userInfo = userInfo[0]

      //要广播给各个订阅的客户端
      const member = {
        id: userInfo.id,
        key: userInfo.login || userInfo.mobile || userInfo.email || userInfo.id,
        name: userInfo.username,
        email: userInfo.email,
        uuid: uuidv3(documentId.concat("/" + userInfo.id), uuidv3.URL)
      }

      let doc = this.getDoc(documentId)
      if (!doc) {
        doc = new Doc(documentId, this.sharedbConnection)
        this.docs.push(doc)
      } else {
        // 关闭此用户此文档之前未关闭的链接
        doc.sockets.forEach(socket => {
          if (socket.member.id === member.id) {
            // socket.connection.close()
          }
        });
      }

      doc.addSocket(token, conection, member, () => {
        // 建立协作 socket 连接
        const stream = new WebSocketJSONStream(conection)
        // 监听消息
        this.sharedb.listen(stream)
      }, doc_id => {
        // 没有编辑用户了，移除文档
        const docIndex = this.docs.findIndex(d => d.id === doc_id)
        if (docIndex > -1) {
          this.docs.splice(docIndex, 1)
        }
      })

      // this.docs.push(doc)


    }).catch(err => {
      console.log(err);
    })



  }

}
module.exports = Client