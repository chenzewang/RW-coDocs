const fetch = require('node-fetch')
const query = require('../../dao/connection').query
const host = 'http://localhost:5000'

const getUserInfo = async (id) => {
  const sql = `Select * from user Where id='${id}'`
  const res = await query(sql)
  return res
}
module.exports = {
  getUserInfo
}