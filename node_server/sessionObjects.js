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
  LOCATE_PLANET_X: "LOCATE_PLANET_X"
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
      case "L": return LocateTurn.parse(s, playerID, turnTime);
    }
  }

  static fromJson(info) {
    switch(info.turnType) {
      case TurnType.SURVEY: return new SurveyTurn(SpaceObject.parse(info.spaceObject), info.sectors, info.playerID, info.time);
      case TurnType.TARGET: return new TargetTurn(info.sector, info.playerID, info.time);
      case TurnType.RESEARCH: return new ResearchTurn(info.index, info.playerID, info.time);
      case TurnType.LOCATE_PLANET_X: return new LocateTurn(info.successful, info.playerID, info.time);
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
    return "Survey: " + this.spaceObject.initial + ", " + this.sectors.join("-");
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
    return "Target: Sector " + (this.sector + 1);
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
    return "Research: " + String.fromCharCode(this.researchIndex + 65);
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

class LocateTurn extends Turn {
  turnType = TurnType.LOCATE_PLANET_X;

  constructor(successful, playerID, turnTime) {
    super(playerID, turnTime);
    this.successful = successful;
  }

  toString() {
    return "Locate Planet X: " + this.successful ? "success" : "failure";
  }

  code() {
    return "L" + +this.successful
  }

  json() {
    return {
      turnType: "LOCATE_PLANET_X",
      successful: this.successful,
      text: this.toString(),
      time: this.time,
      playerID: this.playerID
    }
  }

  static parse(s, playerID, turnTime) {
    const successful = !!+s[1];
    return new LocateTurn(successful, playerID, turnTime);
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
      id: this.playeriD
    }
  }
}

class Theory {
  constructor(spaceObject, sector, playerID=null, progress=0) {
    this.spaceObject = spaceObject;
    this.sector = sector;
    this.progress = progress;
    this.playerID = playerID;
  }

  toString() {
    return "Theory: Sector " + (this.sector + 1) + " is " +
            this.spaceObject.one + " " + this.spaceObject.name;
  }

  revealed() {
    return this.progress == 3;
  }

  json() {
    return {
      spaceObject: this.spaceObject.json(),
      sector: this.sector,
      progress: this.progress,
      revealed: this.revealed(),
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
  LocateTurn,
  ActionType,
  Action,
  Player,
  Theory
}
