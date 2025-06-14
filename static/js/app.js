// import { Chart } from "@/components/ui/chart"
// Global variables
let currentUser = null
let authToken = null
let clothingItems = []
let orders = []

// API Base URL
const API_BASE = "/api"

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
  initializeApp()
})

function initializeApp() {
  // Check if user is already logged in
  const token = localStorage.getItem("authToken")
  if (token) {
    authToken = token
    loadUserInfo()
  } else {
    showLogin()
  }

  // Setup event listeners
  setupEventListeners()
}

function setupEventListeners() {
  // Login form
  document.getElementById("loginFormElement").addEventListener("submit", handleLogin)

  // Logout button
  document.getElementById("logoutBtn").addEventListener("click", handleLogout)

  // Navigation
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", handleNavigation)
  })

  // Modal close buttons
  document.querySelectorAll(".close").forEach((closeBtn) => {
    closeBtn.addEventListener("click", function () {
      const modal = this.closest(".modal")
      closeModal(modal.id)
    })
  })

  // Clothing management
  document.getElementById("addClothingBtn").addEventListener("click", () => openClothingModal())
  document.getElementById("clothingForm").addEventListener("submit", handleClothingSubmit)

  // Order management
  document.getElementById("addOrderBtn").addEventListener("click", () => openOrderModal())
  document.getElementById("orderForm").addEventListener("submit", handleOrderSubmit)
  document.getElementById("addOrderItemBtn").addEventListener("click", addOrderItemForm)

  // Sales
  document.getElementById("processSaleForm").addEventListener("submit", handleSaleProcessing)

  // Reports
  document.getElementById("generateReportBtn").addEventListener("click", generateMonthlyReport)

  // User management
  document.getElementById("addUserBtn").addEventListener("click", () => openModal("userModal"))
  document.getElementById("userForm").addEventListener("submit", handleUserSubmit)
}

// Authentication functions
async function handleLogin(e) {
  e.preventDefault()

  const username = document.getElementById("username").value
  const password = document.getElementById("password").value
  const errorDiv = document.getElementById("loginError")

  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    })

    if (response.ok) {
      const data = await response.json()
      authToken = data.access_token
      localStorage.setItem("authToken", authToken)
      await loadUserInfo()
      showDashboard()
      errorDiv.style.display = "none"
    } else {
      const error = await response.json()
      errorDiv.textContent = error.detail || "Login failed"
      errorDiv.style.display = "block"
    }
  } catch (error) {
    errorDiv.textContent = "Network error. Please try again."
    errorDiv.style.display = "block"
  }
}

async function loadUserInfo() {
  try {
    const response = await apiCall("/users/me")
    currentUser = response
    document.getElementById("currentUser").textContent =
      `${currentUser.username} (${getRoleDisplayName(currentUser.role)})`

    // Show/hide admin features
    if (currentUser.role === "admin") {
      document.getElementById("usersNavItem").style.display = "block"
    }

    return true
  } catch (error) {
    console.error("Failed to load user info:", error)
    handleLogout()
    return false
  }
}

function handleLogout() {
  authToken = null
  currentUser = null
  localStorage.removeItem("authToken")
  showLogin()
}

function showLogin() {
  document.getElementById("loginForm").style.display = "flex"
  document.getElementById("dashboard").style.display = "none"
}

function showDashboard() {
  document.getElementById("loginForm").style.display = "none"
  document.getElementById("dashboard").style.display = "grid"
  loadDashboardData()
}

// Navigation
function handleNavigation(e) {
  e.preventDefault()
  const section = e.target.getAttribute("data-section")

  // Update active nav link
  document.querySelectorAll(".nav-link").forEach((link) => link.classList.remove("active"))
  e.target.classList.add("active")

  // Show corresponding section
  document.querySelectorAll(".content-section").forEach((section) => section.classList.remove("active"))
  document.getElementById(`${section}Section`).classList.add("active")

  // Load section data
  loadSectionData(section)
}

