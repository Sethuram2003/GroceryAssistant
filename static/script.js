// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State
let categories = [];
let products = [];
let currentEditingCategoryId = null;
let currentEditingProductId = null;
let selectedCsvFile = null;

// ============= Initialization =============
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Page loaded, starting initialization...');
    initializeEventListeners();
    console.log('📊 Checking database connection...');
    checkDatabaseConnection();
    console.log('📈 Loading dashboard...');
    loadDashboard();
    console.log('✅ Initialization complete!');
});

// ============= Event Listeners =============
function initializeEventListeners() {
    console.log('🔧 Initializing event listeners...');
    
    // Navigation tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', switchTab);
    });
    console.log('✓ Tab navigation listeners attached');

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

    // Category products modal buttons
    const categoryProductsModalClose = document.getElementById('categoryProductsModalClose');
    if (categoryProductsModalClose) {
        categoryProductsModalClose.addEventListener('click', () => {
            document.getElementById('categoryProductsModal').classList.remove('active');
        });
    }
    const categoryProductsModal = document.getElementById('categoryProductsModal');
    if (categoryProductsModal) {
        categoryProductsModal.addEventListener('click', (e) => {
            if (e.target === categoryProductsModal) {
                categoryProductsModal.classList.remove('active');
            }
        });
    }

    // Product filters
    document.getElementById('searchProducts').addEventListener('input', filterProducts);
    document.getElementById('filterCategory').addEventListener('change', filterProducts);
    document.getElementById('filterStatus').addEventListener('change', filterProducts);

    // Chat
    document.getElementById('sendChatBtn').addEventListener('click', sendChatMessage);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
    console.log('✓ Chat listeners attached');
    
    // Import CSV Tab
    initializeImportTab();
    console.log('✓ Import tab listeners attached');
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
            <div class="category-card" onclick="viewCategoryProducts(${category.id})" style="cursor: pointer;">
                <div class="category-card-content">
                    <h3>📁 ${category.name}</h3>
                    <p>${category.description || 'No description'}</p>
                    <div class="category-stats">
                        <div class="category-stat">
                            <div class="category-stat-value">${categoryProducts.length}</div>
                            <div class="category-stat-label">Products</div>
                        </div>
                    </div>
                    <p class="click-hint">� Click to view products</p>
                </div>
                <div class="category-actions">
                    <button class="btn-edit" onclick="editCategory(${category.id}); event.stopPropagation();">Edit</button>
                    <button class="btn-delete" onclick="deleteCategory(${category.id}); event.stopPropagation();">Delete</button>
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

