const http = require('http');
const WebSocket = require('ws');
const { createBroker } = require('pubsub-ws');
const express = require('express');
const bodyParser = require('body-parser');
const operations = require('./dbOps');
const { Session, SessionManager } = require("./session");
const { Turn } = require("./sessionObjects");

const app = express();
app.use(bodyParser.json());

const server = http.createServer({}, app);
const sessionManager = new SessionManager(server);

app.get("/createGame/:numSectors/", function(req, res, next) {
  const numSectors = parseInt(req.params.numSectors);
  operations.pickGame(numSectors).then(({game, gameCode}) => {
    res.json({game, gameCode});
  });
});

app.get("/joinGame/:gameCode/", function(req, res, next) {
  operations.getGameByGameCode(req.params.gameCode).then(({game, gameCode}) => {
    res.json({game, gameCode});
  });
});

app.post("/createSession/:numSectors/", function(req, res, next) {
  const numSectors = parseInt(req.params.numSectors);
  sessionManager.createSession(numSectors, req.query.name).then(async ({playerID, playerNum, session}) => {
    const gameJson = await session.gameJson();
    const stateJson = await session.stateJson();
    res.json({
      playerID,
      playerNum,
      game: gameJson,
      state: stateJson
    });
  });
});

app.post("/joinSession/:sessionCode/", function(req, res, next) {
  sessionManager.joinSession(req.params.sessionCode, req.query.name).then(async ({playerID, playerNum, session}) => {
    const gameJson = await session.gameJson();
    const stateJson = await session.stateJson();
    res.json({
      playerID,
      playerNum,
      game: gameJson,
      state: stateJson
    });
  });
});

app.get("/reconnectSessionID/:sessionID", function(req, res, next) {
  const sessionID = parseInt(req.params.sessionID);
  Session.findByID(sessionID).then(async (session) => {
    const gameJson = await session.gameJson();
    const stateJson = await session.stateJson();
    res.json({
      game: gameJson,
      state: stateJson
    })
  });
});

app.get("/reconnectSessionCode/:sessionCode", function(req, res, next) {
  Session.findByCode(req.params.sessionCode).then(async (session) => {
    const gameJson = await session.gameJson();
    const stateJson = await session.stateJson();
    res.json({
      game: gameJson,
      state: stateJson
    })
  });
});

app.post("/startGame/", function(req, res, next) {
  const sessionID = parseInt(req.query.sessionID);
  const playerID = parseInt(req.query.playerID);
  sessionManager.startGame(sessionID, playerID).then(() => {
    res.send();
  });
});

app.post("/submitTheories/", function(req, res, next) {
  const sessionID = parseInt(req.query.sessionID);
  const playerID = parseInt(req.query.playerID);
  sessionManager.submitTheories(sessionID, playerID, req.body.theories).then((result) => {
    res.json(result);
  });
});

app.post("/readConference/", function(req, res, next) {
  const sessionID = parseInt(req.query.sessionID);
  const playerID = parseInt(req.query.playerID);
  sessionManager.readConference(sessionID, playerID).then((allowed) => {
    res.json({ allowed })
  });
});

app.post("/makeMove/", function(req, res, next) {
  const sessionID = parseInt(req.query.sessionID);
  const playerID = parseInt(req.query.playerID);
  const sectors = req.body.timeCost;
  const turnData = Object.assign({sessionID: req.query.sessionID, playerID: req.query.playerID}, req.body);
  const turn = Turn.fromJson(turnData);
  sessionManager.makeMove(sessionID, playerID, turn, sectors).then((allowed) => {
    res.json({ allowed });
  });
});

server.listen(8000);
