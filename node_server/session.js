const { createBroker } = require('pubsub-ws');

const operations = require("./dbOps");
const { Game, SpaceObject, SECTOR_TYPES } = require("./game");
const { Turn, TurnType, Action, ActionType,
        Player, Theory, ResearchTurn, SurveyTurn,
        LocateTurn, TargetTurn, TheoryTurn, Score,
        ConferenceTurn } = require("./sessionObjects");

class Session {
  static NUM_CODES = 24*8*24*8*24;

  constructor(sessionID, code, boardLength, gameID, firstRotation,
              currentSector, currentAction) {
    this.sessionID = sessionID;
    this.code = code;
    this.boardLength = boardLength;
    this.gameID = gameID;
    this.firstRotation = firstRotation;
    this.currentSector = currentSector;
    this.currentAction = currentAction;
    this.game = undefined;
    this.players = undefined;
    this.kickedPlayers = undefined;
    this.theories = undefined;
    this.actions = undefined;
    this.history = undefined;
  }

  static #letterToInt(letter) {
    const l = letter.charCodeAt(0) - 65;
    if (l < 8) {
      return l;
    } else if (l < 14) {
      return l - 1;
    } else {
      return l - 2;
    }
  }

  static #intToLetter(i) {
    if (i < 8) {
      return String.fromCharCode(i + 65);
    } else if (i < 13) {
      return String.fromCharCode(i + 66);
    } else {
      return String.fromCharCode(i + 67);
    }
  }

  static #codeToInt(code) {
    let i = Session.#letterToInt(code[0]);
    code = code.slice(1);

    while (code.length > 0) {
      i *= (24 * 8);
      const d = parseInt(code[0]) - 2;
      const l = Session.#letterToInt(code[1]);

      i += d * 24;
      i += l;

      code = code.slice(2);
    }

    return i;
  }

  static #intToCode(i) {
    let code = Session.#intToLetter(i % 24);
    i = Math.floor(i / 24);

    while (i > 0) {
      const d = i % 8 + 2;
      i = Math.floor(i / 8);
      const l = Session.#intToLetter(i % 24);
      i = Math.floor(i / 24);
      code = l + d + code;
    }

    while (code.length < 5) {
      code = "A2" + code;
    }

    return code;
  }

  static async create(numSectors, connection=undefined) {
    const { gameID, game } = await operations.pickGame(numSectors, connection);

    let sessionID = null;
    let randomCode;

    while (sessionID === null) {
      const randomInt = Math.floor(Math.random() * (Session.NUM_CODES));
      randomCode = Session.#intToCode(randomInt);
      sessionID = await operations.createSession(randomCode, numSectors, gameID, connection);
    }

    const session = new Session(sessionID, randomCode, numSectors, gameID, true, 0, new Action(ActionType.START_GAME, null, 0));
    session.game = game;
    return session;
  }

  static async findByID(sessionID, connection=undefined) {
    const info = await operations.getSessionByID(sessionID, connection);
    if (info == null) {
      return null;
    }
    return new Session(
      info.sessionID, info.sessionCode, info.gameSize, info.gameID,
      info.firstRotation, info.currentSector,
      new Action(ActionType[info.actionType], info.actionPlayer, info.actionTurn)
    );
  }

  static async findByCode(sessionCode, connection=undefined) {
    const info = await operations.getSessionByCode(sessionCode, connection);
    if (info == null) {
      return null;
    }
    return new Session(
      info.sessionID, info.sessionCode, info.gameSize, info.gameID,
      info.firstRotation, info.currentSector,
      new Action(ActionType[info.actionType], info.actionPlayer, info.actionTurn)
    );
  }

  static async findByPlayerID(playerID, connection=undefined) {
    const info = await operations.getSessionByPlayerID(playerID, connection);
    if (info == null) {
      return null;
    }
    return new Session(
      info.sessionID, info.sessionCode, info.gameSize, info.gameID,
      info.firstRotation, info.currentSector,
      new Action(ActionType[info.actionType], info.actionPlayer, info.actionTurn)
    );
  }

  async refreshTheories(connection=undefined) {
    this.theories = undefined;
    return this.getTheories(connection);
  }

  async refreshPlayers(connection=undefined) {
    this.players = undefined;
    return this.getPlayers(connection);
  }

  async refreshActions(connection=undefined) {
    this.actions = undefined;
    return this.getActions(connection);
  }

  async refreshHistory(connection=undefined) {
    this.history = undefined;
    return this.getHistory(connection);
  }

  async refreshStatus(connection=undefined) {
    const info = await operations.getSessionByID(this.sessionID, connection);
    this.firstRotation = info.firstRotation;
    this.currentAction = new Action(ActionType[info.actionType], info.actionPlayer, info.actionTurn);
    this.currentSector = info.currentSector;
  }

  async refresh(connection=undefined) {
    return Promise.all([
      this.refreshTheories(connection),
      this.refreshPlayers(connection),
      this.refreshActions(connection),
      this.refreshHistory(connection),
      this.refreshStatus(connection)
    ]);
  }

  async getTheories(connection=undefined) {
    if (this.theories === undefined) {
      this.theories = await operations.getTheoriesForSession(this.sessionID, connection);
    }
    return this.theories;
  }

  async getPlayers(connection=undefined) {
    if (this.players === undefined) {
      const allPlayers = await operations.getPlayersForSession(this.sessionID, connection);
      this.players = allPlayers.filter((player) => !player.kicked);
      this.kickedPlayeres = allPlayers.filter((player) => player.kicked);
    }
    return this.players;
  }

  async getKickedPlayers(connection=undefined) {
    if (this.kickedPlayers === undefined) {
      const allPlayers = await operations.getPlayersForSession(this.sessionID, connection);
      this.players = allPlayers.filter((player) => !player.kicked);
      this.kickedPlayers = allPlayers.filter((player) => player.kicked);
    }
    return this.kickedPlayers;
  }

  async getKickVotes(connection=undefined) {
    if (this.kickVotes === undefined) {
      this.kickVotes = await operations.getKickVotesForSession(this.sessionID, connection);
    }
    return this.kickVotes;
  }

  async getActions(connection=undefined) {
    if (this.actions === undefined) {
      this.actions = await operations.getCurrentActionsForSession(this.sessionID, connection);
    }
    return this.actions;
  }

  async getHistory(connection=undefined) {
    if (this.history === undefined) {
      this.history = await operations.getPreviousTurns(this.sessionID, connection);
    }
    return this.history;
  }

  async getGame(connection=undefined) {
    if (this.game === undefined) {
      const { game } = await operations.getGameByID(this.gameID, connection);
      this.game = game;
    }
    return this.game;
  }

  async sectorsBehind(playerID, connection=undefined) {
    let players = await this.getPlayers(connection);
    players = players.slice().sort((a, b) => a.sector - b.sector);

    if (players.length == 1) {
      return 0;
    }

    let maxDiff = 0;
    let sector = players[0].sector;

    for (let i = 0; i < players.length - 1; i++) {
      const diff = players[i+1].sector - players[i].sector;

      if (diff > maxDiff) {
        maxDiff = diff;
        sector = players[i].sector;
      }
    }

    const lastDiff = players[0].sector - players[players.length-1].sector + this.boardLength;
    if (lastDiff > maxDiff) {
      maxDiff = lastDiff;
      sector = players[players.length-1].sector;
    }

    const mySector = players.filter((p) => p.playerID === playerID)[0].sector;

    let behind = sector - mySector;
    if (behind < 0) {
      behind += this.boardLength;
    }

    return behind;
  }

  async getScores(final, connection=undefined) {
    const players = await this.getPlayers(connection);
    const correctTheories = (await this.getTheories(connection)).filter((theory) => (theory.revealed() || final) && theory.accurate).sort((a, b) => b.progress - a.progress);
    const planetXTurns = (await this.getHistory(connection)).filter((turn) => turn.turnType === TurnType.LOCATE_PLANET_X && turn.successful).sort((a, b) => a.turnNumber - b.turnNumber);

    const scores = {};
    for (let i = 0; i < players.length; i++) {
      scores[players[i].playerID] = new Score(players[i].playerID, 0, 0, SECTOR_TYPES[this.boardLength].scoreValues);
    }

    const theorySectors = {};
    for (let i = 0; i < correctTheories.length; i++) {
      const theory = correctTheories[i];
      if (!theorySectors.hasOwnProperty(theory.sector) || theorySectors[theory.sector] === theory.progress) {
        scores[theory.playerID].addFirstPoint();
        theorySectors[theory.sector] = theory.progress;
      }
      scores[theory.playerID].addPoints(theory.spaceObject.initial);
    }

    for (let i = 0; i < planetXTurns.length; i++) {
      const turn = planetXTurns[i];
      if (i === 0) {
        scores[turn.playerID].setPlanetXPoints(10);
      } else {
        const sectorsBehind = await this.sectorsBehind(turn.playerID);
        scores[turn.playerID].setPlanetXPoints(2*sectorsBehind);
      }
    }

    return Object.values(scores);
  }

  async getNextSector(connection=undefined) {
    const players = await this.getPlayers(connection);

    if (players.length == 1) {
      return players[0].sector;
    }

    players.sort((a, b) => a.sector - b.sector);

    let maxDiff = 0;
    let sector = players[0].sector;

    for (let i = -1; i < players.length - 1; i++) {
      let diff;
      if (i >= 0) {
        diff = players[i+1].sector - players[i].sector;
      } else {
        diff = players[0].sector - players[players.length - 1].sector;

        if (diff < 0) {
          diff += this.boardLength;
        }
      }

      if (diff > maxDiff) {
        maxDiff = diff;
        sector = players[(i+1)%players.length].sector;
      }
    }

    return sector;
  }

  async getNextPlayerTurn(connection=undefined) {
    const nextSector = await this.getNextSector(connection);
    const players = await this.getPlayers(connection);
    const nextPlayer = players.filter((p) => p.sector === nextSector)
                              .sort((a, b) => a.arrival - b.arrival)[0];

    return { nextSector, nextPlayer };
  }

  async gameJson(connection=undefined) {
    const game = await this.getGame(connection);
    return game.json();
  }

  async stateJson(connection=undefined) {
    const final = this.currentAction.actionType === ActionType.END_GAME;
    const [players, kickedPlayers, kickVotes, theories, actions, history, scores] = await Promise.all([
      this.getPlayers(connection),
      this.getKickedPlayers(connection),
      this.getKickVotes(connection),
      this.getTheories(connection),
      this.getActions(connection),
      this.getHistory(connection),
      this.getScores(final, connection)
    ]);
    return {
      players: players.sort((a, b) => a.num - b.num).map((p) => p.json()),
      kickedPlayers: kickedPlayers.sort((a, b) => a.num - b.num).map((p) => p.json()),
      kickVotes: kickVotes,
      theories: theories.map((t) => t.json()),
      actions: actions.map((a) => a.json()),
      history: history.map((t) => t.json()),
      scores: scores.map((s) => s.json()),
      firstRotation: this.firstRotation,
      currentSector: this.currentSector,
      currentAction: this.currentAction.json(),
      sessionID: this.sessionID,
      sessionCode: this.code
    }
  }
}

