const operations = require("./dbOps");
const { Game, SpaceObject } = require("./game");

operations.pickGame(18).then(({game, gameCode, gameID}) => {
  console.log(game.json());
  console.log(gameCode);
  console.log(gameID);
});

operations.getGameByID(1160830).then(({game, gameCode, gameID}) => {
  console.log(gameCode);
});

operations.getGameByGameCode("A7M3D7").then(({game, gameCode, gameID}) => {
  console.log(gameID);
});
