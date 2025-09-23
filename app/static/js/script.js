// Základní funkce pro dashboard
class IoTDashboard {
    constructor() {
        this.socket = null;
        this.init();
    }

    init() {
        this.initNavigation();
        this.initModals();
        this.initWebSocket();
        this.loadPageContent();
    }

    // Navigace mezi stránkami
    initNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                navLinks.forEach(l => l.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    }

    // Modal windows
    initModals() {
        // Zavírání modalů
        document.querySelectorAll('.modal .close').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                closeBtn.closest('.modal').style.display = 'none';
            });
        });

        // Kliknutí mimo modal
        window.addEventListener('click', (e) => {
            document.querySelectorAll('.modal').forEach(modal => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });
    }

    // WebSocket connection
    initWebSocket() {
        // Bude implementováno později
        console.log('WebSocket inicializace...');
    }

    // Načítání obsahu stránky
    loadPageContent() {
        // Dynamické načítání podle aktuální stránky
        const currentPage = window.location.pathname.split('/').pop();
        this.updatePageTitle(currentPage);
    }

    updatePageTitle(page) {
        const titles = {
            'index.html': 'Přehled',
            'sensors.html': 'Senzory',
            'live-data.html': 'Živá data',
            'devices.html': 'Zařízení',
            'camera.html': 'Kamera',
            'history.html': 'Historie',
            'documentation.html': 'Dokumentace',
            'settings.html': 'Nastavení'
        };
        
        const title = titles[page] || 'IoT Dashboard';
        document.title = `IoT Dashboard - ${title}`;
    }
}

// Inicializace dashboardu při načtení stránky
document.addEventListener('DOMContentLoaded', () => {
    window.iotDashboard = new IoTDashboard();
});

// Utility funkce
function showNotification(message, type = 'info') {
    // Implementace notifikací
    console.log(`[${type}] ${message}`);
}

function formatDateTime(date) {
    return new Intl.DateTimeFormat('cs-CZ', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    }).format(date);
}