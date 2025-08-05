/*
 * SKYFORSKNING.NO PROSJEKTREGLER:
 * - Backend port: 8010 kun
 * - API: https://skyforskning.no/api/v1/ (FastAPI)
 * - Ingen demo/placeholder-data
 * - Bruk kun godkjente API-nøkler
 * - All frontend kommuniserer kun med FastAPI-server
 * - Spør alltid før endringer som bryter disse regler
 */

const CONFIG = {
    API_BASE_URL: 'https://skyforskning.no/api/v1',
    API_PORT: '8010',
    AUTH_ENDPOINTS: {
        LOGIN: '/auth/login',
        LOGOUT: '/auth/logout',
        CHECK: '/auth/check'
    },
    DASHBOARD_ENDPOINTS: {
        SYSTEM_STATUS: '/system/status',
        API_KEY_STATUS: '/system/api-keys/status',
        LAST_RUN: '/system/last-run',
        QUESTIONS_STATS: '/stats/questions',
        RUN_AI_CHECK: '/system/run-ai-check'
    },
    API_KEYS_ENDPOINTS: {
        LIST_PROVIDERS: '/api-keys/providers',
        LIST_KEYS: '/api-keys/list',
        ADD_KEY: '/api-keys/add',
        DELETE_KEY: '/api-keys/delete',
        UPDATE_KEY: '/api-keys/update',
        REFRESH_MODELS: '/api-keys/refresh-models'
    },
    LLM_ENDPOINTS: {
        LIST: '/llm/list',
        UPDATE: '/llm/update',
        TEST: '/llm/test',
        TEST_ALL: '/llm/test-all',
        DELETE: '/llm/delete'
    },
    NEWS_ENDPOINTS: {
        LIST: '/news/list',
        ADD: '/news/add',
        UPDATE: '/news/update',
        DELETE: '/news/delete'
    },
    LOG_ENDPOINTS: {
        GET: '/logs/get',
        CLEAR: '/logs/clear'
    },
    STATS_ENDPOINTS: {
        VISITORS: '/stats/visitors',
        LLM_USAGE: '/stats/llm-usage',
        COSTS: '/stats/costs'
    },
    SETTINGS_ENDPOINTS: {
        GET: '/settings/get',
        UPDATE: '/settings/update'
    }
};

// Export for ES modules
export { CONFIG as config };

// For backwards compatibility
if (typeof module !== 'undefined') {
    module.exports = CONFIG;
}
