// Configuración de la API
const API_URL = 'http://localhost:3000/api'; // Cambiar por tu backend

// Event listener para el formulario de login
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('loginBtn');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('errorMessage');
    
    // Limpiar mensajes anteriores
    errorMessage.classList.remove('show');
    
    // Mostrar loading
    loginBtn.disabled = true;
    loading.classList.add('show');
    
    try {
        // Llamada al backend
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Guardar datos en localStorage
            localStorage.setItem('authToken', data.token);
            localStorage.setItem('userName', data.user.name);
            localStorage.setItem('userId', data.user.id);
            
            // Redirigir al dashboard
            window.location.href = 'dashboard.html';
        } else {
            // Mostrar error
            showError(data.message || 'Usuario o contraseña incorrectos');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError('Error de conexión. Verifica tu internet o intenta más tarde.');
    } finally {
        loginBtn.disabled = false;
        loading.classList.remove('show');
    }
});

// Función para mostrar mensajes de error
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
}

// Función para verificar si el usuario está autenticado
function checkAuth() {
    const token = localStorage.getItem('authToken');
    if (!token) {
        return false;
    }
    return true;
}

// Función para cerrar sesión
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userName');
    localStorage.removeItem('userId');
    window.location.href = 'login.html';
}