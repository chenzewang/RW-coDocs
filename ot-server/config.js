const mysqlConfig = (() => {
  const config = {
    dev: {
      host: '127.0.0.1',
      user: 'root',
      password: '123456',
      database: 'doc',
      port: 3306
    },
    production: {
      host: '127.0.0.1',
      user: 'root',
      password: '123456',
      database: 'doc',
      port: 3306
    }
  }
  return config[process.env.NODE_ENV]
})()


exports.mysqlConfig = mysqlConfig