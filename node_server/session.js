const { Connector, ...operations } = require("./dbOps");
const { Game, SectorElement, SECTOR_TYPES } = require("./game");
const { Turn, TurnType, Action, ActionType,
        Player, Theory, ResearchTurn, SurveyTurn,
        LocateTurn, TargetTurn, TheoryTurn, Score,
        ConferenceTurn } = require("./sessionObjects");

const { WebSocketMessageFormat } = require("@fanoutio/grip");

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

  setConnector(connector) {
    this.connector = connector;
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

  static async create(numSectors, connector=undefined) {
    const { gameID, game } = await operations.pickGame(numSectors, connector);

    let sessionID = null;
    let randomCode;

    while (sessionID === null) {
      const randomInt = Math.floor(Math.random() * (Session.NUM_CODES));
      randomCode = Session.#intToCode(randomInt);
      sessionID = await operations.createSession(randomCode, numSectors, gameID, connector);
    }

    const session = new Session(sessionID, randomCode, numSectors, gameID, true, 0, new Action(ActionType.START_GAME, null, 0));
    session.setConnector(connector);
    session.game = game;
    return session;
  }

  static async findByID(sessionID, connector=undefined) {
    const info = await operations.getSessionByID(sessionID, connector);
    if (info == null) {
      return null;
    }
    const session = new Session(
      info.sessionID, info.sessionCode, info.gameSize, info.gameID,
      info.firstRotation, info.currentSector,
      new Action(ActionType[info.actionType], info.actionPlayer, info.actionTurn)
    );

    session.setConnector(connector);
    return session;
  }

  static async findByCode(sessionCode, connector) {
    const info = await operations.getSessionByCode(sessionCode, connector);
    if (info == null) {
      return null;
    }
    const session = new Session(
      info.sessionID, info.sessionCode, info.gameSize, info.gameID,
      info.firstRotation, info.currentSector,
      new Action(ActionType[info.actionType], info.actionPlayer, info.actionTurn)
    );

    session.setConnector(connector);
    return session;
  }

  static async findByPlayerID(playerID, connector=undefined) {
    const info = await operations.getSessionByPlayerID(playerID, connector);
    if (info == null) {
      return null;
    }
    const session = new Session(
      info.sessionID, info.sessionCode, info.gameSize, info.gameID,
      info.firstRotation, info.currentSector,
      new Action(ActionType[info.actionType], info.actionPlayer, info.actionTurn)
    );

    session.setConnector(connector);
    return session;
  }

  async refreshTheories() {
    this.theories = undefined;
    return this.getTheories();
  }

  async refreshPlayers() {
    this.players = undefined;
    return this.getPlayers();
  }

  async refreshActions() {
    this.actions = undefined;
    return this.getActions();
  }

  async refreshHistory() {
    this.history = undefined;
    return this.getHistory();
  }

  async refreshStatus() {
    const info = await operations.getSessionByID(this.sessionID, this.connector);
    this.firstRotation = info.firstRotation;
    this.currentAction = new Action(ActionType[info.actionType], info.actionPlayer, info.actionTurn);
    this.currentSector = info.currentSector;
  }

  async refresh() {
    return Promise.all([
      this.refreshTheories(),
      this.refreshPlayers(),
      this.refreshActions(),
      this.refreshHistory(),
      this.refreshStatus()
    ]);
  }

  async getTheories() {
    if (this.theories === undefined) {
      this.theories = await operations.getTheoriesForSession(this.sessionID, this.connector);
    }
    return this.theories;
  }

  async getPlayers() {
    if (this.players === undefined) {
      const allPlayers = await operations.getPlayersForSession(this.sessionID, this.connector);
      this.players = allPlayers.filter((player) => !player.kicked);
      this.kickedPlayeres = allPlayers.filter((player) => player.kicked);
    }
    return this.players;
  }

  async getKickedPlayers() {
    if (this.kickedPlayers === undefined) {
      const allPlayers = await operations.getPlayersForSession(this.sessionID, this.connector);
      this.players = allPlayers.filter((player) => !player.kicked);
      this.kickedPlayers = allPlayers.filter((player) => player.kicked);
    }
    return this.kickedPlayers;
  }

  async getKickVotes() {
    if (this.kickVotes === undefined) {
      this.kickVotes = await operations.getKickVotesForSession(this.sessionID, this.connector);
    }
    return this.kickVotes;
  }

  async getActions() {
    if (this.actions === undefined) {
      this.actions = await operations.getCurrentActionsForSession(this.sessionID, this.connector);
    }
    return this.actions;
  }

  async getHistory() {
    if (this.history === undefined) {
      this.history = await operations.getPreviousTurns(this.sessionID, this.connector);
    }
    return this.history;
  }

  async getGame() {
    if (this.game === undefined) {
      const { game } = await operations.getGameByID(this.gameID, this.connector);
      this.game = game;
    }
    return this.game;
  }

  async sectorsBehind(playerID) {
    let players = await this.getPlayers();
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

  async getScores(final) {
    const players = await this.getPlayers();
    const correctTheories = (await this.getTheories()).filter((theory) => (theory.revealed() || final) && theory.accurate).sort((a, b) => b.progress - a.progress);
    const planetXTurns = (await this.getHistory()).filter((turn) => turn.turnType === TurnType.LOCATE_PLANET_X && turn.successful).sort((a, b) => a.turnNumber - b.turnNumber);

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
      scores[theory.playerID].addPoints(theory.spaceObject.NAME);
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

  async getNextSector() {
    const players = await this.getPlayers();

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

  async getNextPlayerTurn() {
    const nextSector = await this.getNextSector();
    const players = await this.getPlayers();
    const nextPlayer = players.filter((p) => p.sector === nextSector)
                              .sort((a, b) => a.arrival - b.arrival)[0];

    return { nextSector, nextPlayer };
  }

  async gameJson(theme) {
    const game = await this.getGame();
    return game.json(theme);
  }

  async stateJson(theme) {
    const final = this.currentAction.actionType === ActionType.END_GAME;
    const [players, kickedPlayers, kickVotes, theories, actions, history, scores] = await Promise.all([
      this.getPlayers(),
      this.getKickedPlayers(),
      this.getKickVotes(),
      this.getTheories(),
      this.getActions(),
      this.getHistory(),
      this.getScores(final)
    ]);
    return {
      players: players.sort((a, b) => a.num - b.num).map((p) => p.json()),
      kickedPlayers: kickedPlayers.sort((a, b) => a.num - b.num).map((p) => p.json()),
      kickVotes: kickVotes,
      theories: theories.map((t) => t.json(theme)),
      actions: actions.map((a) => a.json()),
      history: history.map((t) => t.json(theme)),
      scores: scores.map((s) => s.json(theme)),
      firstRotation: this.firstRotation,
      currentSector: this.currentSector,
      currentAction: this.currentAction.json(),
      sessionID: this.sessionID,
      sessionCode: this.code
    }
  }
}

class SessionManager {
  setPublisher(publisher) {
    this.publisher = publisher;
  }

  async notifySubscribers(session) {
    await session.refresh();
    const themes = ["space", "ocean", "castle"];
    for (const theme of themes) {
      const j = await session.stateJson(theme);
      const text = JSON.stringify(j);
      this.publisher.publishFormats(session.sessionID.toString() + "-" + theme, new WebSocketMessageFormat(text));
    }
  }

  async setPlayerConnected(playerID, connected, connector=undefined) {
    await operations.setPlayerConnected(playerID, connected, connector);
    const session = await Session.findByPlayerID(playerID, connector);
    await this.notifySubscribers(session);
  }

  async joinSession(sessionCode, name, connector=undefined) {
    const session = await Session.findByCode(sessionCode, connector);

    if (session == null) {
      return {};
    }

    if (session.currentAction.actionType !== ActionType.START_GAME) {
      return {};
    }

    const players = await session.getPlayers();
    if (players.some((player) => player.name === name)) {
      return {};
    }

    const { playerNum, playerID } = await operations.newPlayer(sessionCode, name, false, connector);
    this.notifySubscribers(session);
    return { playerID, playerNum, session } ;
  }

  async startSession(sessionID, playerID, connector=undefined) {
    const currentAction = await operations.getCurrentAction(playerID, connector);
    if (currentAction === null || currentAction.actionType !== ActionType.START_GAME) {
      return false;
    }

    await operations.resolveAction(currentAction.actionID, null, connector);
    await this.randomizeOrder(sessionID, connector);

    return true;
  }

  async setColor(playerID, color, connector=undefined) {
    const allowed = await operations.setColor(playerID, color, connector);
    if (allowed) {
      const session = await Session.findByPlayerID(playerID, connector);
      await this.notifySubscribers(session, connector);
    }
    return allowed;
  }

  async castKickVote(sessionID, votePlayerID, kickPlayerID, vote, connector=undefined) {
    const callbackKicked = async (cxn) => {
      const session = await Session.findByID(sessionID, cxn);

      if (session.currentAction.playerID === kickPlayerID || session.currentAction.playerID === null) {
        if (session.currentAction.actionType === ActionType.START_GAME) {
          const players = await session.getPlayers();
          const randomPlayer = players[Math.floor(Math.random() * players.length)];
          const action = new Action(ActionType.START_GAME, randomPlayer.playerID, 0);
          await operations.setCurrentAction(sessionID, action, cxn);
          await operations.createAction(ActionType.START_GAME, randomPlayer.playerID, 0, cxn);
        } else {
          const actions = await session.getActions();
          if (actions.length === 0) {
            if (session.currentAction.actionType === ActionType.THEORY_PHASE) {
              await this.advanceTheories(session);
              await this.setNextAction(session);
            } else if (session.currentAction.actionType === ActionType.LAST_ACTION) {
              await operations.setCurrentAction(sessionID, new Action(ActionType.END_GAME, null, session.currentAction.turn + 1), cxn);
            } else {
              await this.setNextAction(session);
            }
          }
          await session.refresh();
        }
      }

      await this.notifySubscribers(session);
    }

    const callbackNotKicked = async (cxn) => {
      const session = await Session.findByID(sessionID, cxn);
      await this.notifySubscribers(session);
    }

    const { allowed, kicked } = await operations.kickVote(sessionID, kickPlayerID, votePlayerID, vote, callbackKicked, callbackNotKicked, connector);
    return allowed;
  }

  async randomizeOrder(sessionID, connector=undefined) {
    let players = await operations.getPlayersForSession(sessionID, connector);
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
      await operations.movePlayer(player.playerID, player.sector, player.arrival, connector);
    }

    if (players.length > 0) {
      await operations.createAction(ActionType.PLAYER_TURN, players[0].playerID, 1, connector);
      await operations.setCurrentAction(sessionID, new Action(ActionType.PLAYER_TURN, players[0].playerID, 1), connector);
    }

    const session = await Session.findByID(sessionID, connector);
    this.notifySubscribers(session);
  }

  async getNextAction(session) {
    const sectorType = SECTOR_TYPES[session.boardLength];
    const currentSector = session.currentSector;
    const nextTurn = session.currentAction.turn + 1;
    let { nextSector, nextPlayer } = await session.getNextPlayerTurn();

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

  async setNextAction(session) {
    const { action, sector, stillFirstRotation } = await this.getNextAction(session);

    await operations.setCurrentStatus(session.sessionID, action, sector, stillFirstRotation, session.connector);

    if (action.actionType === ActionType.PLAYER_TURN) {
      await operations.createAction(action.actionType, action.playerID, action.turn, session.connector);
    } else {
      const players = await session.getPlayers();
      await Promise.all(players.map((p) => operations.createAction(action.actionType, p.playerID, action.turn, session.connector)));
    }
  }

  async submitTheories(sessionID, playerID, theories, turn, connector=undefined) {
    let needClose = false;
    if (connector == undefined) {
      connector = new Connector();
      await connector.startTransaction();
      needClose = true;
    }
    const currentAction = await operations.getCurrentAction(playerID, connector);

    if (currentAction === null || (currentAction.actionType !== ActionType.THEORY_PHASE &&
      currentAction.actionType !== ActionType.LAST_ACTION) || (currentAction.turn !== turn)) {
      if (needClose) {
        connector.rollback();
      }
      return {
        allowed: false,
        successfulTheories: []
      };
    }

    theories.forEach((theory) => theory.setTurn(currentAction.turn));

    const session = await Session.findByID(sessionID, connector);

    let maxTheories;

    if (currentAction.actionType === ActionType.LAST_ACTION) {
      const sectorsBehind = await session.sectorsBehind(playerID);

      if (sectorsBehind <= 3) {
        maxTheories = 1;
      } else {
        maxTheories = 2;
      }
    } else {
      maxTheories = SECTOR_TYPES[session.boardLength].theoriesPerTurn;
    }

    theories = theories.slice(0, maxTheories);

    const existingTheories = await session.getTheories();
    const myTheories = existingTheories.filter((theory) => theory.playerID === playerID);
    const numObjects = SECTOR_TYPES[session.boardLength].numObjects;

    const tokensLeft = Object.assign({}, numObjects);
    for (let i = 0; i < myTheories.length; i++) {
      tokensLeft[myTheories[i].spaceObject.NAME] -= 1;
    }

    const board = (await session.getGame()).board;
    const revealedSectors = new Set(existingTheories.filter((theory) => theory.revealed() && theory.accurate).map((theory) => theory.sector));

    let successfulTheories = [];
    for (let i = 0; i < theories.length; i++) {
      const theory = theories[i];
      theory.setAccuracy(board);
      const hasTokens = tokensLeft[theory.spaceObject.NAME] > 0;
      const notRevealed = !revealedSectors.has(theory.sector);
      const uniqueSector = !successfulTheories.some((t) => t.sector === theory.sector);
      const uniqueObject = !myTheories.some((t) => t.spaceObject.NAME === theory.spaceObject.NAME && t.sector === theory.sector);
      if (hasTokens && notRevealed && uniqueSector && uniqueObject) {
        await operations.createTheory(sessionID, playerID, theory.spaceObject["space"].initial, theory.sector, theory.accurate, theory.turn, connector);
        successfulTheories.push(theory);
        tokensLeft[theory.spaceObject.NAME] -= 1;
      }
    }

    await operations.resolveAction(currentAction.actionID, new TheoryTurn(successfulTheories, playerID, new Date()), connector);
    const actions = await session.getActions();

    if (actions.length === 0) {
      if (currentAction.actionType === ActionType.LAST_ACTION) {
        await operations.setCurrentAction(sessionID, new Action(ActionType.END_GAME, null, currentAction.turn + 1), connector);
      } else {
        await this.advanceTheories(session);
        await this.setNextAction(session);
      }
    }

    await this.notifySubscribers(session);

    if (needClose) {
      connector.commit();
    }

    return {
      allowed: true,
      successfulTheories
    }
  }

  async readConference(sessionID, playerID, connector=undefined) {
    const currentAction = await operations.getCurrentAction(playerID, connector);
    if (currentAction === null || currentAction.actionType !== ActionType.CONFERENCE_PHASE) {
      return false;
    }
    const session = await Session.findByID(sessionID, connector);
    const conferenceIndex = SECTOR_TYPES[session.boardLength].conferencePhases.indexOf(session.currentSector);

    const turn = new ConferenceTurn(conferenceIndex);
    turn.setTurnNumber(currentAction.turn);
    await operations.resolveAction(currentAction.actionID, turn, connector);

    const actions = await session.getActions();
    if (actions.length === 0) {
      await this.setNextAction(session);
    }

    this.notifySubscribers(session);
    return true;
  }

  async advanceTheories(session) {
    await operations.advanceTheories(session.sessionID, session.connector);
  }

  async makeMove(sessionID, playerID, turn, sectors, connector=undefined) {
    let needClose = false;
    if (connector == undefined) {
      connector = new Connector();
      await connector.startTransaction();
      needClose = true;
    }
    const currentAction = await operations.getCurrentAction(playerID, connector);

    const actionMatches = currentAction !== null
      && (currentAction.turn == turn.turnNumber)
      && ((currentAction.actionType === ActionType.PLAYER_TURN)
      || (currentAction.actionType === ActionType.LAST_ACTION
          && turn.turnType === TurnType.LOCATE_PLANET_X));

    if (!actionMatches) {
      if (needClose) {
        await connector.rollback();
      }
      return false;
    }

    const session = await Session.findByID(sessionID, connector);

    if (turn.turnType === TurnType.TARGET) {
      const history = await session.getHistory();
      const previousTargets = history.filter((turn) => turn.playerID === playerID && turn.turnType === TurnType.TARGET);
      const allowedTargets = SECTOR_TYPES[session.boardLength].numTargets;
      if (previousTargets.length >= allowedTargets) {
        if (needClose) {
          await connector.rollback();
        }
        return false;
      }
    }

    if (currentAction.actionType !== ActionType.LAST_ACTION) {
      await operations.advancePlayer(playerID, sectors, connector);
    }

    await operations.resolveAction(currentAction.actionID, turn, connector);

    if (currentAction.actionType !== ActionType.LAST_ACTION &&
      turn.turnType === TurnType.LOCATE_PLANET_X && turn.successful) {

      const players = await session.getPlayers();
      if (players.length > 1) {
        for (let i = 0; i < players.length; i++) {
          const player = players[i];
          if (player.playerID !== playerID) {
            await operations.createAction(ActionType.LAST_ACTION, player.playerID, currentAction.turn + 1, connector);
          }
        }

        await operations.setCurrentAction(sessionID, new Action(ActionType.LAST_ACTION, null, currentAction.turn + 1), connector);
      } else {
        await operations.setCurrentAction(sessionID, new Action(ActionType.END_GAME, null, currentAction.turn + 1), connector);
      }

    } else {
      const actions = await session.getActions();
      if (actions.length == 0) {
        if (currentAction.actionType === ActionType.LAST_ACTION) {
          await operations.setCurrentAction(sessionID, new Action(ActionType.END_GAME, null, currentAction.turn + 1), connector);
        } else {
          await this.setNextAction(session);
        }
      }
    }

    await this.notifySubscribers(session);

    if (needClose) {
      await connector.commit();
    }

    return true;
  }

  async createSession(numSectors, name, connector=undefined) {
    const session = await Session.create(numSectors, connector);
    const { playerNum, playerID } = await operations.newPlayer(session.code, name, true, connector);
    const action = new Action(ActionType.START_GAME, playerID, 0);
    await operations.setCurrentAction(session.sessionID, action, connector);
    session.currentAction = action;
    return { playerID, playerNum, session };
  }
}

module.exports = {
  Session,
  SessionManager
};
