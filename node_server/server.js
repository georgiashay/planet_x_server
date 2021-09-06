const http = require('http');
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const axios = require('axios');
const { encodeWebSocketEvents, decodeWebSocketEvents, WebSocketContext, Publisher } = require('@fanoutio/grip');

const operations = require('./dbOps');
const { Session, SessionManager } = require("./session");
const { Turn, Theory } = require("./sessionObjects");

const websocketEventParser = async function(req, res, next) {
  if(req.is("application/websocket-events")) {
    let cid = req.headers['connection-id'];
    if (Array.isArray(cid)) {
      cid = cid[0];
    }

    const inEventsEncoded = await new Promise(resolve => {
      let body = '';
      req.on('data', function (chunk) {
        body += chunk;
      });
      req.on('end', function() {
        resolve(body);
      });
    });

    const inEvents = decodeWebSocketEvents(inEventsEncoded);
    const wsContext = new WebSocketContext(cid, {}, inEvents);
    req.wsContext = wsContext;
    next();
  } else {
    next();
  }
}

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(websocketEventParser);

app.set("trust proxy", true);

let pushpinIPs;
const server = http.createServer({}, app);
const sessionManager = new SessionManager();

const refreshPublisher = function() {
  const config = pushpinIPs.map((ip) => {
    return {
      'control_uri': 'http://' + ip + ":5561"
    }
  });
  const publisher = new Publisher(config);
  sessionManager.setPublisher(publisher);
}

const setup = async function() {
  let IS_PROD;
  if (process.env.LANDSCAPE === "PRODUCTION") {
    IS_PROD = true;
  } else {
    IS_PROD = false;
  }

  console.log(JSON.stringify({level: "info", message: "Production: " + IS_PROD}));

  if (IS_PROD) {
    axios.get("http://prouter.prouter/pushpinIPs").then((response) => {
      pushpinIPs = response.data.ips;
      refreshPublisher();
      console.log(JSON.stringify({level: "info", message: "pushpin IPs: " + pushpinIPs}));
      return Promise.resolve();
    });
  } else {
    pushpinIPs = ["localhost"];
    refreshPublisher();
    return Promise.resolve();
  }
}


app.get("/createGame/:numSectors/", function(req, res, next) {
  const numSectors = parseInt(req.params.numSectors);
  const theme = req.query.theme || "space";
  operations.pickGame(numSectors).then(({game, gameCode}) => {
    if (game == undefined) {
      res.json({success: false});
    } else {
      res.json({success: true, game: game.json(theme), gameCode});
    }
  });
});

app.get("/joinGame/:gameCode/", function(req, res, next) {
  const theme = req.query.theme || "space";
  operations.getGameByGameCode(req.params.gameCode).then(({game, gameCode}) => {
    if (game == undefined) {
      res.json({found: false});
    } else {
      res.json({found: true, game: game.json(theme), gameCode});
    }
  });
});

app.post("/createSession/:numSectors/", function(req, res, next) {
  const numSectors = parseInt(req.params.numSectors);
  const theme = req.body.theme || "space";
  sessionManager.createSession(numSectors, req.body.name).then(async ({playerID, playerNum, session}) => {
    const gameJson = await session.gameJson(theme);
    const stateJson = await session.stateJson(theme);
    console.log(JSON.stringify({level: "info", action: "Create Session", sectors: numSectors, name: req.body.name, success: true }));
    res.json({
      playerID,
      playerNum,
      game: gameJson,
      state: stateJson
    });
  }).catch((err) => {
    console.log(JSON.stringify({level: "error", action: "Create Session", sectors: numSectors, name: req.body.name, success: false, error: err.message }));
  })
});