async function loadSectionData(section) {
  switch (section) {
    case "overview":
      await loadOverviewData()
      break
    case "clothing":
      await loadClothing()
      break
    case "orders":
      await loadOrders()
      break
    case "sales":
      await loadSalesData()
      break
    case "reports":
      await loadReportsData()
      break
    case "users":
      if (currentUser.role === "admin") {
        await loadUsers()
      }
      break
  }
}

async function loadDashboardData() {
  await loadOverviewData()
}

// Overview functions
async function loadOverviewData() {
  try {
    const [stats, lowStockAlerts] = await Promise.all([
      apiCall("/reports/dashboard-stats"),
      apiCall("/clothing/low-stock/alerts"),
    ])

    // Update stats
    document.getElementById("todaySales").textContent = stats.today_sales
    document.getElementById("lowStockCount").textContent = stats.low_stock_count
    document.getElementById("totalClothing").textContent = stats.total_clothing
    document.getElementById("recentSales").textContent = stats.recent_sales

    // Update alerts
    displayLowStockAlerts(lowStockAlerts)
  } catch (error) {
    console.error("Failed to load overview data:", error)
  }
}

function displayLowStockAlerts(alertsData) {
  const container = document.getElementById("lowStockAlerts")

  if (alertsData.count === 0) {
    container.innerHTML =
      '<div class="alert-item alert-info"><i class="fas fa-check-circle"></i> Barcha kiyimlar yetarli miqdorda mavjud</div>'
    return
  }

  container.innerHTML = alertsData.items
    .map(
      (item) => `
            <div class="alert-item alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>${item.name}</strong> - Qolgan: ${item.quantity} dona (Minimum: ${item.minimum_quantity} dona)
            </div>
        `,
    )
    .join("")
}

// Clothing functions
async function loadClothing() {
  try {
    clothingItems = await apiCall("/clothing/")
    displayClothing()
  } catch (error) {
    console.error("Failed to load clothing:", error)
  }
}

