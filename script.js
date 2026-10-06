// ==========================================================
// NAMUDE KADDA - Frontend JavaScript
// Connecting the UI to the Node.js/Express Backend & MySQL
// ==========================================================

// Step 15: Base API URL configuration
// All backend requests will use this URL prefix
const API_URL = "http://localhost:5000/api";

// Current active user ID
// Defaulting to 1 (Demo User) for the prototype as requested.
// When a user logs in, this is dynamically updated.
let currentUserId = 1;
let currentUser = null;

// ================= DOM ELEMENT REFERENCES =================
const productGrid = document.getElementById("productGrid");
const storeGrid = document.getElementById("storeGrid");
const cartCountEl = document.getElementById("cartCount");
const toastEl = document.getElementById("toast");
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");
const productsHeading = document.getElementById("productsHeading");
const showAllProductsBtn = document.getElementById("showAllProductsBtn");

// Kadda AI elements
const aiInput = document.getElementById("aiInput");
const aiBtn = document.getElementById("aiBtn");
const aiResponse = document.getElementById("aiResponse");
const aiResultsGrid = document.getElementById("aiResultsGrid");

// Navigation & Mobile menu
const navLinks = document.getElementById("navLinks");
const hamburger = document.getElementById("hamburger");

// Cart Drawer elements
const cartToggleBtn = document.getElementById("cartToggleBtn");
const cartOverlay = document.getElementById("cartOverlay");
const closeCartBtn = document.getElementById("closeCartBtn");
const cartItemsContainer = document.getElementById("cartItemsContainer");
const cartTotalAmount = document.getElementById("cartTotalAmount");
const checkoutBtn = document.getElementById("checkoutBtn");

// Auth Modal elements
const signInBtn = document.getElementById("signInBtn");
const authOverlay = document.getElementById("authOverlay");
const closeAuthBtn = document.getElementById("closeAuthBtn");
const tabLogin = document.getElementById("tabLogin");
const tabRegister = document.getElementById("tabRegister");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

let toastTimer;

// ================= TOAST NOTIFICATION =================
// Displays a temporary floating message at the bottom of the screen
function showToast(message) {
  toastEl.textContent = message;
  toastEl.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2500);
}

// ================= STEP 5: FETCH AND DISPLAY PRODUCTS =================
// Fetches all products from the backend API: GET /api/products
async function loadProducts() {
  try {
    productGrid.innerHTML = `<p class="loading-state">Loading fresh products...</p>`;
    const response = await fetch(`${API_URL}/products`);

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    const products = await response.json();
    renderProducts(products);
    productsHeading.textContent = "Trending Near You 🔥";
    if (showAllProductsBtn) showAllProductsBtn.style.display = "none";
  } catch (error) {
    console.error("Error loading products:", error);
    productGrid.innerHTML = `
      <div class="empty-state">
        <p>⚠️ Unable to load products from server.</p>
        <small>Make sure the backend is running at http://localhost:5000</small>
      </div>
    `;
  }
}

// Dynamically creates HTML cards for products matching the original design
function renderProducts(products) {
  if (!products || products.length === 0) {
    productGrid.innerHTML = `
      <div class="empty-state">
        <p>No products found.</p>
        <button class="btn btn-primary" onclick="loadProducts()">View All Products</button>
      </div>
    `;
    return;
  }

  productGrid.innerHTML = products.map((product) => {
    // Calculate badge text (e.g. -27%)
    const badgeHtml = product.discount 
      ? `<span class="badge">${product.discount}</span>` 
      : "";

    // Strikethrough original price if available
    const originalPriceHtml = product.original_price 
      ? `<s>₹${Number(product.original_price).toLocaleString()}</s>` 
      : "";

    return `
      <article class="product-card">
        <div class="product-visual" style="--bg: ${product.bg_color || '#ede9fe'}">
          ${product.emoji || '🛍️'}
          ${badgeHtml}
        </div>
        <p class="seller">${escapeHtml(product.seller || 'Local Seller')}</p>
        <h3>${escapeHtml(product.name)}</h3>
        <p class="rating">★ ${product.rating || '4.5'} <small>(${product.review_count || 0})</small></p>
        <p class="price">₹${Number(product.price).toLocaleString()} ${originalPriceHtml}</p>
        <button class="btn btn-primary add-to-cart" data-id="${product.id}">Add to Cart</button>
      </article>
    `;
  }).join("");

  // Attach click listener to each Add to Cart button
  productGrid.querySelectorAll(".add-to-cart").forEach((button) => {
    button.addEventListener("click", () => {
      const productId = button.getAttribute("data-id");
      addToCart(productId);
    });
  });
}

