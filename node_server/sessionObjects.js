const { SectorElement } = require("./game");

const ActionType = {
  START_GAME: "START_GAME",
  PLAYER_TURN: "PLAYER_TURN",
  CONFERENCE_PHASE: "CONFERENCE_PHASE",
  THEORY_PHASE: "THEORY_PHASE",
  LAST_ACTION: "LAST_ACTION",
  END_GAME: "END_GAME"
};

class Action {
  constructor(actionType, playerID, turn, actionID=null) {
    this.actionType = actionType;
    this.playerID = playerID;
    this.turn = turn;
    this.actionID = actionID;
  }

  json() {
    return {
      actionType: this.actionType,
      playerID: this.playerID,
      turn: this.turn
    }
  }
}

const TurnType = {
  SURVEY: "SURVEY",
  TARGET: "TARGET",
  RESEARCH: "RESEARCH",
  CONFERENCE: "CONFERENCE",
  LOCATE_PLANET_X: "LOCATE_PLANET_X",
  THEORY: "THEORY"
};

class Turn {
  constructor(turnNumber=undefined, playerID=undefined, turnTime=undefined) {
    this.turnNumber = turnNumber;
    this.playerID = playerID;
    if (turnTime === undefined) {
      turnTime = new Date();
    }
    this.time = turnTime;
  }

  setTurnNumber(turnNumber) {
    this.turnNumber = turnNumber;
  }

  static parse(s, turnNumber, playerID, turnTime) {
    switch(s[0]) {
      case "S": return SurveyTurn.parse(s, turnNumber, playerID, turnTime);
      case "T": return TargetTurn.parse(s, turnNumber, playerID, turnTime);
      case "R": return ResearchTurn.parse(s, turnNumber, playerID, turnTime);
      case "C": return ConferenceTurn.parse(s, turnNumber, playerID, turnTime);
      case "L": return LocateTurn.parse(s, turnNumber, playerID, turnTime);
      case "G": return TheoryTurn.parse(s, turnNumber, playerID, turnTime);
    }
  }

  static fromJson(info, theme="space") {
    switch(info.turnType) {
      case TurnType.SURVEY: return new SurveyTurn(SectorElement.parse(info.spaceObject, theme), info.sectors, info.turn, info.playerID, info.time);
      case TurnType.TARGET: return new TargetTurn(info.sector, info.turn, info.playerID, info.time);
      case TurnType.RESEARCH: return new ResearchTurn(info.index, info.turn, info.playerID, info.time);
      case TurnType.CONFERENCE: return new ConferenceTurn(info.index, info.turn, info.playerID, info.time);
      case TurnType.LOCATE_PLANET_X: return new LocateTurn(info.sector, SectorElement.parse(info.leftObject, theme), SectorElement.parse(info.rightObject, theme), info.successful, info.turn, info.playerID, info.time);
    }
  }
}

class SurveyTurn extends Turn {
  turnType = TurnType.SURVEY;

  constructor(spaceObject, sectors, turnNumber=undefined, playerID=undefined, turnTime=undefined) {
    super(turnNumber, playerID, turnTime);
    this.spaceObject = spaceObject;
    this.sectors = sectors;
  }

  toString(theme) {
    return "Survey, " + this.spaceObject[theme].proper() + ", " + this.sectors.map((s) => s+1).join("-");
  }

  code() {
    return "S" + this.spaceObject.space.initial + this.sectors.join(",");
  }

  json(theme) {
    return {
      turnType: "SURVEY",
      spaceObject: this.spaceObject[theme].json(),
      sectors: this.sectors,
      text: this.toString(theme),
      turn: this.turnNumber,
			time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, turnNumber, playerID, turnTime) {
    const spaceObject = SectorElement.parse(s[1]);
    const sectors = s.slice(2).split(",").map((sector) => parseInt(sector));
    return new SurveyTurn(spaceObject, sectors, turnNumber, playerID, turnTime);
  }
}

class TargetTurn extends Turn {
  turnType = TurnType.TARGET;

  constructor(sector, turnNumber=undefined, playerID=undefined, turnTime=undefined) {
    super(turnNumber, playerID, turnTime);
    this.sector = sector;
  }

  toString() {
    return "Target, Sector " + (this.sector + 1);
  }