class SessionManager {
  constructor(server) {
    const broker = createBroker(server, (req) => {
      const sessionID = req.url.slice(1);
      return Promise.resolve(sessionID);
    });
    this.broker = broker;
  }

  async notifySubscribers(session, connection=undefined) {
    await session.refresh(connection);
    const j = await session.stateJson(connection);
    const text = JSON.stringify(j);
    this.broker.publish(session.sessionID.toString(), text);
  }

  async joinSession(sessionCode, name, connection=undefined) {
    const session = await Session.findByCode(sessionCode, connection);
    // TODO: ensure session hasn't been started already
    if (session == null) {
      return {
        playerID: undefined,
        playerNum: undefined,
        session: undefined
      }
    }
    if (session.currentAction.actionType !== ActionType.START_GAME) {
      return false;
    }

    const { playerNum, playerID } = await operations.newPlayer(sessionCode, name, false, connection);
    this.notifySubscribers(session, connection);
    return { playerID, playerNum, session } ;
  }

  async startSession(sessionID, playerID, connection=undefined) {
    console.log("Start Session:");
    console.log(sessionID, playerID);
    const currentAction = await operations.getCurrentAction(playerID, connection);
    if (currentAction === null || currentAction.actionType !== ActionType.START_GAME) {
      return false;
    }

    await operations.resolveAction(currentAction.actionID, null, connection);
    await this.randomizeOrder(sessionID, connection);

    return true;
  }

