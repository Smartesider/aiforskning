/*
 * SKYFORSKNING.NO PROSJEKTREGLER:
 * - Backend port: 8010 kun
 * - API: https://skyforskning.no/api/v1/ (FastAPI)
 * - Ingen demo/placeholder-data
 * - Bruk kun godkjente API-nøkler
 * - All frontend kommuniserer kun med FastAPI-server
 * - Spør alltid før endringer som bryter disse regler
 */

const loginView = {
    // Store references to services
    uiManager: null,
    authService: null,
    
    // Set service references
    setServices: function(uiManager, authService) {
        this.uiManager = uiManager;
        this.authService = authService;
    },
    
    // Generer login-skjema
    render: function() {
        const container = document.createElement('div');
        container.className = 'login-container';
        
        container.innerHTML = `
            <div class="login-form-wrapper">
                <div class="login-header">
                    <h1>SkyForskning Admin</h1>
                    <p>Logg inn for å få tilgang til administrasjonspanelet</p>
                </div>
                
                <form id="login-form" class="login-form">
                    <div class="form-group">
                        <label for="username">Brukernavn</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Passord</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn primary">Logg inn</button>
                    </div>
                    
                    <div id="login-error" class="login-error" style="display: none;"></div>
                </form>
                
                <div class="login-footer">
                    <p>SkyForskning.no &copy; ${new Date().getFullYear()}</p>
                </div>
            </div>
        `;
        
        return container;
    },
    
    // Initialiser login-skjema
    init: function() {
        const loginForm = document.getElementById('login-form');
        const loginError = document.getElementById('login-error');
        
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                // Skjul eventuelle tidligere feilmeldinger
                if (loginError) {
                    loginError.style.display = 'none';
                }
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                if (!username || !password) {
                    this.showError('Vennligst fyll inn både brukernavn og passord');
                    return;
                }
                
                try {
                    if (this.uiManager) {
                        this.uiManager.showLoading(true);
                    }
                    
                    // Use proper API call instead of auth.login
                    const response = await fetch('https://skyforskning.no/api/v1/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            username: username,
                            password: password
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`Login failed: ${response.status}`);
                    }
                    
                    const result = await response.json();
                    
                    if (result.authenticated) {
                        // Store user info
                        localStorage.setItem('currentUser', JSON.stringify({
                            username: result.username,
                            role: result.role,
                            email: result.email
                        }));
                        localStorage.setItem('token', 'authenticated');
                        
                        // Nullstill skjema
                        loginForm.reset();
                        
                        // Vis vellykket innlogging-melding
                        if (this.uiManager) {
                            this.uiManager.showNotification('Innlogging vellykket', 'success');
                            // Oppdater UI basert på innloggingsstatus
                            this.uiManager.updateAuthUI();
                            // Last dashboard
                            this.uiManager.loadView('dashboard');
                        }
                    } else {
                        throw new Error('Authentication failed');
                    }
                } catch (error) {
                    console.error('Innlogging feilet:', error);
                    
                    // Vis feilmelding
                    if (error.message.includes('401')) {
                        this.showError('Feil brukernavn eller passord');
                    } else {
                        this.showError('Innlogging feilet: ' + error.message);
                    }
                } finally {
                    if (this.uiManager) {
                        this.uiManager.showLoading(false);
                    }
                }
            });
        }
    },
    
    // Vis feilmelding
    showError: function(message) {
        const loginError = document.getElementById('login-error');
        if (loginError) {
            loginError.textContent = message;
            loginError.style.display = 'block';
        }
    }
};

// Export to global window object for UIManager
window.loginView = loginView;
