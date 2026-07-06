// ── Global API Helper ──────────────────────────────────
async function apiCall(url, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        };
        if (body) options.body = JSON.stringify(body);

        const response = await fetch(url, options);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Something went wrong!');
        }

        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}


// ── Toast Notification ─────────────────────────────────
function showToast(message, type = 'info') {
    const colors = {
        success: { bg: '#43E97B', icon: '✅' },
        error: { bg: '#FF6B6B', icon: '⚠️' },
        info: { bg: '#6C63FF', icon: 'ℹ️' }
    };

    const config = colors[type] || colors.info;

    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: #13131F;
        border: 1px solid ${config.bg}40;
        border-left: 4px solid ${config.bg};
        color: white;
        padding: 14px 20px;
        border-radius: 12px;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        display: flex;
        align-items: center;
        gap: 10px;
        max-width: 350px;
        animation: slideInRight 0.4s ease forwards;
    `;
    toast.innerHTML = `<span>${config.icon}</span><span>${message}</span>`;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}


// ── Button Loading State Helper ────────────────────────
function setButtonLoading(button, isLoading, loadingText = 'Loading...') {
    if (isLoading) {
        button.dataset.originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = `<span class="spinner inline-block mr-2"></span>${loadingText}`;
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
    }
}


// ── Inject fadeOut animation ───────────────────────────
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        to { opacity: 0; transform: translateX(30px); }
    }
`;
document.head.appendChild(style);