const http = require('http');
const express = require('express')
const WebSocket = require('ws')
const bodyParser = require('body-parser')
const Client = require('./comp/client')


function startServer() {
  // Create a web server to serve files and listen to WebSocket connections
  const app = express()

  app.use(bodyParser.json({
    limit: '10mb'
  }))
  app.use(bodyParser.urlencoded({
    extended: false
  }))

  const server = http.createServer(app)

  const client = new Client()
  // Connect any incoming WebSocket connection to ShareDB
  const webSocketServer = new WebSocket.Server({
    server: server
  });
  webSocketServer.on('connection', (connection, request) => {
    client.addDocV2(connection, request)
  })

  webSocketServer.on('error', (err) => {
    console.log("-------", err);
  })

  webSocketServer.on('close', (ws) => {
    console.log(ws);
  })

  server.listen(8088)
  console.log('Listening on http://localhost:8088');
}


startServer()