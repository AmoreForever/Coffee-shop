// Проверка прав доступа
async function checkAdminAccess() {
    try {
        const user = await api.getCurrentUser();
        if (!user || user.role !== 'admin') {
            window.location.href = '/';
        }
    } catch (error) {
        window.location.href = '/';
    }
}

// Переключение между разделами
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const section = e.target.dataset.section;
        
        // Обновляем активный пункт меню
        document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
        e.target.classList.add('active');
        
        // Показываем нужную секцию
        document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
        document.getElementById(section).classList.add('active');
        
        // Загружаем данные для секции
        loadSectionData(section);
    });
});

// Загрузка данных для разных секций
async function loadSectionData(section) {
    switch(section) {
        case 'products':
            await loadProducts();
            break;
        case 'categories':
            await loadCategories();
            break;
        case 'orders':
            await loadOrders();
            break;
        case 'users':
            await loadUsers();
            break;
    }
}

// Загрузка продуктов
async function loadProducts() {
    try {
        const products = await api.getProducts();
        const tbody = document.querySelector('#productsTable tbody');
        tbody.innerHTML = '';
        
        products.forEach(product => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${product.id}</td>
                <td>${product.name}</td>
                <td>${product.price} ₽</td>
                <td>${product.category_name || '-'}</td>
                <td>
                    <button class="btn-action btn-edit" onclick="editProduct(${product.id})">Изменить</button>
                    <button class="btn-action btn-delete" onclick="deleteProduct(${product.id})">Удалить</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// Добавляем функции для других секций...

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    checkAdminAccess();
    loadSectionData('products'); // Загружаем продукты по умолчанию
});

// Обработка выхода
document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    api.clearToken();
    window.location.href = '/';
}); 