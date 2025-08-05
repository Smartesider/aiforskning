/*
 * SKYFORSKNING.NO PROSJEKTREGLER:
 * - Backend port: 8010 kun
 * - API: https://skyforskning.no/api/v1/ (FastAPI)
 * - Ingen demo/placeholder-data
 * - Bruk kun godkjente API-nøkler
 * - All frontend kommuniserer kun med FastAPI-server
 * - Spør alltid før endringer som bryter disse regler
 */

const llmManagementView = {
    render: function() {
        const container = document.createElement('div');
        container.className = 'llm-management-container';
        
        container.innerHTML = `
            <div class="page-header">
                <h1>LLM Management</h1>
                <p>Manage AI language models and API configurations</p>
            </div>
            
            <div class="content-grid">
                <div class="card">
                    <div class="card-header">
                        <h3>Active Models</h3>
                    </div>
                    <div class="card-body" id="active-models">
                        <div class="loading">Loading models...</div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3>Model Status</h3>
                    </div>
                    <div class="card-body" id="model-status">
                        <div class="loading">Loading status...</div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3>Add New Model</h3>
                    </div>
                    <div class="card-body">
                        <form id="add-model-form">
                            <div class="form-group">
                                <label for="provider">Provider</label>
                                <select id="provider" name="provider" required>
                                    <option value="">Select Provider</option>
                                    <option value="openai">OpenAI</option>
                                    <option value="anthropic">Anthropic</option>
                                    <option value="google">Google</option>
                                    <option value="mistral">Mistral</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="model-name">Model Name</label>
                                <input type="text" id="model-name" name="model-name" required>
                            </div>
                            <div class="form-group">
                                <label for="api-key">API Key</label>
                                <input type="password" id="api-key" name="api-key" required>
                            </div>
                            <button type="submit" class="btn primary">Add Model</button>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        return container;
    },
    
    init: function() {
        this.loadActiveModels();
        this.loadModelStatus();
        this.initFormHandlers();
    },
    
    async loadActiveModels() {
        try {
            const response = await fetch('https://skyforskning.no/api/v1/llm-models');
            const data = await response.json();
            
            const container = document.getElementById('active-models');
            if (data.models && data.models.length > 0) {
                container.innerHTML = data.models.map(model => `
                    <div class="model-item">
                        <div class="model-info">
                            <h4>${model.name}</h4>
                            <p>Provider: ${model.provider}</p>
                            <span class="status ${model.status}">${model.status}</span>
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<p>No models configured</p>';
            }
        } catch (error) {
            console.error('Error loading models:', error);
            document.getElementById('active-models').innerHTML = '<p class="error">Failed to load models</p>';
        }
    },
    
    async loadModelStatus() {
        try {
            const response = await fetch('https://skyforskning.no/api/v1/llm-status');
            const data = await response.json();
            
            const container = document.getElementById('model-status');
            container.innerHTML = `
                <div class="status-grid">
                    <div class="status-item">
                        <h4>Active Models</h4>
                        <span class="value">${data.activeModels || 0}</span>
                    </div>
                    <div class="status-item">
                        <h4>Tests Today</h4>
                        <span class="value">${data.testsToday || 0}</span>
                    </div>
                    <div class="status-item">
                        <h4>Last Update</h4>
                        <span class="value">${new Date(data.lastUpdate).toLocaleString()}</span>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error loading status:', error);
            document.getElementById('model-status').innerHTML = '<p class="error">Failed to load status</p>';
        }
    },
    
    initFormHandlers() {
        const form = document.getElementById('add-model-form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                const modelData = {
                    provider: formData.get('provider'),
                    name: formData.get('model-name'),
                    api_key: formData.get('api-key')
                };
                
                try {
                    const response = await fetch('https://skyforskning.no/api/v1/add-llm', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(modelData)
                    });
                    
                    if (response.ok) {
                        form.reset();
                        this.loadActiveModels();
                        // Show success notification if available
                        if (window.ui && window.ui.showNotification) {
                            window.ui.showNotification('Model added successfully', 'success');
                        }
                    } else {
                        throw new Error('Failed to add model');
                    }
                } catch (error) {
                    console.error('Error adding model:', error);
                    if (window.ui && window.ui.showNotification) {
                        window.ui.showNotification('Failed to add model: ' + error.message, 'error');
                    }
                }
            });
        }
    }
};

// Export to global window object for UIManager
window.llmView = llmManagementView;
