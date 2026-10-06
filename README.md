# 🛍️ NAMUDE KADDA - Full-Stack E-Commerce Web Application

> **Nammude Kadda. Nammude Shopping.**  
> A full-stack local e-commerce platform connecting shoppers with nearby sellers and stores.

---

## 📁 Project Directory Structure

```text
NAMUDE-KADDA/
│
├── frontend/
│   ├── index.html          # Main web page (semantic HTML5 structure)
│   ├── style.css           # Styling (Purple/Orange/Lime theme, responsive layout)
│   └── script.js           # Client-side logic & API communication (fetch)
│
└── backend/
    ├── server.js           # Main Express server & middleware setup
    ├── db.js               # MySQL connection pool configuration
    ├── schema.sql          # Database tables and initial seed data
    ├── package.json        # Dependencies (Express, MySQL2, CORS, Dotenv, Bcryptjs)
    ├── .env                # Database credentials & port configuration (ignored by git)
    ├── .env.example        # Template for environment configuration
    ├── .gitignore          # Ignores node_modules and .env
    │
    ├── routes/
    │   ├── productRoutes.js # /api/products endpoints
    │   ├── cartRoutes.js    # /api/cart endpoints
    │   ├── storeRoutes.js   # /api/stores endpoints
    │   ├── userRoutes.js    # /api/users endpoints
    │   ├── orderRoutes.js   # /api/orders endpoints
    │   └── aiRoutes.js      # /api/ai endpoints
    │
    └── controllers/
        ├── productController.js # Handles product queries, categories & search
        ├── cartController.js    # Handles cart additions, updates & deletions
        ├── storeController.js   # Handles local store listings
        ├── userController.js    # Handles user signup, login & bcrypt hashing
        ├── orderController.js   # Handles transactions, checkout & order history
        └── aiController.js       # Natural language shopping recommendation engine
```

---

## 🚀 How to Run the Application

### 1. Start the MySQL Database
Make sure your MySQL server is running on port `3306`.
If you haven't imported the database schema yet, run:
```bash
mysql -u root -p < backend/schema.sql
```
*(Enter your MySQL password when prompted).*

### 2. Configure Backend Credentials
Check `backend/.env` and update `DB_PASSWORD` to match your MySQL password if you have one:
```env
PORT=5000
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=namude_kadda
```

### 3. Start the Backend Server (Choose Either Node.js OR Python)

You have two interchangeable backend options! Both connect to the exact same MySQL database and serve the exact same frontend.

#### Option A: Node.js / Express
```bash
cd backend
npm install
npm start
```
*(Or double-click `start.bat` on Windows)*

#### Option B: Python / Flask
```bash
pip install flask flask-cors mysql-connector-python python-dotenv
python app.py
```
*(Or double-click `start-python.bat` on Windows)*

Either backend will start on: **`http://localhost:5000`**

### 4. Open the Frontend
You can run the frontend in either of two easy ways:
- **Option A (VS Code Live Server):** Right-click `frontend/index.html` in VS Code and select **"Open with Live Server"**.
- **Option B (Direct Backend URL):** Open your browser and navigate to:  
  **`http://localhost:5000/frontend/index.html`**