  async setColor(playerID, color, connection=undefined) {
    const allowed = await operations.setColor(playerID, color, connection);
    if (allowed) {
      const session = await Session.findByPlayerID(playerID, connection);
      await this.notifySubscribers(session, connection);
    }
    return allowed;
  }

  async castKickVote(sessionID, votePlayerID, kickPlayerID, vote, connection=undefined) {
    const callbackKicked = async (cxn) => {
      const session = await Session.findByID(sessionID, cxn);

      if (session.currentAction.playerID === kickPlayerID || session.currentAction.playerID === null) {
        if (session.currentAction.actionType === ActionType.START_GAME) {
          const players = await session.getPlayers(cxn);
          const randomPlayer = players[Math.floor(Math.random() * players.length)];
          const action = new Action(ActionType.START_GAME, randomPlayer.playerID, 0);
          await operations.setCurrentAction(sessionID, action, cxn);
          await operations.createAction(ActionType.START_GAME, randomPlayer.playerID, 0, cxn);
        } else {
          const actions = await session.getActions(cxn);
          if (actions.length === 0) {
            if (session.currentAction.actionType === ActionType.THEORY_PHASE) {
              await this.advanceTheories(session, cxn);
            }
            await this.setNextAction(session, cxn);
          }
          await session.refresh(cxn);
        }
      }

      await this.notifySubscribers(session, cxn);
    }

    const callbackNotKicked = async (cxn) => {
      const session = await Session.findByID(sessionID, cxn);
      await this.notifySubscribers(session, cxn);
    }

    const { allowed, kicked } = await operations.kickVote(sessionID, kickPlayerID, votePlayerID, vote, callbackKicked, callbackNotKicked, connection);
    return allowed;
  }