  code() {
    return "T" + this.sector;
  }

  json() {
    return {
      turnType: "TARGET",
      sector: this.sector,
      text: this.toString(),
      turn: this.turnNumber,
			time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, turnNumber, playerID, turnTime) {
    const sector = parseInt(s.slice(1));
    return new TargetTurn(sector, turnNumber, playerID, turnTime);
  }
}

class ResearchTurn extends Turn {
  turnType = TurnType.RESEARCH;

  constructor(researchIndex, turnNumber, playerID, turnTime) {
    super(turnNumber, playerID, turnTime);
    this.researchIndex = researchIndex;
  }

  toString() {
    return "Research " + String.fromCharCode(this.researchIndex + 65);
  }

  code() {
    return "R" + this.researchIndex;
  }

  json() {
    return {
      turnType: "RESEARCH",
      index: this.researchIndex,
      text: this.toString(),
      turn: this.turnNumber,
			time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, turnNumber, playerID, turnTime) {
    const researchIndex = parseInt(s.slice(1));
    return new ResearchTurn(researchIndex, turnNumber, playerID, turnTime);
  }
}

class ConferenceTurn extends Turn {
  turnType = TurnType.CONFERENCE;

  constructor(conferenceIndex, turnNumber, playerID, turnTime) {
    super(turnNumber, playerID, turnTime);
    this.conferenceIndex = conferenceIndex;
  }

  toString() {
    return "Conference X" + (this.conferenceIndex + 1);
  }

  code() {
    return "C" + this.conferenceIndex;
  }

  json() {
    return {
      turnType: "CONFERENCE",
      index: this.conferenceIndex,
      text: this.toString(),
      turn: this.turnNumber,
			time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, turnNumber, playerID, turnTime) {
    const conferenceIndex = parseInt(s.slice(1));
    return new ConferenceTurn(conferenceIndex, turnNumber, playerID, turnTime);
  }
}

class LocateTurn extends Turn {
  turnType = TurnType.LOCATE_PLANET_X;

  constructor(sector, leftObject, rightObject, successful, turnNumber, playerID, turnTime) {
    super(turnNumber, playerID, turnTime);
    this.sector = sector;
    this.leftObject = leftObject;
    this.rightObject = rightObject;
    this.successful = successful;
  }

  toString() {
    return "Locate Planet X, " + (this.successful ? "Success" : "Fail");
  }

  code() {
    return "L" + +this.successful + this.leftObject.space.initial + this.rightObject.space.initial + this.sector;
  }

  json(theme) {
    return {
      turnType: "LOCATE_PLANET_X",
      sector: this.sector,
      leftObject: this.leftObject[theme].json(),
      rightObject: this.rightObject[theme].json(),
      successful: this.successful,
      text: this.toString(),
      turn: this.turnNumber,
			time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, turnNumber, playerID, turnTime) {
    const successful = !!+s[1];
    const leftObject = SectorElement.parse(s[2]);
    const rightObject = SectorElement.parse(s[3]);
    const sector = parseInt(s.slice(4));
    return new LocateTurn(sector, leftObject, rightObject, successful, turnNumber, playerID, turnTime);
  }
}

class TheoryTurn extends Turn {
  turnType = TurnType.THEORY;

  constructor(theories, turnNumber, playerID, turnTime) {
    super(turnNumber, playerID, turnTime);
    this.theories = theories;
  }

  toString() {
    return "Submit Theories, " + this.theories.map((theory) => theory.sector + 1).join(" ");
  }

  code() {
    return "G" + this.theories.map((theory) => theory.spaceObject.space.initial + theory.sector).join(",");
  }

  json(theme) {
    return {
      turnType: "THEORY",
      theories: this.theories.map((theory) => theory.json(theme)),
      text: this.toString(),
      turn: this.turnNumber,
			time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, turnNumber, playerID, turnTime) {
    const theoryStrings = s.slice(1).split(",");
    let theories = [];
    if (s.length > 1) {
      theories = theoryStrings.map((theoryString) => {
        const object = SectorElement.parse(theoryString[0]);
        const sector = parseInt(theoryString.slice(1));
        return new Theory(object, sector, playerID);
      });
    }
    return new TheoryTurn(theories, turnNumber, playerID, turnTime);
  }
}

class Player {
  constructor(playerID, num, name, color, sector, arrival, kicked, connected) {
    this.playerID = playerID;
    this.num = num;
    this.name = name;
    this.color = color;
    this.sector = sector;
    this.arrival = arrival;
    this.kicked = kicked;
    this.connected = connected;
  }

