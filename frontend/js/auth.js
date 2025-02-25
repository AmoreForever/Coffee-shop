// Функция для показа ошибок
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    const form = document.querySelector('.auth-form');
    form.insertBefore(errorDiv, form.firstChild);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}

// Обработчик входа
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            await handleLogin(email, password);
        } catch (error) {
            showError('Неверный email или пароль');
        }
    });
}

// Обработчик регистрации
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // Валидация
        if (password !== confirmPassword) {
            showError('Пароли не совпадают');
            return;
        }

        if (password.length < 6) {
            showError('Пароль должен содержать минимум 6 символов');
            return;
        }

        try {
            await api.register({
                username,
                email,
                password
            });
            
            await api.login(email, password);
            window.location.href = '/';
        } catch (error) {
            showError('Ошибка при регистрации. Возможно, email уже используется');
        }
    });
}

// Обновим проверку авторизации
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const token = localStorage.getItem('token');
        if (token) {
            const user = await api.getCurrentUser();
            if (!user && window.location.href.includes('/auth/')) {
                window.location.href = '/';
            }
        }
    } catch (error) {
        api.clearToken();
    }
});

// Изменим пути для редиректа
async function handleLogin(email, password) {
    try {
        await api.login(email, password);
        window.location.href = '/';
    } catch (error) {
        showError('Неверный email или пароль');
    }
} 