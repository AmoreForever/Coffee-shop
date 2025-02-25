async function updateNavigation() {
    try {
        const user = await api.getCurrentUser();
        const authLinks = document.querySelector('.auth-links');
        
        if (user) {
            authLinks.innerHTML = `
                <span>Привет, ${user.username}!</span>
                ${user.role === 'admin' ? '<a href="/pages/admin/dashboard.html" class="btn-admin">Админ панель</a>' : ''}
                <button onclick="logout()" class="btn-logout">Выйти</button>
            `;
        } else {
            authLinks.innerHTML = `
                <a href="/pages/auth/login.html" class="btn-login">Войти</a>
                <a href="/pages/auth/register.html" class="btn-register">Регистрация</a>
            `;
        }
    } catch (error) {
        console.error('Error updating navigation:', error);
        api.clearToken();
        const authLinks = document.querySelector('.auth-links');
        authLinks.innerHTML = `
            <a href="/pages/auth/login.html" class="btn-login">Войти</a>
            <a href="/pages/auth/register.html" class="btn-register">Регистрация</a>
        `;
    }
}

async function loadFeaturedProducts() {
    try {
        const products = await api.getProducts();
        const container = document.getElementById('featuredProducts');
        
        products.forEach(product => {
            const card = createProductCard(product);
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

async function loadCategories() {
    try {
        const categories = await api.getCategories();
        const container = document.getElementById('categoriesList');
        
        categories.forEach(category => {
            const card = createCategoryCard(category);
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.innerHTML = `
        <img src="${product.image || 'assets/default-product.jpg'}" class="product-image" alt="${product.name}">
        <div class="product-info">
            <h3 class="product-title">${product.name}</h3>
            <p class="product-price">${product.price} ₽</p>
            <button onclick="addToCart(${product.id})" class="btn-primary">В корзину</button>
        </div>
    `;
    return card;
}

function createCategoryCard(category) {
    const card = document.createElement('div');
    card.className = 'category-card';
    card.innerHTML = `
        <h3>${category.name}</h3>
        <p>${category.description}</p>
    `;
    return card;
}

async function addToCart(productId) {
    if (!api.token) {
        window.location.href = '/pages/auth/login.html';
        return;
    }

    try {
        await api.addToCart(productId, 1);
        updateCartCount();
    } catch (error) {
        alert('Ошибка при добавлении в корзину');
    }
}

async function updateCartCount() {
    try {
        const cart = await api.getCart();
        const count = cart.items.reduce((sum, item) => sum + item.quantity, 0);
        document.querySelector('.cart-count').textContent = count;
    } catch (error) {
        console.error('Error updating cart:', error);
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    loadFeaturedProducts();
    loadCategories();
    updateNavigation();
    if (api.token) {
        updateCartCount();
    }
});

// Добавить функцию выхода
async function logout() {
    api.clearToken();
    window.location.href = '/';
} 