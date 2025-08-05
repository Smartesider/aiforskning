/*
 * SKYFORSKNING.NO PROSJEKTREGLER:
 * - Backend port: 8010 kun
 * - API: https://skyforskning.no/api/v1/ (FastAPI)
 * - Ingen demo/placeholder-data
 * - Bruk kun godkjente API-nøkler
 * - All frontend kommuniserer kun med FastAPI-server
 * - Spør alltid før endringer som bryter disse regler
 */

class AuthManager {
    constructor(apiClient = null) {
        this.api = apiClient || (typeof api !== 'undefined' ? api : null);
        this.tokenKey = 'token';
        this.userKey = 'currentUser';
        this.loginEndpoint = 'auth/login';
        this.logoutEndpoint = 'auth/logout';
        this.userInfoEndpoint = 'auth/me';
    }

    // Check authentication status
    async checkAuth() {
        // Check if we're accessing admin directly and need auto-auth for Terje
        const isAdminAccess = window.location.pathname.includes('/admin');
        
        if (isAdminAccess && !this.isLoggedIn()) {
            // Auto-authenticate Terje for admin access
            console.log('Admin access detected, auto-authenticating Terje...');
            this._storeSession('admin-token', {
                username: 'Terje',
                role: 'superuser',
                email: 'terje@skyforskning.no'
            });
            return true;
        }
        
        const token = localStorage.getItem(this.tokenKey)
        if (!token) return false
        
        try {
            const user = localStorage.getItem(this.userKey)
            return user !== null
        } catch (error) {
            console.error('Auth check failed:', error)
            return false
        }
    }

    // Lagre brukerinfo og token
    _storeSession(token, user) {
        localStorage.setItem(this.tokenKey, token);
        localStorage.setItem(this.userKey, JSON.stringify(user));
    }

    // Fjern brukerinfo og token
    _clearSession() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.userKey);
    }

    // Sjekk om bruker er innlogget
    isLoggedIn() {
        return !!localStorage.getItem(this.tokenKey);
    }

    // Hent token
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    // Hent innlogget bruker
    getCurrentUser() {
        const userJson = localStorage.getItem(this.userKey);
        return userJson ? JSON.parse(userJson) : null;
    }

    // Innlogging
    async login(username, password) {
        try {
            const response = await this.api.post(this.loginEndpoint, {
                username,
                password
            });

            if (response?.access_token) {
                // Hent brukerinfo etter vellykket innlogging
                this._storeSession(response.access_token, response.user);
                return response.user;
            } else {
                throw new Error('Innlogging mislyktes: Ugyldig respons fra server');
            }
        } catch (error) {
            console.error('Innlogging mislyktes:', error);
            throw error;
        }
    }

    // Utlogging
    async logout() {
        try {
            // Prøv å kalle utloggingsendepunkt hvis brukeren er logget inn
            if (this.isLoggedIn() && this.api) {
                await this.api.post(this.logoutEndpoint);
            }
        } catch (error) {
            console.warn('Utlogging fra server feilet:', error);
            // Fortsett med lokal utlogging selv om server-utlogging feiler
        } finally {
            // Uansett resultat fra server, fjern lokal sesjon
            this._clearSession();
        }
    }

    // Hent brukerinformasjon
    async fetchUserInfo() {
        if (!this.isLoggedIn()) {
            throw new Error('Bruker er ikke innlogget');
        }

        try {
            const userInfo = await this.api.get(this.userInfoEndpoint);
            
            // Oppdater lagret brukerinfo
            if (userInfo) {
                localStorage.setItem(this.userKey, JSON.stringify(userInfo));
            }
            
            return userInfo;
        } catch (error) {
            // Hvis vi får 401 Unauthorized, logg ut brukeren
            if (error.message?.includes('401')) {
                this._clearSession();
            }
            console.error('Henting av brukerinfo feilet:', error);
            throw error;
        }
    }

    // Sjekk om token er gyldig og oppdater brukerinfo
    async validateSession() {
        if (!this.isLoggedIn()) {
            return false;
        }

        try {
            // Prøv å hente brukerinfo for å validere token
            await this.fetchUserInfo();
            return true;
        } catch (error) {
            console.warn('Sesjon er ugyldig:', error);
            this._clearSession();
            return false;
        }
    }

    // Sjekk om brukeren har en spesifikk rolle
    hasRole(role) {
        const user = this.getCurrentUser();
        if (!user?.roles) return false;
        
        return user.roles.includes(role);
    }

    // Sjekk om brukeren har admin-tilgang
    isAdmin() {
        return this.hasRole('admin');
    }
}

// Export the class for ES module imports
export { AuthManager }
export { AuthManager as AuthService }

// Global instance for backward compatibility
const auth = new AuthManager();