  async randomizeOrder(sessionID, connection=undefined) {
    let players = await operations.getPlayersForSession(sessionID, connection);
    players = players.filter((player) => !player.kicked)

    // Randomly shuffle players
    for (let i = players.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      let temp = players[i];
      players[i] = players[j];
      players[j] = temp;
    }

    for (let i = 0; i < players.length; i++) {
      const player = players[i];
      player.arrival = i + 1;
      await operations.movePlayer(player.playerID, player.sector, player.arrival, connection);
    }

    if (players.length > 0) {
      await operations.createAction(ActionType.PLAYER_TURN, players[0].playerID, 1, connection);
      await operations.setCurrentAction(sessionID, new Action(ActionType.PLAYER_TURN, players[0].playerID, 1), connection);
    }

    const session = await Session.findByID(sessionID, connection);
    this.notifySubscribers(session, connection);
  }

  async getNextAction(session, connection=undefined) {
    const sectorType = SECTOR_TYPES[session.boardLength];
    const currentSector = session.currentSector;
    const nextTurn = session.currentAction.turn + 1;
    let { nextSector, nextPlayer } = await session.getNextPlayerTurn(connection);

    if (nextSector < currentSector) {
      nextSector += session.boardLength;
    }

    let sector = nextSector;
    let action = new Action(ActionType.PLAYER_TURN, nextPlayer.playerID, nextTurn);

    const theoryOffset = (((-currentSector - 1) % sectorType.theoryPhaseInterval) + sectorType.theoryPhaseInterval) % sectorType.theoryPhaseInterval;
    let nextTheory = currentSector + theoryOffset;

    if (session.currentAction.actionType === ActionType.THEORY_PHASE ||
        (session.currentAction.actionType === ActionType.CONFERENCE_PHASE && currentSector === nextTheory)) {
      nextTheory += sectorType.theoryPhaseInterval;
    }

    if (nextTheory < sector) {
      sector = nextTheory;
      action = new Action(ActionType.THEORY_PHASE, null, nextTurn);
    }

    if (session.firstRotation) {
      let conferenceIndex;

      if (session.currentAction.actionType !== ActionType.CONFERENCE_PHASE) {
        conferenceIndex = sectorType.conferencePhases.findIndex((s) => s >= currentSector);
      } else {
        conferenceIndex = sectorType.conferencePhases.findIndex((s) => s > currentSector);
      }

      if (conferenceIndex >= 0) {
        const nextConference = sectorType.conferencePhases[conferenceIndex];
        if (nextConference < sector) {
          sector = nextConference;
          action = new Action(ActionType.CONFERENCE_PHASE, null, nextTurn);
        }
      }
    }

    sector %= session.boardLength;
    const stillFirstRotation = session.firstRotation && sector >= currentSector;

    return {
      action,
      sector,
      stillFirstRotation
    }
  }

