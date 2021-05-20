const mysql = require("mysql");
const creds = require("./creds.json");

const { Game, SpaceObject, StartingInformation,
        Research, Conference, Board } = require("./game");

const { Turn, Action, Theory, Player, ActionType, KickVote } = require("./sessionObjects");

const Mutex = require('async-mutex').Mutex;

const pool  = mysql.createPool({
    host     : creds.hostname,
    user     : creds.username,
    password : creds.password,
    database : creds.database
});

function _getPoolConnection() {
  return new Promise(function(resolve, reject) {
    pool.getConnection(function(err, connection) {
      if (err) {
        reject(err);
      } else {
        resolve(connection);
      }
    })
  });
}

function _queryPromise(query, values=[]) {
  return new Promise(function(resolve, reject) {
    pool.query(query, values, function(error, results, fields) {
      if (error) {
        reject(error);
      } else {
        resolve({results, fields});
      }
    })
  });
}

function _queryConnectionPromise(connection, query, values=[]) {
  return new Promise(function(resolve, reject) {
    connection.query(query, values, function(error, results, fields) {
      if (error) {
        reject(error);
      } else {
        resolve({results, fields});
      }
    })
  });
}

class Connector {
  constructor(connection=undefined) {
    this.connection = undefined;
    this.transactionStack = [];
    this.lock = new Mutex();
  }

  async query(query, values=[]) {
    if (this.connection === undefined) {
      return _queryPromise(query, values);
    } else {
      return _queryConnectionPromise(this.connection, query, values);
    }
  }

  async startTransaction() {
    if (this.connection === undefined) {
      this.acquireLock();
      this.connection = await _getPoolConnection();
      return _queryConnectionPromise(this.connection, "START TRANSACTION;");
    } else {
      const index = this.transactionStack.length;
      this.transactionStack.push(index);
      return _queryConnectionPromise(this.connection, "SAVEPOINT intermediate_?", [index]);
    }
  }

  async commit() {
    if (this.transactionStack.length === 0) {
      const result = await _queryConnectionPromise(this.connection, "COMMIT;")
      this.release();
      this.connection = undefined;
      this.releaseLock();
      return result;
    } else {
      const index = this.transactionStack.pop();
      return _queryConnectionPromise(this.connection, "RELEASE SAVEPOINT intermediate_?", [index]);
    }
  }

  async rollback(connection) {
    if (this.transactionStack.length === 0) {
      const result = await _queryConnectionPromise(this.connection, "ROLLBACK;")
      this.release();
      this.connection = undefined;
      this.releaseLock();
      return result;
    } else {
      const index = this.transactionStack.pop();
      return _queryConnectionPromise(this.connection, "ROLLBACK TO intermediate_?", [index]);
    }
  }

  async release() {
    if (this.connection !== undefined && this.transactionStack.length === 0) {
      this.connection.release();
    }
  }

  async acquireLock() {
    this.releaseLockFunc = await this.lock.acquire();
  }

  async releaseLock() {
    this.releaseLockFunc();
  }
}

function queryWrapper(fn) {
  return async function() {
    if (arguments.length > fn.length && arguments[arguments.length - 1] !== undefined) {
      let connector = arguments[arguments.length - 1];
      if (connector === undefined) {
        connector = new Connector();
      }
      const context = { connector };
      return fn.apply(context, arguments);
    } else {
      const connector = new Connector();
      const context = { connector };
      return fn.apply(context, arguments);
    }
  }
}

