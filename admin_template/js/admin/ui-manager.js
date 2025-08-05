/*
 * SKYFORSKNING.NO PROSJEKTREGLER:
 * - Backend port: 8010 kun
 * - API: https://skyforskning.no/api/v1/ (FastAPI)
 * - Ingen demo/placeholder-data
 * - Bruk kun godkjente API-nøkler
 * - All frontend kommuniserer kun med FastAPI-server
 * - Spør alltid før endringer som bryter disse regler
 */

export class UIManager {
    constructor(authService = null) {
        this.authService = authService
        this.currentView = 'dashboard'
        this.views = {
            dashboard: 'dashboard',
            llm: 'llm-management', 
            news: 'news-management',
            users: 'user-management',
            logs: 'logs',
            login: 'login'
        }
        
        // Define required selectors and IDs
        this.sidebarItemsSelector = '.sidebar a[data-view]'
        this.loadingOverlayId = 'loading-overlay'
        this.notificationId = 'notification-area'
        this.viewContainerId = 'main-content'
        this.notificationTimeout = 5000
        
        this._initEventListeners()
    }
    
    // Initialiser event listeners
    _initEventListeners() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this._setupEventHandlers());
        } else {
            // DOM is already ready
            this._setupEventHandlers();
        }
    }
    
    _setupEventHandlers() {
        // Legg til click handlers på sidebar menyelementer
        document.querySelectorAll(this.sidebarItemsSelector).forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = link.getAttribute('data-view');
                if (view) {
                    this.loadView(view);
                }
            });
        });
        
        // Legg til event listener for login/logout knapper
        const loginButton = document.getElementById('login-button');
        const logoutButton = document.getElementById('logout-button');
        
        if (loginButton) {
            loginButton.addEventListener('click', () => {
                this.showLoginForm();
            });
        }
        
        if (logoutButton) {
            logoutButton.addEventListener('click', () => {
                this.handleLogout();
            });
        }
        
        // Sjekk om brukeren er innlogget og oppdater UI
        this.updateAuthUI();
        
        // Last standard view basert på login-status
        this._loadDefaultView();
    }
    
    // Last standardvisning basert på innloggingsstatus
    _loadDefaultView() {
        if (this.authService && this.authService.isLoggedIn()) {
            // Bruker er innlogget - last dashboard
            this.loadView('dashboard');
        } else {
            // Bruker er ikke innlogget - vis login-form
            this.showLoginForm();
        }
    }
    
    // Vis/skjul loading overlay
    showLoading(show = true) {
        const overlay = document.getElementById(this.loadingOverlayId);
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }
    
    // Vis melding til brukeren
    showNotification(message, type = 'info') {
        const notificationArea = document.getElementById(this.notificationId);
        if (!notificationArea) return;
        
        // Opprett melding-element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Legg til i DOM
        notificationArea.appendChild(notification);
        
        // Fjern etter timeout
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                notificationArea.removeChild(notification);
            }, 300);
        }, this.notificationTimeout);
    }
    
    // Last inn en spesifikk visning
    async loadView(viewName) {
        if (this.activeView === viewName) return;
        
        try {
            this.showLoading(true);
            
            // Sjekk om bruker har tilgang til denne visningen
            if (!this._checkViewAccess(viewName)) {
                this.showNotification('Du har ikke tilgang til denne visningen', 'error');
                return;
            }
            
            const viewContainer = document.getElementById(this.viewContainerId);
            if (!viewContainer) {
                console.error('Kunne ikke finne hovedinnholdscontainer');
                return;
            }
            
            // Hent view-modul
            const viewModule = await this._loadViewModule(viewName);
            if (!viewModule) {
                this.showNotification(`Kunne ikke laste visning: ${viewName}`, 'error');
                return;
            }
            
            // Marker aktiv menylenke
            this._updateActiveMenuItem(viewName);
            
            // Oppdater innhold
            viewContainer.innerHTML = '';
            viewContainer.appendChild(await viewModule.render());
            
            // Pass service references to view if it supports it
            if (typeof viewModule.setServices === 'function') {
                viewModule.setServices(this, this.authService);
            }
            
            // Initialiser view etter at DOM er oppdatert
            if (typeof viewModule.init === 'function') {
                viewModule.init();
            }
            
            this.activeView = viewName;
        } catch (error) {
            console.error(`Feil ved lasting av visning '${viewName}':`, error);
            this.showNotification(`Feil ved lasting av visning: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    // Last view-modul dynamisk
    async _loadViewModule(viewName) {
        try {
            // Map view names to actual file names
            const fileName = this.views[viewName] || viewName;
            const modulePath = `/js/admin/views/${fileName}.js`;
            
            // Sjekk om modulen allerede er lastet
            if (window[viewName + 'View']) {
                return window[viewName + 'View'];
            }
            
            // Laste inn script dynamisk
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = modulePath;
                script.onload = () => {
                    // Modulen bør eksportere seg selv til window[viewName + 'View']
                    if (window[viewName + 'View']) {
                        resolve(window[viewName + 'View']);
                    } else {
                        reject(new Error(`Visning ${viewName} eksporterte ikke seg selv korrekt`));
                    }
                };
                script.onerror = () => reject(new Error(`Kunne ikke laste ${modulePath}`));
                document.head.appendChild(script);
            });
        } catch (error) {
            console.error(`Feil ved lasting av visning-modul '${viewName}':`, error);
            throw error;
        }
    }
    
    // Sjekk om brukeren har tilgang til en visning
    _checkViewAccess(viewName) {
        // Sjekk om brukeren er innlogget
        if (!this.authService?.isLoggedIn()) {
            // Tillat kun login-visning for ikke-innloggede brukere
            return viewName === 'login';
        }
        
        // Sjekk rollebasert tilgang
        const user = this.authService.getCurrentUser();
        
        // Visninger som krever admin-rolle
        const adminViews = ['user-management', 'system-settings', 'logs'];
        
        // Returner false hvis visningen krever admin og brukeren ikke er admin
        const isAdmin = user?.role === 'admin' || user?.role === 'superuser';
        return !(adminViews.includes(viewName) && !isAdmin);
    }
    
    // Marker aktiv menylenke i sidebaren
    _updateActiveMenuItem(viewName) {
        document.querySelectorAll(this.sidebarItemsSelector).forEach(link => {
            const linkView = link.getAttribute('data-view');
            if (linkView === viewName) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }
    
    // Vis login-skjema
    showLoginForm() {
        this.loadView('login');
    }
    
    // Håndter utlogging
    async handleLogout() {
        try {
            this.showLoading(true);
            if (this.authService?.logout) {
                await this.authService.logout();
            }
            this.showNotification('Du er nå logget ut', 'success');
            this.updateAuthUI();
            this.showLoginForm();
        } catch (error) {
            console.error('Feil ved utlogging:', error);
            this.showNotification('Feil ved utlogging: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    // Oppdater UI basert på innloggingsstatus
    updateAuthUI() {
        if (!this.authService) return
        
        const isLoggedIn = this.authService.isLoggedIn();
        const loginButton = document.getElementById('login-button');
        const logoutButton = document.getElementById('logout-button');
        const userDisplay = document.getElementById('user-display');
        const sidebar = document.querySelector('.sidebar');
        
        // Vis/skjul login/logout knapper
        if (loginButton) loginButton.style.display = isLoggedIn ? 'none' : 'block';
        if (logoutButton) logoutButton.style.display = isLoggedIn ? 'block' : 'none';
        
        // Vis/skjul sidebar
        if (sidebar) sidebar.style.display = isLoggedIn ? 'block' : 'none';
        
        // Vis brukerinfo hvis innlogget
        if (userDisplay && isLoggedIn) {
            const currentUser = this.authService.getCurrentUser();
            userDisplay.textContent = currentUser?.name || currentUser?.username || 'Innlogget bruker';
            userDisplay.style.display = 'block';
        } else if (userDisplay) {
            userDisplay.style.display = 'none';
        }
    }
}

// For backwards compatibility - but don't export duplicate
if (typeof window !== 'undefined') {
    window.UIManager = UIManager;
}
