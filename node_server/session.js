const { createBroker } = require('pubsub-ws');

const operations = require("./dbOps");
const { Game, SpaceObject, SECTOR_TYPES } = require("./game");
const { Turn, TurnType, Action, ActionType,
        Player, Theory, ResearchTurn, SurveyTurn,
        LocateTurn, TargetTurn } = require("./sessionObjects");

class Session {
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

  static async create(numSectors) {
    const existingCodes = await operations.getSessionCodes();
    const existingInts = new Set(existingCodes.map((code) => Session.#codeToInt(code)));
    const availableInts = Array.from(Array(24*8*24*8*24)).map((el, i) => i).filter(i => !existingInts.has(i));

    const randomIndex = Math.floor(Math.random() * availableInts.length);
    const chosenInt = availableInts[randomIndex];
    const chosenCode = Session.#intToCode(chosenInt);

    const { gameID, game } = await operations.pickGame(numSectors);
    const sessionID = await operations.createSession(chosenCode, numSectors, gameID);
    const session = new Session(sessionID, chosenCode, numSectors, gameID, true, 0, new Action(ActionType.START_GAME, null));
    session.game = game;
    return session;
  }

  static async findByID(sessionID) {
    const info = await operations.getSessionByID(sessionID);
    return new Session(
      info.sessionID, info.sessionCode, info.gameSize, info.gameID,
      info.firstRotation, info.currentSector,
      new Action(ActionType[info.actionType], info.actionPlayer)
    );
  }

  static async findByCode(sessionCode) {
    const info = await operations.getSessionByCode(sessionCode);
    return new Session(
      info.sessionID, info.sessionCode, info.gameSize, info.gameID,
      info.firstRotation, info.currentSector,
      new Action(ActionType[info.actionType], info.actionPlayer)
    );
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
    const info = await operations.getSessionByID(this.sessionID);
    this.firstRotation = info.firstRotation;
    this.currentAction = new Action(ActionType[info.actionType], info.actionPlayer);
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
      this.theories = await operations.getTheoriesForSession(this.sessionID);
    }
    return this.theories;
  }

  async getPlayers() {
    if (this.players === undefined) {
      this.players = await operations.getPlayersForSession(this.sessionID);
    }
    return this.players;
  }

  async getActions() {
    if (this.actions === undefined) {
      this.actions = await operations.getCurrentActionsForSession(this.sessionID);
    }
    return this.actions;
  }

  async getHistory() {
    if (this.history === undefined) {
      this.history = await operations.getPreviousTurns(this.sessionID);
    }
    return this.history;
  }

  async getGame() {
    if (this.game === undefined) {
      const { game } = await operations.getGameByID(this.gameID);
      this.game = game;
    }
    return this.game;
  }

  async getNextSector() {
    const players = await this.getPlayers();
    players.sort((a, b) => a.sector - b.sector);

    let maxDiff = this.boardLength;
    let sector = players[0].sector;

    for (let i = -1; i < players.length - 1; i++) {
      let diff;
      if (i > 0) {
        diff = players[i+1] - players[i];
      } else {
        diff = players[0] - players[players.length - 1];
      }

      if (diff > maxDiff) {
        maxDiff = diff;
        sector = i;
      }
    }

    return sector;
  }

  async getNextPlayerTurn() {
    const nextSector = await this.getNextSector();
    const players = await this.getPlayers();
    const nextPlayer = players.filter((p) => p.sector === nextSector)
                              .reduce((a, b) => Math.min(a.arrival, b.arrival));
    return { nextSector, nextPlayer };
  }

  async gameJson() {
    const game = await this.getGame();
    return game.json();
  }

  async stateJson() {
    const [players, theories, actions, history] = await Promise.all([
      this.getPlayers(),
      this.getTheories(),
      this.getActions(),
      this.getHistory()
    ]);
    return {
      players: this.players.map((p) => p.json()),
      theories: this.theories.map((t) => t.json()),
      actions: this.actions.map((a) => a.json()),
      history: this.history.map((t) => t.json()),
      firstRotation: this.firstRotation,
      currentSector: this.currentSector,
      currentAction: this.currentAction.json(),
      sessionID: this.sessionID
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

  async notifySubscribers(session) {
    const j = await session.stateJson();
    const text = JSON.stringify(j);
    this.broker.publish(session.sessionID.toString(), text);
  }

  async joinSession(sessionCode, name) {
    const session = await Session.findByCode(sessionCode);
    if (session.currentAction.actionType !== ActionType.START_GAME) {
      return false;
    }

    const { playerNum, playerID } = await operations.newPlayer(sessionCode, name, false);
    return { playerID, playerNum, session } ;
  }

  async startGame(sessionID, playerID) {
    const currentAction = await operations.getCurrentAction(playerID);
    if (currentAction === null || currentAction.actionType !== ActionType.START_GAME) {
      return false;
    }

    await operations.resolveAction(currentAction.actionID, null);
    await this.randomizeOrder(sessionID);
  }

  async randomizeOrder(sessionID) {
    const players = await operations.getPlayersForSession(sessionID);

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
      await operations.movePlayer(player.playerID, player.sector, player.arrival);
    }

    if (players.length > 0) {
      await operations.createAction(ActionType.PLAYER_TURN, players[0].playerID);
      await operations.setCurrentAction(sessionID, new Action(ActionType.PLAYER_TURN, players[0].playerID));
    }

    const session = await Session.findByID(sessionID);

    this.notifySubscribers(session);
  }

  async nextAction(session) {
    const sectorType = SECTOR_TYPES[session.boardLength];
    const currentSector = session.currentSector;
    let { nextSector, nextPlayer } = await session.getNextPlayerTurn();

    if (nextSector < currentSector) {
      nextSector += session.boardLength;
    }

    let sector = nextSector;
    let action = new Action(ActionType.PLAYER_TURN, nextPlayer.playerID);

    const theoryOffset = (((-currentSector - 1) % sectorType.theoryPhaseInterval) + sectorType.theoryPhaseInterval) % sectorType.theoryPhaseInterval;
    let nextTheory = currentSector + theoryOffset;

    if (session.currentAction.actionType === ActionType.THEORY_PHASE ||
        (session.currentAction.actionType === ActionType.CONFERENCE_PHASE && currentSector === nextTheory)) {
      nextTheory += sectorType.theoryPhaseInterval;
    }

    if (nextTheory < sector) {
      sector = nextTheory;
      action = new Action(ActionType.THEORY_PHASE, null);
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
          action = new Action(ActionType.CONFERENCE_PHASE, null);
        }
      }
    }

    sector %= session.boardLength;
    const stillFirstRotation = session.firstRotation && sector >= currentSector;

    await operations.setCurrentStatus(session.sessionID, action, sector, stillFirstRotation);

    if (action.actionType === ActionType.PLAYER_TURN) {
      await operations.createAction(action.actionType, action.playerID);
    } else {
      const players = await session.getPlayers();
      await Promise.all(players.map((p) => operations.createAction(action.actionType, p.playerID)));
    }
  }

