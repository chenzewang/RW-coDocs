const Socket = require('./socket')

const docApi = require('../dao/api/doc')


class Doc {

  constructor(id, connection, callback) {
    this.id = id.toString()
    this.members = []
    this.sockets = []
    this.indexCount = 0
    this.create(connection, id, callback)
  }

  /**
   * 
   * @param {*} connection 
   * @param {*} callback 
   * @returns 
   */
  create(connection, documentId, callback) {
    callback = callback || function () {}
    // console.log(this.id)
    const doc = connection.get('multiDoc', this.id)
    doc.fetch(function (err) {
      if (err) throw err
      if (doc.type === null) {
        docApi.getDocumentContent(documentId).then(res => {
          // console.log(res);
          doc.create({
            content: res[0].content
          }, callback)
          return
        })
      }
      callback()
    })
    return doc
  }

  getMembers() {
    return this.members
  }

  getSockets() {
    return this.sockets
  }

  /**
   * 
   * @param {*} token 
   * @param {*} connection 
   * @param {*} member 
   * @param {*} callback 回调
   * @param {*} closeBack 
   */
  addSocket(token, connection, member, callback, closeBack) {
    this.indexCount++
    const socket = new Socket(token, member, connection)

    socket.on("close", () => {
      const socketIndex = this.sockets.findIndex(socket => socket.token === token)
      if (socketIndex > -1) {
        this.sockets.splice(socketIndex, 1)
      }

      const memberIndex = this.members.findIndex(m => m.uuid === member.uuid)
      if (memberIndex > -1) {
        const leaveMember = this.members[memberIndex]
        this.members.splice(memberIndex, 1)
        this.sockets.forEach(socket => {
          socket.sendMessage("members", this.members)
          socket.sendMessage("leave", leaveMember)
        })
      }
      if (closeBack && this.sockets.length === 0) {
        closeBack(this.id)
      }
    })

    socket.on("message", message => {
      const data = JSON.parse(message)
      if (data.action === "broadcast") {
        this.sockets.forEach(socket => {
          socket.sendMessage("broadcast", data.data)
        })
      }
      if (data.action === "vCaretInsert") {
        this.sockets.forEach(socket => {
          socket.sendMessage("vCaretInsert", data.data)
        })
      }
    })
    member.iid = this.indexCount

    this.members.push(member)
    this.sockets.push(socket)
    this.sockets.forEach(socket => {
      socket.sendMessage("members", this.members)
      socket.sendMessage("join", member)
    })
    socket.sendMessage("ready", member, callback)
  }
}

module.exports = Doc