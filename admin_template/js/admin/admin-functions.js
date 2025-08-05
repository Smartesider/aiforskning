/*
### 🧠 AI ENFORCEMENT HEADER – OBLIGATORISK I ALLE FILER ###
🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
🧷 Kun MariaDB skal brukes – ingen andre drivere!
🛑 Ingen templating! HTML-servering skjer via statiske filer – kun API med JSON
🔒 AI-FILTER AKTIVERT – DU HAR INGEN KREATIV FRIHET
*/

// Admin Panel Functions for SkyForskning.no
// 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON

const API_BASE_URL = 'https://skyforskning.no/api/v1';

// ===========================================
// DASHBOARD FUNCTIONS
// ===========================================

async function loadDashboardData() {
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const [systemStatus, llmStatus] = await Promise.all([
            fetch(`${API_BASE_URL}/system-status`).then(r => r.json()),
            fetch(`${API_BASE_URL}/llm-status`).then(r => r.json())
        ]);

        // Update dashboard cards
        updateDashboardCards(systemStatus, llmStatus);
        updateLLMStatusGrid(llmStatus.models || []);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('error', 'Failed to load dashboard data');
    }
}

function updateDashboardCards(systemStatus, llmStatus) {
    // Update server status
    document.getElementById('server-status').textContent = systemStatus.status || 'Unknown';
    
    // Update active API keys count
    const activeKeys = (llmStatus.models || []).filter(m => m.status === 'active').length;
    document.getElementById('active-api-keys').textContent = activeKeys;
    
    // Update last run
    document.getElementById('last-run').textContent = systemStatus.lastUpdate ? 
        new Date(systemStatus.lastUpdate).toLocaleString() : 'Never';
    
    // Update questions today
    document.getElementById('questions-today').textContent = systemStatus.testsToday || 0;
}

function updateLLMStatusGrid(llmModels) {
    const grid = document.getElementById('llm-status-grid');
    if (!grid) return;

    grid.innerHTML = llmModels.map(model => `
        <div class="col-md-4 mb-3">
            <div class="card border-left-${model.status === 'active' ? 'success' : 'warning'} shadow h-100">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col">
                            <div class="text-xs font-weight-bold text-uppercase mb-1">${model.name}</div>
                            <div class="h6 mb-0 font-weight-bold text-gray-800">
                                Status: ${getStatusIcon(model.status)} ${model.status}
                            </div>
                            <div class="text-xs text-gray-600">
                                Questions: ${model.questionsAnswered || 0} | 
                                Bias Score: ${model.biasScore || 'N/A'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

async function runAICheck() {
    try {
        showAlert('info', 'Running AI system check...');
        
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/system/ai-check`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.issues && result.issues.length > 0) {
            displaySystemIssues(result.issues);
        } else {
            showAlert('success', 'AI Check completed - No issues detected');
        }
        
    } catch (error) {
        console.error('AI Check failed:', error);
        showAlert('error', 'AI Check failed: ' + error.message);
    }
}

function displaySystemIssues(issues) {
    const alertDiv = document.getElementById('system-issues');
    const issuesList = document.getElementById('issues-list');
    
    issuesList.innerHTML = issues.map(issue => `
        <div class="alert alert-warning">
            <strong>${issue.type}:</strong> ${issue.description}
            <br><small><strong>Recommendation:</strong> ${issue.recommendation}</small>
        </div>
    `).join('');
    
    alertDiv.style.display = 'block';
}

function refreshDashboard() {
    loadDashboardData();
    showAlert('success', 'Dashboard refreshed');
}

// ===========================================
// API KEYS MANAGEMENT FUNCTIONS
// ===========================================