  async lastAction(session) {
    await operations.setCurrentStatus(session.sessionID, ActionType.LAST_ACTION, null, session.firstRotation);

    const players = await session.getPlayers();
    await Promise.all(players.map((p) => operations.createAction(ActionType.LAST_ACTION, p.playerID)));

    // TODO: Notify subscribers
  }

  async submitTheories(sessionID, playerID, theories) {
    const currentAction = await operations.getCurrentAction(playerID);

    if (currentAction === null || (currentAction.actionType !== ActionType.THEORY_PHASE &&
      currentAction.actionType !== ActionType.LAST_ACTION)) {
      return {
        allowed: false,
        successfulTheories: []
      };
    }

    // TODO: Limit number of theories allowed on last action

    const session = await Session.findByID(sessionID);
    const existingTheories = await session.getTheories();
    const numObjects = SECTOR_TYPES[session.boardLength].numObjects;

    const tokensLeft = Object.assign({}, numObjects);
    for (let i = 0; i < existingTheories.length; i++) {
      if (existingTheories[i].playerID === playerID) {
        tokensLeft[existingTheories[i].spaceObject] -= 1;
      }
    }

    const revealedSectors = new Set(existingTheories.filter((theory) => theory.revealed()).map((theory) => theory.sector));

    let successfulTheories = [];
    for (let i = 0; i < theories.length; i++) {
      const theory = theories[i];
      if (tokensLeft[theory.spaceObject.initial] > 0 && !revealedSectors.has(theory.sector)) {
        await operations.createTheory(sessionID, playerID, theory.spaceObject.initial, theory.sector);
        successfulTheories.push(theory);
      }
    }

    await operations.resolveAction(currentAction.actionID, null);
    const actions = await session.getActions();

    if (actions.length === 0) {
      await this.advanceTheories(session.sessionID);
      await this.nextAction(session);
    }

    this.notifySubscribers(session);

    return {
      allowed: true,
      successfulTheories
    }
  }

  async readConference(sessionID, playerID) {
    const currentAction = await operations.getCurrentAction(playerID);
    if (currentAction === null || currentAction.actionType !== ActionType.CONFERENCE_PHASE) {
      return false;
    }

    await operations.resolveAction(currentAction.actionID, null);
    const session = await Session.findByID(sessionID);
    const actions = await session.getActions();
    if (actions.length === 0) {
      await this.nextAction(session);
    }

    this.notifySubscribers(session);
    return true;
  }

  async advanceTheories(sessionID) {
    await operations.advanceTheories(sessionID);
  }

  async makeMove(sessionID, playerID, turn, sectors) {
    const currentAction = await operations.getCurrentAction(playerID);
    const actionMatches = currentAction !== null
      && ((currentAction.actionType === ActionType.PLAYER_TURN)
      || (currentAction.actionType === ActionType.LAST_ACTION
          && turn.turnType === TurnType.LOCATE_PLANET_X));

    if (!actionMatches) {
      return false;
    }

    if (currentAction.actionType !== ActionType.LAST_ACTION) {
      await operations.advancePlayer(playerID, sectors);
    }

    await operations.resolveAction(currentAction.actionID, turn);

    const session = await Session.findByID(sessionID);

    if (turn.turnType === TurnType.LOCATE_PLANET_X && turn.successful) {
      const players = await session.getPlayers();
      for (let i = 0; i < players.length; i++) {
        const player = players[i];
        if (player.playerID !== playerID) {
          await operations.createAction(ActionType.LAST_ACTION, player.playerID);
        }
      }
      await operations.setCurrentAction(sessionID, new Action(ActionType.LAST_ACTION, null));
    } else {
      const actions = await session.getActions();
      if (actions.length == 0) {
        if (currentAction.actionType === ActionType.LAST_ACTION) {
          await operations.setCurrentAction(sessionID, new Action(ActionType.END_GAME, null));
        } else {
          await this.nextAction(session);
        }
      }
    }

    this.notifySubscribers(session);
    return true;
  }

  async createSession(numSectors, name) {
    const session = await Session.create(numSectors);
    const { sessionID, playerNum, playerID } = await operations.newPlayer(session.code, name, true);
    const action = new Action(ActionType.START_GAME, playerID)
    await operations.setCurrentAction(sessionID, action);
    session.currentAction = action;
    return { playerID, playerNum, session };
  }
}

module.exports = {
  Session,
  SessionManager
};