function displayClothing() {
  const tbody = document.querySelector("#clothingTable tbody")
  tbody.innerHTML = clothingItems
    .map(
      (item) => `
            <tr>
                <td>${item.name}</td>
                <td>${item.type}</td>
                <td>${item.size}</td>
                <td>${item.color}</td>
                <td>${item.quantity}</td>
                <td>$${item.price}</td>
                <td>${item.supplier || "-"}</td>
                <td>
                    <span class="status-badge ${getStockStatus(item)}">
                        ${getStockStatusText(item)}
                    </span>
                </td>
                <td>
                    ${
                      canManageClothing()
                        ? `
                            <button class="btn btn-warning btn-sm" onclick="editClothing(${item.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="deleteClothing(${item.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        `
                        : ""
                    }
                </td>
            </tr>
        `,
    )
    .join("")
}

function getStockStatus(item) {
  if (item.quantity <= item.minimum_quantity) {
    return "status-low"
  }
  return "status-normal"
}

function getStockStatusText(item) {
  if (item.quantity <= item.minimum_quantity) {
    return "Kam"
  }
  return "Normal"
}

function openClothingModal(clothingId = null) {
  const modal = document.getElementById("clothingModal")
  const title = document.getElementById("clothingModalTitle")
  const form = document.getElementById("clothingForm")

  if (clothingId) {
    const item = clothingItems.find((c) => c.id === clothingId)
    title.textContent = "Kiyimni tahrirlash"
    document.getElementById("clothingName").value = item.name
    document.getElementById("clothingType").value = item.type
    document.getElementById("clothingSize").value = item.size
    document.getElementById("clothingColor").value = item.color
    document.getElementById("clothingQuantity").value = item.quantity
    document.getElementById("clothingPrice").value = item.price
    document.getElementById("clothingCostPrice").value = item.cost_price
    document.getElementById("clothingMinimum").value = item.minimum_quantity
    document.getElementById("clothingSupplier").value = item.supplier || ""
    document.getElementById("clothingDeliveryDate").value = item.delivery_date || ""
    form.dataset.clothingId = clothingId
  } else {
    title.textContent = "Kiyim qo'shish"
    form.reset()
    delete form.dataset.clothingId
  }

  openModal("clothingModal")
}

async function handleClothingSubmit(e) {
  e.preventDefault()

  const form = e.target
  const clothingId = form.dataset.clothingId
  const isEdit = !!clothingId

  const clothingData = {
    name: document.getElementById("clothingName").value,
    type: document.getElementById("clothingType").value,
    size: document.getElementById("clothingSize").value,
    color: document.getElementById("clothingColor").value,
    quantity: Number.parseInt(document.getElementById("clothingQuantity").value),
    unit: "dona",
    price: Number.parseFloat(document.getElementById("clothingPrice").value),
    cost_price: Number.parseFloat(document.getElementById("clothingCostPrice").value),
    minimum_quantity: Number.parseInt(document.getElementById("clothingMinimum").value),
    supplier: document.getElementById("clothingSupplier").value || null,
    delivery_date: document.getElementById("clothingDeliveryDate").value || null,
  }

  try {
    if (isEdit) {
      await apiCall(`/clothing/${clothingId}`, "PUT", clothingData)
    } else {
      await apiCall("/clothing/", "POST", clothingData)
    }

    closeModal("clothingModal")
    await loadClothing()
    showSuccessMessage("Kiyim muvaffaqiyatli saqlandi")
  } catch (error) {
    showErrorMessage("Kiyimni saqlashda xatolik yuz berdi")
  }
}

function editClothing(clothingId) {
  openClothingModal(clothingId)
}

async function deleteClothing(clothingId) {
  if (!confirm("Kiyimni o'chirishni tasdiqlaysizmi?")) {
    return
  }

  try {
    await apiCall(`/clothing/${clothingId}`, "DELETE")
    await loadClothing()
    showSuccessMessage("Kiyim muvaffaqiyatli o'chirildi")
  } catch (error) {
    showErrorMessage("Kiyimni o'chirishda xatolik yuz berdi")
  }
}

// Orders functions
async function loadOrders() {
  try {
    orders = await apiCall("/orders/")
    displayOrders()
    updateOrderSelect()
  } catch (error) {
    console.error("Failed to load orders:", error)
  }
}

function displayOrders() {
  const container = document.getElementById("ordersGrid")
  container.innerHTML = orders
    .map(
      (order) => `
            <div class="order-card">
                <h3>${order.name}</h3>
                <p><strong>Mijoz:</strong> ${order.customer_name}</p>
                <p><strong>Telefon:</strong> ${order.customer_phone}</p>
                <p><strong>Status:</strong> ${getOrderStatusText(order.status)}</p>
                <p><strong>Jami summa:</strong> $${order.total_amount}</p>
                
                <div class="order-items">
                    <h4>Buyurtma elementlari:</h4>
                    ${order.items
                      .map(
                        (item) => `
                            <div class="order-item">
                                <span>${item.clothing_name}</span>
                                <span>${item.quantity} x $${item.price}</span>
                            </div>
                        `,
                      )
                      .join("")}
                </div>
                
                <div class="order-actions">
                    ${
                      canManageOrders()
                        ? `
                            <button class="btn btn-warning btn-sm" onclick="editOrder(${order.id})">
                                <i class="fas fa-edit"></i> Tahrirlash
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="deleteOrder(${order.id})">
                                <i class="fas fa-trash"></i> O'chirish
                            </button>
                        `
                        : ""
                    }
                </div>
            </div>
        `,
    )
    .join("")
}

function getOrderStatusText(status) {
  const statusMap = {
    pending: "Kutilmoqda",
    completed: "Bajarildi",
    cancelled: "Bekor qilindi",
  }
  return statusMap[status] || status
}

function updateOrderSelect() {
  const select = document.getElementById("orderSelect")
  select.innerHTML =
    '<option value="">Buyurtma tanlang...</option>' +
    orders
      .filter((order) => order.status === "pending")
      .map(
        (order) => `
                <option value="${order.id}">${order.name} - $${order.total_amount}</option>
            `,
      )
      .join("")
}

// Sales functions
async function loadSalesData() {
  try {
    await loadOrders() // Ensure orders are loaded for the select
    const todaySales = await apiCall("/sales/today")
    displayTodaySales(todaySales)
  } catch (error) {
    console.error("Failed to load sales data:", error)
  }
}

function displayTodaySales(sales) {
  const container = document.getElementById("todaySalesList")

  if (sales.length === 0) {
    container.innerHTML = "<p>Bugun hech qanday sotuv amalga oshirilmagan</p>"
    return
  }

  container.innerHTML = sales
    .map(
      (sale) => `
            <div class="sale-item">
                <div class="sale-info">
                    <h4>${sale.order_name}</h4>
                    <p>${sale.items_sold} element - $${sale.total_amount}</p>
                    <p><strong>To'lov usuli:</strong> ${sale.payment_method}</p>
                    <p><strong>Sotuvchi:</strong> ${sale.username}</p>
                    ${sale.notes ? `<p><em>${sale.notes}</em></p>` : ""}
                </div>
                <div class="sale-meta">
                    ${formatDateTime(sale.sold_at)}
                </div>
            </div>
        `,
    )
    .join("")
}

async function handleSaleProcessing(e) {
  e.preventDefault()

  const orderId = Number.parseInt(document.getElementById("orderSelect").value)
  const paymentMethod = document.getElementById("paymentMethod").value
  const notes = document.getElementById("saleNotes").value

  if (!orderId) {
    showErrorMessage("Buyurtmani tanlang")
    return
  }

  const selectedOrder = orders.find((o) => o.id === orderId)
  if (!selectedOrder) {
    showErrorMessage("Buyurtma topilmadi")
    return
  }

  try {
    await apiCall("/sales/", "POST", {
      order_id: orderId,
      items_sold: selectedOrder.items.reduce((sum, item) => sum + item.quantity, 0),
      total_amount: selectedOrder.total_amount,
      payment_method: paymentMethod,
      notes: notes || null,
    })

    document.getElementById("processSaleForm").reset()
    await loadSalesData()
    await loadOrders() // Refresh orders list
    showSuccessMessage("Sotuv muvaffaqiyatli amalga oshirildi")
  } catch (error) {
    showErrorMessage(error.detail || "Sotuvda xatolik yuz berdi")
  }
}

// Reports functions
async function loadReportsData() {
  try {
    const [reports, salesAnalytics] = await Promise.all([
      apiCall("/reports/monthly"),
      apiCall("/reports/sales-analytics"),
    ])

    displayMonthlyReports(reports)
    displaySalesChart(salesAnalytics)
  } catch (error) {
    console.error("Failed to load reports data:", error)
  }
}

function displayMonthlyReports(reports) {
  const tbody = document.querySelector("#reportsTable tbody")
  tbody.innerHTML = reports
    .map(
      (report) => `
            <tr>
                <td>${report.month}/${report.year}</td>
                <td>${report.total_items_sold}</td>
                <td>$${report.total_revenue.toFixed(2)}</td>
                <td>$${report.total_profit.toFixed(2)}</td>
                <td>${report.profit_margin.toFixed(1)}%</td>
                <td>
                    <span class="status-badge ${report.is_suspicious ? "status-suspicious" : "status-good"}">
                        ${report.is_suspicious ? "Shubhali" : "Normal"}
                    </span>
                </td>
            </tr>
        `,
    )
    .join("")
}

function displaySalesChart(salesData) {
  const ctx = document.getElementById("salesChart").getContext("2d")

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: salesData.map((item) => item.type),
      datasets: [
        {
          label: "Sotilgan miqdor",
          data: salesData.map((item) => item.sold),
          backgroundColor: "rgba(102, 126, 234, 0.8)",
          borderColor: "rgba(102, 126, 234, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  })
}

async function generateMonthlyReport() {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1

  try {
    await apiCall(`/reports/generate-monthly/${year}/${month}`, "POST")
    await loadReportsData()
    showSuccessMessage("Oylik hisobot yaratildi")
  } catch (error) {
    showErrorMessage("Hisobot yaratishda xatolik yuz berdi")
  }
}

// Users functions
async function loadUsers() {
  try {
    const users = await apiCall("/users/")
    displayUsers(users)
  } catch (error) {
    console.error("Failed to load users:", error)
  }
}

function displayUsers(users) {
  const tbody = document.querySelector("#usersTable tbody")
  tbody.innerHTML = users
    .map(
      (user) => `
            <tr>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>${getRoleDisplayName(user.role)}</td>
                <td>
                    <span class="status-badge ${user.is_active ? "status-active" : "status-inactive"}">
                        ${user.is_active ? "Faol" : "Nofaol"}
                    </span>
                </td>
                <td>${formatDateTime(user.created_at)}</td>
                <td>
                    <button class="btn btn-warning btn-sm" onclick="toggleUserActive(${user.id})">
                        <i class="fas fa-toggle-${user.is_active ? "on" : "off"}"></i>
                    </button>
                </td>
            </tr>
        `,
    )
    .join("")
}

async function handleUserSubmit(e) {
  e.preventDefault()

  const userData = {
    username: document.getElementById("newUsername").value,
    email: document.getElementById("newUserEmail").value,
    password: document.getElementById("newUserPassword").value,
    role: document.getElementById("newUserRole").value,
  }

  try {
    await apiCall("/users/", "POST", userData)
    closeModal("userModal")
    await loadUsers()
    showSuccessMessage("Foydalanuvchi muvaffaqiyatli yaratildi")
  } catch (error) {
    showErrorMessage("Foydalanuvchi yaratishda xatolik yuz berdi")
  }
}

async function toggleUserActive(userId) {
  try {
    await apiCall(`/users/${userId}/toggle-active`, "PUT")
    await loadUsers()
    showSuccessMessage("Foydalanuvchi holati o'zgartirildi")
  } catch (error) {
    showErrorMessage("Foydalanuvchi holatini o'zgartirishda xatolik yuz berdi")
  }
}

// Utility functions
async function apiCall(endpoint, method = "GET", data = null) {
  const config = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  }

  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`
  }

  if (data) {
    config.body = JSON.stringify(data)
  }

  const response = await fetch(`${API_BASE}${endpoint}`, config)

  if (response.status === 401) {
    handleLogout()
    throw new Error("Unauthorized")
  }

  if (!response.ok) {
    const error = await response.json()
    throw error
  }

  return await response.json()
}

function openModal(modalId) {
  document.getElementById(modalId).style.display = "block"
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none"
}

function showSuccessMessage(message) {
  alert(message)
}

function showErrorMessage(message) {
  alert(message)
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("uz-UZ")
}

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString("uz-UZ")
}

function getRoleDisplayName(role) {
  const roleNames = {
    admin: "Administrator",
    manager: "Menejer",
    seller: "Sotuvchi",
  }
  return roleNames[role] || role
}

function canManageClothing() {
  return currentUser && ["admin", "manager"].includes(currentUser.role)
}

function canManageOrders() {
  return currentUser && ["admin", "manager", "seller"].includes(currentUser.role)
}

// Close modals when clicking outside
window.onclick = (event) => {
  if (event.target.classList.contains("modal")) {
    event.target.style.display = "none"
  }
}

// Order functions
async function openOrderModal(orderId = null) {
  const modal = document.getElementById("orderModal")
  const title = document.getElementById("orderModalTitle")
  const form = document.getElementById("orderForm")
  const orderItemsContainer = document.getElementById("orderItemsContainer")

  if (orderId) {
    const order = orders.find((o) => o.id === orderId)
    title.textContent = "Buyurtmani tahrirlash"
    document.getElementById("orderName").value = order.name
    document.getElementById("customerName").value = order.customer_name
    document.getElementById("customerPhone").value = order.customer_phone
    document.getElementById("orderStatus").value = order.status
    form.dataset.orderId = orderId

    // Display order items
    orderItemsContainer.innerHTML = order.items
      .map(
        (item, index) => `
                <div class="order-item-form">
                    <label>Kiyim:</label>
                    <input type="text" value="${item.clothing_name}" disabled>
                    <label>Miqdor:</label>
                    <input type="number" value="${item.quantity}" class="orderItemQuantity">
                    <label>Narx:</label>
                    <input type="number" value="${item.price}" class="orderItemPrice">
                    <button type="button" class="btn btn-danger btn-sm" onclick="removeOrderItemForm(this)">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `,
      )
      .join("")
  } else {
    title.textContent = "Buyurtma qo'shish"
    form.reset()
    delete form.dataset.orderId
    orderItemsContainer.innerHTML = "" // Clear existing items
    addOrderItemForm() // Add at least one item form
  }

  openModal("orderModal")
}

async function handleOrderSubmit(e) {
  e.preventDefault()

  const form = e.target
  const orderId = form.dataset.orderId
  const isEdit = !!orderId

  const orderData = {
    name: document.getElementById("orderName").value,
    customer_name: document.getElementById("customerName").value,
    customer_phone: document.getElementById("customerPhone").value,
    status: document.getElementById("orderStatus").value,
    items: Array.from(document.querySelectorAll(".order-item-form")).map((itemForm) => {
      return {
        clothing_name: itemForm.querySelector('input[type="text"]').value,
        quantity: Number.parseInt(itemForm.querySelector(".orderItemQuantity").value),
        price: Number.parseFloat(itemForm.querySelector(".orderItemPrice").value),
      }
    }),
  }

  try {
    if (isEdit) {
      await apiCall(`/orders/${orderId}`, "PUT", orderData)
    } else {
      await apiCall("/orders/", "POST", orderData)
    }

    closeModal("orderModal")
    await loadOrders()
    showSuccessMessage("Buyurtma muvaffaqiyatli saqlandi")
  } catch (error) {
    showErrorMessage("Buyurtmani saqlashda xatolik yuz berdi")
  }
}

function editOrder(orderId) {
  openOrderModal(orderId)
}

async function deleteOrder(orderId) {
  if (!confirm("Buyurtmani o'chirishni tasdiqlaysizmi?")) {
    return
  }

  try {
    await apiCall(`/orders/${orderId}`, "DELETE")
    await loadOrders()
    showSuccessMessage("Buyurtma muvaffaqiyatli o'chirildi")
  } catch (error) {
    showErrorMessage("Buyurtmani o'chirishda xatolik yuz berdi")
  }
}

function addOrderItemForm() {
  const container = document.getElementById("orderItemsContainer")
  const newItemForm = document.createElement("div")
  newItemForm.classList.add("order-item-form")

  newItemForm.innerHTML = `
        <label>Kiyim:</label>
        <input type="text" placeholder="Kiyim nomini kiriting">
        <label>Miqdor:</label>
        <input type="number" class="orderItemQuantity" value="1">
        <label>Narx:</label>
        <input type="number" class="orderItemPrice" value="0">
        <button type="button" class="btn btn-danger btn-sm" onclick="removeOrderItemForm(this)">
            <i class="fas fa-trash"></i>
        </button>
    `

  container.appendChild(newItemForm)
}

function removeOrderItemForm(btn) {
  btn.closest(".order-item-form").remove()
}