async function loadApiKeys() {
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/api-keys/list`);
        const data = await response.json();
        
        displayApiKeysTable(data.keys || []);
        
    } catch (error) {
        console.error('Error loading API keys:', error);
        showAlert('error', 'Failed to load API keys');
    }
}

function displayApiKeysTable(apiKeys) {
    const tbody = document.getElementById('api-keys-table');
    if (!tbody) return;

    tbody.innerHTML = apiKeys.map(key => `
        <tr>
            <td>
                <div class="d-flex align-items-center">
                    <span class="me-2">${getProviderIcon(key.provider)}</span>
                    <div>
                        <div class="fw-bold">${key.provider}</div>
                        <div class="text-muted small">${key.name || 'Default Key'}</div>
                    </div>
                </div>
            </td>
            <td>
                <span class="badge ${key.status === 'active' ? 'bg-success' : 'bg-warning'}">
                    ${key.status === 'active' ? '✅ Active' : '⚠️ Testing'}
                </span>
            </td>
            <td>
                <div class="small">
                    ${(key.available_models || []).slice(0, 3).join(', ')}
                    ${key.available_models && key.available_models.length > 3 ? 
                        ` +${key.available_models.length - 3} more` : ''}
                </div>
            </td>
            <td class="small text-muted">
                ${key.last_tested ? new Date(key.last_tested).toLocaleString() : 'Never'}
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="testApiKey('${key.provider}')">
                        🧪 Test
                    </button>
                    <button class="btn btn-outline-secondary" onclick="refreshModels('${key.provider}')">
                        🔄 Refresh Models
                    </button>
                    <button class="btn btn-outline-warning" onclick="editApiKey('${key.provider}')">
                        ✏️ Edit
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteApiKey('${key.provider}')">
                        🗑️ Delete
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function showAddApiKeyModal() {
    const modal = new bootstrap.Modal(document.getElementById('addApiKeyModal'));
    modal.show();
}

async function saveApiKey() {
    const provider = document.getElementById('provider-select').value;
    const apiKey = document.getElementById('api-key-input').value;
    
    if (!provider || !apiKey) {
        showAlert('error', 'Please fill in all fields');
        return;
    }
    
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/api-keys/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider, api_key: apiKey })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('success', `API Key added successfully. Retrieved ${result.models_count || 0} models.`);
            bootstrap.Modal.getInstance(document.getElementById('addApiKeyModal')).hide();
            loadApiKeys(); // Refresh the table
        } else {
            showAlert('error', result.detail || 'Failed to add API key');
        }
        
    } catch (error) {
        console.error('Error saving API key:', error);
        showAlert('error', 'Failed to save API key: ' + error.message);
    }
}

async function testApiKey(provider) {
    try {
        showAlert('info', `Testing ${provider} API key...`);
        
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/api-keys/test/${provider}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('success', `${provider} API key test successful. Response time: ${result.response_time}ms`);
        } else {
            showAlert('error', `${provider} API key test failed: ${result.detail}`);
        }
        
        loadApiKeys(); // Refresh to show updated status
        
    } catch (error) {
        console.error('Error testing API key:', error);
        showAlert('error', `Failed to test ${provider} API key: ` + error.message);
    }
}

async function refreshModels(provider) {
    try {
        showAlert('info', `Refreshing models for ${provider}...`);
        
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/api-keys/refresh-models/${provider}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('success', `${provider} models refreshed. Found ${result.models_count} models.`);
            loadApiKeys(); // Refresh the table
        } else {
            showAlert('error', `Failed to refresh ${provider} models: ${result.detail}`);
        }
        
    } catch (error) {
        console.error('Error refreshing models:', error);
        showAlert('error', `Failed to refresh ${provider} models: ` + error.message);
    }
}

async function deleteApiKey(provider) {
    if (!confirm(`Are you sure you want to delete the API key for ${provider}?`)) {
        return;
    }
    
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/api-keys/delete/${provider}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('success', `${provider} API key deleted successfully`);
            loadApiKeys(); // Refresh the table
        } else {
            const result = await response.json();
            showAlert('error', `Failed to delete ${provider} API key: ${result.detail}`);
        }
        
    } catch (error) {
        console.error('Error deleting API key:', error);
        showAlert('error', `Failed to delete ${provider} API key: ` + error.message);
    }
}

// ===========================================
// LLM MANAGER FUNCTIONS
// ===========================================

