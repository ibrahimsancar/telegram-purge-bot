// Global state
let botStatus = {
    isRunning: false,
    token: "",
    deleteServiceMessages: false,
};

let loading = {
    start: false,
    stop: false,
    restart: false,
    saveToken: false,
    setCommands: false,
    toggleService: false,
};

let recentActivities = [];

// Token visibility state
let isTokenVisible = false;

// API base URL - adjust this to match your backend
const API_BASE_URL = '/api';

// Log yönetimi
let autoRefreshInterval = null;
let isAutoRefreshActive = false;

// Utility functions
function showToast(title, description = '', type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    // Maksimum 5 toast
    while (toastContainer.children.length >= 5) {
        toastContainer.removeChild(toastContainer.firstChild);
    }

    // İkon seçimi
    let iconHtml = '';
    if (type === 'success') iconHtml = '<span class="toast-icon"></span>';
    else if (type === 'error') iconHtml = '<span class="toast-icon"><i class="fas fa-times"></i></span>';
    else if (type === 'warning') iconHtml = '<span class="toast-icon"><i class="fas fa-exclamation"></i></span>';
    else iconHtml = '<span class="toast-icon"><i class="fas fa-info"></i></span>';

    // Sol tarafta renkli daire
    const dotHtml = `<span class="toast-dot"></span>`;

    // Toast HTML
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    // Rastgele başlangıç açısı (0-359)
    const randomAngle = Math.floor(Math.random() * 360);
    toast.style.setProperty('--toast-glow-angle', randomAngle + 'deg');
    toast.innerHTML = `
        ${dotHtml}
        ${iconHtml}
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            ${description ? `<div class="toast-description">${description}</div>` : ''}
        </div>
        <button class="toast-close" onclick="this.parentElement.classList.add('hide'); setTimeout(()=>this.parentElement.remove(), 450)">&times;</button>
    `;

    // Kapatma animasyonu
    toast.addEventListener('animationend', function (e) {
        if (e.animationName === 'toast-out') {
            toast.remove();
        }
    });

    // Otomatik kapanma
    setTimeout(() => {
        toast.classList.add('hide');
    }, 3500);

    toastContainer.appendChild(toast);
}

function updateButtonLoading(buttonId, isLoading, loadingText, originalText) {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    const btnText = button.querySelector('.btn-text');
    if (isLoading) {
        button.disabled = true;
        if (btnText) btnText.textContent = loadingText;
    } else {
        button.disabled = false;
        if (btnText) btnText.textContent = originalText;
    }
}

function updateBotStatusUI() {
    const statusBadge = document.getElementById('bot-status-badge');
    const startBtn = document.getElementById('start-bot-btn');
    const stopBtn = document.getElementById('stop-bot-btn');
    const restartBtn = document.getElementById('restart-bot-btn');
    const setCommandsBtn = document.getElementById('set-commands-btn');
    const tokenInput = document.getElementById('bot-token-input');
    const serviceToggle = document.getElementById('delete-service-messages-toggle');
    const serviceStatusText = document.getElementById('service-status-text');
    
    // Update status badge
    if (statusBadge) {
        let dotClass = botStatus.isRunning ? 'badge-dot badge-dot-success' : 'badge-dot badge-dot-error';
        let text = botStatus.isRunning ? 'Çalışıyor' : 'Durduruldu';
        statusBadge.className = botStatus.isRunning ? 'badge badge-success' : 'badge badge-error';
        statusBadge.innerHTML = `<span class="${dotClass}"></span>${text}`;
    }
    
    // Update button states
    if (startBtn) startBtn.disabled = botStatus.isRunning || loading.start;
    if (stopBtn) stopBtn.disabled = !botStatus.isRunning || loading.stop;
    if (restartBtn) restartBtn.disabled = !botStatus.isRunning || loading.restart;
    if (setCommandsBtn) setCommandsBtn.disabled = loading.setCommands || !botStatus.token;
    
    // Update token input
    if (tokenInput) {
        tokenInput.value = botStatus.token || '';
    }
    
    // Update service messages toggle
    if (serviceToggle) {
        serviceToggle.checked = botStatus.deleteServiceMessages;
    }
    if (serviceStatusText) {
        serviceStatusText.textContent = botStatus.deleteServiceMessages ? 'Açık' : 'Kapalı';
    }
}

