const { Pool } = require("pg");

const pool = new Pool({
    host: "localhost",
    port: 5432,
    database: "nivora",
    user: "postgres",
    password:"rossni0987654321"
});

module.exports = pool;