  async setNextAction(session, connection=undefined) {
    const { action, sector, stillFirstRotation } = await this.getNextAction(session, connection);

    await operations.setCurrentStatus(session.sessionID, action, sector, stillFirstRotation, connection);

    if (action.actionType === ActionType.PLAYER_TURN) {
      await operations.createAction(action.actionType, action.playerID, action.turn, connection);
    } else {
      const players = await session.getPlayers(connection);
      await Promise.all(players.map((p) => operations.createAction(action.actionType, p.playerID, action.turn, connection)));
    }
  }

  async submitTheories(sessionID, playerID, theories, connection=undefined) {
    console.log("Submit theories");
    console.log(sessionID, playerID);
    console.log(theories);
    const currentAction = await operations.getCurrentAction(playerID, connection);

    if (currentAction === null || (currentAction.actionType !== ActionType.THEORY_PHASE &&
      currentAction.actionType !== ActionType.LAST_ACTION)) {
      return {
        allowed: false,
        successfulTheories: []
      };
    }

    theories.forEach((theory) => theory.setTurn(currentAction.turn));

    const session = await Session.findByID(sessionID, connection);

    let maxTheories;

    if (currentAction.actionType === ActionType.LAST_ACTION) {
      const sectorsBehind = await session.sectorsBehind(playerID, connection);

      if (sectorsBehind <= 3) {
        maxTheories = 1;
      } else {
        maxTheories = 2;
      }
    } else {
      maxTheories = SECTOR_TYPES[session.boardLength].theoriesPerTurn;
    }

    theories = theories.slice(0, maxTheories);

    const existingTheories = await session.getTheories(connection);
    const myTheories = existingTheories.filter((theory) => theory.playerID === playerID);
    const numObjects = SECTOR_TYPES[session.boardLength].numObjects;

    const tokensLeft = Object.assign({}, numObjects);
    for (let i = 0; i < myTheories.length; i++) {
      tokensLeft[existingTheories[i].spaceObject.initial] -= 1;
    }

    const board = (await session.getGame(connection)).board;
    const revealedSectors = new Set(existingTheories.filter((theory) => theory.revealed() && theory.accurate).map((theory) => theory.sector));

    let successfulTheories = [];
    for (let i = 0; i < theories.length; i++) {
      const theory = theories[i];
      theory.setAccuracy(board);
      const hasTokens = tokensLeft[theory.spaceObject.initial] > 0;
      const notRevealed = !revealedSectors.has(theory.sector);
      const uniqueSector = !successfulTheories.some((t) => t.sector === theory.sector);
      const uniqueObject = !myTheories.some((t) => t.spaceObject.initial === theory.spaceObject.initial && t.sector === theory.sector);

      if (hasTokens && notRevealed && uniqueSector && uniqueObject) {
        await operations.createTheory(sessionID, playerID, theory.spaceObject.initial, theory.sector, theory.accurate, theory.turn, connection);
        successfulTheories.push(theory);
        tokensLeft[theory.spaceObject.initial] -= 1;
      }
    }

    await operations.resolveAction(currentAction.actionID, new TheoryTurn(successfulTheories, playerID, new Date()), connection);
    const actions = await session.getActions(connection);

    if (actions.length === 0) {
      if (currentAction.actionType === ActionType.LAST_ACTION) {
        await operations.setCurrentAction(sessionID, new Action(ActionType.END_GAME, null, currentAction.turn + 1), connection);
      } else {
        await this.advanceTheories(session, connection);
        await this.setNextAction(session, connection);
      }
    }

    this.notifySubscribers(session, connection);

    return {
      allowed: true,
      successfulTheories
    }
  }

