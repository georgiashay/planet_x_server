const { SpaceObject } = require("./game");

const ActionType = {
  START_GAME: "START_GAME",
  PLAYER_TURN: "PLAYER_TURN",
  CONFERENCE_PHASE: "CONFERENCE_PHASE",
  THEORY_PHASE: "THEORY_PHASE",
  LAST_ACTION: "LAST_ACTION",
  END_GAME: "END_GAME"
};

class Action {
  constructor(actionType, playerID, actionID=null) {
    this.actionType = actionType;
    this.playerID = playerID;
    this.actionID = actionID;
  }

  json() {
    return {
      actionType: this.actionType,
      playerID: this.playerID
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
  constructor(playerID=undefined, turnTime=undefined) {
    if (turnTime === undefined) {
      turnTime = new Date();
    }
    this.time = turnTime;
    this.playerID = playerID;
  }

  static parse(s, playerID, turnTime) {
    switch(s[0]) {
      case "S": return SurveyTurn.parse(s, playerID, turnTime);
      case "T": return TargetTurn.parse(s, playerID, turnTime);
      case "R": return ResearchTurn.parse(s, playerID, turnTime);
      case "C": return ConferenceTurn.parse(s, playerID, turnTime);
      case "L": return LocateTurn.parse(s, playerID, turnTime);
      case "G": return TheoryTurn.parse(s, playerID, turnTime);
    }
  }

  static fromJson(info) {
    switch(info.turnType) {
      case TurnType.SURVEY: return new SurveyTurn(SpaceObject.parse(info.spaceObject), info.sectors, info.playerID, info.time);
      case TurnType.TARGET: return new TargetTurn(info.sector, info.playerID, info.time);
      case TurnType.RESEARCH: return new ResearchTurn(info.index, info.playerID, info.time);
      case TurnType.CONFERENCE: return new ConferenceTurn(info.index, info.playerID, info.time);
      case TurnType.LOCATE_PLANET_X: return new LocateTurn(info.sector, SpaceObject.parse(info.leftObject), SpaceObject.parse(info.rightObject), info.successful, info.playerID, info.time);
    }
  }
}

class SurveyTurn extends Turn {
  turnType = TurnType.SURVEY;

  constructor(spaceObject, sectors, playerID=undefined, turnTime=undefined) {
    super(playerID, turnTime);
    this.spaceObject = spaceObject;
    this.sectors = sectors;
  }

  toString() {
    return "Survey, " + this.spaceObject.proper() + ", " + this.sectors.map((s) => s+1).join("-");
  }

  code() {
    return "S" + this.spaceObject.initial + this.sectors.join(",");
  }

  json() {
    return {
      turnType: "SURVEY",
      spaceObject: this.spaceObject.json(),
      sectors: this.sectors,
      text: this.toString(),
      time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, playerID, turnTime) {
    const spaceObject = SpaceObject.parse(s[1]);
    const sectors = s.slice(2).split(",").map((sector) => parseInt(sector));
    return new SurveyTurn(spaceObject, sectors, playerID, turnTime);
  }
}

class TargetTurn extends Turn {
  turnType = TurnType.TARGET;

  constructor(sector, playerID=undefined, turnTime=undefined) {
    super(playerID, turnTime);
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
      time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, playerID, turnTime) {
    const sector = parseInt(s.slice(1));
    return new TargetTurn(sector, playerID, turnTime);
  }
}

class ResearchTurn extends Turn {
  turnType = TurnType.RESEARCH;

  constructor(researchIndex, playerID, turnTime) {
    super(playerID, turnTime);
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
      time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, playerID, turnTime) {
    const researchIndex = parseInt(s.slice(1));
    return new ResearchTurn(researchIndex, playerID, turnTime);
  }
}

class ConferenceTurn extends Turn {
  turnType = TurnType.CONFERENCE;

  constructor(conferenceIndex, playerID, turnTime) {
    super(playerID, turnTime);
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
      time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, playerID, turnTime) {
    const conferenceIndex = parseInt(s.slice(1));
    return new ConferenceTurn(conferenceIndex, playerID, turnTime);
  }
}

class LocateTurn extends Turn {
  turnType = TurnType.LOCATE_PLANET_X;

  constructor(sector, leftObject, rightObject, successful, playerID, turnTime) {
    super(playerID, turnTime);
    this.sector = sector;
    this.leftObject = leftObject;
    this.rightObject = rightObject;
    this.successful = successful;
  }

  toString() {
    return "Locate Planet X, " + (this.successful ? "Success" : "Fail");
  }

  code() {
    return "L" + +this.successful + this.leftObject.initial + this.rightObject.initial + this.sector;
  }

  json() {
    return {
      turnType: "LOCATE_PLANET_X",
      sector: this.sector,
      leftObject: this.leftObject.json(),
      rightObject: this.rightObject.json(),
      successful: this.successful,
      text: this.toString(),
      time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, playerID, turnTime) {
    const successful = !!+s[1];
    const leftObject = SpaceObject.parse(s[2]);
    const rightObject = SpaceObject.parse(s[3]);
    const sector = parseInt(s.slice(4));
    return new LocateTurn(sector, leftObject, rightObject, successful, playerID, turnTime);
  }
}

class TheoryTurn extends Turn {
  turnType = TurnType.THEORY;

  constructor(theories, playerID, turnTime) {
    super(playerID, turnTime);
    this.theories = theories;
  }

  toString() {
    return "Submit Theories, " + this.theories.map((theory) => theory.sector + 1).join(" ");
  }

  code() {
    return "G" + this.theories.map((theory) => theory.spaceObject.initial + theory.sector).join(",");
  }

  json() {
    return {
      turnType: "THEORY",
      theories: this.theories.map((theory) => theory.json()),
      text: this.toString(),
      time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, playerID, turnTime) {
    const theoryStrings = s.slice(1).split(",");
    let theories = [];
    if (s.length > 1) {
      theories = theoryStrings.map((theoryString) => {
        const object = SpaceObject.parse(theoryString[0]);
        const sector = parseInt(theoryString.slice(1));
        return new Theory(object, sector, playerID);
      });
    }
    return new TheoryTurn(theories, playerID, turnTime);
  }
}

class Player {
  constructor(playerID, num, name, sector, arrival) {
    this.playerID = playerID;
    this.num = num;
    this.name = name;
    this.sector = sector;
    this.arrival = arrival;
  }

  toString() {
    return "Player " + this.num + ": " + this.name + " (#" + this.arrival +
            " in sector " + (this.sector + 1) + ")";
  }

  json() {
    return {
      num: this.num,
      name: this.name,
      sector: this.sector,
      arrival: this.arrival,
      id: this.playerID
    }
  }
}

class Theory {
  constructor(spaceObject, sector, accuracy=undefined, playerID=null, progress=0, frozen=false, time=null, id=null) {
    this.spaceObject = spaceObject;
    this.sector = sector;
    this.progress = progress;
    this.frozen = frozen;
    this.playerID = playerID;
    this.accurate = accuracy;
    this.id = id;
    this.time = time;
  }

  toString() {
    return "Theory: Sector " + (this.sector + 1) + " is " +
            this.spaceObject.one + " " + this.spaceObject.name;
  }

  code() {
    return this.spaceObject.initial + this.sector;
  }

  revealed() {
    return this.frozen;
  }

  setAccuracy(board) {
    const accuracy = board.objects[this.sector].initial === this.spaceObject.initial;
    this.accurate = accuracy;
  }

  json(board) {
    return {
      spaceObject: this.spaceObject.json(),
      sector: this.sector,
      progress: this.progress,
      revealed: this.revealed(),
      accurate: this.accurate,
      playerID: this.playerID,
      time: this.time,
      id: this.id
    }
  }

  static fromJson(obj) {
    return new Theory(SpaceObject.parse(obj.spaceObject), obj.sector);
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

  json() {
    return {
      first: this.firstPoints,
      planetX: this.planetXPoints,
      objects: this.objectPoints,
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
  Theory,
  Score
}