function updateActivitiesUI() {
    const container = document.getElementById('activities-container');
    if (!container) return;
    
    if (recentActivities.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-chart-line"></i>
                <p>Henüz işlem kaydı bulunmuyor</p>
            </div>
        `;
        return;
    }
    
    const activitiesHTML = recentActivities.map(activity => {
        const badgeClass = activity.status === 'success' ? 'badge-primary' : 
                          activity.status === 'error' ? 'badge-destructive' : 'badge-secondary';
        
        return `
            <div class="activity-item">
                <div class="activity-content">
                    <div class="activity-badge">
                        <span class="badge ${badgeClass}">${activity.action}</span>
                    </div>
                    <p class="activity-description">${activity.description}</p>
                </div>
                <div class="activity-time">
                    <i class="fas fa-clock"></i>
                    <span>${new Date(activity.timestamp).toLocaleString('tr-TR')}</span>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = activitiesHTML;
}

// API functions
async function fetchBotStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/bot/status`);
        if (response.ok) {
            const data = await response.json();
            botStatus.isRunning = data.status === 'running';
            botStatus.token = data.token || ""; // Assuming token might be returned here
            // botStatus.deleteServiceMessages will be fetched separately or from settings API
            updateBotStatusUI();
        } else {
            showToast('Hata', 'Bot durumu alınamadı', 'error');
        }
    } catch (error) {
        console.error('Failed to fetch bot status:', error);
        showToast('Hata', 'Bağlantı hatası', 'error');
    }
}

async function fetchRecentActivities() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`); // Assuming /api/stats returns history
        if (response.ok) {
            const data = await response.json();
            // Map existing history data to new activity format
            recentActivities = data.history.map(item => ({
                id: item.timestamp, // Use timestamp as a unique ID for simplicity
                action: item.command,
                description: `Silinen Mesaj: ${item.deleted_messages}`,
                timestamp: item.timestamp,
                status: 'success' // Assuming all history items are successful operations
            }));
            updateActivitiesUI();
        } else {
            showToast('Hata', 'Aktivite geçmişi alınamadı', 'error');
        }
    } catch (error) {
        console.error('Failed to fetch recent activities:', error);
        showToast('Hata', 'Bağlantı hatası', 'error');
    }
}

async function fetchServiceMessagesSetting() {
    try {
        const response = await fetch(`${API_BASE_URL}/settings/delete_service_messages`);
        if (response.ok) {
            const data = await response.json();
            botStatus.deleteServiceMessages = data.value;
            updateBotStatusUI();
        }
    } catch (error) {
        console.error('Failed to fetch service messages setting:', error);
    }
}

// Event handlers
async function handleBotAction(action) {
    loading[action] = true;
    updateBotStatusUI();
    
    const loadingTexts = {
        start: 'Başlatılıyor...',
        stop: 'Durduruluyor...',
        restart: 'Yeniden Başlatılıyor...'
    };
    
    const successMessages = {
        start: 'Bot başlatıldı',
        stop: 'Bot durduruldu',
        restart: 'Bot yeniden başlatıldı'
    };
    
    updateButtonLoading(
        `${action}-bot-btn`,
        true,
        loadingTexts[action],
        action === 'start' ? 'Başlat' : action === 'stop' ? 'Durdur' : 'Yeniden Başlat'
    );
    
    try {
        const response = await fetch(`${API_BASE_URL}/bot/${action}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('Başarılı', data.message || successMessages[action], 'success');
            await fetchBotStatus();
            await fetchRecentActivities();
        } else {
            const errorData = await response.json();
            showToast('Hata', errorData.message || 'İşlem başarısız', 'error');
        }
    } catch (error) {
        showToast('Hata', 'Bağlantı hatası', 'error');
    } finally {
        loading[action] = false;
        updateBotStatusUI();
        updateButtonLoading(
            `${action}-bot-btn`,
            false,
            loadingTexts[action],
            action === 'start' ? 'Başlat' : action === 'stop' ? 'Durdur' : 'Yeniden Başlat'
        );
    }
}

async function handleSaveToken() {
    const tokenInput = document.getElementById('bot-token-input');
    const token = tokenInput.value.trim();
    
    if (!token) {
        showToast('Hata', 'Lütfen geçerli bir token girin', 'error');
        return;
    }
    
    loading.saveToken = true;
    updateBotStatusUI();
    updateButtonLoading('save-token-btn', true, 'Kaydediliyor...', 'Tokeni Kaydet');
    
    try {
        const response = await fetch(`${API_BASE_URL}/bot/set_token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token: token })
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('Başarılı', data.message, 'success');
            await fetchBotStatus();
            await fetchRecentActivities();
        } else {
            const errorData = await response.json();
            showToast('Hata', errorData.message || 'Token kaydedilemedi', 'error');
        }
    } catch (error) {
        showToast('Hata', 'Bağlantı hatası', 'error');
    } finally {
        loading.saveToken = false;
        updateBotStatusUI();
        updateButtonLoading('save-token-btn', false, 'Kaydediliyor...', 'Tokeni Kaydet');
    }
}

