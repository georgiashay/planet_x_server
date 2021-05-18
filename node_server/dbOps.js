const mysql = require("mysql");
const creds = require("./creds.json");

const { Game, SpaceObject, StartingInformation,
        Research, Conference, Board } = require("./game");

const { Turn, Action, Theory, Player, ActionType } = require("./sessionObjects");

const pool  = mysql.createPool({
    host     : creds.hostname,
    user     : creds.username,
    password : creds.password,
    database : creds.database
});

function queryPromise(query, values=[]) {
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

function queryConnectionPromise(connection, query, values=[]) {
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

function getPoolConnection() {
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

const operations = {
  pickGame: async function(numSectors) {
    connection = await getPoolConnection();
    await queryConnectionPromise(connection, "START TRANSACTION;");
    await queryConnectionPromise(connection, "SET @maxID := (SELECT MAX(id) FROM games WHERE board_size = ?);", [numSectors]);
    await queryConnectionPromise(connection, "SET @minID := (SELECT MIN(id) FROM games WHERE board_size = ?);", [numSectors]);

    const { results } = await queryConnectionPromise(connection,
      `SELECT *
         FROM games AS r1 JOIN
             (SELECT CEIL(RAND() *
                 (@maxID - @minID) + @minID)  AS id)
             AS r2
         WHERE r1.id >= r2.id AND board_size = ?
         ORDER BY r1.id ASC
         LIMIT 1;`, [numSectors]);

    await queryConnectionPromise(connection, "COMMIT;");
    connection.release();

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
    const { results } = await queryPromise("SELECT * FROM games WHERE id = ?", [gameID]);
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
    const { results } = await queryPromise("SELECT * from games WHERE game_code = ?", [gameCode]);
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
    const { results } = await queryPromise("SELECT session_code FROM sessions");
    return results.map((row) => row.session_code);
  },
  createSession: async function(sessionCode, numSectors, gameID) {
    try {
      const { results } = await queryPromise("INSERT INTO sessions (session_code, game_size, game_id) VALUES (?, ?, ?)", [sessionCode, numSectors, gameID]);
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
    const { results } = await queryPromise("SELECT * FROM sessions WHERE session_code = ?", [sessionCode]);
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
    const { results } = await queryPromise("SELECT * FROM sessions WHERE id = ?", [sessionID]);
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
    const { results } = await queryPromise("SELECT * FROM theories WHERE session_id = ?", [sessionID]);
    return results.map((row) => new Theory(SpaceObject.parse(row.object), row.sector, !!+row.accurate, row.player_id, row.progress, !!+row.frozen, row.turn, row.id));
  },
  getPlayersForSession: async function(sessionID) {
    const { results } = await queryPromise("SELECT * FROM players WHERE session_id = ?", [sessionID]);
    return results.map((row) => new Player(row.id, row.num, row.name, row.sector, row.arrival));
  },
  newPlayer: async function(sessionCode, name, creator) {
    const connection = await getPoolConnection();
    await queryConnectionPromise(connection, "START TRANSACTION;");
    await queryConnectionPromise(connection, "CALL NewPlayer(?, ?, @PlayerNum, @PlayerID)", [sessionCode, name]);
    const { results } = await queryConnectionPromise(connection, "SELECT @PlayerNum, @PlayerID");

    if(creator) {
      await queryConnectionPromise(connection, "INSERT INTO actions(action_type, player_id, turn, resolved) VALUES('START_GAME', ?, 0, FALSE);", [results[0]["@PlayerID"]]);
    }

    await queryConnectionPromise(connection, "COMMIT;");
    connection.release();

    return {
      playerNum: results[0]["@PlayerNum"],
      playerID: results[0]["@PlayerID"]
    }
  },
  movePlayer: async function(playerID, sector, arrival) {
    await queryPromise("UPDATE players SET sector = ?, arrival = ? WHERE id = ?", [sector, arrival, playerID]);
  },
  createTheory: async function(sessionID, playerID, spaceObject, sector, accurate, turn) {
    await queryPromise("INSERT INTO theories (session_id, player_id, object, sector, progress, accurate, turn) VALUES (?, ?, ?, ?, 0, ?, ?);", [sessionID, playerID, spaceObject, sector, accurate, turn]);
  },
  advanceTheories: async function(sessionID) {
    const connection = await getPoolConnection();
    await queryConnectionPromise("START TRANSACTION;");
    const { results } = await queryConnectionPromise(connection,
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
        await queryConnectionPromise(connection, "CALL MovePlayer(?, ?)", [results[i].id, results[i].move_sectors]);
      }
    }
    await queryConnectionPromise(connection, "UPDATE theories SET progress = progress + 1 WHERE session_id = ? AND frozen IS FALSE;", [sessionID]);
    await queryConnectionPromise(connection,
      `UPDATE theories SET frozen = 1 WHERE session_id = ? AND (sector IN (
        SELECT * FROM (
        SELECT sector FROM theories WHERE progress = 3 AND accurate IS TRUE AND frozen is FALSE AND session_id = ?
        ) AS revealed_sectors

      ) OR progress = 3);`, [sessionID, sessionID]);
    await queryConnectionPromise("COMMIT;");

    connection.release();
  },
  advancePlayer: async function(playerID, sectors) {
    await queryPromise("CALL MovePlayer(?, ?)", [playerID, sectors]);
  },
  getCurrentActionsForSession: async function(sessionID) {
    const { results } = await queryPromise(
      `SELECT actions.id, actions.action_type, actions.player_id, actions.turn
      FROM actions, players
      WHERE actions.resolved IS FALSE AND actions.player_id = players.id
      AND players.session_id = ?`, [sessionID]);

    return results.map((row) => new Action(ActionType[row.action_type], row.player_id, row.turn, row.id));
  },
  getPreviousTurns: async function(sessionID) {
    const { results } = await queryPromise(
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
    await queryPromise("INSERT INTO actions(action_type, player_id, turn, resolved) VALUES(?, ?, ?, FALSE);", [actionType, playerID, turn]);
  },
  getCurrentAction: async function(playerID) {
    const { results } = await queryPromise("SELECT id, action_type, player_id, turn FROM actions WHERE player_id = ? AND resolved IS FALSE", [playerID]);

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

    await queryPromise("UPDATE actions SET resolved = TRUE, resolve_time = ?, resolve_action = ? WHERE id = ?;", [turnTime, turnCode, actionID]);
  },
  setCurrentAction: async function(sessionID, action) {
    await queryPromise("UPDATE sessions SET current_action = ?, current_turn = ?, action_player = ? WHERE id = ?;", [action.actionType, action.turn, action.playerID, sessionID]);
  },
  setCurrentStatus: async function(sessionID, action, currentSector, firstRotation) {
    await queryPromise(
      `UPDATE sessions SET first_rotation = ?, current_sector = ?,
      current_action = ?, current_turn = ?, action_player = ?
      WHERE id = ?;`,
      [firstRotation, currentSector, action.actionType, action.turn, action.playerID, sessionID]
    );
  }
};

module.exports = operations;
