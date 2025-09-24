// Frontend Integration JavaScript for Grocery Store Management System
const API_BASE_URL = '/api';

// Utility Functions
function showMessage(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed; top: 20px; right: 20px;
        background: ${type === 'success' ? '#4CAF50' : '#f44336'};
        color: white; padding: 15px 20px; border-radius: 5px;
        z-index: 1000; animation: slideIn 0.3s ease; font-family: 'Poppins', sans-serif; font-size: 1.4rem;
    `;
    if (!document.getElementById('notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }`;
        document.head.appendChild(styles);
    }
    document.body.appendChild(notification);
    setTimeout(() => { notification.remove(); }, 3000);
}

async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, { ...options, headers: { 'Content-Type': 'application/json', ...options.headers } });
        const contentType = response.headers.get("content-type");
        const isJson = contentType && contentType.indexOf("application/json") !== -1;

        const data = isJson ? await response.json() : { error: `Server returned non-JSON content or no content for status ${response.status}` };

        if (!response.ok) {
            const errorMessage = data.error || data.message || `Request failed with status ${response.status}`;
            throw new Error(errorMessage);
        }
        return data;
    } catch (error) {
        showMessage(error.message, 'error');
        throw error;
    }
}

// --- Authentication Functions ---
class Auth {
    static async login(email, password) {
        // FIX: Changed 'username' key to 'email' to match backend expectation.
        const data = await makeRequest(`${API_BASE_URL}/login`, { method: 'POST', body: JSON.stringify({ email: email, password: password }) });
        localStorage.setItem('user', JSON.stringify(data.user));
        showMessage('Login successful!');
        return data;
    }
    static async register(username, email, password) {
        const data = await makeRequest(`${API_BASE_URL}/register`, { method: 'POST', body: JSON.stringify({ username, email, password }) });
        showMessage('Registration successful! Please login.');
        return data;
    }
    static logout() {
        localStorage.removeItem('user');
        CartManager.clearCartDisplay();
        showMessage('Logged out successfully!');
        window.location.href = '/logout';
    }
    static isLoggedIn() { return localStorage.getItem('user') !== null; }
    static getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
}

// --- Product Functions ---
class ProductManager {
    static async getProducts() { return await makeRequest(`${API_BASE_URL}/products`); }
    static async searchProducts(query) { return await makeRequest(`/search?query=${encodeURIComponent(query)}`); }

    static renderProducts(products, container) {
        if (!container) return;
        container.innerHTML = products.map(product => `
            <div class="swiper-slide box" data-product-id="${product.id}">
                <a href="/product/${product.id}" style="text-decoration: none; color: inherit;">
                    <img src="/static/images/product-${product.id}.png" alt="${product.name}">
                    <h1>${product.name}</h1>
                </a>
                <div class="price">₹${product.price.toFixed(2)}</div>
                <div class="stars">${Array.from({ length: 5 }, (_, i) => `<i class="fas fa-star ${i < 4 ? '' : 'far'}"></i>`).join('')}</div>
                <a href="#" class="btn add-to-cart-btn" data-product-id="${product.id}">Add to cart</a>
            </div>`).join('');
    }
}

// --- Cart Functions ---
class CartManager {
    static async addToCart(productId, quantity = 1) {
        if (!Auth.isLoggedIn()) {
            showMessage('Please login to add items to cart', 'error');
            return false;
        }
        try {
            await makeRequest(`${API_BASE_URL}/cart/add`, {
                method: 'POST',
                body: JSON.stringify({ product_id: productId, quantity })
            });
            showMessage('Product added to cart!');
            // await this.updateCartDisplay();
            return true;
        } catch (error) {
            console.error('Add to cart error:', error);
            showMessage('Failed to add product to cart', 'error');
            return false;
        }
    }

    static async getCart() {
        if (!Auth.isLoggedIn()) { return { items: [], total: 0 }; }
        try {
            const response = await makeRequest(`${API_BASE_URL}/cart`);
            return response || { items: [], total: 0 };
        }
        catch (error) {
            console.error('Get cart error:', error);
            return { items: [], total: 0 };
        }
    }

    static async removeFromCart(productId) {
        try {
            await makeRequest(`${API_BASE_URL}/cart/remove`, {
                method: 'POST',
                body: JSON.stringify({ product_id: productId })
            });
            showMessage('Product removed from cart');
            await this.updateCartDisplay();
        } catch (error) {
            console.error('Remove from cart error:', error);
            showMessage('Failed to remove product from cart', 'error');
        }
    }

