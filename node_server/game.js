class Game {
  constructor(board, startingInfo, research, conference) {
    this.board = board;
    this.startingInfo = startingInfo;
    this.research = research;
    this.conference = conference;
  }

  json() {
    return {
      board: this.board.json(),
      research: this.research.json(this.board),
      conference: this.conference.json(this.board),
      startingInformation: this.startingInfo.json()
    }
  }
}

class Conference {
  constructor(rules) {
    this.rules = rules;
  }

  static parse(s) {
    const ruleStrs = s.split("|");
    const rules = ruleStrs.map((ruleStr) => Rule.parse(ruleStr));
    return new Conference(rules);
  }

  json(board) {
    return this.rules.map((rule) => rule.json(board));
  }
}

class Research {
  constructor(rules) {
    this.rules = rules;
  }

  static parse(s) {
    const ruleStrs = s.split("|");
    const rules = ruleStrs.map((ruleStr) => Rule.parse(ruleStr));
    return new Research(rules);
  }

  json(board) {
    return this.rules.map((rule) => rule.json(board));
  }
}

class StartingInformation {
  constructor(clues) {
    this.clues = clues;
  }

  static parse(s) {
    const clueStrs = s.split("|");
    const clues = {};

    for (let i = 0; i < SEASONS.length; i++) {
      const seasonClues = [];
      const clueStr = clueStrs[i];
      for (let j = 0; j < clueStr.length; j+=2) {
        seasonClues.push(EliminationClue.parse(clueStr.slice(j, j+2)));
      }
      clues[SEASONS[i]] = seasonClues;
    }

    return new StartingInformation(clues);
  }

  json() {
    const jObject = {};
    for (let i = 0; i < SEASONS.length; i++) {
      jObject[SEASONS[i]] = this.clues[SEASONS[i]].map((clue) => clue.json());
    }
    return jObject;
  }
}

class EliminationClue {
  constructor(sectorNumber, eliminatedObject) {
    this.sectorNumber = sectorNumber;
    this.eliminatedObject = eliminatedObject;
  }

  static parse(s) {
    const sectorCode = s[0];
    const objectCode = s[1];
    const sectorNumber = sectorCode.charCodeAt(0) - 65;
    const eliminatedObject = SpaceObject.parse(objectCode);
    return new EliminationClue(sectorNumber, eliminatedObject);
  }

  text() {
    return "Sector " + (this.sectorNumber + 1) + " does not contain " +
            this.eliminatedObject.one + " " + this.eliminatedObject.name + ".";
  }

  json() {
    return {
      sector: this.sectorNumber,
      eliminatedObject: this.eliminatedObject.json(),
      text: this.text()
    }
  }
}

const Season = {
  WINTER: "WINTER",
  SPRING: "SPRING",
  SUMMER: "SUMMER",
  AUTUMN: "AUTUMN"
};

const SEASONS = [Season.WINTER, Season.SPRING, Season.SUMMER, Season.AUTUMN];

class SpaceObject {
  static Empty = new SpaceObject("E", "empty sector", false);
  static Comet = new SpaceObject("C", "comet", false);
  static Asteroid = new SpaceObject("A", "asteroid", false);
  static DwarfPlanet = new SpaceObject("D", "dwarf planet", false);
  static PlanetX = new SpaceObject("X", "Planet X", true);
  static GasCloud = new SpaceObject("G", "gas cloud", false);
  static BlackHole = new SpaceObject("B", "black hole", false);

  constructor(initial, name, unique) {
    this.initial = initial;
    this.name = name;
    this.unique = unique;

    if (["a", "e", "i", "o", "u"].indexOf(this.name[0].toLowerCase()) >= 0) {
      this.one = "an";
    } else {
      this.one = "a";
    }
  }

  static parse(s) {
    switch(s) {
      case "E": return SpaceObject.Empty;
      case "C": return SpaceObject.Comet;
      case "A": return SpaceObject.Asteroid;
      case "D": return SpaceObject.DwarfPlanet;
      case "X": return SpaceObject.PlanetX;
      case "G": return SpaceObject.GasCloud;
      case "B": return SpaceObject.BlackHole;
      case "-": return null;
    }
  }

  plural() {
    return this.name + "s";
  }

  singular() {
    if (this.unique) {
      return this.name;
    } else {
      return "the " + this.name;
    }
  }

