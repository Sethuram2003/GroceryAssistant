// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let categories = [];
let products = [];
let currentEditingCategoryId = null;
let currentEditingProductId = null;

// ============= Initialization =============
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    checkDatabaseConnection();
    loadDashboard();
});

// ============= Event Listeners =============
function initializeEventListeners() {
    // Navigation tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', switchTab);
    });

    // Category modal buttons
    document.getElementById('addCategoryBtn').addEventListener('click', openCategoryModal);
    document.getElementById('categoryModalClose').addEventListener('click', closeCategoryModal);
    document.querySelector('#categoryModal .modal-close').addEventListener('click', closeCategoryModal);
    document.getElementById('categoryForm').addEventListener('submit', handleCategorySubmit);
    document.getElementById('categoryModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('categoryModal')) {
            closeCategoryModal();
        }
    });

    // Product modal buttons
    document.getElementById('addProductBtn').addEventListener('click', openProductModal);
    document.getElementById('productModalClose').addEventListener('click', closeProductModal);
    document.querySelector('#productModal .modal-close').addEventListener('click', closeProductModal);
    document.getElementById('productForm').addEventListener('submit', handleProductSubmit);
    document.getElementById('productModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('productModal')) {
            closeProductModal();
        }
    });

    // Filters
    document.getElementById('searchProducts').addEventListener('input', filterProducts);
    document.getElementById('filterCategory').addEventListener('change', filterProducts);
    document.getElementById('filterStatus').addEventListener('change', filterProducts);
}

// ============= Connection Check =============
async function checkDatabaseConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health/`);
        if (response.ok) {
            updateConnectionStatus(true);
        }
    } catch (error) {
        console.warn('Database connection check failed:', error);
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected) {
    const indicator = document.getElementById('statusIndicator');
    const dot = indicator.querySelector('.status-dot');
    const text = indicator.querySelector('.status-text');

    if (connected) {
        dot.classList.add('connected');
        dot.classList.remove('disconnected');
        text.textContent = 'Connected';
    } else {
        dot.classList.add('disconnected');
        dot.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

// ============= Navigation & Tabs =============
function switchTab(e) {
    const tabName = e.target.dataset.tab;

    // Update active tab
    document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
    e.target.classList.add('active');

    // Update active content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');

    // Load content
    if (tabName === 'dashboard') {
        loadDashboard();
    } else if (tabName === 'categories') {
        loadCategories();
    } else if (tabName === 'products') {
        loadProducts();
    }
}

// ============= Dashboard =============
async function loadDashboard() {
    try {
        const [categoriesRes, productsRes] = await Promise.all([
            fetch(`${API_BASE_URL}/categories/`),
            fetch(`${API_BASE_URL}/products/`)
        ]);

        categories = categoriesRes.ok ? await categoriesRes.json() : [];
        products = productsRes.ok ? await productsRes.json() : [];

        // Update stats
        document.getElementById('totalCategories').textContent = categories.length;
        document.getElementById('totalProducts').textContent = products.length;

        const activeProducts = products.filter(p => p.is_active === 1).length;
        document.getElementById('activeProducts').textContent = activeProducts;

        const totalStockValue = products.reduce((sum, p) => {
            return sum + (p.stock_quantity * p.selling_price);
        }, 0);
        document.getElementById('totalStockValue').textContent = `$${totalStockValue.toFixed(2)}`;

        // Display recent products
        displayRecentProducts();
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Error loading dashboard', 'error');
    }
}

function displayRecentProducts() {
    const container = document.getElementById('recentProductsContainer');
    const recent = products.slice(0, 5);

    if (recent.length === 0) {
        container.innerHTML = '<p class="empty-state">No products yet. Create your first product!</p>';
        return;
    }

    container.innerHTML = recent.map(product => {
        const category = categories.find(c => c.id === product.category_id);
        return `
            <div class="product-row">
                <div>
                    <div class="product-name">${product.name}</div>
                    <div class="product-category">${category?.name || 'Unknown'}</div>
                </div>
                <div class="product-price">$${product.selling_price.toFixed(2)}</div>
                <div class="product-stock">${product.stock_quantity} ${product.unit}</div>
                <div>
                    <span class="product-status ${product.is_active ? 'active' : 'inactive'}">
                        ${product.is_active ? 'Active' : 'Inactive'}
                    </span>
                </div>
            </div>
        `;
    }).join('');
}

// ============= Categories Management =============
async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE_URL}/categories/`);
        if (!response.ok) {
            if (response.status === 503) {
                showToast('Database service is unavailable', 'error');
            }
            return;
        }

        categories = await response.json();
        displayCategories();
        updateCategoryFilter();
    } catch (error) {
        console.error('Error loading categories:', error);
        showToast('Error loading categories', 'error');
    }
}

