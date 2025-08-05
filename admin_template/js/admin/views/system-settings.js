/*
 * SKYFORSKNING.NO PROSJEKTREGLER:
 * - Backend port: 8010 kun
 * - API: https://skyforskning.no/api/v1/ (FastAPI)
 * - Ingen demo/placeholder-data
 * - Bruk kun godkjente API-nøkler
 * - All frontend kommuniserer kun med FastAPI-server
 * - Spør alltid før endringer som bryter disse regler
 */

const systemSettingsView = {
    // API-endepunkter
    endpoints: {
        settings: 'admin/settings',
        setting: 'admin/settings/:id',
        categories: 'admin/settings/categories'
    },
    
    // Kategorier av innstillinger
    categories: [],
    
    // Generer systeminnstillinger-skjerm
    render: async function() {
        const container = document.createElement('div');
        container.className = 'system-settings-container';
        
        // Opprett header
        const header = document.createElement('div');
        header.className = 'page-header';
        header.innerHTML = `
            <h1>Systeminnstillinger</h1>
            <div class="header-actions">
                <button id="save-all-settings-btn" class="btn primary">Lagre alle endringer</button>
            </div>
        `;
        container.appendChild(header);
        
        // Opprett innholdscontainer
        const contentContainer = document.createElement('div');
        contentContainer.className = 'settings-content';
        contentContainer.innerHTML = '<div class="loading-indicator">Laster innstillinger...</div>';
        container.appendChild(contentContainer);
        
        return container;
    },
    
    // Initialiser systeminnstillinger-visning
    init: async function() {
        try {
            // Hent innstillingskategorier
            await this.loadCategories();
            
            // Hent innstillinger
            await this.loadSettings();
            
            // Sett opp event handlers
            this.setupEventHandlers();
        } catch (error) {
            console.error('Feil ved initialisering av systeminnstillinger:', error);
            ui.showNotification('Kunne ikke laste systeminnstillinger: ' + error.message, 'error');
            
            // Vis feilmelding i innholdscontainer
            const contentContainer = document.querySelector('.settings-content');
            if (contentContainer) {
                contentContainer.innerHTML = `
                    <div class="error-message">
                        <h3>Feil ved lasting av innstillinger</h3>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        }
    },
    
    // Last inn innstillingskategorier
    loadCategories: async function() {
        try {
            // Hent kategorier fra API
            this.categories = await api.get(this.endpoints.categories);
        } catch (error) {
            console.error('Feil ved lasting av innstillingskategorier:', error);
            throw new Error('Kunne ikke laste innstillingskategorier: ' + error.message);
        }
    },
    
    // Last inn innstillinger
    loadSettings: async function() {
        try {
            // Hent innstillinger fra API
            const settings = await api.get(this.endpoints.settings);
            
            // Opprett innstillingsseksjoner
            const contentContainer = document.querySelector('.settings-content');
            if (!contentContainer) return;
            
            if (this.categories?.length > 0 && settings?.length > 0) {
                // Gruppere innstillinger etter kategori
                const settingsByCategory = {};
                
                // Initialiser tomme kategorier
                this.categories.forEach(category => {
                    settingsByCategory[category.id] = {
                        name: category.name,
                        description: category.description,
                        settings: []
                    };
                });
                
                // Sorter innstillinger inn i kategorier
                settings.forEach(setting => {
                    if (settingsByCategory[setting.category_id]) {
                        settingsByCategory[setting.category_id].settings.push(setting);
                    }
                });
                
                // Bygg HTML
                let html = '<form id="settings-form">';
                
                // Opprett tabs
                html += '<div class="settings-tabs">';
                this.categories.forEach((category, index) => {
                    html += `<button type="button" class="tab-btn ${index === 0 ? 'active' : ''}" 
                                      data-category="${category.id}">${category.name}</button>`;
                });
                html += '</div>';
                
                // Opprett innholdspaneler
                html += '<div class="settings-panels">';
                
                this.categories.forEach((category, index) => {
                    const categorySettings = settingsByCategory[category.id];
                    
                    html += `
                        <div class="settings-panel ${index === 0 ? 'active' : ''}" data-category="${category.id}">
                            <div class="panel-header">
                                <h2>${categorySettings.name}</h2>
                                <p>${categorySettings.description || ''}</p>
                            </div>
                            <div class="panel-content">
                    `;
                    
                    if (categorySettings.settings.length > 0) {
                        categorySettings.settings.forEach(setting => {
                            html += this.generateSettingField(setting);
                        });
                    } else {
                        html += '<p class="no-settings">Ingen innstillinger i denne kategorien</p>';
                    }
                    
                    html += `
                            </div>
                        </div>
                    `;
                });
                
                html += '</div></form>';
                
                contentContainer.innerHTML = html;
            } else {
                contentContainer.innerHTML = '<p class="no-settings">Ingen systeminnstillinger tilgjengelig</p>';
            }
        } catch (error) {
            console.error('Feil ved lasting av innstillinger:', error);
            throw new Error('Kunne ikke laste innstillinger: ' + error.message);
        }
    },
    
    // Generer HTML for en innstilling basert på type
    generateSettingField: function(setting) {
        const id = `setting-${setting.id}`;
        let fieldHtml = '';
        
        // Oprett felles label
        fieldHtml += `
            <div class="setting-item">
                <label for="${id}" class="setting-label">${setting.name}</label>
        `;
        
        // Generer input-felt basert på type
        switch (setting.type) {
            case 'text': {
                fieldHtml += `
                    <input type="text" id="${id}" name="${setting.key}" 
                           value="${setting.value || ''}" 
                           class="setting-input" 
                           data-id="${setting.id}" 
                           data-type="${setting.type}">
                `;
                break;
            }
                
            case 'number': {
                fieldHtml += `
                    <input type="number" id="${id}" name="${setting.key}" 
                           value="${setting.value || 0}" 
                           class="setting-input" 
                           data-id="${setting.id}" 
                           data-type="${setting.type}">
                `;
                break;
            }
                
            case 'boolean': {
                const checked = setting.value === 'true' || setting.value === true ? 'checked' : '';
                fieldHtml += `
                    <label class="toggle-switch">
                        <input type="checkbox" id="${id}" name="${setting.key}" 
                               ${checked} 
                               class="setting-input" 
                               data-id="${setting.id}" 
                               data-type="${setting.type}">
                        <span class="toggle-slider"></span>
                    </label>
                `;
                break;
            }
                
            case 'select': {
                fieldHtml += `
                    <select id="${id}" name="${setting.key}" 
                            class="setting-input" 
                            data-id="${setting.id}" 
                            data-type="${setting.type}">
                `;
                
                // Legg til options
                const options = setting.options ? JSON.parse(setting.options) : [];
                options.forEach(option => {
                    const selected = option.value === setting.value ? 'selected' : '';
                    fieldHtml += `<option value="${option.value}" ${selected}>${option.label}</option>`;
                });
                
                fieldHtml += '</select>';
                break;
            }
                
            case 'textarea': {
                fieldHtml += `
                    <textarea id="${id}" name="${setting.key}" 
                              class="setting-input" 
                              data-id="${setting.id}" 
                              data-type="${setting.type}" 
                              rows="4">${setting.value || ''}</textarea>
                `;
                break;
            }
                
            default: {
                // Legg til en klasse for å markere ukjent type
                fieldHtml += `
                    <input type="text" id="${id}" name="${setting.key}" 
                           value="${setting.value || ''}" 
                           class="setting-input unknown-type" 
                           data-id="${setting.id}" 
                           data-type="unknown">
                    <small class="type-warning">Ukjent innstillingstype: ${setting.type}</small>
                `;
            }
        }
        
        // Legg til beskrivelse hvis tilgjengelig
        if (setting.description) {
            fieldHtml += `<div class="setting-description">${setting.description}</div>`;
        }
        
        fieldHtml += '</div>';
        
        return fieldHtml;
    },
    
    // Sett opp event handlers
    setupEventHandlers: function() {
        // Tab-navigasjon
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const categoryId = btn.dataset.category;
                this.switchTab(categoryId);
            });
        });
        
        // Lagre alle innstillinger
        const saveAllBtn = document.getElementById('save-all-settings-btn');
        if (saveAllBtn) {
            saveAllBtn.addEventListener('click', () => {
                this.saveAllSettings();
            });
        }
    },
    
    // Bytt mellom tabs
    switchTab: function(categoryId) {
        // Sett aktiv tab-knapp
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.category === categoryId);
        });
        
        // Sett aktivt panel
        document.querySelectorAll('.settings-panel').forEach(panel => {
            panel.classList.toggle('active', panel.dataset.category === categoryId);
        });
    },
    
    // Samle inn alle innstillinger fra skjema
    collectSettings: function() {
        const settings = [];
        const inputs = document.querySelectorAll('.setting-input');
        
        inputs.forEach(input => {
            const id = input.dataset.id;
            const type = input.dataset.type;
            let value;
            
            // Hent verdi basert på inputtype
            if (type === 'boolean') {
                value = input.checked;
            } else {
                value = input.value;
            }
            
            settings.push({
                id,
                value
            });
        });
        
        return settings;
    },
    
    // Lagre alle innstillinger
    saveAllSettings: async function() {
        try {
            ui.showLoading(true);
            
            // Samle inn alle innstillinger
            const settings = this.collectSettings();
            
            // Send til API
            await api.post(this.endpoints.settings, { settings });
            
            ui.showNotification('Innstillinger lagret', 'success');
        } catch (error) {
            console.error('Feil ved lagring av innstillinger:', error);
            ui.showNotification('Kunne ikke lagre innstillinger: ' + error.message, 'error');
        } finally {
            ui.showLoading(false);
        }
    }
};

// Export to global window object for UIManager
window['system-settingsView'] = systemSettingsView;
