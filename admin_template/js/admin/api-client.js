/*
 * SKYFORSKNING.NO PROSJEKTREGLER:
 * - Backend port: 8010 kun
 * - API: https://skyforskning.no/api/v1/ (FastAPI)
 * - Ingen demo/placeholder-data
 * - Bruk kun godkjente API-nøkler
 * - All frontend kommuniserer kun med FastAPI-server
 * - Spør alltid før endringer som bryter disse regler
 */

class ApiClient {
    constructor(config = null) {
        // Use passed config or global CONFIG
        const apiConfig = config || (typeof CONFIG !== 'undefined' ? CONFIG : {
            API_BASE_URL: 'https://skyforskning.no/api/v1',
            API_PORT: '8010'
        });
        
        this.baseUrl = apiConfig.API_BASE_URL;
        this.port = apiConfig.API_PORT;
    }

    // Valider at URL følger jernregelsettet
    _validateUrl(endpoint) {
        if (!endpoint.startsWith('/')) {
            endpoint = '/' + endpoint;
        }
        
        const url = `${this.baseUrl}${endpoint}`;
        
        if (!url.startsWith(this.baseUrl)) {
            console.error('JERNREGEL BRUDD: API kall må gå til', this.baseUrl);
            throw new Error(`Ugyldig API URL: ${url}. Alle kall må gå til ${this.baseUrl}`);
        }
        
        return url;
    }
    
    // Valider at data ikke inneholder demo/placeholder data
    _validateData(data) {
        if (!data) return true;
        
        const dataStr = JSON.stringify(data).toLowerCase();
        const forbiddenTerms = ['demo', 'placeholder', 'test123', 'example', 'foo', 'bar', 'lorem ipsum'];
        
        for (const term of forbiddenTerms) {
            if (dataStr.includes(term)) {
                console.error(`JERNREGEL BRUDD: Data inneholder forbudt innhold: "${term}"`);
                throw new Error(`Data inneholder forbudt innhold: "${term}". Kun reelle data er tillatt.`);
            }
        }
        
        return true;
    }

    // Hent autentiseringstoken
    _getAuthHeader() {
        const token = localStorage.getItem('token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    // GET forespørsel
    async get(endpoint, params = {}) {
        const url = this._validateUrl(endpoint);
        
        // Legg til query params hvis de finnes
        const queryParams = new URLSearchParams();
        for (const key in params) {
            if (params.hasOwnProperty(key)) {
                queryParams.append(key, params[key]);
            }
        }
        
        const queryString = queryParams.toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        
        try {
            const response = await fetch(fullUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...this._getAuthHeader()
                }
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Request Failed:', error);
            throw error;
        }
    }

    // POST forespørsel
    async post(endpoint, data = {}) {
        const url = this._validateUrl(endpoint);
        this._validateData(data);
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this._getAuthHeader()
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            
            const responseData = await response.json();
            return responseData;
        } catch (error) {
            console.error('API Request Failed:', error);
            throw error;
        }
    }

    // PUT forespørsel
    async put(endpoint, data = {}) {
        const url = this._validateUrl(endpoint);
        this._validateData(data);
        
        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...this._getAuthHeader()
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            
            const responseData = await response.json();
            return responseData;
        } catch (error) {
            console.error('API Request Failed:', error);
            throw error;
        }
    }

    // DELETE forespørsel
    async delete(endpoint, data = {}) {
        const url = this._validateUrl(endpoint);
        this._validateData(data);
        
        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    ...this._getAuthHeader()
                },
                body: Object.keys(data).length ? JSON.stringify(data) : undefined
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            
            const responseData = await response.json();
            return responseData;
        } catch (error) {
            console.error('API Request Failed:', error);
            throw error;
        }
    }
}

// Export for ES modules
export { ApiClient };

// For backwards compatibility
const api = new ApiClient();