async function handleSetCommands() {
    loading.setCommands = true;
    updateBotStatusUI();
    updateButtonLoading('set-commands-btn', true, 'Ayarlanıyor...', 'Kısayolları Ekle');
    
    try {
        const response = await fetch(`${API_BASE_URL}/bot/set_commands`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            showToast('Başarılı', data.message, 'success');
        } else {
            const errorData = await response.json();
            showToast('Hata', errorData.message || 'Komutlar ayarlanamadı', 'error');
        }
    } catch (error) {
        showToast('Hata', 'Bağlantı hatası', 'error');
    } finally {
        loading.setCommands = false;
        updateBotStatusUI();
        updateButtonLoading('set-commands-btn', false, 'Ayarlanıyor...', 'Kısayolları Ekle');
    }
}

async function handleToggleServiceMessages(checked) {
    loading.toggleService = true;
    updateBotStatusUI();
    
    try {
        const response = await fetch(`${API_BASE_URL}/settings/delete_service_messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ value: checked }) // Changed from 'enabled' to 'value'
        });
        
        if (response.ok) {
            const data = await response.json();
            botStatus.deleteServiceMessages = checked;
            showToast('Başarılı', data.message, 'success');
            await fetchRecentActivities();
        } else {
            const errorData = await response.json();
            showToast('Hata', errorData.message || 'Ayar güncellenemedi', 'error');
            // Revert the toggle if failed
            const toggle = document.getElementById('delete-service-messages-toggle');
            if (toggle) toggle.checked = !checked;
        }
    } catch (error) {
        showToast('Hata', 'Bağlantı hatası', 'error');
        // Revert the toggle if failed
        const toggle = document.getElementById('delete-service-messages-toggle');
        if (toggle) toggle.checked = !checked;
    } finally {
        loading.toggleService = false;
        updateBotStatusUI();
    }
}

// Initialize the application
async function initializeApp() {
    await fetchBotStatus();
    await fetchRecentActivities();
    await fetchServiceMessagesSetting();

    // Buton event handler'larını ata
    const startBtn = document.getElementById('start-bot-btn');
    const stopBtn = document.getElementById('stop-bot-btn');
    const restartBtn = document.getElementById('restart-bot-btn');
    const saveTokenBtn = document.getElementById('save-token-btn');
    const setCommandsBtn = document.getElementById('set-commands-btn');
    const serviceToggle = document.getElementById('delete-service-messages-toggle');

    if (startBtn) startBtn.onclick = () => handleBotAction('start');
    if (stopBtn) stopBtn.onclick = () => handleBotAction('stop');
    if (restartBtn) restartBtn.onclick = () => handleBotAction('restart');
    if (saveTokenBtn) saveTokenBtn.onclick = handleSaveToken;
    if (setCommandsBtn) setCommandsBtn.onclick = handleSetCommands;
    if (serviceToggle) serviceToggle.onchange = (e) => handleToggleServiceMessages(e.target.checked);
}

document.addEventListener('DOMContentLoaded', initializeApp);

// Logları yükle
async function loadLogs() {
    const logsContainer = document.getElementById('logs-container');
    
    try {
        logsContainer.innerHTML = `
            <div class="logs-loading">
                <i class="fas fa-spinner"></i>
                Log kayıtları yükleniyor...
            </div>
        `;
        
        const response = await fetch('/api/logs?limit=50');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        if (!data.logs || data.logs.length === 0) {
            logsContainer.innerHTML = `
                <div class="logs-empty">
                    <i class="fas fa-chart-line"></i>
                    <p>Henüz log kaydı bulunmuyor</p>
                </div>
            `;
            return;
        }
        
        // Logları render et
        logsContainer.innerHTML = data.logs.map(log => `
            <div class="log-entry">
                <div class="log-icon">${log.icon}</div>
                <div class="log-content">
                    <div class="log-header">
                        <span class="log-timestamp">${log.timestamp}</span>
                        <span class="log-level ${log.level.toLowerCase()}">${log.level}</span>
                        ${log.module ? `<span class="log-module">${log.module}</span>` : ''}
                        ${log.function ? `<span class="log-function">${log.function}</span>` : ''}
                    </div>
                    <div class="log-message">${escapeHtml(log.message)}</div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Log yükleme hatası:', error);
        logsContainer.innerHTML = `
            <div class="logs-empty">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Log kayıtları yüklenemedi: ${error.message}</p>
            </div>
        `;
    }
}

// HTML escape fonksiyonu
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Logları yenile
function refreshLogs() {
    loadLogs();
}

// Otomatik yenilemeyi aç/kapat
function toggleAutoRefresh() {
    const toggleBtn = document.getElementById('auto-refresh-toggle');
    const icon = toggleBtn.querySelector('i');
    
    if (isAutoRefreshActive) {
        // Otomatik yenilemeyi durdur
        clearInterval(autoRefreshInterval);
        isAutoRefreshActive = false;
        toggleBtn.classList.remove('auto-refresh-active');
        icon.className = 'fas fa-play';
        toggleBtn.innerHTML = '<i class="fas fa-play"></i> Otomatik';
    } else {
        // Otomatik yenilemeyi başlat
        autoRefreshInterval = setInterval(loadLogs, 5000); // 5 saniyede bir
        isAutoRefreshActive = true;
        toggleBtn.classList.add('auto-refresh-active');
        icon.className = 'fas fa-pause';
        toggleBtn.innerHTML = '<i class="fas fa-pause"></i> Otomatik';
    }
}

// Sayfa yüklendiğinde logları yükle
document.addEventListener('DOMContentLoaded', function() {
    // Mevcut fonksiyonlar...
    // Logları yükle
    loadLogs();
    // Otomatik log yenilemeyi varsayılan olarak başlat
    if (!isAutoRefreshActive) {
        autoRefreshInterval = setInterval(loadLogs, 5000);
        isAutoRefreshActive = true;
    }
    // Sayfa görünür olduğunda logları yenile
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden && isAutoRefreshActive) {
            loadLogs();
        }
    });
});

function updateBotStatusBadge(isRunning) {
    const statusBadge = document.getElementById('bot-status-badge');
    if (statusBadge) {
        let dotClass = isRunning ? 'badge-dot badge-dot-success' : 'badge-dot badge-dot-error';
        let text = isRunning ? 'Çalışıyor' : 'Durduruldu';
        statusBadge.className = isRunning ? 'badge badge-success' : 'badge badge-error';
        statusBadge.innerHTML = `<span class="${dotClass}"></span>${text}`;
    }
}

// Token visibility toggle function
function toggleTokenVisibility() {
    const tokenInput = document.getElementById('bot-token-input');
    const visibilityIcon = document.getElementById('token-visibility-icon');
    
    if (!tokenInput || !visibilityIcon) return;
    
    isTokenVisible = !isTokenVisible;
    
    if (isTokenVisible) {
        tokenInput.type = 'text';
        visibilityIcon.className = 'fas fa-eye-slash';
        visibilityIcon.title = 'Token\'ı gizle';
    } else {
        tokenInput.type = 'password';
        visibilityIcon.className = 'fas fa-eye';
        visibilityIcon.title = 'Token\'ı göster';
    }
}
