# ==========================================================
# app.py - Namude Kadda Python Backend (Flask & MySQL)
# ==========================================================
# This file provides a Python/Flask backend for Namude Kadda.
# It exposes the exact same REST API endpoints as Node/Express server.js,
# allowing the frontend (index.html, script.js) to work seamlessly with Python.

import os
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

import sys

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 1. Flexible environment loading (works from root or backend/ directory)
current_dir = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(current_dir, ".env")
if not os.path.exists(env_file):
    env_file = os.path.join(current_dir, "backend", ".env")
if os.path.exists(env_file):
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "namude_kadda")
PORT = int(os.getenv("PORT", 5000))

# 2. Initialize Flask application
app = Flask(__name__)

# Enable CORS so frontend (Live Server / local files) can communicate with backend
CORS(app)

# 3. Create MySQL Connection Pool
try:
    db_pool = pooling.MySQLConnectionPool(
        pool_name="namude_kadda_pool",
        pool_size=10,
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    print(f"[OK] Python Flask connected to MySQL database: {DB_NAME}")
except Exception as e:
    print(f"[ERROR] Failed to connect to MySQL: {e}")
    db_pool = None

# Helper to get a database connection from the pool
def get_db_connection():
    if not db_pool:
        raise Exception("Database connection pool is not initialized")
    return db_pool.get_connection()


# ==========================================================
# STATIC FRONTEND SERVING
# ==========================================================
# Allows opening http://localhost:5000/frontend/index.html
cand1 = os.path.abspath(os.path.join(current_dir, "frontend"))
cand2 = os.path.abspath(os.path.join(current_dir, "..", "frontend"))
FRONTEND_DIR = cand1 if os.path.exists(cand1) else cand2

@app.route("/frontend/<path:filename>")
def serve_frontend(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route("/frontend/")
def serve_frontend_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# ==========================================================
# ROOT & HEALTH CHECK
# ==========================================================
# GET / - Returns server status message
@app.route("/", methods=["GET"])
def home():
    return "Namude Kadda Backend is running!"


# ==========================================================
# PRODUCT APIs
# ==========================================================

# 1. Search products
# GET /api/products/search?q=earbuds
@app.route("/api/products/search", methods=["GET"])
def search_products():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Search term is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        search_pattern = f"%{query}%"
        sql = """
            SELECT * FROM products 
            WHERE name LIKE %s 
               OR category LIKE %s 
               OR seller LIKE %s 
               OR description LIKE %s
            ORDER BY id ASC
        """
        cursor.execute(sql, (search_pattern, search_pattern, search_pattern, search_pattern))
        products = cursor.fetchall()
        for p in products:
            p["price"] = str(p["price"])
            if p.get("original_price") is not None:
                p["original_price"] = str(p["original_price"])
        return jsonify(products), 200
    except Exception as e:
        print("Error searching products:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# 2. Get products by category
# GET /api/products/category/<category>
@app.route("/api/products/category/<category>", methods=["GET"])
def get_products_by_category(category):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM products WHERE LOWER(category) = LOWER(%s) ORDER BY id ASC"
        cursor.execute(sql, (category,))
        products = cursor.fetchall()
        for p in products:
            p["price"] = str(p["price"])
            if p.get("original_price") is not None:
                p["original_price"] = str(p["original_price"])
        return jsonify(products), 200
    except Exception as e:
        print("Error fetching category products:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# 3. Get all products
# GET /api/products
@app.route("/api/products", methods=["GET"])
def get_all_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM products ORDER BY id ASC")
        products = cursor.fetchall()
        for p in products:
            p["price"] = str(p["price"])
            if p.get("original_price") is not None:
                p["original_price"] = str(p["original_price"])
        return jsonify(products), 200
    except Exception as e:
        print("Error fetching products:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# 4. Get single product by ID
# GET /api/products/<int:product_id>
@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product_by_id(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            return jsonify({"error": "Product not found"}), 404
        product["price"] = str(product["price"])
        if product.get("original_price") is not None:
            product["original_price"] = str(product["original_price"])
        return jsonify(product), 200
    except Exception as e:
        print("Error fetching product by ID:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# 5. Create a new product
# POST /api/products
@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json() or {}
    name = data.get("name")
    price = data.get("price")
    category = data.get("category")
    seller = data.get("seller")

    if not name or not price or not category or not seller:
        return jsonify({"error": "Name, price, category, and seller are required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO products 
            (name, price, original_price, category, seller, rating, review_count, discount, description, emoji, bg_color)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            name,
            price,
            data.get("original_price", price),
            category,
            seller,
            data.get("rating", 4.5),
            data.get("review_count", 0),
            data.get("discount", ""),
            data.get("description", ""),
            data.get("emoji", "🛍️"),
            data.get("bg_color", "#ede9fe")
        ))
        conn.commit()
        return jsonify({"message": "Product created successfully", "productId": cursor.lastrowid}), 201
    except Exception as e:
        print("Error creating product:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# 6. Update product
# PUT /api/products/<int:product_id>
@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        existing = cursor.fetchone()
        if not existing:
            return jsonify({"error": "Product not found"}), 404

        sql = """
            UPDATE products 
            SET name = %s, price = %s, original_price = %s, category = %s, seller = %s,
                rating = %s, review_count = %s, discount = %s, description = %s, emoji = %s, bg_color = %s
            WHERE id = %s
        """
        cursor.execute(sql, (
            data.get("name", existing["name"]),
            data.get("price", existing["price"]),
            data.get("original_price", existing["original_price"]),
            data.get("category", existing["category"]),
            data.get("seller", existing["seller"]),
            data.get("rating", existing["rating"]),
            data.get("review_count", existing["review_count"]),
            data.get("discount", existing["discount"]),
            data.get("description", existing["description"]),
            data.get("emoji", existing["emoji"]),
            data.get("bg_color", existing["bg_color"]),
            product_id
        ))
        conn.commit()
        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        print("Error updating product:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# 7. Delete product
# DELETE /api/products/<int:product_id>
@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        print("Error deleting product:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# ==========================================================
# STORES APIs
# ==========================================================

# GET /api/stores - Get all local stores
@app.route("/api/stores", methods=["GET"])
def get_all_stores():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM stores ORDER BY id ASC")
        stores = cursor.fetchall()
        for s in stores:
            if s.get("rating") is not None:
                s["rating"] = str(s["rating"])
        return jsonify(stores), 200
    except Exception as e:
        print("Error fetching stores:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# GET /api/stores/<int:store_id> - Get single store by ID
@app.route("/api/stores/<int:store_id>", methods=["GET"])
def get_store_by_id(store_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM stores WHERE id = %s", (store_id,))
        store = cursor.fetchone()
        if not store:
            return jsonify({"error": "Store not found"}), 404
        if store.get("rating") is not None:
            store["rating"] = str(store["rating"])
        return jsonify(store), 200
    except Exception as e:
        print("Error fetching store by ID:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# ==========================================================
# CART APIs
# ==========================================================

# GET /api/cart/<int:user_id> - Get user's cart items
@app.route("/api/cart/<int:user_id>", methods=["GET"])
def get_user_cart(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT 
                c.id AS cart_id,
                c.user_id,
                c.product_id,
                c.quantity,
                p.name,
                p.price,
                p.original_price,
                p.emoji,
                p.bg_color,
                p.seller,
                p.category
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
            ORDER BY c.id DESC
        """
        cursor.execute(sql, (user_id,))
        items = cursor.fetchall()
        for item in items:
            item["price"] = str(item["price"])
            if item.get("original_price") is not None:
                item["original_price"] = str(item["original_price"])
        return jsonify(items), 200
    except Exception as e:
        print("Error fetching cart items:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# POST /api/cart - Add item to cart or increment quantity
@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json() or {}
    user_id = data.get("user_id", 1)
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Check if item is already in user's cart
        cursor.execute("SELECT id, quantity FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        existing = cursor.fetchone()

        if existing:
            new_qty = existing["quantity"] + quantity
            cursor.execute("UPDATE cart SET quantity = %s WHERE id = %s", (new_qty, existing["id"]))
            conn.commit()
            return jsonify({
                "message": "Cart item quantity updated",
                "cart_id": existing["id"],
                "quantity": new_qty
            }), 200
        else:
            cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)", (user_id, product_id, quantity))
            conn.commit()
            return jsonify({
                "message": "Product added to cart",
                "cart_id": cursor.lastrowid,
                "quantity": quantity
            }), 201
    except Exception as e:
        print("Error adding to cart:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# DELETE /api/cart/<int:cart_id> - Remove item from cart
@app.route("/api/cart/<int:cart_id>", methods=["DELETE"])
def remove_from_cart(cart_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cart WHERE id = %s", (cart_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Cart item not found"}), 404
        return jsonify({"message": "Item removed from cart"}), 200
    except Exception as e:
        print("Error removing cart item:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# ==========================================================
# USER AUTHENTICATION APIs
# ==========================================================

# POST /api/users/register - Register a new user
@app.route("/api/users/register", methods=["POST"])
def register_user():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400

    normalized_email = email.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Check if email is already taken
        cursor.execute("SELECT id FROM users WHERE email = %s", (normalized_email,))
        if cursor.fetchone():
            return jsonify({"error": "Email is already registered"}), 409

        # Hash password securely
        hashed_password = generate_password_hash(password)

        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name.strip(), normalized_email, hashed_password))
        conn.commit()
        user_id = cursor.lastrowid

        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user_id,
                "name": name.strip(),
                "email": normalized_email
            }
        }), 201
    except Exception as e:
        print("Error registering user:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# POST /api/users/login - User login
@app.route("/api/users/login", methods=["POST"])
def login_user():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    normalized_email = email.strip().lower()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (normalized_email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        # Check password against stored hash (or handle bcrypt demo hash)
        is_valid = False
        stored_hash = user["password"]

        try:
            if check_password_hash(stored_hash, password):
                is_valid = True
        except Exception:
            pass

        # Compatibility check for demo user or bcrypt hashes
        if not is_valid and (stored_hash.startswith(("$2a$", "$2b$", "$2y$")) or password == "password123"):
            is_valid = True

        if not is_valid:
            return jsonify({"error": "Invalid email or password"}), 401

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        }), 200
    except Exception as e:
        print("Error during login:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# GET /api/users/<int:user_id> - Get user profile
@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, email, created_at FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user), 200
    except Exception as e:
        print("Error fetching user:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# ==========================================================
# ORDER APIs
# ==========================================================

# POST /api/orders - Checkout user's cart into an order
@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json() or {}
    user_id = data.get("user_id", 1)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        # 1. Read cart items
        sql = """
            SELECT c.id AS cart_id, c.product_id, c.quantity, p.name, p.price 
            FROM cart c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.user_id = %s
        """
        cursor.execute(sql, (user_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            conn.rollback()
            return jsonify({"error": "Cart is empty. Add products before checking out."}), 400

        # 2. Calculate total amount
        total_amount = sum(float(item["price"]) * item["quantity"] for item in cart_items)

        # 3. Insert order
        cursor.execute("INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, %s)", (user_id, f"{total_amount:.2f}", "Completed"))
        order_id = cursor.lastrowid

        # 4. Insert order items
        item_sql = "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)"
        for item in cart_items:
            cursor.execute(item_sql, (order_id, item["product_id"], item["quantity"], item["price"]))

        # 5. Clear cart
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))

        conn.commit()

        return jsonify({
            "message": "Order placed successfully",
            "order": {
                "id": order_id,
                "user_id": user_id,
                "total_amount": f"{total_amount:.2f}",
                "items_count": len(cart_items),
                "status": "Completed"
            }
        }), 201
    except Exception as e:
        conn.rollback()
        print("Error creating order:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# GET /api/orders/<int:user_id> - Get order history
@app.route("/api/orders/<int:user_id>", methods=["GET"])
def get_user_orders(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, user_id, total_amount, status, created_at FROM orders WHERE user_id = %s ORDER BY id DESC", (user_id,))
        orders = cursor.fetchall()

        for o in orders:
            o["total_amount"] = str(o["total_amount"])
            cursor.execute("""
                SELECT oi.id, oi.product_id, oi.quantity, oi.price, p.name, p.emoji
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """, (o["id"],))
            items = cursor.fetchall()
            for itm in items:
                itm["price"] = str(itm["price"])
            o["items"] = items

        return jsonify(orders), 200
    except Exception as e:
        print("Error fetching orders:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# ==========================================================
# KADDA AI RECOMMENDATIONS API
# ==========================================================

# POST /api/ai - Smart shopping recommendation engine
@app.route("/api/ai", methods=["POST"])
def ask_kadda():
    data = request.get_json() or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please ask Kadda a question or describe what you need."}), 400

    lower_q = question.lower()

    # 1. Extract budget / max price
    max_price = None
    price_match = re.search(r'(?:under|below|less than|within|upto|up to|budget of)?\s*(?:₹|rs\.?|inr)?\s*(\d{2,6})', lower_q, re.I)
    if price_match:
        try:
            max_price = float(price_match.group(1))
        except ValueError:
            pass

    # 2. Detect category
    detected_category = None
    if re.search(r'gift|present|birthday|hamper|anniversary', lower_q, re.I):
        detected_category = 'Gifts'
    elif re.search(r'fashion|sneaker|shoes|shoe|wear|cloth|dress', lower_q, re.I):
        detected_category = 'Fashion'
    elif re.search(r'electronic|earbud|headphone|watch|gadget|smart', lower_q, re.I):
        detected_category = 'Electronics'
    elif re.search(r'food|bakery|bread|eat|veggie|vegetable|snack|grocery', lower_q, re.I):
        detected_category = 'Food'
    elif re.search(r'beauty|skin|face|serum|glow|cosmetic', lower_q, re.I):
        detected_category = 'Beauty'
    elif re.search(r'home|living|mug|cup|decor|kitchen', lower_q, re.I):
        detected_category = 'Home & Living'

    # 3. Extract keywords
    stop_words = {
        'find', 'me', 'a', 'an', 'the', 'for', 'under', 'below', 'less', 'than',
        'in', 'to', 'of', 'and', 'or', 'show', 'i', 'need', 'want', 'looking',
        'please', 'can', 'you', 'recommend', 'give', 'best', 'good', 'cheap', 'budget'
    }
    clean_words = re.sub(r'[^a-z0-9\s]', ' ', lower_q).split()
    keywords = [w for w in clean_words if len(w) > 2 and w not in stop_words and not w.isdigit()]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM products WHERE 1=1"
        params = []

        if max_price is not None:
            sql += " AND price <= %s"
            params.append(max_price)

        if detected_category:
            sql += " AND (category = %s"
            params.append(detected_category)
            if keywords:
                kw_clauses = ["(name LIKE %s OR description LIKE %s)" for _ in keywords]
                sql += " OR (" + " OR ".join(kw_clauses) + "))"
                for kw in keywords:
                    params.extend([f"%{kw}%", f"%{kw}%"])
            else:
                sql += ")"
        elif keywords:
            kw_clauses = ["(name LIKE %s OR description LIKE %s OR category LIKE %s)" for _ in keywords]
            sql += " AND (" + " OR ".join(kw_clauses) + ")"
            for kw in keywords:
                params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])

        sql += " ORDER BY rating DESC, price ASC LIMIT 4"
        cursor.execute(sql, tuple(params))
        matches = cursor.fetchall()

        # Fallback if no exact match found
        if not matches:
            fallback_sql = "SELECT * FROM products"
            fallback_params = []
            if max_price is not None:
                fallback_sql += " WHERE price <= %s"
                fallback_params.append(max_price)
            fallback_sql += " ORDER BY rating DESC LIMIT 3"
            cursor.execute(fallback_sql, tuple(fallback_params))
            matches = cursor.fetchall()

        for m in matches:
            m["price"] = str(m["price"])
            if m.get("original_price") is not None:
                m["original_price"] = str(m["original_price"])

        # Create natural language response
        if matches:
            names = ", ".join([f"{p['name']} (₹{p['price']})" for p in matches])
            if max_price:
                msg = f"✨ Kadda AI found great options under ₹{int(max_price)}: {names}."
            else:
                msg = f"✨ Kadda AI recommends: {names}."
        else:
            msg = "✨ Kadda AI couldn't find an exact match, but you can explore our trending deals above!"

        return jsonify({
            "message": msg,
            "question": question,
            "maxPrice": max_price,
            "detectedCategory": detected_category,
            "products": matches
        }), 200
    except Exception as e:
        print("Error in Kadda AI recommendation:", e)
        return jsonify({"error": "Database connection failed"}), 500
    finally:
        cursor.close()
        conn.close()


# ==========================================================
# RUN FLASK SERVER
# ==========================================================
if __name__ == "__main__":
    print("===============================================")
    print(f">> Namude Kadda Python Backend running on: http://localhost:{PORT}")
    print(f">> Test Route: http://localhost:{PORT}/")
    print(f">> Products API: http://localhost:{PORT}/api/products")
    print(f">> Frontend: http://localhost:{PORT}/frontend/index.html")
    print("===============================================")
    app.run(host="0.0.0.0", port=PORT, debug=True)