    static clearCartDisplay() {
        const cartContainer = document.querySelector('.shopping-cart');
        const totalElement = document.querySelector('.shopping-cart .total');

        if (cartContainer) {
            // Clear cart items but keep the structure
            const cartItems = cartContainer.querySelectorAll('.box');
            cartItems.forEach(item => item.remove());
        }

        if (totalElement) {
            totalElement.textContent = 'Total: ₹0.00';
        }
    }

    // In api.js, inside the CartManager class

    // static async updateCartDisplay() {
    //     try {
    //         const cart = await this.getCart();
    //         const cartContainer = document.querySelector('.shopping-cart');
    //         const totalElement = document.querySelector('.shopping-cart .total');

    //         if (!cartContainer) return;

    //         // Remove existing cart items
    //         const existingItems = cartContainer.querySelectorAll('.box');
    //         existingItems.forEach(item => item.remove());

    //         if (!cart.items || cart.items.length === 0) {
    //             if (totalElement) {
    //                 totalElement.textContent = 'Total: ₹0.00';
    //                 // --- ADD THIS LINE ---
    //                 const emptyCartHTML = '<div class="box" style="text-align: center; color: #666; padding: 20px 10px;">Your cart is empty.</div>';
    //                 totalElement.insertAdjacentHTML('beforebegin', emptyCartHTML);
    //             }
    //             return;
    //         }

    //         // Add cart items (this part remains the same)
    //         const cartItemsHTML = cart.items.map(item => `
    //             <div class="box">
    //                 <i class="fas fa-trash remove-item" data-product-id="${item.product_id}" style="cursor: pointer; color: #ff6b6b;"></i>
    //                 <img src="/static/images/product-${item.product_id}.png" alt="${item.name}" style="width: 60px; height: 60px; object-fit: cover;">
    //                 <div class="content">
    //                     <h3 style="font-size: 1.4rem; margin: 5px 0;">${item.name}</h3>
    //                     <span class="price" style="color: #27ae60; font-weight: bold;">₹${item.price.toFixed(2)}</span>
    //                     <span class="quantity" style="margin-left: 10px;">qty: ${item.quantity}</span>
    //                 </div>
    //             </div>`).join('');

    //         // Insert cart items before total
    //         if (totalElement) {
    //             totalElement.insertAdjacentHTML('beforebegin', cartItemsHTML);
    //             totalElement.textContent = `Total: ₹${cart.total.toFixed(2)}`;
    //         }

    //         // Re-attach listeners for dynamically created cart items
    //         cartContainer.querySelectorAll('.remove-item').forEach(btn => {
    //             btn.addEventListener('click', async (e) => {
    //                 e.stopPropagation();
    //                 await this.removeFromCart(parseInt(e.target.dataset.productId));
    //             });
    //         });

    //     } catch (error) { 
    //         console.error('Error updating cart display:', error); 
    //     }
    // }
}

