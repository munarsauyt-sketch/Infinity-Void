const API_BASE = '';

function showAlert(elementId, message, type) {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        setTimeout(() => { el.innerHTML = ''; }, 4000);
    }
}

function updateNav() {
    const user = JSON.parse(localStorage.getItem('hotel_user') || 'null');
    const navUser = document.getElementById('nav-user');
    const navLogin = document.getElementById('nav-login');
    const navRegister = document.getElementById('nav-register');
    const navLogout = document.getElementById('nav-logout');
    if (user) {
        if (navUser) navUser.textContent = `👤 ${user.username}`;
        if (navLogin) navLogin.style.display = 'none';
        if (navRegister) navRegister.style.display = 'none';
        if (navLogout) navLogout.style.display = 'inline';
    } else {
        if (navUser) navUser.textContent = '';
        if (navLogin) navLogin.style.display = 'inline';
        if (navRegister) navRegister.style.display = 'inline';
        if (navLogout) navLogout.style.display = 'none';
    }
}

function logout() {
    localStorage.removeItem('hotel_user');
    window.location.href = 'index.html';
}

async function apiLogin(email, password) {
    try {
        const res = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('hotel_user', JSON.stringify(data));
        }
        return data;
    } catch (e) {
        return { detail: 'Ошибка сервера' };
    }
}

async function apiRegister(username, email, password) {
    try {
        const res = await fetch(`${API_BASE}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        return await res.json();
    } catch (e) {
        return { detail: 'Ошибка сервера' };
    }
}

async function apiGetRooms(type) {
    try {
        const url = type ? `${API_BASE}/rooms?type=${encodeURIComponent(type)}` : `${API_BASE}/rooms`;
        const res = await fetch(url);
        return await res.json();
    } catch (e) {
        return [];
    }
}

async function apiGetBookings() {
    try {
        const res = await fetch(`${API_BASE}/bookings`);
        return await res.json();
    } catch (e) {
        return [];
    }
}

async function apiCreateBooking(data) {
    try {
        const res = await fetch(`${API_BASE}/bookings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    } catch (e) {
        return { detail: 'Ошибка сервера' };
    }
}