async function loadLLMManager() {
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/llm/list`);
        const data = await response.json();
        
        displayLLMModels(data.models || []);
        
    } catch (error) {
        console.error('Error loading LLM models:', error);
        showAlert('error', 'Failed to load LLM models');
    }
}

function displayLLMModels(models) {
    const container = document.getElementById('llm-models-list');
    if (!container) return;

    // Group models by provider
    const groupedModels = models.reduce((groups, model) => {
        const provider = model.provider || 'Unknown';
        if (!groups[provider]) groups[provider] = [];
        groups[provider].push(model);
        return groups;
    }, {});

    container.innerHTML = Object.entries(groupedModels).map(([provider, providerModels]) => `
        <div class="card shadow mb-4">
            <div class="card-header py-3">
                <h6 class="m-0 font-weight-bold text-primary">
                    ${getProviderIcon(provider)} LLM Model: ${provider}
                </h6>
            </div>
            <div class="card-body">
                ${providerModels.map(model => `
                    <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                        <div class="d-flex align-items-center">
                            <span class="me-3">
                                ${model.status === 'active' ? 
                                    '<span class="badge bg-success">🟢 Active</span>' : 
                                    '<span class="badge bg-danger">🔴 Inactive</span>'}
                            </span>
                            <div>
                                <strong>${model.name}</strong>
                                <br><small class="text-muted">${model.id || model.name}</small>
                            </div>
                        </div>
                        <div class="btn-group btn-group-sm">
                            <button class="btn ${model.status === 'active' ? 'btn-warning' : 'btn-success'}" 
                                    onclick="toggleLLMStatus('${model.id}', '${model.status}')">
                                ${model.status === 'active' ? 'DEACTIVATE' : 'ACTIVATE'}
                            </button>
                            <button class="btn btn-primary" onclick="testLLM('${model.id}')">
                                TEST
                            </button>
                            <button class="btn btn-info" onclick="editLLM('${model.id}')">
                                EDIT
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

async function testAllLLMs() {
    try {
        showAlert('info', 'Starting comprehensive LLM testing...');
        
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/llm/test-all`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('success', `LLM testing completed. ${result.successful} passed, ${result.failed} failed.`);
            loadLLMManager(); // Refresh the display
        } else {
            showAlert('error', 'LLM testing failed: ' + result.detail);
        }
        
    } catch (error) {
        console.error('Error testing all LLMs:', error);
        showAlert('error', 'Failed to test all LLMs: ' + error.message);
    }
}

async function toggleLLMStatus(modelId, currentStatus) {
    const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
    
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/llm/update/${modelId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (response.ok) {
            showAlert('success', `Model ${modelId} ${newStatus === 'active' ? 'activated' : 'deactivated'}`);
            loadLLMManager(); // Refresh the display
        } else {
            const result = await response.json();
            showAlert('error', 'Failed to update model status: ' + result.detail);
        }
        
    } catch (error) {
        console.error('Error updating LLM status:', error);
        showAlert('error', 'Failed to update model status: ' + error.message);
    }
}

async function testLLM(modelId) {
    try {
        showAlert('info', `Testing ${modelId}...`);
        
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/llm/test/${modelId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('success', `${modelId} test successful. Response time: ${result.response_time}ms`);
        } else {
            showAlert('error', `${modelId} test failed: ${result.detail}`);
        }
        
    } catch (error) {
        console.error('Error testing LLM:', error);
        showAlert('error', `Failed to test ${modelId}: ` + error.message);
    }
}

// ===========================================
// NEWS MANAGEMENT FUNCTIONS
// ===========================================

