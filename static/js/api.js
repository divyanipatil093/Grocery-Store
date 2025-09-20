// Frontend Integration JavaScript for Grocery Store Management System
// This file connects your existing HTML/CSS frontend with the Flask backend

const API_BASE_URL = '/api';

// Utility Functions
function showMessage(message, type = 'success') {
    // Create and show notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : '#f44336'};
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        showMessage(error.message, 'error');
        throw error;
    }
}

// Authentication Functions
class Auth {
    static async login(username, password) {
        const data = await makeRequest(`${API_BASE_URL}/login`, {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        
        localStorage.setItem('user', JSON.stringify(data.user));
        showMessage('Login successful!');
        return data;
    }
    
    static async register(username, email, password) {
        const data = await makeRequest(`${API_BASE_URL}/register`, {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
        
        showMessage('Registration successful! Please login.');
        return data;
    }
    
    static async logout() {
        await makeRequest(`${API_BASE_URL}/logout`, { method: 'POST' });
        localStorage.removeItem('user');
        showMessage('Logged out successfully!');
        window.location.reload();
    }
    
    static isLoggedIn() {
        return localStorage.getItem('user') !== null;
    }
    
    static getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
}

// Product Functions
class ProductManager {
    static async getProducts(filters = {}) {
        const params = new URLSearchParams(filters);
        const data = await makeRequest(`${API_BASE_URL}/products?${params}`);
        return data;
    }
    
    static async getProduct(id) {
        const data = await makeRequest(`${API_BASE_URL}/products/${id}`);
        return data;
    }
    
    static async getFeaturedProducts() {
        const data = await makeRequest(`${API_BASE_URL}/products?featured=true`);
        return data;
    }
    
    static renderProducts(products, container) {
        if (!container) return;
        
        container.innerHTML = products.map(product => `
            <div class="box" data-product-id="${product.id}">
                <img src="${product.image_url}" alt="${product.name}">
                <h3>${product.name}</h3>
                <div class="price">$${product.price}</div>
                <div class="stars">
                    ${Array.from({length: 5}, (_, i) => 
                        `<i class="fas fa-star ${i < 4 ? '' : 'far'}"></i>`
                    ).join('')}
                </div>
                <a href="#" class="btn add-to-cart-btn" data-product-id="${product.id}">
                    add to cart
                </a>
            </div>
        `).join('');
        
        // Add event listeners to "add to cart" buttons
        container.querySelectorAll('.add-to-cart-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const productId = parseInt(btn.dataset.productId);
                await CartManager.addToCart(productId);
            });
        });
    }
}

// Category Functions
class CategoryManager {
    static async getCategories() {
        const data = await makeRequest(`${API_BASE_URL}/categories`);
        return data;
    }
    
    static renderCategories(categories, container) {
        if (!container) return;
        
        container.innerHTML = categories.map(category => `
            <div class="box" data-category-id="${category.id}">
                <img src="${category.image_url}" alt="${category.name}">
                <h3>${category.name}</h3>
                <p>${category.description}</p>
                <a href="#" class="btn category-btn" data-category-id="${category.id}">
                    shop now
                </a>
            </div>
        `).join('');
        
        // Add event listeners
        container.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.preventDefault();
                const categoryId = parseInt(btn.dataset.categoryId);
                await this.showCategoryProducts(categoryId);
            });
        });
    }
    
    static async showCategoryProducts(categoryId) {
        const products = await ProductManager.getProducts({ category_id: categoryId });
        const productsContainer = document.querySelector('#products .box-container');
        if (productsContainer) {
            ProductManager.renderProducts(products.products, productsContainer);
            document.querySelector('#products').scrollIntoView();
        }
    }
}

// Cart Functions
class CartManager {
    static async addToCart(productId, quantity = 1) {
        if (!Auth.isLoggedIn()) {
            showMessage('Please login to add items to cart', 'error');
            return;
        }
        
        await makeRequest(`${API_BASE_URL}/cart/add`, {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity })
        });
        
        showMessage('Product added to cart!');
        await this.updateCartDisplay();
    }
    
    static async getCart() {
        const data = await makeRequest(`${API_BASE_URL}/cart`);
        return data;
    }
    
    static async removeFromCart(productId) {
        await makeRequest(`${API_BASE_URL}/cart/remove`, {
            method: 'POST',
            body: JSON.stringify({ product_id: productId })
        });
        
        showMessage('Product removed from cart');
        await this.updateCartDisplay();
    }
    
    static async updateCartDisplay() {
        try {
            const cart = await this.getCart();
            const cartContainer = document.querySelector('#shopping-cart');
            const cartCount = document.querySelector('.cart-count');
            
            if (cartCount) {
                cartCount.textContent = cart.items.length;
            }
            
            if (cartContainer) {
                const cartItemsHTML = cart.items.map(item => `
                    <div class="box">
                        <i class="fas fa-trash remove-item" data-product-id="${item.product_id}"></i>
                        <img src="${item.image_url}" alt="${item.name}">
                        <div class="content">
                            <h3>${item.name}</h3>
                            <span class="price">$${item.price}</span>
                            <span class="quantity">qty: ${item.quantity}</span>
                        </div>
                    </div>
                `).join('');
                
                cartContainer.innerHTML = `
                    ${cartItemsHTML}
                    <div class="total">Total: $${cart.total.toFixed(2)}</div>
                    <a href="#" class="btn checkout-btn">Checkout</a>
                `;
                
                // Add remove item event listeners
                cartContainer.querySelectorAll('.remove-item').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        const productId = parseInt(btn.dataset.productId);
                        await this.removeFromCart(productId);
                    });
                });
                
                // Add checkout event listener
                const checkoutBtn = cartContainer.querySelector('.checkout-btn');
                if (checkoutBtn) {
                    checkoutBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        OrderManager.showCheckoutForm();
                    });
                }
            }
        } catch (error) {
            console.error('Error updating cart display:', error);
        }
    }
}

// Order Management
class OrderManager {
    static showCheckoutForm() {
        if (!Auth.isLoggedIn()) {
            showMessage('Please login to place an order', 'error');
            return;