function displayCategories() {
    const container = document.getElementById('categoriesContainer');

    if (categories.length === 0) {
        container.innerHTML = '<p class="empty-state">No categories yet. Create your first category!</p>';
        return;
    }

    container.innerHTML = categories.map(category => {
        const categoryProducts = products.filter(p => p.category_id === category.id);
        return `
            <div class="category-card">
                <h3>📁 ${category.name}</h3>
                <p>${category.description || 'No description'}</p>
                <div class="category-stats">
                    <div class="category-stat">
                        <div class="category-stat-value">${categoryProducts.length}</div>
                        <div class="category-stat-label">Products</div>
                    </div>
                </div>
                <div class="category-actions">
                    <button class="btn-edit" onclick="editCategory(${category.id})">Edit</button>
                    <button class="btn-delete" onclick="deleteCategory(${category.id})">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

function openCategoryModal() {
    currentEditingCategoryId = null;
    document.getElementById('categoryId').value = '';
    document.getElementById('categoryForm').reset();
    document.getElementById('categoryModalTitle').textContent = 'Add Category';
    document.getElementById('categoryModal').classList.add('active');
}

function closeCategoryModal() {
    document.getElementById('categoryModal').classList.remove('active');
    document.getElementById('categoryForm').reset();
}

function editCategory(id) {
    const category = categories.find(c => c.id === id);
    if (!category) return;

    currentEditingCategoryId = id;
    document.getElementById('categoryId').value = id;
    document.getElementById('categoryName').value = category.name;
    document.getElementById('categoryDescription').value = category.description || '';
    document.getElementById('categoryModalTitle').textContent = 'Edit Category';
    document.getElementById('categoryModal').classList.add('active');
}

async function handleCategorySubmit(e) {
    e.preventDefault();

    const id = document.getElementById('categoryId').value;
    const name = document.getElementById('categoryName').value;
    const description = document.getElementById('categoryDescription').value;

    try {
        let response;
        if (id) {
            response = await fetch(`${API_BASE_URL}/categories/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            });
        } else {
            response = await fetch(`${API_BASE_URL}/categories/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            });
        }

        if (response.status === 503) {
            showToast('Database service is unavailable', 'error');
            return;
        }

        if (!response.ok) {
            const error = await response.json();
            showToast(error.detail || 'Error saving category', 'error');
            return;
        }

        showToast(id ? 'Category updated successfully!' : 'Category created successfully!', 'success');
        closeCategoryModal();
        loadCategories();
    } catch (error) {
        console.error('Error saving category:', error);
        showToast('Error saving category', 'error');
    }
}

async function deleteCategory(id) {
    if (!confirm('Are you sure you want to delete this category?')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/categories/${id}`, {
            method: 'DELETE'
        });

        if (response.status === 503) {
            showToast('Database service is unavailable', 'error');
            return;
        }

        if (!response.ok) {
            const error = await response.json();
            showToast(error.detail || 'Error deleting category', 'error');
            return;
        }

        showToast('Category deleted successfully!', 'success');
        loadCategories();
    } catch (error) {
        console.error('Error deleting category:', error);
        showToast('Error deleting category', 'error');
    }
}

function updateCategoryFilter() {
    const select = document.getElementById('filterCategory');
    const select2 = document.getElementById('productCategory');

    select.innerHTML = '<option value="">All Categories</option>';
    select2.innerHTML = '';

    categories.forEach(category => {
        select.innerHTML += `<option value="${category.id}">${category.name}</option>`;
        select2.innerHTML += `<option value="${category.id}">${category.name}</option>`;
    });
}

// ============= Products Management =============
async function loadProducts() {
    try {
        const response = await fetch(`${API_BASE_URL}/products/`);
        if (!response.ok) {
            if (response.status === 503) {
                showToast('Database service is unavailable', 'error');
            }
            return;
        }

        products = await response.json();
        displayProducts(products);
        updateCategoryFilter();
    } catch (error) {
        console.error('Error loading products:', error);
        showToast('Error loading products', 'error');
    }
}