  proper() {
    const words = this.name.split();
    const properWords = words.map((word) => word.slice(0, 1).toUpperCase() + word.slice(1));
    return properWords.join(" ");
  }

  properPlural() {
    return this.proper() + "s";
  }

  category() {
    if (this.unique) {
      return this.name;
    } else {
      return this.properPlural();
    }
  }

  anyOf(numObject) {
    if (numObject == 1) {
      return this.singular();
    } else {
      return this.one + " " + this.name;
    }
  }

  json() {
    return {
      initial: this.initial,
      name: this.name
    }
  }
}

class Board {
  constructor(objects) {
    this.objects = objects;
    this.numObjects = {};
    for (let i = 0; i < objects.length; i++) {
      if (this.numObjects[objects[i].initial] !== undefined) {
        this.numObjects[objects[i].initial] += 1;
      } else {
        this.numObjects[objects[i].initial] = 1;
      }
    }
  }

  toString() {
    return this.objects.map((obj) => obj == null ? "-" : obj.initial);
  }

  static parse(s) {
    const objects = s.split("").map((c) => SpaceObject.parse(c));
    return new Board(objects);
  }

  json() {
    return {
      objects: this.objects.map((obj) => obj.json()),
      size: this.objects.length,
      numObjects: this.numObjects
    }
  }
}

class RuleQualifier {
  static NONE = new RuleQualifier();
  static AT_LEAST_ONE = new RuleQualifier();
  static EVERY = new RuleQualifier();

  toString() {
    switch(this) {
      case RuleQualifier.NONE: return "No";
      case RuleQualifier.AT_LEAST_ONE: return "At least one";
      case RuleQualifier.EVERY: return "Every";
    }
  }

  forObject(obj, numObject) {
    if (this == RuleQualifier.NONE) {
      if (numObject == 1) {
        return obj.singular().slice(0, 1).toUpperCase() + obj.singular().slice(1) + " is not";
      } else {
        return "No " + obj.name + " is";
      }
    } else if (this == RuleQualifier.AT_LEAST_ONE) {
      return "At least one " + obj.name + " is";
    } else if (this == RuleQualifier.EVERY) {
      if (numObject == 1) {
        return obj.singular().slice(0, 1).toUpperCase() + obj.singular().slice(1) + " is";
      } else {
        return "Every " + obj.name + " is";
      }
    }
  }

  static parse(s) {
    switch(s) {
      case "N": return RuleQualifier.NONE;
      case "A": return RuleQualifier.AT_LEAST_ONE;
      case "E": return RuleQualifier.EVERY;
    }
  }

  json() {
    switch(this) {
      case RuleQualifier.NONE: return "NONE";
      case RuleQualifier.AT_LEAST_ONE: return "AT_LEAST_ONE";
      case RuleQualifier.EVERY: return "EVERY";
    }
  }
}

class Precision {
  static STRICT = new Precision();
  static WITHIN = new Precision();

  toString() {
    switch(this) {
      case Precision.STRICT: return "exactly";
      case Precision.WITHIN: return "at most";
    }
  }

  static parse(s) {
    switch(s) {
      case "S": return Precision.STRICT;
      case "W": return Precision.WITHIN;
    }
  }

  json() {
    switch(this) {
      case Precision.STRICT: return "STRICT";
      case Precision.WITHIN: return "WITHIN";
    }
  }
}

class Rule {
  constructor() {
    if (new.target === Rule) {
      throw new TypeError("Cannot construct Rule instances directly");
    }
  }

  static parse(ruleStr) {
    switch(ruleStr[0]) {
      case "B": return BandRule.parse(ruleStr);
      case "O": return OppositeRule.parse(ruleStr);
      case "S": return OppositeSelfRule.parse(ruleStr);
      case "A": return AdjacentRule.parse(ruleStr);
      case "C": return AdjacentSelfRule.parse(ruleStr);
      case "W": return WithinRule.parse(ruleStr);
      case "P": return SectorsRule.parse(ruleStr);
    }
  }

  categoryName() {
    let objects = this.spaceObjects();
    if (objects[objects.length - 1] === SpaceObject.Empty) {
      objects = objects.slice(0, objects.length - 1);
    }
    let objectTitles = objects.map((obj) => obj.category());
    return objectTitles.join(" & ");
  }
}

