-- ==========================================================
-- NAMUDE KADDA - MySQL Database Schema & Sample Data
-- ==========================================================

-- 1. Create the database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS namude_kadda;
USE namude_kadda;

-- 2. Create products table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    original_price DECIMAL(10, 2),
    category VARCHAR(100) NOT NULL,
    seller VARCHAR(255) NOT NULL,
    rating DECIMAL(2, 1) DEFAULT 4.5,
    review_count INT DEFAULT 0,
    discount VARCHAR(20),
    description TEXT,
    emoji VARCHAR(50) DEFAULT '🛍️',
    bg_color VARCHAR(50) DEFAULT '#ede9fe',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create stores table
CREATE TABLE IF NOT EXISTS stores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    location VARCHAR(255),
    distance VARCHAR(50),
    rating DECIMAL(2, 1) DEFAULT 4.8,
    emoji VARCHAR(50) DEFAULT '🏪',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Create cart table
CREATE TABLE IF NOT EXISTS cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ==========================================================
-- SEED SAMPLE DATA
-- ==========================================================

-- Insert sample products (matching existing frontend + more categories)
INSERT INTO products (name, price, original_price, category, seller, rating, review_count, discount, description, emoji, bg_color) VALUES
('Everyday Street Sneakers', 2199.00, 2999.00, 'Fashion', 'Sole Street, Indiranagar', 4.6, 312, '-27%', 'Comfortable and stylish street sneakers designed for daily walking and fashion.', '👟', '#ede9fe'),
('Pulse Wireless Earbuds', 1799.00, 2999.00, 'Electronics', 'Abhi Electronics', 4.7, 890, '-40%', 'Wireless earbuds with active noise cancellation, deep bass, and 30-hour battery life.', '🎧', '#ffedd5'),
('Active Smart Watch', 2499.00, 3599.00, 'Electronics', 'Abhi Electronics', 4.5, 455, '-31%', 'Fitness tracking smartwatch featuring heart rate sensor, sleep tracking, and water resistance.', '⌚', '#ecfccb'),
('Personalised Gift Box', 699.00, 875.00, 'Gifts', 'Giftly Crafts', 4.9, 128, '-20%', 'Custom curated gift hamper box ideal for birthdays, anniversaries, and celebrations.', '🎁', '#fce7f3'),
('Handcrafted Ceramic Mug', 399.00, 599.00, 'Home & Living', 'Giftly Crafts', 4.7, 85, '-33%', 'Minimalist ceramic coffee mug handmade with organic clay.', '☕', '#e0e7ff'),
('Fresh Sourdough Bread', 180.00, 220.00, 'Food', 'Sweet Home Bakery', 4.8, 210, '-18%', 'Crusty artisan sourdough loaf made daily with organic flour.', '🥐', '#fef3c7'),
('Organic Vegetable Basket', 450.00, 550.00, 'Food', 'Green Basket', 4.9, 340, '-18%', 'Fresh local seasonal vegetables harvested daily and delivered fast.', '🥬', '#dcfce7'),
('Natural Glow Face Serum', 849.00, 1199.00, 'Beauty', 'Aura Naturals', 4.6, 142, '-29%', 'Herbal brightening face serum enriched with Vitamin C and Aloe Vera.', '✨', '#fdf2f8')
ON DUPLICATE KEY UPDATE id=id;

-- Insert sample stores (matching existing frontend)
INSERT INTO stores (name, category, location, distance, rating, emoji) VALUES
('Sweet Home Bakery', 'Bakery & Confectionery', 'Kaloor', '1.2 km away', 4.8, '🥐'),
('Abhi Electronics', 'Electronics & Gadgets', 'MG Road', '2.3 km away', 4.7, '🔌'),
('Green Basket', 'Organic & Grocery', 'Panampilly Nagar', '0.8 km away', 4.9, '🥬'),
('Sole Street', 'Footwear & Streetwear', 'Indiranagar', '1.5 km away', 4.6, '👟'),
('Giftly Crafts', 'Handmade & Custom Gifts', 'Fort Kochi', '3.1 km away', 4.9, '🎁')
ON DUPLICATE KEY UPDATE id=id;

-- Insert a default demo user (Password: "password123" hashed using bcrypt)
INSERT INTO users (id, name, email, password) VALUES
(1, 'Demo Shopper', 'demo@namudekadda.com', '$2a$10$fVl63u6XQZ5L/B5yF261t.z35pU.eM5a6s0qYy2kPsp98V3pYkZzS')
ON DUPLICATE KEY UPDATE id=id;
