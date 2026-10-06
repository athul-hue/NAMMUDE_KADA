// ==========================================================
// db.js - MySQL Database Connection Configuration
// ==========================================================

const mysql = require('mysql2/promise');
const dotenv = require('dotenv');

// Load environment variables from .env file
dotenv.config();

// Create a connection pool to MySQL
// Using a pool is better than a single connection because it reuses connections efficiently
const pool = mysql.createPool({
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT ? parseInt(process.env.DB_PORT) : 3306,
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'namude_kadda',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

// Function to test the database connection when the server boots
async function testConnection() {
    try {
        const connection = await pool.getConnection();
        console.log('✅ Connected to MySQL database:', process.env.DB_NAME || 'namude_kadda');
        connection.release(); // release connection back to pool
        return true;
    } catch (error) {
        console.error('❌ Database connection failed:', error.message);
        console.log('👉 Tip: Ensure your MySQL server is running and .env credentials are correct.');
        return false;
    }
}

// Export the pool and testConnection helper
module.exports = {
    pool,
    testConnection
};