app.post("/joinSession/:sessionCode/", function(req, res, next) {
  const theme = req.body.theme || "space";
  sessionManager.joinSession(req.params.sessionCode, req.body.name).then(async ({playerID, playerNum, session}) => {
    if (session == undefined) {
      console.log(JSON.stringify({level: "info", action: "Join Session", name: req.body.name, sessionCode: req.params.sessionCode, found: false}));
      res.json({ found: false });
    } else {
      console.log(JSON.stringify({level: "info", action: "Join Session", name: req.body.name, sessionCode: req.params.sessionCode, found: true}));
      const gameJson = await session.gameJson(theme);
      const stateJson = await session.stateJson(theme);
      res.json({
        found: true,
        playerID,
        playerNum,
        game: gameJson,
        state: stateJson
      });
    }
  }).catch((err) => {
    console.log(JSON.stringify({level: "error", action: "Join Session", name: req.body.name, sessionCode: req.params.sessionCode, error: err.message }));
  });
});

app.get("/reconnectSession/:sessionCode", function(req, res, next) {
  const sessionCode = req.params.sessionCode;
  const playerNum = parseInt(req.query.playerNum);
  const theme = req.query.theme || "space";
  Session.findByCode(sessionCode).then(async (session) => {
    const gameJson = await session.gameJson(theme);
    const stateJson = await session.stateJson(theme);
    const players = await session.getPlayers();
    const myPlayers = players.filter((player) => player.num === playerNum);
    if (myPlayers.length == 0) {
      console.log(JSON.stringify({level: "info", action: "Reconnect Session", sessionCode, playerNum, found: false}));
      res.json({
        found: false
      });
    } else {
      console.log(JSON.stringify({level: "info", action: "Reconnect Session", sessionCode, playerNum, found: true}));
      const player = myPlayers[0];
      res.json({
        found: true,
        game: gameJson,
        state: stateJson,
        playerID: player.playerID,
        playerNum: player.num,
        playerName: player.name
      });
    }
  }).catch((err) => {
    console.log(JSON.stringify({level: "error", action: "Reconnect Session", sessionCode, playerNum, error: err.message }));
  });
});

app.post("/setColor", function(req, res, next) {
  const playerID = parseInt(req.query.playerID);
  const color = parseInt(req.query.color);
  sessionManager.setColor(playerID, color).then((allowed) => {
    console.log(JSON.stringify({level: "info", action: "Set Color", playerID, color, allowed}));
    res.json({allowed});
  }).catch((err) => {
    console.log(JSON.stringify({level: "error", action: "Set Color", playerID, color, error: err.message }));
  });
});

app.post("/castKickVote", function(req, res, next) {
  const sessionID = parseInt(req.query.sessionID);
  const playerID = parseInt(req.query.playerID);
  const kickPlayerID = req.body.kickPlayerID;
  const vote = req.body.vote;
  sessionManager.castKickVote(sessionID, playerID, kickPlayerID, vote).then((allowed) => {
    console.log(JSON.stringify({level: "info", action: "Cast Kick Vote", sessionID, playerID, kickPlayerID, vote, allowed}));
    res.json({allowed});
  }).catch((err) => {
    console.log(JSON.stringify({level: "error", action: "Cast Kick Vote", sessionID, playerID, kickPlayerID, vote, error: err.message}));
  });
});

app.post("/startSession/", function(req, res, next) {
  const sessionID = parseInt(req.query.sessionID);
  const playerID = parseInt(req.query.playerID);
  sessionManager.startSession(sessionID, playerID).then((result) => {
    console.log(JSON.stringify({level: "info", action: "Start Session", sessionID, playerID, allowed: result }));
    res.json({allowed: result});
  }).catch((err) => {
    console.log(JSON.stringify({level: "error", action: "Start Session", sessionID, playerID, error: err.message }));
  });
});

app.post("/submitTheories/", function(req, res, next) {
  const sessionID = parseInt(req.query.sessionID);
  const playerID = parseInt(req.query.playerID);
  const turn = req.body.turn;
  const theme = req.body.theme || "space";
  const theories = req.body.theories.map((t) => Theory.fromJson(t, theme));
  sessionManager.submitTheories(sessionID, playerID, theories, turn).then(({ allowed, successfulTheories}) => {
    console.log(JSON.stringify({level: "info", action: "Submit Theories", sessionID, playerID, theories: theories.map((t) => t.json(theme)), allowed: allowed, successfulTheories: successfulTheories.map((t) => t.json(theme))}));
    res.json({
      allowed,
      successfulTheories: successfulTheories.map((t) => t.json(theme))
    });
  }).catch((err) => {
    console.log(JSON.stringify({level: "error", action: "Submit Theories", sessionID, playerID, theories: theories.map((t) => t.json(theme)), error: err.message }));
  });
});

