// ==========================================================
// server.js - Namude Kadda Main Express Server
// ==========================================================

const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { testConnection } = require('./db');

// Load environment variables (.env)
dotenv.config();

// Initialize express app
const app = express();
const PORT = process.env.PORT || 5000;

// ================= MIDDLEWARE =================
// 1. Enable CORS so frontend (running on live server / different port) can call APIs
app.use(cors());

// 2. Enable JSON request body parsing
app.use(express.json());

// 3. Optional: Request logger to help beginners see incoming API calls
app.use((req, res, next) => {
    console.log(`[${new Date().toLocaleTimeString()}] ${req.method} ${req.originalUrl}`);
    next();
});

// ================= TEST ROUTE =================
// Step 1: GET / - Returns confirmation message exactly as requested
app.get('/', (req, res) => {
    res.send('Namude Kadda Backend is running!');
});

// Serve frontend static assets (allows opening http://localhost:5000/frontend as an alternative to Live Server)
const path = require('path');
app.use('/frontend', express.static(path.join(__dirname, '../frontend')));

// ================= API ROUTES =================
// Connect each route file to its API endpoint prefix
app.use('/api/products', require('./routes/productRoutes'));
app.use('/api/cart', require('./routes/cartRoutes'));
app.use('/api/stores', require('./routes/storeRoutes'));
app.use('/api/users', require('./routes/userRoutes'));
app.use('/api/orders', require('./routes/orderRoutes'));
app.use('/api/ai', require('./routes/aiRoutes'));

// ================= 404 HANDLER =================
app.use((req, res) => {
    res.status(404).json({ error: 'API route not found' });
});

// ================= GLOBAL ERROR HANDLER =================
app.use((err, req, res, next) => {
    console.error('Unhandled Server Error:', err);
    res.status(500).json({ error: 'Internal server error occurred' });
});

// ================= START SERVER =================
app.listen(PORT, async () => {
    console.log(`===============================================`);
    console.log(`🚀 Namude Kadda Backend running on: http://localhost:${PORT}`);
    console.log(`👉 Test Route: http://localhost:${PORT}/`);
    console.log(`👉 Products API: http://localhost:${PORT}/api/products`);
    console.log(`👉 Stores API: http://localhost:${PORT}/api/stores`);
    console.log(`===============================================`);

    // Verify MySQL database connection
    await testConnection();
});