// ================= STEP 6: SEARCH PRODUCTS =================
// Connects the search input to GET /api/products/search?q=SEARCH_TERM
async function runSearch(term) {
  const clean = term.trim();
  if (clean === "") {
    showToast("Please type something to search");
    return;
  }

  try {
    productGrid.innerHTML = `<p class="loading-state">Searching for "${clean}"...</p>`;
    const response = await fetch(`${API_URL}/products/search?q=${encodeURIComponent(clean)}`);

    if (!response.ok) {
      throw new Error("Search request failed");
    }

    const results = await response.json();
    productsHeading.textContent = `Search Results for "${clean}" (${results.length})`;
    if (showAllProductsBtn) showAllProductsBtn.style.display = "inline-block";
    renderProducts(results);

    // Scroll smoothly to products section to view results
    document.getElementById("deals").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    console.error("Search error:", error);
    showToast("Error searching products");
  }
}

// Search button and Enter key listeners
searchBtn.addEventListener("click", () => runSearch(searchInput.value));
searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") runSearch(searchInput.value);
});

// Popular search chips trigger real backend search
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    searchInput.value = chip.textContent;
    runSearch(chip.textContent);
  });
});

if (showAllProductsBtn) {
  showAllProductsBtn.addEventListener("click", () => {
    searchInput.value = "";
    loadProducts();
  });
}

// Header search icon focuses on search bar
const headerSearchBtn = document.getElementById("headerSearchBtn");
if (headerSearchBtn) {
  headerSearchBtn.addEventListener("click", () => {
    searchInput.focus();
    searchInput.scrollIntoView({ behavior: "smooth", block: "center" });
  });
}

// ================= STEP 7: CATEGORY FILTERING =================
// Fetches products by category: GET /api/products/category/:category
async function filterByCategory(categoryName) {
  try {
    productGrid.innerHTML = `<p class="loading-state">Loading ${categoryName} items...</p>`;
    const response = await fetch(`${API_URL}/products/category/${encodeURIComponent(categoryName)}`);

    if (!response.ok) {
      throw new Error("Category request failed");
    }

    const products = await response.json();
    productsHeading.textContent = `${categoryName} Products (${products.length})`;
    if (showAllProductsBtn) showAllProductsBtn.style.display = "inline-block";
    renderProducts(products);

    // Scroll smoothly to products
    document.getElementById("deals").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    console.error("Error filtering by category:", error);
    showToast("Error loading category products");
  }
}

// Attach click listeners to all category cards
document.querySelectorAll(".category-card").forEach((card) => {
  card.addEventListener("click", (e) => {
    e.preventDefault();
    const category = card.getAttribute("data-category");
    if (category) {
      filterByCategory(category);
    }
  });
});

// ================= STEP 8: CART FUNCTIONALITY =================
// Fetches the user's cart items from GET /api/cart/:user_id
async function fetchCart() {
  try {
    const response = await fetch(`${API_URL}/cart/${currentUserId}`);
    if (!response.ok) return;

    const cartItems = await response.json();

    // Calculate total quantity of items in cart
    const totalCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);
    cartCountEl.textContent = totalCount;

    // Render items inside the drawer
    renderCartDrawer(cartItems);
  } catch (error) {
    console.error("Error fetching cart count:", error);
  }
}

// Adds a product to cart via POST /api/cart
async function addToCart(productId) {
  try {
    const response = await fetch(`${API_URL}/cart`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: currentUserId,
        product_id: parseInt(productId, 10),
        quantity: 1
      })
    });

    if (!response.ok) {
      throw new Error("Failed to add product to cart");
    }

    // Refresh cart from backend
    await fetchCart();

    // Trigger cart bump animation
    cartCountEl.classList.remove("bump");
    void cartCountEl.offsetWidth;
    cartCountEl.classList.add("bump");

    showToast("Added to cart ✓");
  } catch (error) {
    console.error("Cart error:", error);
    showToast("Could not add to cart");
  }
}

// Removes a cart item via DELETE /api/cart/:id
async function removeCartItem(cartId) {
  try {
    const response = await fetch(`${API_URL}/cart/${cartId}`, {
      method: "DELETE"
    });

    if (!response.ok) {
      throw new Error("Failed to delete cart item");
    }

    await fetchCart();
    showToast("Item removed from cart");
  } catch (error) {
    console.error("Error removing cart item:", error);
    showToast("Could not remove item");
  }
}