async function loadNews() {
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/news`);
        const data = await response.json();
        
        displayNewsArticles(data.news || []);
        
    } catch (error) {
        console.error('Error loading news:', error);
        showAlert('error', 'Failed to load news articles');
    }
}

function displayNewsArticles(articles) {
    const container = document.getElementById('news-articles-list');
    if (!container) return;

    container.innerHTML = articles.map(article => `
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h5 class="card-title">${article.title}</h5>
                        <p class="card-text text-muted small">
                            By ${article.author || 'Terje W Dahl'} • 
                            ${article.date ? new Date(article.date).toLocaleDateString() : 'No date'}
                        </p>
                        <p class="card-text">${article.content.substring(0, 150)}...</p>
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="editNews(${article.id})">
                            ✏️ Edit
                        </button>
                        <button class="btn btn-outline-danger" onclick="deleteNews(${article.id})">
                            🗑️ Delete
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function showAddNewsModal() {
    const modal = new bootstrap.Modal(document.getElementById('addNewsModal'));
    modal.show();
}

async function saveNewsArticle() {
    const title = document.getElementById('news-title').value;
    const excerpt = document.getElementById('news-excerpt').value;
    const article = document.getElementById('news-article').value;
    const author = document.getElementById('news-author').value;
    
    if (!title || !article) {
        showAlert('error', 'Please fill in title and article content');
        return;
    }
    
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/news`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                excerpt,
                article,
                author: author || 'Terje W Dahl'
            })
        });
        
        if (response.ok) {
            showAlert('success', 'News article saved successfully');
            bootstrap.Modal.getInstance(document.getElementById('addNewsModal')).hide();
            loadNews(); // Refresh the list
            
            // Clear form
            document.getElementById('addNewsForm').reset();
        } else {
            const result = await response.json();
            showAlert('error', 'Failed to save article: ' + result.detail);
        }
        
    } catch (error) {
        console.error('Error saving news article:', error);
        showAlert('error', 'Failed to save article: ' + error.message);
    }
}

// ===========================================
// LOGS FUNCTIONS
// ===========================================

async function loadLogs() {
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/logs`);
        const data = await response.json();
        
        displayLogs(data.logs || []);
        
    } catch (error) {
        console.error('Error loading logs:', error);
        showAlert('error', 'Failed to load system logs');
    }
}

function displayLogs(logs) {
    const container = document.getElementById('logs-container');
    if (!container) return;

    container.innerHTML = logs.map(log => `
        <div class="log-entry mb-1" style="color: ${getLogColor(log.level)};">
            [${log.timestamp}] [${log.level.toUpperCase()}] ${log.message}
        </div>
    `).join('');
    
    // Auto-scroll to bottom
    container.scrollTop = container.scrollHeight;
}

async function clearLogs() {
    if (!confirm('Are you sure you want to delete all logs? This action cannot be undone.')) {
        return;
    }
    
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/logs/clear`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('success', 'Logs cleared successfully');
            loadLogs(); // Refresh to show empty logs
        } else {
            const result = await response.json();
            showAlert('error', 'Failed to clear logs: ' + result.detail);
        }
        
    } catch (error) {
        console.error('Error clearing logs:', error);
        showAlert('error', 'Failed to clear logs: ' + error.message);
    }
}

// ===========================================
// STATISTICS FUNCTIONS
// ===========================================

async function loadStatistics() {
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const [stats, redFlags, apiCosts] = await Promise.all([
            fetch(`${API_BASE_URL}/statistics`).then(r => r.json()),
            fetch(`${API_BASE_URL}/red-flags`).then(r => r.json()),
            fetch(`${API_BASE_URL}/api-costs`).then(r => r.json())
        ]);
        
        displayStatistics(stats, redFlags, apiCosts);
        
    } catch (error) {
        console.error('Error loading statistics:', error);
        showAlert('error', 'Failed to load statistics');
    }
}

function displayStatistics(stats, redFlags, apiCosts) {
    // Update main stats cards
    document.getElementById('total-visitors').textContent = stats.total_visitors || 0;
    document.getElementById('total-questions').textContent = stats.total_questions || 0;
    document.getElementById('total-answers').textContent = stats.total_answers || 0;
    document.getElementById('red-flags-count').textContent = (redFlags.flags || []).length;
    
    // Display visitor statistics
    const visitorStatsContainer = document.getElementById('visitor-stats');
    visitorStatsContainer.innerHTML = `
        <div class="row">
            <div class="col-6">
                <strong>Today:</strong> ${stats.visitors_today || 0}
            </div>
            <div class="col-6">
                <strong>This Week:</strong> ${stats.visitors_week || 0}
            </div>
            <div class="col-6">
                <strong>This Month:</strong> ${stats.visitors_month || 0}
            </div>
            <div class="col-6">
                <strong>Total:</strong> ${stats.total_visitors || 0}
            </div>
        </div>
        <hr>
        <div>
            <strong>Top Countries:</strong><br>
            ${(stats.top_countries || []).map(country => 
                `${country.name}: ${country.count} visits`
            ).join('<br>')}
        </div>
        <hr>
        <div>
            <strong>Top Referrers:</strong><br>
            ${(stats.top_referrers || []).map(ref => 
                `${ref.source}: ${ref.count} visits`
            ).join('<br>')}
        </div>
    `;
    
    // Display API costs
    const apiCostsContainer = document.getElementById('api-costs');
    apiCostsContainer.innerHTML = (apiCosts.providers || []).map(provider => `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <div>
                <strong>${provider.name}</strong>
                <br><small class="text-muted">${provider.requests || 0} requests</small>
            </div>
            <div class="text-end">
                <strong>$${provider.cost || '0.00'}</strong>
                <br><small class="text-muted">
                    ${provider.remaining_credit !== undefined ? 
                        `$${provider.remaining_credit} remaining` : 
                        'Credit info not available'}
                </small>
            </div>
        </div>
    `).join('');
    
    // Display red flags details
    const redFlagsContainer = document.getElementById('red-flags-details');
    redFlagsContainer.innerHTML = (redFlags.flags || []).map(flag => `
        <div class="alert alert-${flag.severity === 'high' ? 'danger' : 'warning'} mb-2">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <strong>${flag.title || flag.model}</strong>
                    <p class="mb-1">${flag.description}</p>
                    <small class="text-muted">
                        ${flag.timestamp ? new Date(flag.timestamp).toLocaleString() : 'No timestamp'}
                    </small>
                </div>
                <span class="badge bg-${flag.severity === 'high' ? 'danger' : 'warning'}">
                    ${flag.severity || 'medium'}
                </span>
            </div>
        </div>
    `).join('');
}

// ===========================================
// SETTINGS FUNCTIONS
// ===========================================

async function loadSettings() {
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/settings`);
        const settings = await response.json();
        
        // Populate settings form
        document.getElementById('testing-frequency').value = settings.testing_frequency || 'monthly';
        document.getElementById('auto-test-enabled').checked = settings.auto_test_enabled !== false;
        document.getElementById('bias-detection-enabled').checked = settings.bias_detection_enabled !== false;
        document.getElementById('red-flag-alerts-enabled').checked = settings.red_flag_alerts_enabled !== false;
        document.getElementById('auto-logging-enabled').checked = settings.auto_logging_enabled !== false;
        
    } catch (error) {
        console.error('Error loading settings:', error);
        showAlert('error', 'Failed to load settings');
    }
}