class RelationRule extends Rule {
  constructor() {
    super();
    if (new.target === RelationRule) {
      throw new TypeError("Cannot construct RelationRule instances directly");
    }
  }

  spaceObjects() {
    return [this.spaceObject1, this.spaceObject2];
  }
}

class SelfRule extends Rule {
  constructor() {
    super();
    if (new.target === SelfRule) {
      throw new TypeError("Cannot construct SelfRule instances directly");
    }
  }

  spaceObjects() {
    return [this.spaceObject];
  }
}

class AdjacentRule extends RelationRule {
  constructor(spaceObject1, spaceObject2, qualifier) {
    super();
    this.spaceObject1 = spaceObject1;
    this.spaceObject2 = spaceObject2;
    this.qualifier = qualifier;
  }

  text(board) {
    const numObject1 = board.numObjects[this.spaceObject1.initial];
    const numObject2 = board.numObjects[this.spaceObject2.initial];

    return this.qualifier.forObject(this.spaceObject1, numObject1) + " adjacent to "
            + this.spaceObject2.anyOf(numObject2) + ".";
  }

  static parse(s) {
    const spaceObject1 = SpaceObject.parse(s[1]);
    const spaceObject2 = SpaceObject.parse(s[2]);
    const qualifier = RuleQualifier.parse(s[3]);
    return new AdjacentRule(spaceObject1, spaceObject2, qualifier);
  }

  json(board) {
    return {
      ruleType: "ADJACENT",
      spaceObject1: this.spaceObject1.json(),
      spaceObject2: this.spaceObject2.json(),
      qualifier: this.qualifier.json(),
      categoryName: this.categoryName(),
      text: this.text(board)
    }
  }
}

class OppositeRule extends RelationRule {
  constructor(spaceObject1, spaceObject2, qualifier) {
    super();
    this.spaceObject1 = spaceObject1;
    this.spaceObject2 = spaceObject2;
    this.qualifier = qualifier;
  }

  text(board) {
    const numObject1 = board.numObjects[this.spaceObject1.initial];
    const numObject2 = board.numObjects[this.spaceObject2.initial];

    return this.qualifier.forObject(this.spaceObject1, numObject1) + " directly opposite "
            + this.spaceObject2.anyOf(numObject2) + ".";
  }

  static parse(s) {
    const spaceObject1 = SpaceObject.parse(s[1]);
    const spaceObject2 = SpaceObject.parse(s[2]);
    const qualifier = RuleQualifier.parse(s[3]);
    return new OppositeRule(spaceObject1, spaceObject2, qualifier);
  }

  json(board) {
    return {
      ruleType: "OPPOSITE",
      spaceObject1: this.spaceObject1.json(),
      spaceObject2: this.spaceObject2.json(),
      qualifier: this.qualifier.json(),
      categoryName: this.categoryName(),
      text: this.text(board)
    }
  }
}

class WithinRule extends RelationRule {
  constructor(spaceObject1, spaceObject2, qualifier, numSectors) {
    super();
    this.spaceObject1 = spaceObject1;
    this.spaceObject2 = spaceObject2;
    this.qualifier = qualifier;
    this.numSectors = numSectors;
  }

  text(board) {
    const numObject1 = board.numObjects[this.spaceObject1.initial];
    const numObject2 = board.numObjects[this.spaceObject2.initial];

    return this.qualifier.forObject(this.spaceObject1, numObject1) + " within "
            + this.numSectors + " sectors of " + this.spaceObject2.anyOf(numObject2) + ".";
  }

  static parse(s) {
    const spaceObject1 = SpaceObject.parse(s[1]);
    const spaceObject2 = SpaceObject.parse(s[2]);
    const qualifier = RuleQualifier.parse(s[3]);
    const numSectors = parseInt(s.slice(4));
    return new WithinRule(spaceObject1, spaceObject2, qualifier, numSectors);
  }

  json(board) {
    return {
      ruleType: "WITHIN",
      spaceObject1: this.spaceObject1.json(),
      spaceObject2: this.spaceObject2.json(),
      numSectors: this.numSectors,
      qualifier: this.qualifier.json(),
      categoryName: this.categoryName(),
      text: this.text(board)
    }
  }
}

class AdjacentSelfRule extends SelfRule {
  constructor(spaceObject, qualifier) {
    super();
    this.spaceObject = spaceObject;
    this.qualifier = qualifier;
  }

