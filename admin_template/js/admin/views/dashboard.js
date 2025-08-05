/*
 * SKYFORSKNING.NO PROSJEKTREGLER:
 * - Backend port: 8010 kun
 * - API: https://skyforskning.no/a    // Last inn statistikker
    loadStatistics: async function() {
        try {
            const response = await fetch('https://skyforskning.no/api/v1/system-status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const statistics = await response.json();1/ (FastAPI)
 * - Ingen demo/placeholder-data
 * - Bruk kun godkjente API-nøkler
 * - All frontend kommuniserer kun med FastAPI-server
 * - Spør alltid før endringer som bryter disse regler
 */

const dashboardView = {
    // Service references
    uiManager: null,
    authService: null,
    
    // Set service references
    setServices: function(uiManager, authService) {
        this.uiManager = uiManager;
        this.authService = authService;
    },
    
    // API-endepunkter
    endpoints: {
        statistics: 'dashboard/statistics',
        recentActivity: 'dashboard/activity',
        systemStatus: 'dashboard/system-status'
    },
    
    // Generer dashboard HTML
    render: async function() {
        const container = document.createElement('div');
        container.className = 'dashboard-container';
        
        // Legg til overskrift
        const header = document.createElement('div');
        header.className = 'dashboard-header';
        header.innerHTML = `
            <h1>Dashbord</h1>
            <p>Oversikt over systemet</p>
        `;
        container.appendChild(header);
        
        // Opprett grid-containere for widgets
        const topRow = document.createElement('div');
        topRow.className = 'dashboard-row';
        
        const bottomRow = document.createElement('div');
        bottomRow.className = 'dashboard-row';
        
        // Legg til ladningsindikator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'dashboard-loading';
        loadingIndicator.innerHTML = '<div class="spinner"></div><p>Laster dashbord...</p>';
        container.appendChild(loadingIndicator);
        
        // Opprett tomme widget-containere
        const statsWidget = document.createElement('div');
        statsWidget.className = 'dashboard-widget statistics-widget';
        statsWidget.innerHTML = '<h2>Statistikk</h2><div class="widget-content"></div>';
        
        const activityWidget = document.createElement('div');
        activityWidget.className = 'dashboard-widget activity-widget';
        activityWidget.innerHTML = '<h2>Nylig aktivitet</h2><div class="widget-content"></div>';
        
        const statusWidget = document.createElement('div');
        statusWidget.className = 'dashboard-widget status-widget';
        statusWidget.innerHTML = '<h2>Systemstatus</h2><div class="widget-content"></div>';
        
        // Legg til widgets i rader
        topRow.appendChild(statsWidget);
        topRow.appendChild(statusWidget);
        bottomRow.appendChild(activityWidget);
        
        // Legg til rader i containeren
        container.appendChild(topRow);
        container.appendChild(bottomRow);
        
        return container;
    },
    
    // Initialiser dashboard etter at DOM er lastet
    init: async function() {
        try {
            // Last inn data for alle widgets parallelt
            await Promise.all([
                this.loadStatistics(),
                this.loadRecentActivity(),
                this.loadSystemStatus()
            ]);
            
            // Skjul ladningsindikator
            const loadingIndicator = document.querySelector('.dashboard-loading');
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        } catch (error) {
            console.error('Feil ved initialisering av dashboard:', error);
            if (this.uiManager?.showNotification) {
                this.uiManager.showNotification('Kunne ikke laste dashbordet: ' + error.message, 'error');
            }
        }
    },
    
    // Last inn statistikk-data
    loadStatistics: async function() {
        try {
            const response = await fetch('https://skyforskning.no/api/v1/llm-models');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            const statistics = { models: data.models ? data.models.length : 0 };
            const widgetContent = document.querySelector('.statistics-widget .widget-content');
            
            if (!widgetContent) return;
            
            let html = '<div class="stats-grid">';
            
            // Sjekk om vi har data
            if (statistics && Object.keys(statistics).length > 0) {
                // Vis statistikk-data
                for (const [key, value] of Object.entries(statistics)) {
                    const formattedKey = key
                        .replace(/([A-Z])/g, ' $1') // Legg til mellomrom før store bokstaver
                        .replace(/_/g, ' ') // Erstatt understrek med mellomrom
                        .replace(/^\w/, c => c.toUpperCase()); // Stor forbokstav
                    
                    html += `
                        <div class="stat-item">
                            <div class="stat-value">${value}</div>
                            <div class="stat-label">${formattedKey}</div>
                        </div>
                    `;
                }
            } else {
                // Ingen data
                html += '<p>Ingen statistikk tilgjengelig</p>';
            }
            
            html += '</div>';
            widgetContent.innerHTML = html;
        } catch (error) {
            console.error('Feil ved lasting av statistikk:', error);
            const widgetContent = document.querySelector('.statistics-widget .widget-content');
            if (widgetContent) {
                widgetContent.innerHTML = '<div class="error-message">Kunne ikke laste statistikk</div>';
            }
        }
    },
    
    // Last inn nylig aktivitet
    loadRecentActivity: async function() {
        try {
            const response = await fetch('https://skyforskning.no/api/v1/news');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            const activities = data.news || [];
            const widgetContent = document.querySelector('.activity-widget .widget-content');
            
            if (!widgetContent) return;
            
            if (activities?.length > 0) {
                let html = '<ul class="activity-list">';
                
                for (const activity of activities) {
                    // Formater dato - use 'date' field from news API
                    let formattedDate = 'Unknown date';
                    try {
                        const date = new Date(activity.date);
                        if (!isNaN(date.getTime())) {
                            formattedDate = new Intl.DateTimeFormat('nb-NO', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            }).format(date);
                        }
                    } catch (dateError) {
                        console.warn('Invalid date format:', activity.date);
                    }
                    
                    html += `
                        <li class="activity-item">
                            <div class="activity-time">${formattedDate}</div>
                            <div class="activity-user">${activity.category || 'System'}</div>
                            <div class="activity-description">${activity.title}</div>
                        </li>
                    `;
                }
                
                html += '</ul>';
                widgetContent.innerHTML = html;
            } else {
                widgetContent.innerHTML = '<p>Ingen nylig aktivitet registrert</p>';
            }
        } catch (error) {
            console.error('Feil ved lasting av aktivitet:', error);
            const widgetContent = document.querySelector('.activity-widget .widget-content');
            if (widgetContent) {
                widgetContent.innerHTML = '<div class="error-message">Kunne ikke laste aktivitetslogg</div>';
            }
        }
    },
    
    // Last inn systemstatus
    loadSystemStatus: async function() {
        try {
            const response = await fetch('https://skyforskning.no/api/v1/system-status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const status = await response.json();
            const widgetContent = document.querySelector('.status-widget .widget-content');
            
            if (!widgetContent) return;
            
            if (status) {
                let html = '<div class="status-overview">';
                
                // Basic status display
                html += `
                    <div class="status-section">
                        <h3>System Status</h3>
                        <div class="status-indicator ${status.status === 'operational' ? 'success' : 'warning'}">
                            ${status.status || 'Unknown'}
                        </div>
                        <div class="status-details">
                            <p>Tests Today: ${status.testsToday || 0}</p>
                            <p>Last Update: ${status.lastUpdate ? new Date(status.lastUpdate).toLocaleString() : 'Unknown'}</p>
                        </div>
                    </div>
                `;
                
                html += '</div>';
                widgetContent.innerHTML = html;
            } else {
                widgetContent.innerHTML = '<p>Systemstatusdata ikke tilgjengelig</p>';
            }
        } catch (error) {
            console.error('Feil ved lasting av systemstatus:', error);
            const widgetContent = document.querySelector('.status-widget .widget-content');
            if (widgetContent) {
                widgetContent.innerHTML = '<div class="error-message">Kunne ikke laste systemstatus</div>';
            }
        }
    }
};

// Export to global window object for UIManager
window.dashboardView = dashboardView;