// Renders the cart drawer list with items and total price
function renderCartDrawer(items) {
  if (!items || items.length === 0) {
    cartItemsContainer.innerHTML = `
      <div style="text-align: center; color: var(--muted); padding: 3rem 1rem;">
        <span style="font-size: 3rem; display: block; margin-bottom: 0.5rem;">🛒</span>
        <p>Your cart is empty.</p>
        <p style="font-size: 0.85rem; margin-top: 0.4rem;">Browse products and click "Add to Cart"!</p>
      </div>
    `;
    cartTotalAmount.textContent = "₹0.00";
    checkoutBtn.disabled = true;
    checkoutBtn.style.opacity = "0.5";
    return;
  }

  checkoutBtn.disabled = false;
  checkoutBtn.style.opacity = "1";

  let total = 0;
  cartItemsContainer.innerHTML = items.map((item) => {
    const itemTotal = parseFloat(item.price) * item.quantity;
    total += itemTotal;

    return `
      <div class="cart-item">
        <div class="cart-item-visual" style="background: ${item.bg_color || '#ede9fe'}">
          ${item.emoji || '🛍️'}
        </div>
        <div class="cart-item-info">
          <h4>${escapeHtml(item.name)}</h4>
          <p>Qty: ${item.quantity} × ₹${Number(item.price).toLocaleString()}</p>
          <div class="cart-item-price">₹${itemTotal.toLocaleString()}</div>
        </div>
        <button class="cart-item-remove" onclick="removeCartItem(${item.cart_id})" title="Remove item">🗑️</button>
      </div>
    `;
  }).join("");

  cartTotalAmount.textContent = `₹${total.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
}

// Open / Close Cart Drawer
cartToggleBtn.addEventListener("click", () => {
  fetchCart();
  cartOverlay.classList.add("open");
});
closeCartBtn.addEventListener("click", () => {
  cartOverlay.classList.remove("open");
});
cartOverlay.addEventListener("click", (e) => {
  if (e.target === cartOverlay) cartOverlay.classList.remove("open");
});

// ================= STEP 11: PLACE ORDER =================
// Converts cart items into an order via POST /api/orders
checkoutBtn.addEventListener("click", async () => {
  try {
    checkoutBtn.disabled = true;
    checkoutBtn.textContent = "Processing...";

    const response = await fetch(`${API_URL}/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: currentUserId })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Order placement failed");
    }

    // Refresh cart (which is now empty)
    await fetchCart();
    cartOverlay.classList.remove("open");

    showToast(`🎉 Order #${data.order.id} placed! Total: ₹${data.order.total_amount}`);
  } catch (error) {
    console.error("Order error:", error);
    showToast(error.message || "Failed to place order");
  } finally {
    checkoutBtn.disabled = false;
    checkoutBtn.textContent = "Place Order";
  }
});

