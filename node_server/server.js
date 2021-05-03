const http = require('http');
const WebSocket = require('ws');
const { createBroker } = require('pubsub-ws');
const express = require('express');

const app = express();

app.get("/test", function(req, res, next) {
  res.json({hi: "hi"});
});

const server = http.createServer({}, app);

const broker = createBroker(server, (req) => {
  return Promise.resolve("myChannel")
});

server.listen(7123);

const ws = new WebSocket('ws://localhost:7123');
ws.on('open', () => console.log('ws open'));
ws.on('message', (data) => console.log(`received message: ${data}`));

setInterval(() => {
  broker.publish('myChannel', 'test data');
}, 2000);