const operations = {
  pickGame: async function(numSectors) {
    await this.connector.startTransaction();
    await this.connector.query("SET @maxID := (SELECT MAX(id) FROM games WHERE board_size = ?);", [numSectors]);
    await this.connector.query("SET @minID := (SELECT MIN(id) FROM games WHERE board_size = ?);", [numSectors]);

    const { results } = await this.connector.query(
      `SELECT *
         FROM games AS r1 JOIN
             (SELECT CEIL(RAND() *
                 (@maxID - @minID) + @minID)  AS id)
             AS r2
         WHERE r1.id >= r2.id AND board_size = ?
         ORDER BY r1.id ASC
         LIMIT 1;`, [numSectors]);

    await this.connector.commit();
    this.connector.release();

    if (results.length === 0) {
      return {
        game: undefined,
        gameCode: undefined,
        gameID: undefined
      }
    }

    const gameRow = results[0];

    const game = new Game(
      Board.parse(gameRow.board_objects),
      StartingInformation.parse(gameRow.starting_information),
      Research.parse(gameRow.research),
      Conference.parse(gameRow.conference)
    );

    return {
      game,
      gameCode: gameRow.game_code,
      gameID: gameRow.id
    }
  },
  getGameByID: async function(gameID) {
    const { results } = await this.connector.query("SELECT * FROM games WHERE id = ?", [gameID]);
    if (results.length == 0) {
      return {
        game: undefined,
        gameCode: undefined,
        gameID: undefined
      }
    }

    const gameRow = results[0];

    const game = new Game(
      Board.parse(gameRow.board_objects),
      StartingInformation.parse(gameRow.starting_information),
      Research.parse(gameRow.research),
      Conference.parse(gameRow.conference)
    );

    return {
      game,
      gameCode: gameRow.game_code,
      gameID: gameRow.id
    }
  },
  getGameByGameCode: async function(gameCode) {
    const { results } = await this.connector.query("SELECT * from games WHERE game_code = ?", [gameCode]);
    if (results.length == 0) {
      return {
        game: undefined,
        gameCode: undefined,
        gameID: undefined
      }
    }

    const gameRow = results[0];

    const game = new Game(
      Board.parse(gameRow.board_objects),
      StartingInformation.parse(gameRow.starting_information),
      Research.parse(gameRow.research),
      Conference.parse(gameRow.conference)
    );

    return {
      game,
      gameCode: gameRow.game_code,
      gameID: gameRow.id
    }
  },
  getSessionCodes: async function() {
    const { results } = await this.connector.query("SELECT session_code FROM sessions");
    return results.map((row) => row.session_code);
  },
  createSession: async function(sessionCode, numSectors, gameID) {
    try {
      const { results } = await this.connector.query("INSERT INTO sessions (session_code, game_size, game_id) VALUES (?, ?, ?)", [sessionCode, numSectors, gameID]);
      return results.insertId;
    } catch(e) {
      if (e.code === "ER_DUP_ENTRY") {
        return null;
      } else {
        throw(e);
      }
    }
  },
  getSessionByCode: async function(sessionCode) {
    const { results } = await this.connector.query("SELECT * FROM sessions WHERE session_code = ?", [sessionCode]);
    if (results.length == 0) {
      return null;
    }
    return {
      sessionID: results[0].id,
      sessionCode: results[0].session_code,
      gameSize: results[0].game_size,
      gameID: results[0].game_id,
      firstRotation: !!results[0].first_rotation,
      currentSector: results[0].current_sector,
      actionType: results[0].current_action,
      actionTurn: results[0].current_turn,
      actionPlayer: results[0].action_player,
    };
  },
  getSessionByID: async function(sessionID) {
    const { results } = await this.connector.query("SELECT * FROM sessions WHERE id = ?", [sessionID]);
    if (results.length == 0) {
      return null;
    }
    return {
      sessionID: results[0].id,
      sessionCode: results[0].session_code,
      gameSize: results[0].game_size,
      gameID: results[0].game_id,
      firstRotation: !!results[0].first_rotation,
      currentSector: results[0].current_sector,
      actionType: results[0].current_action,
      actionTurn: results[0].current_turn,
      actionPlayer: results[0].action_player
    };
  },
  getSessionByPlayerID: async function(playerID) {
    const { results } = await this.connector.query("SELECT sessions.* FROM sessions, players WHERE sessions.id = players.session_id AND players.id = ?;", [playerID]);
    if (results.length == 0) {
      return null;
    }
    return {
      sessionID: results[0].id,
      sessionCode: results[0].session_code,
      gameSize: results[0].game_size,
      gameID: results[0].game_id,
      firstRotation: !!results[0].first_rotation,
      currentSector: results[0].current_sector,
      actionType: results[0].current_action,
      actionTurn: results[0].current_turn,
      actionPlayer: results[0].action_player
    };
  },
  getTheoriesForSession: async function(sessionID) {
    const { results } = await this.connector.query("SELECT * FROM theories WHERE session_id = ?", [sessionID]);
    return results.map((row) => new Theory(SpaceObject.parse(row.object), row.sector, !!+row.accurate, row.player_id, row.progress, !!+row.frozen, row.turn, row.id));
  },
  getPlayersForSession: async function(sessionID) {
    const { results } = await this.connector.query("SELECT * FROM players WHERE session_id = ?", [sessionID]);
    return results.map((row) => new Player(row.id, row.num, row.name, row.color, row.sector, row.arrival, !!+row.kicked));
  },
  getKickVotesForSession: async function(sessionID) {
    const { results } = await this.connector.query("SELECT kick_player, vote_player, vote FROM players INNER JOIN kickvotes ON players.id = kickvotes.kick_player WHERE players.session_id = ?", [sessionID]);
    return results.map((row) => new KickVote(row.kick_player, row.vote_player, !!+row.vote));
  },
  getPlayer: async function(playerID) {
    const { results } = await this.connector.query("SELECT * FROM players WHERE id = ?", [playerID]);
    const row = results[0];
    return new Player(row.id, row.num, row.name, row.color, row.sector, row.arrival, row.kicked);
  },
  newPlayer: async function(sessionCode, name, creator) {
    await this.connector.startTransaction();
    await this.connector.query("CALL NewPlayer(?, ?, @PlayerNum, @PlayerID)", [sessionCode, name]);
    const { results } = await this.connector.query("SELECT @PlayerNum, @PlayerID");

    if(creator) {
      await this.connector.query("INSERT INTO actions(action_type, player_id, turn, resolved) VALUES('START_GAME', ?, 0, FALSE);", [results[0]["@PlayerID"]]);
    }

    await this.connector.commit();

    this.connector.release();

    return {
      playerNum: results[0]["@PlayerNum"],
      playerID: results[0]["@PlayerID"]
    }
  },
  movePlayer: async function(playerID, sector, arrival) {
    await this.connector.query("UPDATE players SET sector = ?, arrival = ? WHERE id = ?", [sector, arrival, playerID]);
  },
  kickVote: async function(sessionID, kickPlayerID, votePlayerID, kick, callbackKicked, callbackNotKicked) {
    if (kickPlayerID === votePlayerID) {
      return {
        allowed: false
      };
    }
    await this.connector.startTransaction();
    const bothPlayers = await this.connector.query("SELECT id, kicked FROM players WHERE session_id = ? AND id IN (?, ?) FOR UPDATE", [sessionID, kickPlayerID, votePlayerID]);
    if (bothPlayers.results.length < 2) {
      await this.connector.rollback();
      this.connector.release();
      return {
        allowed: false
      };
    } else if (bothPlayers.results.some((p) => p.kicked)) {
      await this.connector.rollback();
      this.connector.release();
      return {
        allowed: false
      };
    }
    await this.connector.query("INSERT INTO kickvotes(kick_player, vote_player, vote) VALUES(?, ?, ?) ON DUPLICATE KEY UPDATE vote = ?", [kickPlayerID, votePlayerID, kick, kick]);
    const players = await this.connector.query("SELECT COUNT(*) AS num_players FROM players WHERE session_id = ? AND kicked IS FALSE", [sessionID]);
    const numPlayers = players.results[0].num_players;
    const numVotes = await this.connector.query("SELECT * FROM kickvotes WHERE kick_player = ? AND vote IS TRUE", [kickPlayerID]);
    const kicked = numVotes.results.length >= numPlayers / 2;
    if (kicked) {
      await this.connector.query("UPDATE players SET kicked = TRUE WHERE id = ?", [kickPlayerID]);
      await this.connector.query("DELETE FROM actions WHERE player_id = ?", [kickPlayerID]);
      await callbackKicked(this.connector);
    } else {
      await callbackNotKicked(this.connector);
    }
    await this.connector.commit();
    this.connector.release();
    return { allowed: true, kicked };
  },
  createTheory: async function(sessionID, playerID, spaceObject, sector, accurate, turn) {
    await this.connector.query("INSERT INTO theories (session_id, player_id, object, sector, progress, accurate, turn) VALUES (?, ?, ?, ?, 0, ?, ?);", [sessionID, playerID, spaceObject, sector, accurate, turn]);
  },
  advanceTheories: async function(sessionID) {
    await this.connector.startTransaction();
    const { results } = await this.connector.query(
    `SELECT sessions.game_size, sessions.current_sector, players.id, players.sector, players.arrival, move_sectors FROM
      sessions INNER JOIN players ON sessions.id = players.session_id

      INNER JOIN (SELECT player_id, sum((1-accurate) * (1 - (
      sector NOT IN
      (
      SELECT * FROM
      (
      SELECT sector FROM theories WHERE progress = 2 AND accurate IS TRUE AND frozen is FALSE AND session_id = ?
      ) AS revealed_sectors
      )
      ) * (progress != 2))) as move_sectors
      FROM theories group by player_id) theories
      ON players.id = theories.player_id
      WHERE players.session_id = ?;`,
      [sessionID, sessionID]);

    results.sort((row1, row2) => {
      if (row1.sector === row2.sector) {
        return row1.arrival - row2.arrival;
      } else {
        const row1_ahead = (row1.sector - row1.current_sector + row1.game_size) % row1.game_size;
        const row2_ahead = (row2.sector - row2.current_sector + row2.game_size) % row2.game_size;
        return row2_ahead - row1_ahead;
      }
    });
    for (let i = 0; i < results.length; i++) {
      if (results[i].move_sectors > 0) {
        await this.connector.query("CALL MovePlayer(?, ?)", [results[i].id, results[i].move_sectors]);
      }
    }
    await this.connector.query("UPDATE theories SET progress = progress + 1 WHERE session_id = ? AND frozen IS FALSE;", [sessionID]);
    await this.connector.query(
      `UPDATE theories SET frozen = 1 WHERE session_id = ? AND (sector IN (
        SELECT * FROM (
        SELECT sector FROM theories WHERE progress = 3 AND accurate IS TRUE AND frozen is FALSE AND session_id = ?
        ) AS revealed_sectors

      ) OR progress = 3);`, [sessionID, sessionID]);

    await this.connector.commit();

    this.connector.release();
  },
  advancePlayer: async function(playerID, sectors) {
    await this.connector.query("CALL MovePlayer(?, ?)", [playerID, sectors]);
  },
  getCurrentActionsForSession: async function(sessionID) {
    const { results } = await this.connector.query(
      `SELECT actions.id, actions.action_type, actions.player_id, actions.turn
      FROM actions, players
      WHERE actions.resolved IS FALSE AND actions.player_id = players.id
      AND players.session_id = ?`, [sessionID]);

    return results.map((row) => new Action(ActionType[row.action_type], row.player_id, row.turn, row.id));
  },
  getPreviousTurns: async function(sessionID) {
    const { results } = await this.connector.query(
      `SELECT actions.player_id, actions.resolve_time, actions.resolve_action, actions.turn
      FROM actions, players
      WHERE actions.resolved IS TRUE AND actions.action_type != 'START_GAME'
      AND actions.action_type != 'END_GAME'
      AND actions.player_id = players.id AND players.session_id = ?`,
      [sessionID]
    );

    return results.map((row) => Turn.parse(row.resolve_action, row.turn, row.player_id, row.resolve_time));
  },
  createAction: async function(actionType, playerID, turn) {
    await this.connector.query("INSERT INTO actions(action_type, player_id, turn, resolved) VALUES(?, ?, ?, FALSE);", [actionType, playerID, turn]);
  },
  getCurrentAction: async function(playerID) {
    const { results } = await this.connector.query("SELECT id, action_type, player_id, turn FROM actions WHERE player_id = ? AND resolved IS FALSE", [playerID]);

    if (results.length == 0) {
      return null;
    } else {
      return new Action(ActionType[results[0].action_type], results[0].player_id, results[0].turn, results[0].id);
    }
  },
  resolveAction: async function(actionID, turn) {
    if (actionID == null) {
      return;
    }

    let turnTime;
    let turnCode;
    if (turn == null) {
      turnTime = new Date();
      turnCode = "";
    } else {
      turnTime = turn.time;
      turnCode = turn.code();
    }

    await this.connector.query("UPDATE actions SET resolved = TRUE, resolve_time = ?, resolve_action = ? WHERE id = ?;", [turnTime, turnCode, actionID]);
  },
  setCurrentAction: async function(sessionID, action) {
    await this.connector.query("UPDATE sessions SET current_action = ?, current_turn = ?, action_player = ? WHERE id = ?;", [action.actionType, action.turn, action.playerID, sessionID]);
  },
  setCurrentStatus: async function(sessionID, action, currentSector, firstRotation) {
    await this.connector.query(
      `UPDATE sessions SET first_rotation = ?, current_sector = ?,
      current_action = ?, current_turn = ?, action_player = ?
      WHERE id = ?;`,
      [firstRotation, currentSector, action.actionType, action.turn, action.playerID, sessionID]
    );
  },
  setColor: async function(playerID, color) {
    try {
      await this.connector.query("UPDATE players SET color = ? WHERE id = ?", [color, playerID]);
      return true;
    } catch(e) {
      if (e.code === "ER_DUP_ENTRY") {
        return false;
      } else {
        throw(e);
      }
    }
  }
};

const wrappedOperations = {};
for (const funcKey in operations) {
  wrappedOperations[funcKey] = queryWrapper(operations[funcKey]);
}

module.exports = wrappedOperations;