function displayProducts(productsToDisplay) {
    const container = document.getElementById('productsContainer');

    if (productsToDisplay.length === 0) {
        container.innerHTML = '<p class="empty-state">No products found. Create your first product!</p>';
        return;
    }

    container.innerHTML = productsToDisplay.map(product => {
        const category = categories.find(c => c.id === product.category_id);
        return `
            <div class="product-row ${product.is_active ? '' : 'inactive'}">
                <div>
                    <div class="product-name">${product.name}</div>
                    <div class="product-category">${category?.name || 'Unknown'}</div>
                </div>
                <div class="product-price">$${product.selling_price.toFixed(2)}</div>
                <div class="product-stock">${product.stock_quantity} ${product.unit}</div>
                <div>
                    <span class="product-status ${product.is_active ? 'active' : 'inactive'}">
                        ${product.is_active ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <div class="product-actions">
                    <button class="btn-edit" onclick="editProduct(${product.id})">Edit</button>
                    <button class="btn-delete" onclick="deleteProduct(${product.id})">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

function filterProducts() {
    const searchTerm = document.getElementById('searchProducts').value.toLowerCase();
    const categoryFilter = document.getElementById('filterCategory').value;
    const statusFilter = document.getElementById('filterStatus').value;

    let filtered = products.filter(product => {
        const matchesSearch = product.name.toLowerCase().includes(searchTerm);
        const matchesCategory = !categoryFilter || product.category_id === parseInt(categoryFilter);
        const matchesStatus = !statusFilter || product.is_active === parseInt(statusFilter);

        return matchesSearch && matchesCategory && matchesStatus;
    });

    displayProducts(filtered);
}

function openProductModal() {
    currentEditingProductId = null;
    document.getElementById('productId').value = '';
    document.getElementById('productForm').reset();
    document.getElementById('productModalTitle').textContent = 'Add Product';
    updateCategoryFilter();
    document.getElementById('productModal').classList.add('active');
}

function closeProductModal() {
    document.getElementById('productModal').classList.remove('active');
    document.getElementById('productForm').reset();
}

function editProduct(id) {
    const product = products.find(p => p.id === id);
    if (!product) return;

    currentEditingProductId = id;
    document.getElementById('productId').value = id;
    document.getElementById('productName').value = product.name;
    document.getElementById('productCategory').value = product.category_id;
    document.getElementById('productUnit').value = product.unit;
    document.getElementById('productPrice').value = product.selling_price;
    document.getElementById('productStock').value = product.stock_quantity;
    document.getElementById('productActive').value = product.is_active;
    document.getElementById('productDescription').value = product.description || '';
    document.getElementById('productModalTitle').textContent = 'Edit Product';
    updateCategoryFilter();
    document.getElementById('productModal').classList.add('active');
}

async function handleProductSubmit(e) {
    e.preventDefault();

    const id = document.getElementById('productId').value;
    const name = document.getElementById('productName').value;
    const categoryId = parseInt(document.getElementById('productCategory').value);
    const unit = document.getElementById('productUnit').value;
    const price = parseFloat(document.getElementById('productPrice').value);
    const stock = parseFloat(document.getElementById('productStock').value);
    const isActive = parseInt(document.getElementById('productActive').value);
    const description = document.getElementById('productDescription').value;

    try {
        let response;
        const body = { name, category_id: categoryId, unit, selling_price: price, stock_quantity: stock, is_active: isActive, description };

        if (id) {
            response = await fetch(`${API_BASE_URL}/products/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
        } else {
            response = await fetch(`${API_BASE_URL}/products/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
        }

        if (response.status === 503) {
            showToast('Database service is unavailable', 'error');
            return;
        }

        if (!response.ok) {
            const error = await response.json();
            showToast(error.detail || 'Error saving product', 'error');
            return;
        }

        showToast(id ? 'Product updated successfully!' : 'Product created successfully!', 'success');
        closeProductModal();
        loadProducts();
        loadDashboard();
    } catch (error) {
        console.error('Error saving product:', error);
        showToast('Error saving product', 'error');
    }
}

async function deleteProduct(id) {
    if (!confirm('Are you sure you want to delete this product?')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/products/${id}`, {
            method: 'DELETE'
        });

        if (response.status === 503) {
            showToast('Database service is unavailable', 'error');
            return;
        }

        if (!response.ok) {
            const error = await response.json();
            showToast(error.detail || 'Error deleting product', 'error');
            return;
        }

        showToast('Product deleted successfully!', 'success');
        loadProducts();
        loadDashboard();
    } catch (error) {
        console.error('Error deleting product:', error);
        showToast('Error deleting product', 'error');
    }
}

// ============= Toast Notifications =============
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