  text(board) {
    const numObject = board.numObjects[this.spaceObject.initial];
    return this.qualifier.forObject(this.spaceObject, numObject) + " adjacent to another "
            + this.spaceObject.name + ".";
  }

  static parse(s) {
    const spaceObject = SpaceObject.parse(s[1]);
    const qualifier = RuleQualifier.parse(s[2]);
    return new AdjacentSelfRule(spaceObject, qualifier);
  }

  json(board) {
    return {
      ruleType: "ADJACENT_SELF",
      spaceObject: this.spaceObject.json(),
      qualifier: this.qualifier.json(),
      categoryName: this.categoryName(),
      text: this.text(board)
    }
  }
}

class OppositeSelfRule extends SelfRule {
  constructor(spaceObject, qualifier) {
    super();
    this.spaceObject = spaceObject;
    this.qualifier = qualifier;
  }

  text(board) {
    const numObject = board.numObjects[this.spaceObject.initial];
    return this.qualifier.forObject(this.spaceObject, numObject) + " directly opposite another "
            + this.spaceObject.name + ".";
  }

  static parse(s) {
    const spaceObject = SpaceObject.parse(s[1]);
    const qualifier = RuleQualifier.parse(s[2]);
    return new OppositeSelfRule(spaceObject, qualifier);
  }

  json(board) {
    return {
      ruleType: "OPPOSITE_SELF",
      spaceObject: this.spaceObject.json(),
      qualifier: this.qualifier.json(),
      categoryName: this.categoryName(),
      text: this.text(board)
    }
  }
}

class BandRule extends SelfRule {
  constructor(spaceObject, bandSize, precision) {
    super();
    this.spaceObject = spaceObject;
    this.bandSize = bandSize;
    this.precision = precision;
  }

  text(board) {
    return "The " + this.spaceObject.plural() + " are in a band of "
            + this.precision.toString() + " " + this.bandSize + ".";
  }

  static parse(s) {
    const spaceObject = SpaceObject.parse(s[1]);
    const bandSize = parseInt(s[2]);
    const precision = Precision.parse(s[3])
    return new BandRule(spaceObject, bandSize, precision);
  }

  json(board) {
    return {
      ruleType: "BAND",
      spaceObject: this.spaceObject.json(),
      numSectors: this.bandSize,
      precision: this.precision.json(),
      categoryName: this.categoryName(),
      text: this.text(board)
    }
  }
}

class SectorsRule extends SelfRule {
  constructor(spaceObject, positions, boardSize) {
    super();
    this.spaceObject = spaceObject;
    this.positions = positions;
    this.boardSize = boardSize;
  }

  text(board) {
    return "The " + this.spaceObject.plural() + " are only in sectors "
            + this.positions.map((i) => i+1).join(", ") + ".";
  }

  static parse(s) {
    const spaceObject = SpaceObject.parse(s[1]);
    const positions = s.slice(2).map((c) => c.charCodeAt(0) - 65);
    return new SectorsRule(spaceObject, positions);
  }

  json(board) {
    return {
      ruleType: "SECTORS",
      spaceObject: this.spaceObject.json(),
      allowedSectors: this.positions,
      categoryName: this.categoryName(),
      text: this.text(board)
    }
  }
}

class BoardType {
  constructor(boardSize, numObjects, theoryPhaseInterval, conferencePhases) {
    this.boardSize = boardSize;
    this.numObjects = numObjects;
    this.theoryPhaseInterval = theoryPhaseInterval;
    const numTheoryPhases = Math.floor(boardSize/theoryPhaseInterval);
    this.theoryPhases = Array.from(numTheoryPhases).map((el, i) => ((i+1) * theoryPhaseInterval) - 1);
    this.conferencePhases = conferencePhases;
  }
}

const SECTOR_TYPES = {
  12: new BoardType(12, {X: 1, E: 2, G: 2, D: 1, A: 4, C: 2}, 3, [8]),
  18: new BoardType(18, {X: 1, E: 5, G: 2, D: 4, A: 4, C: 2}, 3, [6, 15]),
  24: new BoardType(24, {X: 1, E: 6, G: 3, D: 4, A: 6, C: 3, B: 1}, 3, [6, 15, 21])
};

module.exports = {
  Game,
  SpaceObject,
  Board,
  StartingInformation,
  Conference,
  Research,
  BoardType,
  SECTOR_TYPES
};
