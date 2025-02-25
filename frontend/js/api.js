const API_URL = 'http://localhost:8000/api/v1';

class Api {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    }

    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async handleResponse(response) {
        const data = await response.json();
        
        if (!response.ok) {
            const error = new Error(data.detail || 'Произошла ошибка');
            error.status = response.status;
            error.data = data;
            throw error;
        }
        
        return data;
    }

    async login(email, password) {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/auth/authentication`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await this.handleResponse(response);
        this.setToken(data.access_token);
        return data;
    }

    async register(userData) {
        const response = await fetch(`${API_URL}/auth/registration`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(userData)
        });

        return this.handleResponse(response);
    }

    async getProducts() {
        const response = await fetch(`${API_URL}/products/products`);
        return response.json();
    }

    async getCategories() {
        const response = await fetch(`${API_URL}/categories/categories`);
        return response.json();
    }

    async addToCart(productId, quantity) {
        const response = await fetch(`${API_URL}/cart`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ product_id: productId, quantity })
        });
        return response.json();
    }

    async getCart() {
        const response = await fetch(`${API_URL}/cart`, {
            headers: this.getHeaders()
        });
        return response.json();
    }

    async createOrder() {
        const response = await fetch(`${API_URL}/orders/order`, {
            method: 'POST',
            headers: this.getHeaders()
        });
        return response.json();
    }

    async getCurrentUser() {
        if (!this.token) return null;
        
        try {
            const response = await fetch(`${API_URL}/auth/me`, {
                headers: this.getHeaders()
            });
            
            if (!response.ok) {
                this.clearToken();
                return null;
            }
            
            const user = await this.handleResponse(response);
            return user;
        } catch (error) {
            this.clearToken();
            return null;
        }
    }

    async getUsers() {
        const response = await fetch(`${API_URL}/auth/users`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async updateUserRole(userId, role) {
        const response = await fetch(`${API_URL}/auth/user/${userId}/role`, {
            method: 'PATCH',
            headers: this.getHeaders(),
            body: JSON.stringify({ role })
        });
        return this.handleResponse(response);
    }

    async deleteProduct(productId) {
        const response = await fetch(`${API_URL}/products/product/${productId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }

    async updateProduct(productId, data) {
        const response = await fetch(`${API_URL}/products/product/${productId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }
}

const api = new Api(); 