  async readConference(sessionID, playerID, connection=undefined) {
    const currentAction = await operations.getCurrentAction(playerID, connection);
    if (currentAction === null || currentAction.actionType !== ActionType.CONFERENCE_PHASE) {
      return false;
    }
    const session = await Session.findByID(sessionID, connection);
    const conferenceIndex = SECTOR_TYPES[session.boardLength].conferencePhases.indexOf(session.currentSector);

    const turn = new ConferenceTurn(conferenceIndex);
    turn.setTurnNumber(currentAction.turn);
    await operations.resolveAction(currentAction.actionID, turn, connection);

    const actions = await session.getActions(connection);
    if (actions.length === 0) {
      await this.setNextAction(session, connection);
    }

    this.notifySubscribers(session, connection);
    return true;
  }

  async advanceTheories(session, connection=undefined) {
    await operations.advanceTheories(session.sessionID, connection);
  }

  async makeMove(sessionID, playerID, turn, sectors, connection=undefined) {
    console.log("Make Move:");
    console.log(sessionID, playerID);
    console.log(turn);
    console.log(sectors);
    const currentAction = await operations.getCurrentAction(playerID, connection);
    const actionMatches = currentAction !== null
      && ((currentAction.actionType === ActionType.PLAYER_TURN)
      || (currentAction.actionType === ActionType.LAST_ACTION
          && turn.turnType === TurnType.LOCATE_PLANET_X));

    if (!actionMatches) {
      return false;
    }

    turn.setTurnNumber(currentAction.turn);

    const session = await Session.findByID(sessionID, connection);

    if (turn.turnType === TurnType.TARGET) {
      const history = await session.getHistory(connection);
      const previousTargets = history.filter((turn) => turn.playerID === playerID && turn.turnType === TurnType.TARGET);
      const allowedTargets = SECTOR_TYPES[session.boardLength].numTargets;
      if (previousTargets.length >= allowedTargets) {
        return false;
      }
    }

    if (currentAction.actionType !== ActionType.LAST_ACTION) {
      await operations.advancePlayer(playerID, sectors, connection);
    }

    await operations.resolveAction(currentAction.actionID, turn, connection);


    if (currentAction.actionType !== ActionType.LAST_ACTION &&
      turn.turnType === TurnType.LOCATE_PLANET_X && turn.successful) {

      const players = await session.getPlayers(connection);
      if (players.length > 1) {
        for (let i = 0; i < players.length; i++) {
          const player = players[i];
          if (player.playerID !== playerID) {
            await operations.createAction(ActionType.LAST_ACTION, player.playerID, currentAction.turn + 1, connection);
          }
        }

        await operations.setCurrentAction(sessionID, new Action(ActionType.LAST_ACTION, null, currentAction.turn + 1), connection);
      } else {
        await operations.setCurrentAction(sessionID, new Action(ActionType.END_GAME, null, currentAction.turn + 1), connection);
      }

    } else {
      const actions = await session.getActions(connection);
      if (actions.length == 0) {
        if (currentAction.actionType === ActionType.LAST_ACTION) {
          await operations.setCurrentAction(sessionID, new Action(ActionType.END_GAME, null, currentAction.turn + 1), connection);
        } else {
          await this.setNextAction(session, connection);
        }
      }
    }

    this.notifySubscribers(session, connection);
    return true;
  }

  async createSession(numSectors, name, connection=undefined) {
    const session = await Session.create(numSectors, connection);
    const { playerNum, playerID } = await operations.newPlayer(session.code, name, true, connection);
    const action = new Action(ActionType.START_GAME, playerID, 0);
    await operations.setCurrentAction(session.sessionID, action, connection);
    session.currentAction = action;
    return { playerID, playerNum, session };
  }
}

module.exports = {
  Session,
  SessionManager
};