function viewCategoryProducts(categoryId) {
    const category = categories.find(c => c.id === categoryId);
    if (!category) return;

    // First, load all products to ensure they're available
    async function loadAndFilter() {
        try {
            // Fetch products fresh from the server
            const response = await fetch(`${API_BASE_URL}/products/`);
            if (!response.ok) {
                showToast('Error loading products', 'error');
                return;
            }
            
            products = await response.json();
            
            // Switch to the products tab
            const productsTab = document.querySelector('[data-tab="products"]');
            if (productsTab) {
                document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
                productsTab.classList.add('active');
                
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                document.getElementById('products').classList.add('active');
            }
            
            // Set the filter to the selected category
            document.getElementById('filterCategory').value = categoryId;
            
            // Reset search and status filters
            document.getElementById('searchProducts').value = '';
            document.getElementById('filterStatus').value = '';
            
            // Apply the filter
            filterProducts();
            
            // Scroll to products container
            const productsContainer = document.getElementById('productsContainer');
            if (productsContainer) {
                setTimeout(() => {
                    productsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            }
            
            // Show a toast notification
            showToast(`Filtered by category: ${category.name}`, 'success');
        } catch (error) {
            console.error('Error loading and filtering products:', error);
            showToast('Error loading products', 'error');
        }
    }
    
    loadAndFilter();
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

// ============= Chat Functionality =============
async function sendChatMessage() {
    try {
        const chatInput = document.getElementById('chatInput');
        if (!chatInput) {
            console.error('chatInput element not found!');
            return;
        }
        
        const message = chatInput.value.trim();
        console.log('Message to send:', message);
        
        if (!message) {
            console.warn('Empty message, ignoring');
            return;
        }

        // Add user message to chat
        addChatMessage(message, 'user');
        chatInput.value = '';
        chatInput.focus();

        // Show loading indicator
        addChatMessage('Thinking...', 'assistant-loading');

        // Send message to backend
        const url = `${API_BASE_URL}/chat/?message=${encodeURIComponent(message)}`;
        console.log('🚀 Sending chat request to:', url);
        console.log('📍 API Base URL:', API_BASE_URL);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        console.log('📨 Response received - Status:', response.status, 'OK:', response.ok);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Chat error response:', errorText);
            removeLastMessage();
            addChatMessage(`Error: Server responded with status ${response.status}. Please try again.`, 'assistant');
            return;
        }

        const data = await response.json();
        console.log('✅ Chat response data:', data);
        
        // Remove loading message and add assistant response
        removeLastMessage();
        const responseText = data.response || data.message || 'I couldn\'t generate a response.';
        addChatMessage(responseText, 'assistant');

    } catch (error) {
        console.error('❌ Error in sendChatMessage:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack,
            name: error.name
        });
        removeLastMessage();
        addChatMessage(`Error: ${error.message}. Make sure the backend is running at ${API_BASE_URL}`, 'assistant');
    }
}

function addChatMessage(text, sender = 'user') {
    try {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) {
            console.error('chatMessages element not found!');
            return;
        }
        
        console.log(`📝 Adding ${sender} message:`, text.substring(0, 50) + '...');
        
        // Create message container
        const messageContainer = document.createElement('div');
        messageContainer.className = `message-container ${sender === 'user' ? 'user-message-container' : 'assistant-message-container'}`;
        
        // Create avatar
        const avatar = document.createElement('div');
        avatar.className = `message-avatar ${sender === 'user' ? 'user-avatar' : 'bot-avatar'}`;
        avatar.textContent = sender === 'user' ? '👤' : '🤖';
        
        // Create bubble wrapper
        const bubbleWrapper = document.createElement('div');
        bubbleWrapper.className = 'message-bubble-wrapper';
        
        // Create bubble
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${sender === 'user' ? 'user-bubble' : 'bot-bubble'}`;
        
        if (sender === 'assistant-loading') {
            bubble.innerHTML = '<span class="chat-loading">Thinking<span></span></span>';
        } else if (sender === 'assistant') {
            // Parse markdown for bot messages
            try {
                // Configure marked options
                marked.setOptions({
                    breaks: true,
                    gfm: true,
                    headerIds: false,
                    mangle: false,
                });
                
                const htmlContent = marked.parse(text);
                bubble.innerHTML = `<div class="markdown-content">${htmlContent}</div>`;
            } catch (e) {
                console.error('Markdown parsing error:', e);
                const p = document.createElement('p');
                p.textContent = text;
                bubble.appendChild(p);
            }
        } else {
            // Plain text for user messages
            const p = document.createElement('p');
            p.textContent = text;
            bubble.appendChild(p);
        }
        
        // Add timestamp
        const timestamp = document.createElement('span');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = 'now';
        
        bubbleWrapper.appendChild(bubble);
        bubbleWrapper.appendChild(timestamp);
        messageContainer.appendChild(avatar);
        messageContainer.appendChild(bubbleWrapper);
        chatMessages.appendChild(messageContainer);
        
        console.log('✓ Message added to DOM');

        // Auto-scroll to bottom
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
            console.log('↙️ Auto-scrolled to bottom');
        }, 0);
    } catch (error) {
        console.error('❌ Error in addChatMessage:', error);
    }
}

function removeLastMessage() {
    const chatMessages = document.getElementById('chatMessages');
    const lastMessage = chatMessages.lastElementChild;
    if (lastMessage) {
        lastMessage.remove();
    }
}

// ============= CSV Import Functionality =============
function initializeImportTab() {
    console.log('🔧 Initializing Import Tab listeners...');
    
    // File upload area
    const uploadArea = document.getElementById('uploadArea');
    const csvFileInput = document.getElementById('csvFileInput');
    const browseFileBtn = document.getElementById('browseFileBtn');
    const validateCsvBtn = document.getElementById('validateCsvBtn');
    
    if (!uploadArea || !csvFileInput || !browseFileBtn) {
        console.warn('⚠️ Import tab elements not found');
        return;
    }
    
    // Browse button click
    browseFileBtn.addEventListener('click', () => {
        csvFileInput.click();
    });
    
    // File input change
    csvFileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });
    
    // Upload area drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });
    
    // Click on upload area
    uploadArea.addEventListener('click', () => {
        csvFileInput.click();
    });
    
    // Validate button
    if (validateCsvBtn) {
        validateCsvBtn.addEventListener('click', validateCsv);
    }
    
    // Import button
    const importCsvBtn = document.getElementById('importCsvBtn');
    if (importCsvBtn) {
        importCsvBtn.addEventListener('click', importCsv);
    }
    
    // Import another button
    const importAnotherBtn = document.getElementById('importAnotherBtn');
    if (importAnotherBtn) {
        importAnotherBtn.addEventListener('click', resetImportTab);
    }
    
    // View dashboard button
    const viewDashboardBtn = document.getElementById('viewDashboardBtn');
    if (viewDashboardBtn) {
        viewDashboardBtn.addEventListener('click', () => {
            switchTab({ target: document.querySelector('[data-tab="dashboard"]') });
        });
    }
    
    // Download template button
    const downloadTemplateBtn = document.getElementById('downloadTemplateBtn');
    if (downloadTemplateBtn) {
        downloadTemplateBtn.addEventListener('click', downloadCsvTemplate);
    }
    
    console.log('✓ Import Tab listeners attached');
}

function handleFileSelect(file) {
    if (!file) return;
    
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
        showToast('Please select a valid CSV file', 'error');
        return;
    }
    
    selectedCsvFile = file;
    const uploadArea = document.getElementById('uploadArea');
    const validateCsvBtn = document.getElementById('validateCsvBtn');
    
    // Update UI to show file selected
    uploadArea.innerHTML = `
        <div class="upload-icon">✅</div>
        <h3>File Selected!</h3>
        <p>${file.name}</p>
        <p style="color: var(--gray-600); font-size: 0.85em;">Ready to validate</p>
    `;
    
    // Enable validate button
    if (validateCsvBtn) {
        validateCsvBtn.disabled = false;
        // Re-attach click listener in case it was lost
        validateCsvBtn.onclick = validateCsv;
    }
    
    console.log('📁 File selected:', file.name);
}

async function validateCsv() {
    console.log('Starting validation, selectedCsvFile:', selectedCsvFile);
    
    if (!selectedCsvFile) {
        showToast('Please select a CSV file first', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('file', selectedCsvFile);
        
        console.log('🔍 Validating CSV...');
        const url = `${API_BASE_URL}/api/import-csv/validate`;
        console.log('Request URL:', url);
        
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        console.log('Validation response status:', response.status);
        
        if (!response.ok) {
            const error = await response.json();
            console.error('Validation error:', error);
            showToast(error.detail || 'Validation failed', 'error');
            return;
        }
        
        const data = await response.json();
        console.log('✅ Validation result:', data);
        
        displayValidationResults(data);
        
    } catch (error) {
        console.error('❌ Validation error:', error);
        showToast('Error validating CSV: ' + error.message, 'error');
    }
}

function displayValidationResults(data) {
    const validationSection = document.getElementById('validationResultsSection');
    const validationStatus = document.getElementById('validationStatus');
    const validationRowCount = document.getElementById('validationRowCount');
    const validationCategoryCount = document.getElementById('validationCategoryCount');
    const validationCategories = document.getElementById('validationCategories');
    const validationErrorsSection = document.getElementById('validationErrorsSection');
    const validationErrors = document.getElementById('validationErrors');
    const validationSuccessSection = document.getElementById('validationSuccessSection');
    const importButtonSection = document.getElementById('importButtonSection');
    
    // Show validation section
    validationSection.style.display = 'block';
    
    // Update status badge
    const isValid = data.status === 'valid';
    validationStatus.textContent = isValid ? '✅ Valid' : '❌ Invalid';
    validationStatus.className = isValid ? 'validation-badge valid' : 'validation-badge invalid';
    
    // Update counts
    validationRowCount.textContent = data.row_count || 0;
    validationCategoryCount.textContent = data.unique_categories || 0;
    
    // Display categories as tags/chips
    if (data.categories && data.categories.length > 0) {
        validationCategories.innerHTML = data.categories.map(cat => 
            `<span class="category-tag">${cat}</span>`
        ).join('');
    } else {
        validationCategories.textContent = '-';
    }
    
    // Handle errors
    if (data.validation_errors && data.validation_errors.length > 0) {
        validationErrorsSection.style.display = 'block';
        validationSuccessSection.style.display = 'none';
        validationErrors.innerHTML = data.validation_errors.map(error => 
            `<div>${error}</div>`
        ).join('');
        importButtonSection.style.display = 'none';
    } else {
        validationErrorsSection.style.display = 'none';
        validationSuccessSection.style.display = 'block';
        importButtonSection.style.display = 'block';
    }
    
    // Scroll to results
    validationSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function importCsv() {
    if (!selectedCsvFile) {
        showToast('Please select a CSV file first', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('file', selectedCsvFile);
        
        console.log('🚀 Starting CSV import...');
        
        // Hide validation and import button sections
        const validationSection = document.getElementById('validationResultsSection');
        const importButtonSection = document.getElementById('importButtonSection');
        const progressSection = document.getElementById('importProgressSection');
        
        if (validationSection) validationSection.style.display = 'none';
        if (importButtonSection) importButtonSection.style.display = 'none';
        
        // Show progress section
        if (progressSection) progressSection.style.display = 'block';
        
        // Simulate progress
        const progressFill = document.getElementById('progressFill');
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += Math.random() * 30;
                if (progressFill) {
                    progressFill.style.width = progress + '%';
                }
            }
        }, 500);
        
        const url = `${API_BASE_URL}/api/import-csv`;
        console.log('Import request URL:', url);
        
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        if (progressFill) {
            progressFill.style.width = '100%';
        }
        
        console.log('Import response status:', response.status);
        
        if (!response.ok) {
            const error = await response.json();
            console.error('Import error:', error);
            showToast(error.detail || 'Import failed', 'error');
            if (progressSection) progressSection.style.display = 'none';
            if (importButtonSection) importButtonSection.style.display = 'block';
            return;
        }
        
        const data = await response.json();
        console.log('✅ Import result:', data);
        
        // Display success
        displayImportSuccess(data);
        
        // Reload dashboard data
        loadDashboard();
        
    } catch (error) {
        console.error('❌ Import error:', error);
        showToast('Error importing CSV: ' + error.message, 'error');
        const progressSection = document.getElementById('importProgressSection');
        const importButtonSection = document.getElementById('importButtonSection');
        if (progressSection) progressSection.style.display = 'none';
        if (importButtonSection) importButtonSection.style.display = 'block';
    }
}

function displayImportSuccess(data) {
    const progressSection = document.getElementById('importProgressSection');
    const successSection = document.getElementById('importSuccessSection');
    const successCategoriesCount = document.getElementById('successCategoriesCount');
    const successProductsCount = document.getElementById('successProductsCount');
    const importErrorsList = document.getElementById('importErrorsList');
    const importErrors = document.getElementById('importErrors');
    
    progressSection.style.display = 'none';
    successSection.style.display = 'block';
    
    successCategoriesCount.textContent = data.categories_created || 0;
    successProductsCount.textContent = data.products_created || 0;
    
    // Show errors if any
    if (data.errors && data.errors.length > 0) {
        importErrorsList.style.display = 'block';
        importErrors.innerHTML = data.errors.map(error => 
            `<div>${error}</div>`
        ).join('');
    } else {
        importErrorsList.style.display = 'none';
    }
    
    showToast(`✅ Import successful! ${data.products_created} products created`, 'success');
}

function resetImportTab() {
    selectedCsvFile = null;
    const csvFileInput = document.getElementById('csvFileInput');
    const uploadArea = document.getElementById('uploadArea');
    const validateCsvBtn = document.getElementById('validateCsvBtn');
    
    // Reset file input
    if (csvFileInput) {
        csvFileInput.value = '';
    }
    
    // Reset upload area
    if (uploadArea) {
        uploadArea.innerHTML = `
            <div class="upload-icon">📄</div>
            <h3>Drop your CSV file here</h3>
            <p>or click to browse</p>
        `;
        uploadArea.classList.remove('dragover');
    }
    
    // Reset buttons
    if (validateCsvBtn) {
        validateCsvBtn.disabled = true;
    }
    
    // Hide all sections
    const validationSection = document.getElementById('validationResultsSection');
    const importButtonSection = document.getElementById('importButtonSection');
    const progressSection = document.getElementById('importProgressSection');
    const successSection = document.getElementById('importSuccessSection');
    
    if (validationSection) validationSection.style.display = 'none';
    if (importButtonSection) importButtonSection.style.display = 'none';
    if (progressSection) progressSection.style.display = 'none';
    if (successSection) successSection.style.display = 'none';
    
    console.log('🔄 Import tab reset');
}

function downloadCsvTemplate() {
    const template = `category_name,category_description,product_name,product_description,unit,stock_quantity,selling_price,is_active
Fruits,Fresh and seasonal fruits,Apple,Red delicious apples,kg,25.5,3.99,1
Fruits,Fresh and seasonal fruits,Banana,Ripe Cavendish bananas,kg,40.2,2.49,1
Vegetables,"Organic and locally grown vegetables",Tomato,Vine-ripened tomatoes,kg,32.0,3.79,1
Dairy,"Milk, cheese, yogurt and other dairy products",Milk 2%,2% reduced fat milk,l,120.0,3.49,1
Beverages,"Soft drinks, juices, coffee and tea",Orange Juice,Fresh orange juice,l,35.0,4.99,1`;

    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(template));
    element.setAttribute('download', 'grocery_template.csv');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    
    showToast('✅ Template downloaded successfully!', 'success');
    console.log('⬇️ CSV template downloaded');
}