// ================= STEP 9: LOCAL STORES =================
// Fetches stores from MySQL: GET /api/stores
async function loadStores() {
  try {
    storeGrid.innerHTML = `<p class="loading-state">Loading local stores...</p>`;
    const response = await fetch(`${API_URL}/stores`);

    if (!response.ok) {
      throw new Error("Failed to load stores");
    }

    const stores = await response.json();
    renderStores(stores);
  } catch (error) {
    console.error("Error loading stores:", error);
    storeGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; color: #ddd6fe; padding: 2rem;">
        <p>⚠️ Unable to load local stores.</p>
      </div>
    `;
  }
}

// Dynamically creates store cards matching the original dark-themed layout
function renderStores(stores) {
  if (!stores || stores.length === 0) {
    storeGrid.innerHTML = `<p style="color: #ddd6fe;">No local stores found.</p>`;
    return;
  }

  storeGrid.innerHTML = stores.map((store) => `
    <div class="store-card">
      <span>${store.emoji || '🏪'}</span>
      <h3>${escapeHtml(store.name)}</h3>
      <p>📍 ${escapeHtml(store.distance || store.location || 'Nearby')}</p>
      <p>⭐ ${store.rating || '4.8'}</p>
    </div>
  `).join("");
}

// ================= STEP 12: KADDA AI RECOMMENDATIONS =================
// Sends user query to the backend: POST /api/ai
async function askKadda() {
  const question = aiInput.value.trim();
  if (question === "") {
    aiResponse.textContent = "Tell Kadda what you need, e.g. a birthday gift under ₹1,000.";
    aiResultsGrid.style.display = "none";
    return;
  }

  aiResponse.textContent = "🤖 Kadda AI is analyzing products and budget...";
  aiBtn.disabled = true;

  try {
    const response = await fetch(`${API_URL}/ai`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "AI recommendation failed");
    }

    // Display conversational message
    aiResponse.textContent = data.message;

    // Display matching recommended products
    if (data.products && data.products.length > 0) {
      aiResultsGrid.style.display = "grid";
      aiResultsGrid.innerHTML = data.products.map((p) => `
        <div class="ai-card">
          <div class="ai-card-visual" style="background: ${p.bg_color || '#ede9fe'}">
            ${p.emoji || '🛍️'}
          </div>
          <h4>${escapeHtml(p.name)}</h4>
          <p>${escapeHtml(p.seller || p.category)}</p>
          <div class="ai-card-price">₹${Number(p.price).toLocaleString()}</div>
          <button class="btn btn-primary" onclick="addToCart(${p.id})">Add to Cart</button>
        </div>
      `).join("");
    } else {
      aiResultsGrid.style.display = "none";
    }
  } catch (error) {
    console.error("AI error:", error);
    aiResponse.textContent = "✨ Kadda AI: Could not fetch recommendations right now. Please try again.";
  } finally {
    aiBtn.disabled = false;
  }
}

aiBtn.addEventListener("click", askKadda);
aiInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") askKadda();
});

// ================= STEP 10: USER AUTHENTICATION =================
// Open / Close Auth modal
signInBtn.addEventListener("click", () => {
  if (currentUser) {
    // If already logged in, prompt to log out
    if (confirm(`Logged in as ${currentUser.name} (${currentUser.email}). Do you want to sign out?`)) {
      currentUser = null;
      currentUserId = 1;
      signInBtn.textContent = "Sign In";
      showToast("Signed out successfully");
      fetchCart();
    }
  } else {
    authOverlay.classList.add("open");
  }
});

closeAuthBtn.addEventListener("click", () => authOverlay.classList.remove("open"));
authOverlay.addEventListener("click", (e) => {
  if (e.target === authOverlay) authOverlay.classList.remove("open");
});

// Tab switching (Login vs Register)
tabLogin.addEventListener("click", () => {
  tabLogin.classList.add("active");
  tabRegister.classList.remove("active");
  loginForm.style.display = "block";
  registerForm.style.display = "none";
});

tabRegister.addEventListener("click", () => {
  tabRegister.classList.add("active");
  tabLogin.classList.remove("active");
  registerForm.style.display = "block";
  loginForm.style.display = "none";
});

// Handle Login: POST /api/users/login
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  try {
    const response = await fetch(`${API_URL}/users/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Login failed");
    }

    currentUser = data.user;
    currentUserId = data.user.id;
    signInBtn.textContent = `👤 ${data.user.name.split(" ")[0]}`;
    authOverlay.classList.remove("open");
    loginForm.reset();
    showToast(`Welcome back, ${data.user.name}!`);

    // Load logged-in user's cart
    fetchCart();
  } catch (error) {
    showToast(error.message || "Invalid credentials");
  }
});

// Handle Register: POST /api/users/register
registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("regName").value;
  const email = document.getElementById("regEmail").value;
  const password = document.getElementById("regPassword").value;

  try {
    const response = await fetch(`${API_URL}/users/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Registration failed");
    }

    currentUser = data.user;
    currentUserId = data.user.id;
    signInBtn.textContent = `👤 ${data.user.name.split(" ")[0]}`;
    authOverlay.classList.remove("open");
    registerForm.reset();
    showToast(`Account created! Welcome, ${data.user.name}!`);

    fetchCart();
  } catch (error) {
    showToast(error.message || "Registration failed");
  }
});

// ================= COUNTDOWN TIMER =================
// Deal ends 6 hours after page loads
const dealEnd = Date.now() + 6 * 60 * 60 * 1000;

function updateCountdown() {
  const remaining = Math.max(0, dealEnd - Date.now());
  const h = Math.floor(remaining / 3600000);
  const m = Math.floor((remaining % 3600000) / 60000);
  const s = Math.floor((remaining % 60000) / 1000);
  const pad = (n) => String(n).padStart(2, "0");
  const el = document.getElementById("countdown");
  if (el) el.textContent = `${pad(h)}:${pad(m)}:${pad(s)}`;
}
updateCountdown();
setInterval(updateCountdown, 1000);

// ================= MOBILE NAVIGATION =================
if (hamburger) {
  hamburger.addEventListener("click", () => {
    navLinks.classList.toggle("open");
  });
}
navLinks.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => navLinks.classList.remove("open"));
});

// ================= UTILITY HELPER =================
// Prevents XSS when rendering user-submitted or database text
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ================= INITIALIZE ON PAGE LOAD =================
window.addEventListener("DOMContentLoaded", () => {
  console.log("Namude Kadda frontend initialized. Calling backend APIs...");
  loadProducts();
  loadStores();
  fetchCart();
});