app.post("/readConference/", function(req, res, next) {
  const sessionID = parseInt(req.query.sessionID);
  const playerID = parseInt(req.query.playerID);
  sessionManager.readConference(sessionID, playerID).then((allowed) => {
    console.log(JSON.stringify({level: "info", action: "Read Conference", sessionID, playerID, allowed }));
    res.json({ allowed })
  }).catch((err) => {
    console.log(JSON.stringify({level: "error", action: "Read Conference", sessionID, playerID, error: err.message }));
  });
});

app.post("/makeMove/", function(req, res, next) {
  const sessionID = parseInt(req.query.sessionID);
  const playerID = parseInt(req.query.playerID);
  const sectors = req.body.timeCost;
  const turnData = Object.assign({
    sessionID: req.query.sessionID,
    playerID: req.query.playerID,
    time: new Date()
  }, req.body.turn);
  const theme = req.body.theme || "space";
  const turn = Turn.fromJson(turnData, theme);
  sessionManager.makeMove(sessionID, playerID, turn, sectors).then((allowed) => {
    console.log(JSON.stringify({level: "info", action: "Make Move", turnType: turn.turnType, sessionID, playerID, timeCost: sectors, turn: turn.json(theme), allowed}));
    res.json({ allowed });
  }).catch((err) => {
    console.log(JSON.stringify({level: "error", action: "Make Move", turnType: turn.turnType, sessionID, playerID, timeCost: sectors, turn: turn.json(theme), error: err.message }));
  });
});

app.post("/refreshPushpin/", function(req, res, next) {
  res.json({});
  pushpinIPs = req.body.ips;
  refreshPublisher();
  console.log(JSON.stringify({level: "info", message: "Received request to refresh pushpin ips: " + pushpinIPs }));
});

app.post("/listenSession/:sessionID/:theme?", async function(req, res, next) {
  const theme = req.params.theme || "space";
  const wsContext = req.wsContext;
  if (wsContext.isOpening()) {
    console.log(JSON.stringify({level: "info", message: "Received listen request for session " + req.params.sessionID }));
    wsContext.accept();
    wsContext.subscribe(req.params.sessionID + "-" + theme);

    const outEvents = wsContext.getOutgoingEvents();
    const outEventsEncoded = encodeWebSocketEvents(outEvents);

    res.writeHead(200, wsContext.toHeaders());
    res.write(outEventsEncoded);
    res.end();
  } else if (wsContext.inEvents.some((e) => e.type === "TEXT")) {
    const textEvent = wsContext.inEvents.find((e) => e.type === "TEXT");
    const playerID = JSON.parse(textEvent.content).id;

    console.log(JSON.stringify({level: "info", message: "Websocket identified for player " + playerID}));

    sessionManager.setPlayerConnected(playerID, true).then(() => {
      res.writeHead(200, Object.assign(
        {"Set-Meta-PlayerID": playerID.toString()},
        wsContext.toHeaders()));
      res.end();
    });
  } else if (wsContext.inEvents.some((e) => e.type === "CLOSE" || e.type === "DISCONNECT")) {
    const playerID = req.header("Meta-PlayerID");

    console.log(JSON.stringify({level: "info", message: "Websocket closed for player " + playerID}));

    sessionManager.setPlayerConnected(playerID, false).then(() => {
      res.writeHead(200, wsContext.toHeaders());
      res.end();
    });
  } else {
    res.writeHead(200, wsContext.toHeaders());
    res.end();
  }
});

setup().then(() => {
  console.log(JSON.stringify({level: "info", message: "Starting server..."}));
  server.listen(8000);
});