// --- Payment and Order Management ---
class PaymentManager {
    static showPaymentModal(cartTotal) {
        // Remove existing modal if any
        const existingModal = document.getElementById('payment-modal');
        if (existingModal) existingModal.remove();

        const modal = document.createElement('div');
        modal.id = 'payment-modal';
        modal.innerHTML = `
            <div class="modal-overlay" style="
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.7); z-index: 2000; display: flex;
                justify-content: center; align-items: center;
            ">
                <div class="modal-content" style="
                    background: white; padding: 30px; border-radius: 15px;
                    max-width: 500px; width: 90%; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                ">
                    <h2 style="text-align: center; color: #333; margin-bottom: 20px;">Complete Your Payment</h2>
                    <div style="text-align: center; margin-bottom: 20px;">
                        <p style="font-size: 1.8rem; color: #27ae60; font-weight: bold;">Total: ₹${cartTotal.toFixed(2)}</p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 10px; font-weight: bold;">Delivery Address:</label>
                        <textarea id="delivery-address" placeholder="Enter your full delivery address..." 
                            style="width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 5px; 
                                   font-family: inherit; resize: vertical; min-height: 80px;"></textarea>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 10px; font-weight: bold;">Payment Method:</label>
                        <select id="payment-method" style="
                            width: 100%; padding: 10px; border: 2px solid #ddd; 
                            border-radius: 5px; font-family: inherit;
                        ">
                            <option value="card">Credit/Debit Card</option>
                            <option value="upi">UPI</option>
                            <option value="netbanking">Net Banking</option>
                            <option value="wallet">Digital Wallet</option>
                            <option value="cod">Cash on Delivery</option>
                        </select>
                    </div>
                    
                    <div id="payment-details" style="margin-bottom: 20px;">
                        </div>
                    
                    <div style="display: flex; gap: 10px; justify-content: center;">
                        <button id="confirm-payment" class="btn" style="
                            background: #27ae60; color: white; padding: 12px 30px;
                            border: none; border-radius: 5px; cursor: pointer;
                            font-size: 1.6rem; font-weight: bold;
                        ">Confirm Payment</button>
                        <button id="cancel-payment" class="btn" style="
                            background: #e74c3c; color: white; padding: 12px 30px;
                            border: none; border-radius: 5px; cursor: pointer;
                            font-size: 1.6rem;
                        ">Cancel</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Handle payment method change
        const paymentMethodSelect = modal.querySelector('#payment-method');
        const paymentDetailsDiv = modal.querySelector('#payment-details');

        paymentMethodSelect.addEventListener('change', (e) => {
            this.updatePaymentDetails(e.target.value, paymentDetailsDiv);
        });

        // Initialize with card details
        this.updatePaymentDetails('card', paymentDetailsDiv);

        // Handle confirm payment
        modal.querySelector('#confirm-payment').addEventListener('click', async () => {
            await this.processPayment(modal, cartTotal);
        });

        // Handle cancel
        modal.querySelector('#cancel-payment').addEventListener('click', () => {
            modal.remove();
        });

        // Handle click outside modal
        modal.querySelector('.modal-overlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                modal.remove();
            }
        });
    }

    static updatePaymentDetails(method, container) {
        let detailsHTML = '';

        switch (method) {
            case 'card':
                detailsHTML = `
                    <div>
                        <input type="text" id="card-number" placeholder="Card Number (1234 5678 9012 3456)" 
                               style="width: 100%; padding: 10px; margin-bottom: 10px; border: 2px solid #ddd; border-radius: 5px;">
                        <div style="display: flex; gap: 10px;">
                            <input type="text" id="expiry" placeholder="MM/YY" 
                                   style="flex: 1; padding: 10px; border: 2px solid #ddd; border-radius: 5px;">
                            <input type="text" id="cvv" placeholder="CVV" 
                                   style="flex: 1; padding: 10px; border: 2px solid #ddd; border-radius: 5px;">
                        </div>
                    </div>
                `;
                break;
            case 'upi':
                detailsHTML = `
                    <input type="text" id="upi-id" placeholder="Enter UPI ID (example@paytm)" 
                           style="width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 5px;">
                `;
                break;
            case 'netbanking':
                detailsHTML = `
                    <select id="bank-select" style="width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 5px;">
                        <option value="">Select Your Bank</option>
                        <option value="sbi">State Bank of India</option>
                        <option value="hdfc">HDFC Bank</option>
                        <option value="icici">ICICI Bank</option>
                        <option value="axis">Axis Bank</option>
                        <option value="kotak">Kotak Mahindra Bank</option>
                    </select>
                `;
                break;
            case 'wallet':
                detailsHTML = `
                    <select id="wallet-select" style="width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 5px;">
                        <option value="">Select Wallet</option>
                        <option value="paytm">Paytm</option>
                        <option value="phonepe">PhonePe</option>
                        <option value="googlepay">Google Pay</option>
                        <option value="amazonpay">Amazon Pay</option>
                    </select>
                `;
                break;
            case 'cod':
                detailsHTML = `
                    <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 5px;">
                        <p style="margin: 0; color: #666;">Pay cash when your order is delivered to your doorstep.</p>
                        <p style="margin: 5px 0 0 0; font-size: 1.4rem; color: #27ae60; font-weight: bold;">No online payment required!</p>
                    </div>
                `;
                break;
        }

        container.innerHTML = detailsHTML;
    }

    static async processPayment(modal, total) {
        const address = modal.querySelector('#delivery-address').value.trim();
        const paymentMethod = modal.querySelector('#payment-method').value;

        if (!address) {
            showMessage('Please enter delivery address', 'error');
            return;
        }

        // Validate payment details based on method
        if (!this.validatePaymentDetails(modal, paymentMethod)) {
            return;
        }

        try {
            // Show processing
            const confirmBtn = modal.querySelector('#confirm-payment');
            confirmBtn.textContent = 'Processing...';
            confirmBtn.disabled = true;

            // Call checkout API
            await makeRequest(`${API_BASE_URL}/checkout`, {
                method: 'POST',
                body: JSON.stringify({
                    delivery_address: address, // <-- Changed 'address' to 'delivery_address'
                    payment_method: paymentMethod
                })
            });

            modal.remove();
            showMessage('Order placed successfully!', 'success');

            // Clear cart and refresh
            await CartManager.updateCartDisplay();

        } catch (error) {
            // showMessage('Payment failed. Please try again.', 'error');
            const confirmBtn = modal.querySelector('#confirm-payment');
            confirmBtn.textContent = 'Confirm Payment';
            confirmBtn.disabled = false;
        }
    }

    static validatePaymentDetails(modal, method) {
        switch (method) {
            case 'card':
                const cardNumber = modal.querySelector('#card-number')?.value.trim();
                const expiry = modal.querySelector('#expiry')?.value.trim();
                const cvv = modal.querySelector('#cvv')?.value.trim();

                if (!cardNumber || cardNumber.length < 16) {
                    showMessage('Please enter a valid card number', 'error');
                    return false;
                }
                if (!expiry || !expiry.match(/^\d{2}\/\d{2}$/)) {
                    showMessage('Please enter valid expiry date (MM/YY)', 'error');
                    return false;
                }
                if (!cvv || cvv.length < 3) {
                    showMessage('Please enter valid CVV', 'error');
                    return false;
                }
                break;

            case 'upi':
                const upiId = modal.querySelector('#upi-id')?.value.trim();
                if (!upiId || !upiId.includes('@')) {
                    showMessage('Please enter a valid UPI ID', 'error');
                    return false;
                }
                break;

            case 'netbanking':
                const bank = modal.querySelector('#bank-select')?.value;
                if (!bank) {
                    showMessage('Please select your bank', 'error');
                    return false;
                }
                break;

            case 'wallet':
                const wallet = modal.querySelector('#wallet-select')?.value;
                if (!wallet) {
                    showMessage('Please select a wallet', 'error');
                    return false;
                }
                break;
        }
        return true;
    }
}

class OrderManager {
    static async checkout() {
        if (!Auth.isLoggedIn()) {
            showMessage('Please login to place order', 'error');
            return;
        }

        try {
            const cart = await CartManager.getCart();
            if (!cart.items || cart.items.length === 0) {
                showMessage('Your cart is empty', 'error');
                return;
            }

            // Show payment modal
            PaymentManager.showPaymentModal(cart.total);

        } catch (error) {
            console.error('Checkout error:', error);
            showMessage('Failed to proceed to checkout', 'error');
        }
    }
}

// --- Admin Functions ---
class AdminManager {
    static async addProduct(name, description, price, stock) {
        try {
            await makeRequest(`${API_BASE_URL}/products/add`, { method: 'POST', body: JSON.stringify({ name, description, price, stock }) });
            showMessage('Product added successfully!');
            window.location.reload();
        } catch (error) { console.error('Add product error:', error); }
    }
    static async updateProduct(id, name, description, price, stock) {
        try {
            await makeRequest(`${API_BASE_URL}/products/update/${id}`, { method: 'POST', body: JSON.stringify({ name, description, price, stock }) });
            showMessage('Product updated successfully!');
            window.location.reload();
        } catch (error) { console.error('Update product error:', error); }
    }
    static async deleteProduct(id) {
        try {
            await makeRequest(`${API_BASE_URL}/products/delete/${id}`, { method: 'POST' });
            showMessage('Product deleted successfully!');
            window.location.reload();
        } catch (error) { console.error('Delete product error:', error); }
    }
    static populateProductList(products) {
        const productList = document.getElementById('product-list');
        if (!productList) return;
        productList.innerHTML = products.map(p => `
            <tr>
                <td>${p.id}</td><td>${p.name}</td><td>₹${p.price.toFixed(2)}</td><td>${p.stock}</td>
                <td>
                    <a href="#" class="btn edit-btn" data-id="${p.id}">Edit</a>
                    <a href="#" class="btn delete-btn" data-id="${p.id}">Delete</a>
                </td>
            </tr>`).join('');
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                e.preventDefault();
                const product = products.find(p => p.id == e.target.dataset.id);
                this.populateEditForm(product);
            });
        });
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', e => { e.preventDefault(); this.deleteProduct(e.target.dataset.id); });
        });
    }
    static populateEditForm(product) {
        document.querySelector('#product-form h3').textContent = 'Update Product';
        document.getElementById('product-id').value = product.id;
        document.getElementById('product-name').value = product.name;
        document.getElementById('product-price').value = product.price;
        document.getElementById('product-stock').value = product.stock;
        document.getElementById('product-description').value = product.description;
        document.getElementById('submit-btn').value = 'Update Product';
        document.getElementById('cancel-edit-btn').style.display = 'inline-block';
        window.scrollTo(0, 0);
    }
    static clearForm() {
        document.querySelector('#product-form h3').textContent = 'Add a New Product';
        document.getElementById('product-form').reset();
        document.getElementById('product-id').value = '';
        document.getElementById('submit-btn').value = 'Add Product';
        document.getElementById('cancel-edit-btn').style.display = 'none';
    }
}

// --- Main Initialization on Page Load ---
document.addEventListener('DOMContentLoaded', () => {

    // if (Auth.isLoggedIn()) { 
    //     CartManager.updateCartDisplay(); 
    // }

    // --- Authentication Form Logic ---
    const authForm = document.getElementById('auth-form');
    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('auth-email').value;
            const password = document.getElementById('auth-password').value;
            const action = document.getElementById('auth-action').value;
            try {
                if (action === 'login') {
                    await Auth.login(email, password);
                    window.location.reload();
                } else {
                    const name = document.getElementById('auth-name').value;
                    await Auth.register(name, email, password);
                    document.getElementById('login-link')?.click();
                }
            } catch (error) { console.error("Auth Error:", error); }
        });
    }

    // Event Delegation for Add to Cart Buttons
    document.body.addEventListener('click', async (e) => {
        const btn = e.target.closest('.add-to-cart-btn');

        if (btn) {
            e.preventDefault();
            const productId = parseInt(btn.dataset.productId);

            if (!isNaN(productId) && productId > 0) {
                await CartManager.addToCart(productId);
            } else {
                showMessage(`Error: Invalid Product ID: ${btn.dataset.productId}`, 'error');
                console.error('Invalid Product ID:', btn.dataset.productId);
            }
        }
    });

    // Handle Checkout Button Click
    document.addEventListener('click', (e) => {
        if (e.target.matches('.btn[href="#"]') && e.target.textContent.trim() === 'Checkout') {
            e.preventDefault();
            OrderManager.checkout();
        }
    });

    // --- Admin Page Logic ---
    if (window.location.pathname === '/admin') {
        const productForm = document.getElementById('product-form');
        if (productForm) {
            productForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const id = document.getElementById('product-id').value;
                const name = document.getElementById('product-name').value;
                const price = parseFloat(document.getElementById('product-price').value);
                const stock = parseInt(document.getElementById('product-stock').value);
                const description = document.getElementById('product-description').value;
                if (id) { await AdminManager.updateProduct(id, name, description, price, stock); }
                else { await AdminManager.addProduct(name, description, price, stock); }
            });
        }

        const cancelBtn = document.getElementById('cancel-edit-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', (e) => { e.preventDefault(); AdminManager.clearForm(); });
        }

        ProductManager.getProducts().then(data => {
            AdminManager.populateProductList(data.products);
        });
    }

    // --- Sliders for Homepage ---
    if (window.location.pathname.startsWith('/home') || window.location.pathname === '/') {
        new Swiper(".product-slider", {
            loop: true, spaceBetween: 20,
            autoplay: { delay: 7500, disableOnInteraction: false },
            navigation: { nextEl: ".swiper-button-next", prevEl: ".swiper-button-prev" },
            breakpoints: { 0: { slidesPerView: 1 }, 768: { slidesPerView: 2 }, 1020: { slidesPerView: 3 } }
        });
        new Swiper(".review-slider", {
            loop: true, spaceBetween: 20,
            autoplay: { delay: 6500, disableOnInteraction: false },
            navigation: { nextEl: ".swiper-button-next", prevEl: ".swiper-button-prev" },
            breakpoints: { 0: { slidesPerView: 1 }, 768: { slidesPerView: 2 }, 1020: { slidesPerView: 3 } }
        });
    }
});