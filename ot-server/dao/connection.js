var mysql = require('mysql');
var mysqlconfig = require('../config').mysqlConfig;

var pool = mysql.createPool(mysqlconfig);

var query = function (sql, options = {}, callback = () => {}) {
  return new Promise((resolve) => {
    pool.getConnection(function (err, conn) {
      if (err) {
        callback(err, null, null);
      } else {
        conn.query(sql, options, function (err, results, fields) {
          //事件驱动回调
          callback(err, results, fields);
          conn.release();
          resolve(results)
        });
        //释放连接，需要注意的是连接释放需要在此处释放，而不是在查询回调里面释放
      }
    });
  })

};

exports.query = query