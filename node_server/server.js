const http = require('http');
const WebSocket = require('ws');
const { createBroker } = require('pubsub-ws');
const express = require('express');
const operations = require('./dbOps');
const { Session, SessionManager } = require("./session");
const { Turn } = require("./sessionObjects");

const app = express();
const server = http.createServer({}, app);
const sessionManager = new SessionManager(server);

app.get("/createGame/:numSectors/", function(req, res, next) {
  operations.pickGame(req.params.numSectors).then(({game, gameCode}) => {
    res.json({game, gameCode});
  });
});

app.get("/joinGame/:gameCode/", function(req, res, next) {
  operations.getGameByGameCode(req.params.gameCode).then(({game, gameCode}) => {
    res.json({game, gameCode});
  });
});

app.post("/createSession/:numSectors/", function(req, res, next) {
  sessionManager.createSession(req.params.numSectors, req.query.name).then(async ({playerID, playerNum, session}) => {
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

app.post("/startGame/", function(req, res, next) {
  sessionManager.startGame(req.query.sessionID, req.query.playerID).then(() => {
    res.send();
  });
});

app.post("/submitTheories/", function(req, res, next) {
  sessionManager.submitTheories(req.query.sessionID, req.query.playerID, req.body.theories).then((result) => {
    res.json(result);
  });
});

app.post("/readConference/", function(req, res, next) {
  sessionManager.readConference(req.query.sessionID, req.query.playerID).then((allowed) => {
    res.json({ allowed })
  });
});

app.post("/makeMove/", function(req, res, next) {
  const sectors = req.body.timeCost;
  const turn = Turn.fromJson(req.body);
  sessionManager.makeMove(req.query.sessionID, req.query.playerID, turn, sectors).then((allowed) => {
    res.json({ allowed });
  });
});

server.listen(8000);
