// From Mwni on https://github.com/mysqljs/mysql/pull/2218 comment
function patchMysqlPool(mysql) {
	let createPool = mysql.createPool;

	mysql.createPool = function(config) {
		let pool = createPool(config);

		if(config.idleConnectionTimeout) {
			let getConnection = pool.getConnection;

			pool.getConnection = function(callback) {
				getConnection.call(pool, (err, connection) => {
					if(err){
						callback(err, connection);
						return;
					}

          clearTimeout(connection.__idleTimeout);
          connection.__idleTimeout = setTimeout(() => {
            pool._purgeConnection(connection);
          }, config.idleConnectionTimeout);

					callback(err, connection);
				})
			}
		}

		return pool;
	}
}

module.exports = { patchMysqlPool };