async function saveSettings() {
    const settings = {
        testing_frequency: document.getElementById('testing-frequency').value,
        auto_test_enabled: document.getElementById('auto-test-enabled').checked,
        bias_detection_enabled: document.getElementById('bias-detection-enabled').checked,
        red_flag_alerts_enabled: document.getElementById('red-flag-alerts-enabled').checked,
        auto_logging_enabled: document.getElementById('auto-logging-enabled').checked
    };
    
    try {
        // 🧷 Dette skal være en fetch til FastAPI på port 8010, som svarer med JSON
        const response = await fetch(`${API_BASE_URL}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            showAlert('success', 'Settings saved successfully');
        } else {
            const result = await response.json();
            showAlert('error', 'Failed to save settings: ' + result.detail);
        }
        
    } catch (error) {
        console.error('Error saving settings:', error);
        showAlert('error', 'Failed to save settings: ' + error.message);
    }
}

// ===========================================
// UTILITY FUNCTIONS
// ===========================================

function getStatusIcon(status) {
    switch(status) {
        case 'active': return '🟢';
        case 'inactive': return '🔴';
        case 'testing': return '🟡';
        default: return '⚪';
    }
}

function getProviderIcon(provider) {
    const icons = {
        'OpenAI': '🤖',
        'Anthropic': '🧠',
        'Google': '🌐',
        'xAI': '✨',
        'Mistral': '🌪️',
        'DeepSeek': '🔍',
        'Cohere': '💬',
        'Replicate': '🔄',
        'Together': '🤝',
        'Perplexity': '❓',
        'Hugging Face': '🤗',
        'Stability': '🎨',
        'Claude': '🧠',
        'Meta': '📘',
        'AI21': '🚀'
    };
    return icons[provider] || '💼';
}

function getLogColor(level) {
    const colors = {
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#0dcaf0',
        'debug': '#6c757d'
    };
    return colors[level?.toLowerCase()] || '#6c757d';
}

function showAlert(type, message) {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// TWD!
