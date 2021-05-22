const query = require("../../dao/connection").query


const getDocumentContent = async (documentId) => {
  const sql = `Select * from document Where id='${documentId}'`
  const res = await query(sql)
  return res
}


module.exports = {
  getDocumentContent
}