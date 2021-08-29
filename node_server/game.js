class Game {
  constructor(board, startingInfo, research, conference, version) {
    this.board = board;
    this.startingInfo = startingInfo;
    this.research = research;
    this.conference = conference;
    this.version = version;
  }

  json(theme) {
    return {
      board: this.board.json(theme),
      research: this.research.json(this.board, theme),
      conference: this.conference.json(this.board, theme),
      startingInformation: this.startingInfo.json(theme),
      version: this.version
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

  json(board, theme) {
    return this.rules.map((rule) => rule.json(board, theme));
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

  json(board, theme) {
    return this.rules.map((rule) => rule.json(board, theme));
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

  json(theme) {
    const jObject = {};
    for (let i = 0; i < SEASONS.length; i++) {
      jObject[SEASONS[i]] = this.clues[SEASONS[i]].map((clue) => clue.json(theme));
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
    const eliminatedObject = SectorElement.parse(objectCode);
    return new EliminationClue(sectorNumber, eliminatedObject);
  }

  text(theme) {
    return sectorName[theme].proper + " " + (this.sectorNumber + 1) + " does not contain " +
            this.eliminatedObject[theme].one + " " + this.eliminatedObject[theme].name + ".";
  }

  json(theme) {
    return {
      sector: this.sectorNumber,
      eliminatedObject: this.eliminatedObject[theme].json(),
      text: this.text(theme)
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

class SectorElement {
  static Empty = {
    NAME: "Empty",
    "space": new SectorElement("E", "E", "empty sector", false),
    "ocean": new SectorElement("E", "E", "empty sector", false),
    "castle": new SectorElement("E", "E", "empty seat", false)
  };
  static Prime = {
    NAME: "Prime",
    "space": new SectorElement("C", "C", "comet", false),
    "ocean": new SectorElement("C", "C", "crab", false),
    "castle": new SectorElement("S", "CS", "court scholar", false)
  };
  static Clustered = {
    NAME: "Clustered",
    "space": new SectorElement("A", "A", "asteroid", false),
    "ocean": new SectorElement("S", "S", "seahorse", false),
    "castle": new SectorElement("K", "K", "knight", false)
  };
  static Banded = {
    NAME: "Banded",
    "space": new SectorElement("D", "DP", "dwarf planet", false),
    "ocean": new SectorElement("D", "D", "dolphin", false),
    "castle": new SectorElement("P", "P", "prince", false)
  };
  static Goal = {
    NAME: "Goal",
    "space": new SectorElement("X", "X", "Planet X", true),
    "ocean": new SectorElement("O", "O", "octopus", false),
    "castle": new SectorElement("Q", "Q", "queen", false)
  };
  static NeedsSpace = {
    NAME: "NeedsSpace",
    "space": new SectorElement("G", "GC", "gas cloud", false),
    "ocean": new SectorElement("T", "T", "turtle", false),
    "castle": new SectorElement("J", "J", "jester", false)
  };
  static Surrounded = {
    NAME: "Surrounded",
    "space": new SectorElement("B", "BH", "black hole", false),
    "ocean": new SectorElement("R", "R", "remora", false),
    "castle": new SectorElement("C", "C", "chaplain", false)
  };

  constructor(initial, multiInitial, name, unique) {
    this.initial = initial;
    this.multiInitial = multiInitial;
    this.name = name;
    this.unique = unique;

    if (["a", "e", "i", "o", "u"].indexOf(this.name[0].toLowerCase()) >= 0) {
      this.one = "an";
    } else {
      this.one = "a";
    }
  }

  static parse(s, theme="space") {
    switch(theme) {
      case "space": switch(s) {
        case "E": return SectorElement.Empty;
        case "C": return SectorElement.Prime;
        case "A": return SectorElement.Clustered;
        case "D": return SectorElement.Banded;
        case "X": return SectorElement.Goal;
        case "G": return SectorElement.NeedsSpace;
        case "B": return SectorElement.Surrounded;
        case "-": return null;
      }
      case "ocean": switch(s) {
        case "E": return SectorElement.Empty;
        case "C": return SectorElement.Prime;
        case "S": return SectorElement.Clustered;
        case "T": return SectorElement.Banded;
        case "O": return SectorElement.Goal;
        case "D": return SectorElement.NeedsSpace;
        case "R": return SectorElement.Surrounded;
        case "-": return null;
      }
      case "castle": switch(s) {
        case "E": return SectorElement.Empty;
        case "S": return SectorElement.Prime;
        case "K": return SectorElement.Clustered;
        case "P": return SectorElement.Banded;
        case "Q": return SectorElement.Goal;
        case "J": return SectorElement.NeedsSpace;
        case "C": return SectorElement.Surrounded;
        case "-": return null;
      }
    }
  }

  plural() {
    const esEnds = ["s", "ss", "sh", "ch", "x", "z"];
    if (esEnds.some((end) => this.name.endsWith(end))) {
      return this.name + "es";
    } else {
      return this.name + "s";
    }
  }

  singular() {
    if (this.unique) {
      return this.name;
    } else {
      return "the " + this.name;
    }
  }

  proper() {
    const words = this.name.split(" ");
    const properWords = words.map((word) => word.slice(0, 1).toUpperCase() + word.slice(1));
    return properWords.join(" ");
  }

  properPlural() {
    const esEnds = ["s", "ss", "sh", "ch", "x", "z"];
    if (esEnds.some((end) => this.name.endsWith(end))) {
      return this.proper() + "es";
    } else {
      return this.proper() + "s";
    }
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

const sectorName = {
  "space": {
    name: "sector",
    plural: "sectors",
    proper: "Sector",
    properPlural: "Sectors"
  },
  "ocean": {
    name: "sector",
    plural: "sectors",
    proper: "Sector",
    properPlural: "Sectors"
  },
  "castle": {
    name: "seat",
    plural: "seats",
    proper: "Seat",
    properPlural: "Seats"
  }
};

class Board {
  constructor(objects) {
    this.objects = objects;
    this.numObjects = {};
    for (let i = 0; i < objects.length; i++) {
      if (this.numObjects[objects[i].NAME] !== undefined) {
        this.numObjects[objects[i].NAME] += 1;
      } else {
        this.numObjects[objects[i].NAME] = 1;
      }
    }
  }

  toString() {
    return this.objects.map((obj) => obj == null ? "-" : obj.initial);
  }

  static parse(s) {
    const objects = s.split("").map((c) => SectorElement.parse(c));
    return new Board(objects);
  }

  numObjectsJson(theme) {
    const numObjects = {};
    for (const obj in this.numObjects) {
      numObjects[SectorElement[obj][theme].initial] = this.numObjects[obj];
    }
    return numObjects;
  }

  json(theme) {
    return {
      objects: this.objects.map((obj) => obj[theme].json()),
      size: this.objects.length,
      numObjects: this.numObjectsJson(theme)
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

  shortString() {
    switch(this) {
      case RuleQualifier.NONE: return "No";
      case RuleQualifier.AT_LEAST_ONE: return "≥ 1";
      case RuleQualifier.EVERY: return "Every";
    }
  }

  shortStringForObject(obj, numObject) {
    switch(this) {
      case RuleQualifier.NONE:
        return numObject === 1 ? (obj.initial + " not") : ("No " + obj.initial);
      case RuleQualifier.AT_LEAST_ONE:
        return "≥ 1 " + obj.initial;
      case RuleQualifier.EVERY:
        return numObject === 1 ? obj.initial : ("Every " + obj.initial);
    }
  }

  multiInitialStringForObject(obj, numObject) {
    switch(this) {
      case RuleQualifier.NONE:
        return numObject === 1 ? (obj.multiInitial + " not") : ("No " + obj.multiInitial);
      case RuleQualifier.AT_LEAST_ONE:
        return "≥ 1 " + obj.multiInitial;
      case RuleQualifier.EVERY:
        return numObject === 1 ? obj.multiInitial : ("Every " + obj.multiInitial);
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

  shortString() {
    switch(this) {
      case Precision.STRICT: return "";
      case Precision.WITHIN: return "≤";
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

  categoryName(theme) {
    let objects = this.spaceObjects();
    if (objects[objects.length - 1] === SectorElement.Empty) {
      objects = objects.slice(0, objects.length - 1);
    }
    let objectTitles = objects.map((obj) => obj[theme].category());
    return objectTitles.join(" & ");
  }

  shortCategory(theme) {
    let objects = this.spaceObjects();
    if (objects[objects.length - 1] === SectorElement.Empty) {
      objects = objects.slice(0, objects.length - 1);
    }
    return objects.map((obj) => obj[theme].initial).join("&");
  }

  multiInitialCategory(theme) {
    let objects = this.spaceObjects();
    if (objects[objects.length - 1] === SectorElement.Empty) {
      objects = objects.slice(0, objects.length - 1);
    }
    return objects.map((obj) => obj[theme].multiInitial).join("&");
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

  text(board, theme) {
    const numObject1 = board.numObjects[this.spaceObject1.NAME];
    const numObject2 = board.numObjects[this.spaceObject2.NAME];

    return this.qualifier.forObject(this.spaceObject1[theme], numObject1) + " adjacent to "
            + this.spaceObject2[theme].anyOf(numObject2) + ".";
  }

  shortText(board, theme) {
    const numObject1 = board.numObjects[this.spaceObject1.NAME];

    return this.qualifier.shortStringForObject(this.spaceObject1[theme], numObject1)
            + " adj. to " + this.spaceObject2[theme].initial;
  }

  multiInitialText(board, theme) {
    const numObject1 = board.numObjects[this.spaceObject1.NAME];

    return this.qualifier.multiInitialStringForObject(this.spaceObject1[theme], numObject1)
            + " adj. to " + this.spaceObject2[theme].multiInitial;
  }

  static parse(s) {
    const spaceObject1 = SectorElement.parse(s[1]);
    const spaceObject2 = SectorElement.parse(s[2]);
    const qualifier = RuleQualifier.parse(s[3]);
    return new AdjacentRule(spaceObject1, spaceObject2, qualifier);
  }

  json(board, theme) {
    return {
      ruleType: "ADJACENT",
      spaceObject1: this.spaceObject1[theme].json(),
      spaceObject2: this.spaceObject2[theme].json(),
      qualifier: this.qualifier.json(),
      categoryName: this.categoryName(theme),
			shortCategory: this.shortCategory(theme),
      multiInitialCategory: this.multiInitialCategory(theme),
      text: this.text(board, theme),
      shortText: this.shortText(board, theme),
      multiInitialText: this.multiInitialText(board, theme)
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

  text(board, theme) {
    const numObject1 = board.numObjects[this.spaceObject1.NAME];
    const numObject2 = board.numObjects[this.spaceObject2.NAME];

    return this.qualifier.forObject(this.spaceObject1[theme], numObject1) + " directly opposite "
            + this.spaceObject2[theme].anyOf(numObject2) + ".";
  }

  shortText(board, theme) {
    const numObject1 = board.numObjects[this.spaceObject1.NAME];

    return this.qualifier.shortStringForObject(this.spaceObject1[theme], numObject1)
            + " opp. " + this.spaceObject2[theme].initial;
  }

  multiInitialText(board, theme) {
    const numObject1 = board.numObjects[this.spaceObject1.NAME];

    return this.qualifier.multiInitialStringForObject(this.spaceObject1[theme], numObject1)
            + " opp. " + this.spaceObject2[theme].multiInitial;
  }

  static parse(s) {
    const spaceObject1 = SectorElement.parse(s[1]);
    const spaceObject2 = SectorElement.parse(s[2]);
    const qualifier = RuleQualifier.parse(s[3]);
    return new OppositeRule(spaceObject1, spaceObject2, qualifier);
  }

  json(board, theme) {
    return {
      ruleType: "OPPOSITE",
      spaceObject1: this.spaceObject1[theme].json(),
      spaceObject2: this.spaceObject2[theme].json(),
      qualifier: this.qualifier.json(),
      categoryName: this.categoryName(theme),
			shortCategory: this.shortCategory(theme),
      multiInitialCategory: this.multiInitialCategory(theme),
      text: this.text(board, theme),
      shortText: this.shortText(board, theme),
      multiInitialText: this.multiInitialText(board, theme)
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

  text(board, theme) {
    const numObject1 = board.numObjects[this.spaceObject1.NAME];
    const numObject2 = board.numObjects[this.spaceObject2.NAME];

    return this.qualifier.forObject(this.spaceObject1[theme], numObject1) + " within "
            + this.numSectors + " " + sectorName[theme].plural + " of " + this.spaceObject2[theme].anyOf(numObject2) + ".";
  }

  shortText(board, theme) {
    const numObject1 = board.numObjects[this.spaceObject1.NAME];

    return this.qualifier.shortStringForObject(this.spaceObject1[theme], numObject1)
            + " within " + this.numSectors + " of " + this.spaceObject2[theme].initial;
  }

  multiInitialText(board, theme) {
    const numObject1 = board.numObjects[this.spaceObject1.NAME];

    return this.qualifier.multiInitialStringForObject(this.spaceObject1[theme], numObject1)
            + " within " + this.numSectors + " of " + this.spaceObject2[theme].multiInitial;
  }

  static parse(s) {
    const spaceObject1 = SectorElement.parse(s[1]);
    const spaceObject2 = SectorElement.parse(s[2]);
    const qualifier = RuleQualifier.parse(s[3]);
    const numSectors = parseInt(s.slice(4));
    return new WithinRule(spaceObject1, spaceObject2, qualifier, numSectors);
  }

  json(board, theme) {
    return {
      ruleType: "WITHIN",
      spaceObject1: this.spaceObject1[theme].json(),
      spaceObject2: this.spaceObject2[theme].json(),
      numSectors: this.numSectors,
      qualifier: this.qualifier.json(),
      categoryName: this.categoryName(theme),
			shortCategory: this.shortCategory(theme),
      multiInitialCategory: this.multiInitialCategory(theme),
      text: this.text(board, theme),
      shortText: this.shortText(board, theme),
      multiInitialText: this.multiInitialText(board, theme)
    }
  }
}

class AdjacentSelfRule extends SelfRule {
  constructor(spaceObject, qualifier) {
    super();
    this.spaceObject = spaceObject;
    this.qualifier = qualifier;
  }

  text(board, theme) {
    const numObject = board.numObjects[this.spaceObject.NAME];
    return this.qualifier.forObject(this.spaceObject[theme], numObject) + " adjacent to another "
            + this.spaceObject[theme].name + ".";
  }

  shortText(board, theme) {
    const numObject = board.numObjects[this.spaceObject.NAME];

    return this.qualifier.shortStringForObject(this.spaceObject[theme], numObject)
            + " adj. to " + this.spaceObject[theme].initial;
  }

  multiInitialText(board, theme) {
    const numObject = board.numObjects[this.spaceObject.NAME];

    return this.qualifier.multiInitialStringForObject(this.spaceObject[theme], numObject)
            + " adj. to " + this.spaceObject[theme].multiInitial;
  }

  static parse(s) {
    const spaceObject = SectorElement.parse(s[1]);
    const qualifier = RuleQualifier.parse(s[2]);
    return new AdjacentSelfRule(spaceObject, qualifier);
  }

  json(board, theme) {
    return {
      ruleType: "ADJACENT_SELF",
      spaceObject: this.spaceObject[theme].json(),
      qualifier: this.qualifier.json(),
      categoryName: this.categoryName(theme),
			shortCategory: this.shortCategory(theme),
      multiInitialCategory: this.multiInitialCategory(theme),
      text: this.text(board, theme),
      shortText: this.shortText(board, theme),
      multiInitialText: this.multiInitialText(board, theme)
    }
  }
}

class OppositeSelfRule extends SelfRule {
  constructor(spaceObject, qualifier) {
    super();
    this.spaceObject = spaceObject;
    this.qualifier = qualifier;
  }

  text(board, theme) {
    const numObject = board.numObjects[this.spaceObject.NAME];
    return this.qualifier.forObject(this.spaceObject[theme], numObject) + " directly opposite another "
            + this.spaceObject[theme].name + ".";
  }

  shortText(board, theme) {
    const numObject = board.numObjects[this.spaceObject.NAME];

    return this.qualifier.shortStringForObject(this.spaceObject[theme], numObject)
            + " opp. " + this.spaceObject[theme].initial;
  }

  multiInitialText(board, theme) {
    const numObject = board.numObjects[this.spaceObject.NAME];

    return this.qualifier.multiInitialStringForObject(this.spaceObject[theme], numObject)
            + " opp. " + this.spaceObject[theme].multiInitial;
  }

  static parse(s) {
    const spaceObject = SectorElement.parse(s[1]);
    const qualifier = RuleQualifier.parse(s[2]);
    return new OppositeSelfRule(spaceObject, qualifier);
  }

  json(board, theme) {
    return {
      ruleType: "OPPOSITE_SELF",
      spaceObject: this.spaceObject[theme].json(),
      qualifier: this.qualifier.json(),
      categoryName: this.categoryName(theme),
			shortCategory: this.shortCategory(theme),
      multiInitialCategory: this.multiInitialCategory(theme),
      text: this.text(board, theme),
      shortText: this.shortText(board, theme),
      multiInitialText: this.multiInitialText(board, theme)
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

  text(board, theme) {
    return "The " + this.spaceObject[theme].plural() + " are in a band of "
            + this.precision.toString() + " " + this.bandSize + ".";
  }

  shortText(theme) {
    return this.spaceObject[theme].initial + " in a band of " + this.precision.shortString() + " " + this.bandSize;
  }

  multiInitialText(theme) {
    return this.spaceObject[theme].multiInitial + " in a band of " + this.precision.shortString() + " " + this.bandSize;
  }

  static parse(s) {
    const spaceObject = SectorElement.parse(s[1]);
    const precision = Precision.parse(s[2]);
    const bandSize = parseInt(s.slice(3));
    return new BandRule(spaceObject, bandSize, precision);
  }

  json(board, theme) {
    return {
      ruleType: "BAND",
      spaceObject: this.spaceObject[theme].json(),
      numSectors: this.bandSize,
      precision: this.precision.json(),
      categoryName: this.categoryName(theme),
			shortCategory: this.shortCategory(theme),
      multiInitialCategory: this.multiInitialCategory(theme),
      text: this.text(board, theme),
      shortText: this.shortText(theme),
      multiInitialText: this.multiInitialText(theme)
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

  text(board, theme) {
    return "The " + this.spaceObject[theme].plural() + " are only in " + sectorName[theme].plural + " "
            + this.positions.map((i) => i+1).join(", ") + ".";
  }

  shortText(theme) {
    return this.spaceObject[theme].initial + " only in " + this.positions.map((i) => i+1).join(", ");
  }

  multiInitialText(theme) {
    return this.spaceObject[theme].multiInitial + " only in " + this.positions.map((i) => i+1).join(", ");
  }

  static parse(s) {
    const spaceObject = SectorElement.parse(s[1]);
    const positions = s.slice(2).map((c) => c.charCodeAt(0) - 65);
    return new SectorsRule(spaceObject, positions);
  }

  json(board, theme) {
    return {
      ruleType: "SECTORS",
      spaceObject: this.spaceObject[theme].json(),
      allowedSectors: this.positions,
      categoryName: this.categoryName(theme),
			shortCategory: this.shortCategory(theme),
      multiInitialCategory: this.multiInitialCategory(theme),
      text: this.text(board, theme),
      shortText: this.shortText(theme),
      multiInitialText: this.multiInitialText(theme)
    }
  }
}

class BoardType {
  constructor(boardSize, numObjects, scoreValues, theoryPhaseInterval, conferencePhases, theoriesPerTurn, numTargets) {
    this.boardSize = boardSize;
    this.numObjects = numObjects;
    this.scoreValues = scoreValues;
    this.theoryPhaseInterval = theoryPhaseInterval;
    const numTheoryPhases = Math.floor(boardSize/theoryPhaseInterval);
    this.theoryPhases = Array.from(numTheoryPhases).map((el, i) => ((i+1) * theoryPhaseInterval) - 1);
    this.conferencePhases = conferencePhases;
    this.theoriesPerTurn = theoriesPerTurn;
    this.numTargets = numTargets;
  }
}

const SECTOR_TYPES = {
  12: new BoardType(12, {Goal: 1, Empty: 2, NeedsSpace: 2, Banded: 1, Clustered: 4, Prime: 2}, {Clustered: 2, Prime: 3, NeedsSpace: 4, Banded: 4}, 3, [8], 1, 2),
  18: new BoardType(18, {Goal: 1, Empty: 5, NeedsSpace: 2, Banded: 4, Clustered: 4, Prime: 2}, {Clustered: 2, Prime: 3, NeedsSpace: 4, Banded: 2}, 3, [6, 15], 2, 2),
  24: new BoardType(24, {Goal: 1, Empty: 6, NeedsSpace: 3, Banded: 4, Clustered: 6, Prime: 3, Surrounded: 1}, {Clustered: 2, Banded: 2, Prime: 3, NeedsSpace: 4, Banded: 5}, 3, [6, 15, 21], 2, 3)
};

module.exports = {
  Game,
  SectorElement,
  Board,
  StartingInformation,
  Conference,
  Research,
  BoardType,
  SECTOR_TYPES
};
