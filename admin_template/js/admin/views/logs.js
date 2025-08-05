/*
 * SKYFORSKNING.NO PROSJEKTREGLER:
 * - Backend port: 8010 kun
 * - API: https://skyforskning.no/api/v1/ (FastAPI)
 * - Ingen demo/placeholder-data
 * - Bruk kun godkjente API-nøkler
 * - All frontend kommuniserer kun med FastAPI-server
 * - Spør alltid før endringer som bryter disse regler
 */

const logsView = {
    // API-endepunkter
    endpoints: {
        logs: 'admin/logs',
        logTypes: 'admin/logs/types'
    },
    
    // Paginering
    pagination: {
        page: 1,
        pageSize: 25,
        totalPages: 1,
        totalItems: 0
    },
    
    // Filtrering
    filters: {
        type: 'all',
        level: 'all',
        startDate: null,
        endDate: null,
        searchQuery: ''
    },
    
    // Generer loggvisnings-skjerm
    render: async function() {
        const container = document.createElement('div');
        container.className = 'logs-container';
        
        // Opprett header
        const header = document.createElement('div');
        header.className = 'page-header';
        header.innerHTML = `
            <h1>Systemlogger</h1>
            <div class="header-actions">
                <button id="refresh-logs-btn" class="btn primary">Oppdater</button>
                <button id="export-logs-btn" class="btn">Eksporter</button>
            </div>
        `;
        container.appendChild(header);
        
        // Opprett filtreringsseksjon
        const filterSection = document.createElement('div');
        filterSection.className = 'logs-filter-section';
        filterSection.innerHTML = `
            <div class="filter-row">
                <div class="filter-group">
                    <label for="log-type-filter">Loggtype</label>
                    <select id="log-type-filter">
                        <option value="all">Alle</option>
                        <!-- Logtyper vil bli lagt til dynamisk -->
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="log-level-filter">Loggnivå</label>
                    <select id="log-level-filter">
                        <option value="all">Alle</option>
                        <option value="debug">Debug</option>
                        <option value="info">Info</option>
                        <option value="warning">Warning</option>
                        <option value="error">Error</option>
                        <option value="critical">Critical</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="log-date-from">Fra dato</label>
                    <input type="date" id="log-date-from">
                </div>
                
                <div class="filter-group">
                    <label for="log-date-to">Til dato</label>
                    <input type="date" id="log-date-to">
                </div>
            </div>
            
            <div class="filter-row">
                <div class="filter-group search-group">
                    <input type="text" id="log-search" placeholder="Søk i logger...">
                    <button id="log-search-btn" class="btn">Søk</button>
                </div>
                
                <div class="filter-group">
                    <button id="clear-filters-btn" class="btn">Nullstill filtre</button>
                </div>
            </div>
        `;
        container.appendChild(filterSection);
        
        // Opprett loggtabell
        const tableContainer = document.createElement('div');
        tableContainer.className = 'table-container';
        tableContainer.innerHTML = `
            <table id="logs-table" class="data-table">
                <thead>
                    <tr>
                        <th>Tidspunkt</th>
                        <th>Type</th>
                        <th>Nivå</th>
                        <th>Melding</th>
                        <th>Kilde</th>
                        <th>Bruker</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colspan="6" class="loading-cell">Laster logger...</td>
                    </tr>
                </tbody>
            </table>
        `;
        container.appendChild(tableContainer);
        
        // Opprett paginering
        const paginationContainer = document.createElement('div');
        paginationContainer.className = 'pagination-container';
        paginationContainer.innerHTML = `
            <div class="pagination-info">
                Viser <span id="page-start">0</span>-<span id="page-end">0</span> av <span id="total-logs">0</span> logger
            </div>
            <div class="pagination-controls">
                <button id="prev-page-btn" class="btn pagination-btn" disabled>&laquo; Forrige</button>
                <span id="page-indicator">Side 1 av 1</span>
                <button id="next-page-btn" class="btn pagination-btn" disabled>Neste &raquo;</button>
            </div>
            <div class="pagination-size">
                <label for="page-size">Per side:</label>
                <select id="page-size">
                    <option value="25">25</option>
                    <option value="50">50</option>
                    <option value="100">100</option>
                    <option value="250">250</option>
                </select>
            </div>
        `;
        container.appendChild(paginationContainer);
        
        // Opprett loggdetaljer-modal (skjult ved start)
        const logModal = document.createElement('div');
        logModal.id = 'log-details-modal';
        logModal.className = 'modal';
        logModal.innerHTML = `
            <div class="modal-content log-modal-content">
                <div class="modal-header">
                    <h2>Loggdetaljer</h2>
                    <span class="close-modal">&times;</span>
                </div>
                <div class="modal-body log-details">
                    <div class="log-detail-row">
                        <div class="log-detail-label">Tidspunkt:</div>
                        <div id="log-detail-timestamp" class="log-detail-value"></div>
                    </div>
                    <div class="log-detail-row">
                        <div class="log-detail-label">Type:</div>
                        <div id="log-detail-type" class="log-detail-value"></div>
                    </div>
                    <div class="log-detail-row">
                        <div class="log-detail-label">Nivå:</div>
                        <div id="log-detail-level" class="log-detail-value"></div>
                    </div>
                    <div class="log-detail-row">
                        <div class="log-detail-label">Kilde:</div>
                        <div id="log-detail-source" class="log-detail-value"></div>
                    </div>
                    <div class="log-detail-row">
                        <div class="log-detail-label">Bruker:</div>
                        <div id="log-detail-user" class="log-detail-value"></div>
                    </div>
                    <div class="log-detail-row">
                        <div class="log-detail-label">Melding:</div>
                        <div id="log-detail-message" class="log-detail-value"></div>
                    </div>
                    <div class="log-detail-row full-width">
                        <div class="log-detail-label">Kontekst:</div>
                        <pre id="log-detail-context" class="log-detail-context"></pre>
                    </div>
                    <div class="log-detail-row full-width">
                        <div class="log-detail-label">Stack Trace:</div>
                        <pre id="log-detail-stack" class="log-detail-stack"></pre>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(logModal);
        
        return container;
    },
    
    // Initialiser loggvisning
    init: async function() {
        try {
            // Last inn loggtyper
            await this.loadLogTypes();
            
            // Last inn logger
            await this.loadLogs();
            
            // Sett opp event handlers
            this.setupEventHandlers();
        } catch (error) {
            console.error('Feil ved initialisering av loggvisning:', error);
            ui.showNotification('Kunne ikke laste logger: ' + error.message, 'error');
            
            const tbody = document.querySelector('#logs-table tbody');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="error-cell">Kunne ikke laste logger: ${error.message}</td>
                    </tr>
                `;
            }
        }
    },
    
    // Last inn loggtyper
    loadLogTypes: async function() {
        try {
            const logTypes = await api.get(this.endpoints.logTypes);
            
            // Fyll logtype-nedtrekksmeny
            const typeSelect = document.getElementById('log-type-filter');
            if (typeSelect && logTypes?.length > 0) {
                // Behold "Alle" alternativet og legg til loggtyper
                const firstOption = typeSelect.options[0];
                typeSelect.innerHTML = '';
                typeSelect.appendChild(firstOption);
                
                logTypes.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type.id;
                    option.textContent = type.name;
                    typeSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Feil ved lasting av loggtyper:', error);
            // Fortsett med standardverdier
        }
    },
    
    // Last inn logger
    loadLogs: async function() {
        try {
            ui.showLoading(true);
            
            // Bygg API-endepunkt med paginering og filtre
            let endpoint = `${this.endpoints.logs}?page=${this.pagination.page}&page_size=${this.pagination.pageSize}`;
            
            // Legg til filtre
            if (this.filters.type !== 'all') {
                endpoint += `&type=${this.filters.type}`;
            }
            
            if (this.filters.level !== 'all') {
                endpoint += `&level=${this.filters.level}`;
            }
            
            if (this.filters.startDate) {
                endpoint += `&start_date=${this.filters.startDate}`;
            }
            
            if (this.filters.endDate) {
                endpoint += `&end_date=${this.filters.endDate}`;
            }
            
            if (this.filters.searchQuery) {
                endpoint += `&q=${encodeURIComponent(this.filters.searchQuery)}`;
            }
            
            // Hent logger fra API
            const response = await api.get(endpoint);
            
            // Oppdater paginering
            if (response.pagination) {
                this.pagination = {
                    page: response.pagination.current_page,
                    pageSize: response.pagination.page_size,
                    totalPages: response.pagination.total_pages,
                    totalItems: response.pagination.total_items
                };
                
                this.updatePaginationUI();
            }
            
            // Oppdater loggtabell
            const tbody = document.querySelector('#logs-table tbody');
            if (!tbody) return;
            
            if (response.logs?.length > 0) {
                let html = '';
                
                response.logs.forEach(log => {
                    // Formater tidspunkt
                    const timestamp = new Date(log.timestamp);
                    const formattedTime = new Intl.DateTimeFormat('nb-NO', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                    }).format(timestamp);
                    
                    // Bestem nivåklasse
                    let levelClass = '';
                    switch (log.level.toLowerCase()) {
                        case 'debug':
                            levelClass = 'log-level-debug';
                            break;
                        case 'info':
                            levelClass = 'log-level-info';
                            break;
                        case 'warning':
                            levelClass = 'log-level-warning';
                            break;
                        case 'error':
                            levelClass = 'log-level-error';
                            break;
                        case 'critical':
                            levelClass = 'log-level-critical';
                            break;
                    }
                    
                    // Trunkér melding hvis den er for lang
                    const message = log.message.length > 100 
                        ? log.message.substring(0, 100) + '...' 
                        : log.message;
                    
                    html += `
                        <tr class="log-row" data-id="${log.id}">
                            <td>${formattedTime}</td>
                            <td>${log.type}</td>
                            <td><span class="log-level ${levelClass}">${log.level}</span></td>
                            <td class="log-message">${message}</td>
                            <td>${log.source || '-'}</td>
                            <td>${log.user || '-'}</td>
                        </tr>
                    `;
                });
                
                tbody.innerHTML = html;
            } else {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="no-results">Ingen logger funnet</td>
                    </tr>
                `;
            }
            
            ui.showLoading(false);
        } catch (error) {
            console.error('Feil ved lasting av logger:', error);
            
            const tbody = document.querySelector('#logs-table tbody');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="error-cell">Kunne ikke laste logger: ${error.message}</td>
                    </tr>
                `;
            }
            
            ui.showLoading(false);
        }
    },
    
    // Oppdater paginerings-UI
    updatePaginationUI: function() {
        // Oppdater side-indikator
        const pageIndicator = document.getElementById('page-indicator');
        if (pageIndicator) {
            pageIndicator.textContent = `Side ${this.pagination.page} av ${this.pagination.totalPages}`;
        }
        
        // Oppdater antall-indikatorer
        const totalLogs = document.getElementById('total-logs');
        if (totalLogs) {
            totalLogs.textContent = this.pagination.totalItems;
        }
        
        // Beregn startnummer og sluttnummer for gjeldende side
        const startItem = (this.pagination.page - 1) * this.pagination.pageSize + 1;
        const endItem = Math.min(startItem + this.pagination.pageSize - 1, this.pagination.totalItems);
        
        const pageStart = document.getElementById('page-start');
        const pageEnd = document.getElementById('page-end');
        
        if (pageStart) pageStart.textContent = startItem;
        if (pageEnd) pageEnd.textContent = endItem;
        
        // Aktiver/deaktiver navigasjonsknapper
        const prevBtn = document.getElementById('prev-page-btn');
        const nextBtn = document.getElementById('next-page-btn');
        
        if (prevBtn) prevBtn.disabled = this.pagination.page <= 1;
        if (nextBtn) nextBtn.disabled = this.pagination.page >= this.pagination.totalPages;
        
        // Sett riktig verdi for sideantall-velger
        const pageSizeSelect = document.getElementById('page-size');
        if (pageSizeSelect) {
            pageSizeSelect.value = this.pagination.pageSize;
        }
    },
    
    // Sett opp event handlers
    setupEventHandlers: function() {
        // Søk i logger
        const searchBtn = document.getElementById('log-search-btn');
        const searchInput = document.getElementById('log-search');
        
        if (searchBtn && searchInput) {
            searchBtn.addEventListener('click', () => {
                this.filters.searchQuery = searchInput.value;
                this.pagination.page = 1; // Gå til første side ved søk
                this.loadLogs();
            });
            
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.filters.searchQuery = searchInput.value;
                    this.pagination.page = 1;
                    this.loadLogs();
                }
            });
        }
        
        // Filter-endringer
        const typeFilter = document.getElementById('log-type-filter');
        const levelFilter = document.getElementById('log-level-filter');
        const dateFromFilter = document.getElementById('log-date-from');
        const dateToFilter = document.getElementById('log-date-to');
        
        const applyFilter = () => {
            this.filters.type = typeFilter.value;
            this.filters.level = levelFilter.value;
            this.filters.startDate = dateFromFilter.value || null;
            this.filters.endDate = dateToFilter.value || null;
            this.pagination.page = 1;
            this.loadLogs();
        };
        
        if (typeFilter) typeFilter.addEventListener('change', applyFilter);
        if (levelFilter) levelFilter.addEventListener('change', applyFilter);
        if (dateFromFilter) dateFromFilter.addEventListener('change', applyFilter);
        if (dateToFilter) dateToFilter.addEventListener('change', applyFilter);
        
        // Nullstill filtre
        const clearFiltersBtn = document.getElementById('clear-filters-btn');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                if (typeFilter) typeFilter.value = 'all';
                if (levelFilter) levelFilter.value = 'all';
                if (dateFromFilter) dateFromFilter.value = '';
                if (dateToFilter) dateToFilter.value = '';
                if (searchInput) searchInput.value = '';
                
                this.filters = {
                    type: 'all',
                    level: 'all',
                    startDate: null,
                    endDate: null,
                    searchQuery: ''
                };
                
                this.pagination.page = 1;
                this.loadLogs();
            });
        }
        
        // Paginering
        const prevPageBtn = document.getElementById('prev-page-btn');
        const nextPageBtn = document.getElementById('next-page-btn');
        const pageSizeSelect = document.getElementById('page-size');
        
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => {
                if (this.pagination.page > 1) {
                    this.pagination.page--;
                    this.loadLogs();
                }
            });
        }
        
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => {
                if (this.pagination.page < this.pagination.totalPages) {
                    this.pagination.page++;
                    this.loadLogs();
                }
            });
        }
        
        if (pageSizeSelect) {
            pageSizeSelect.addEventListener('change', () => {
                this.pagination.pageSize = parseInt(pageSizeSelect.value);
                this.pagination.page = 1;
                this.loadLogs();
            });
        }
        
        // Oppdater logger
        const refreshBtn = document.getElementById('refresh-logs-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadLogs();
            });
        }
        
        // Eksporter logger
        const exportBtn = document.getElementById('export-logs-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportLogs();
            });
        }
        
        // Vis loggdetaljer ved klikk på loggrad
        const logsTable = document.getElementById('logs-table');
        if (logsTable) {
            logsTable.addEventListener('click', (e) => {
                const row = e.target.closest('tr.log-row');
                if (row) {
                    const logId = row.dataset.id;
                    this.showLogDetails(logId);
                }
            });
        }
        
        // Lukk loggdetaljer-modal
        const closeModalBtn = document.querySelector('#log-details-modal .close-modal');
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', () => {
                this.closeLogDetailsModal();
            });
        }
        
        // Lukk modal hvis man klikker utenfor
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('log-details-modal');
            if (e.target === modal) {
                this.closeLogDetailsModal();
            }
        });
    },
    
    // Vis detaljer for en spesifikk logg
    showLogDetails: async function(logId) {
        try {
            ui.showLoading(true);
            
            // Hent loggdetaljer fra API
            const log = await api.get(`${this.endpoints.logs}/${logId}`);
            
            // Fyll inn modal med loggdata
            document.getElementById('log-detail-timestamp').textContent = new Date(log.timestamp).toLocaleString('nb-NO');
            document.getElementById('log-detail-type').textContent = log.type;
            document.getElementById('log-detail-level').textContent = log.level;
            document.getElementById('log-detail-source').textContent = log.source || '-';
            document.getElementById('log-detail-user').textContent = log.user || '-';
            document.getElementById('log-detail-message').textContent = log.message;
            
            // Håndter kontekst (JSON)
            const contextElem = document.getElementById('log-detail-context');
            if (log.context) {
                let formattedContext;
                try {
                    // Prøv å parse og formater JSON
                    const contextObj = typeof log.context === 'string' ? JSON.parse(log.context) : log.context;
                    formattedContext = JSON.stringify(contextObj, null, 2);
                } catch (e) {
                    // Hvis ikke gyldig JSON, vis som tekst
                    console.warn('Kunne ikke parse loggkontekst som JSON:', e);
                    formattedContext = log.context;
                }
                contextElem.textContent = formattedContext;
                contextElem.parentElement.style.display = 'block';
            } else {
                contextElem.parentElement.style.display = 'none';
            }
            
            // Håndter stack trace
            const stackElem = document.getElementById('log-detail-stack');
            if (log.stack_trace) {
                stackElem.textContent = log.stack_trace;
                stackElem.parentElement.style.display = 'block';
            } else {
                stackElem.parentElement.style.display = 'none';
            }
            
            // Vis modal
            document.getElementById('log-details-modal').style.display = 'block';
            
            ui.showLoading(false);
        } catch (error) {
            console.error('Feil ved henting av loggdetaljer:', error);
            ui.showNotification('Kunne ikke hente loggdetaljer: ' + error.message, 'error');
            ui.showLoading(false);
        }
    },
    
    // Lukk loggdetaljer-modal
    closeLogDetailsModal: function() {
        const modal = document.getElementById('log-details-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    },
    
    // Eksporter logger til CSV
    exportLogs: async function() {
        try {
            ui.showLoading(true);
            
            // Bygg API-endepunkt med gjeldende filtre men uten paginering
            let endpoint = `${this.endpoints.logs}/export?format=csv`;
            
            // Legg til filtre
            if (this.filters.type !== 'all') {
                endpoint += `&type=${this.filters.type}`;
            }
            
            if (this.filters.level !== 'all') {
                endpoint += `&level=${this.filters.level}`;
            }
            
            if (this.filters.startDate) {
                endpoint += `&start_date=${this.filters.startDate}`;
            }
            
            if (this.filters.endDate) {
                endpoint += `&end_date=${this.filters.endDate}`;
            }
            
            if (this.filters.searchQuery) {
                endpoint += `&q=${encodeURIComponent(this.filters.searchQuery)}`;
            }
            
            // Hent CSV-data
            const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${auth.getToken()}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            
            // Hent blob fra responsen
            const blob = await response.blob();
            
            // Opprett en midlertidig lenke for nedlasting
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            
            // Generer filnavn basert på dato
            const date = new Date();
            const formattedDate = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
            a.download = `skyforskning-logs-${formattedDate}.csv`;
            
            // Legg til i DOM, klikk, og fjern
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            ui.showLoading(false);
        } catch (error) {
            console.error('Feil ved eksport av logger:', error);
            ui.showNotification('Kunne ikke eksportere logger: ' + error.message, 'error');
            ui.showLoading(false);
        }
    }
};

// Export to global window object for UIManager
window.logsView = logsView;