  toString() {
    return "Player " + this.num + ": " + this.name + " (#" + this.arrival +
            " in sector " + (this.sector + 1) + ")";
  }

  json() {
    return {
      num: this.num,
      name: this.name,
      color: this.color,
      sector: this.sector,
      arrival: this.arrival,
      kicked: this.kicked,
      connected: this.connected,
      id: this.playerID
    }
  }
}

class KickVote {
  constructor(kickPlayerID, votePlayerID, vote) {
    this.kickPlayerID = kickPlayerID;
    this.votePlayerID = votePlayerID;
    this.vote = vote;
  }

  json() {
    return {
      kickPlayerID: this.kickPlayerID,
      votePlayerID: this.votePlayerID,
      vote: this.vote
    }
  }
}

class Theory {
  constructor(spaceObject, sector, accuracy=undefined, playerID=null, progress=0, frozen=false, turn=null, id=null) {
    this.spaceObject = spaceObject;
    this.sector = sector;
    this.progress = progress;
    this.frozen = frozen;
    this.playerID = playerID;
    this.accurate = accuracy;
    this.id = id;
    this.turn = turn;
  }

  toString(theme) {
    return "Theory: Sector " + (this.sector + 1) + " is " +
            this.spaceObject[theme].one + " " + this.spaceObject[theme].name;
  }

  code() {
    return this.spaceObject.space.initial + this.sector;
  }

  revealed() {
    return this.frozen;
  }

  setAccuracy(board) {
    const accuracy = board.objects[this.sector].space.initial === this.spaceObject.space.initial;
    this.accurate = accuracy;
  }

  setTurn(turn) {
    this.turn = turn;
  }

  json(theme) {
    return {
      spaceObject: this.spaceObject[theme].json(),
      sector: this.sector,
      progress: this.progress,
      revealed: this.revealed(),
      accurate: this.accurate,
      playerID: this.playerID,
      turn: this.turn,
      id: this.id
    }
  }

  static fromJson(obj, theme="space") {
    return new Theory(SectorElement.parse(obj.spaceObject, theme), obj.sector);
  }
}

class Score {
  constructor(playerID, firstPoints, planetXPoints, objectValues) {
    this.playerID = playerID;
    this.firstPoints = firstPoints;
    this.planetXPoints = planetXPoints;
    this.objectPointValues = objectValues;
    this.objectPoints = Object.keys(objectValues).reduce((o, key) => Object.assign(o, {[key]: 0}), {});
  }

  total() {
    return this.firstPoints + this.planetXPoints + Object.values(this.objectPoints).reduce((a, b) => a + b, 0);
  }

  addPoints(obj) {
    if (!this.objectPointValues.hasOwnProperty(obj)) {
      throw "Unknown object " + obj;
    }
    const points = this.objectPointValues[obj];

    if (this.objectPoints.hasOwnProperty(obj)) {
      this.objectPoints[obj] += points;
    } else {
      this.objectPoints[obj] = points;
    }
  }

  addFirstPoint() {
    this.firstPoints += 1;
  }

  setPlanetXPoints(points) {
    this.planetXPoints = points;
  }

  objectPointsJson(theme) {
    const objectPoints = {};

    for (const obj in this.objectPoints) {
      objectPoints[SectorElement[obj][theme].initial] = this.objectPoints[obj];
    }

    return objectPoints;
  }

  json(theme) {
    return {
      first: this.firstPoints,
      [SectorElement.Goal[theme].initial]: this.planetXPoints,
      objects: this.objectPointsJson(theme),
      total: this.total(),
      playerID: this.playerID
    }
  }
}

module.exports = {
  TurnType,
  Turn,
  SurveyTurn,
  TargetTurn,
  ResearchTurn,
  ConferenceTurn,
  LocateTurn,
  TheoryTurn,
  ActionType,
  Action,
  Player,
  KickVote,
  Theory,
  Score
}
