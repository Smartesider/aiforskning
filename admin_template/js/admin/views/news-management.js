/*
 * SKYFORSKNING.NO PROSJEKTREGLER:
 * - Backend port: 8010 kun
 * - API: https://skyforskning.no/api/v1/ (FastAPI)
 * - Ingen demo/placeholder-data
 * - Bruk kun godkjente API-nøkler
 * - All frontend kommuniserer kun med FastAPI-server
 * - Spør alltid før endringer som bryter disse regler
 */

const newsManagementView = {
    render: function() {
        const container = document.createElement('div');
        container.className = 'news-management-container';
        
        container.innerHTML = `
            <div class="page-header">
                <h1>News Management</h1>
                <p>Create and manage news articles</p>
            </div>
            
            <div class="content-grid">
                <div class="card">
                    <div class="card-header">
                        <h3>Recent Articles</h3>
                    </div>
                    <div class="card-body" id="recent-articles">
                        <div class="loading">Loading articles...</div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3>Create New Article</h3>
                    </div>
                    <div class="card-body">
                        <form id="create-article-form">
                            <div class="form-group">
                                <label for="article-title">Title</label>
                                <input type="text" id="article-title" name="title" required>
                            </div>
                            <div class="form-group">
                                <label for="article-excerpt">Excerpt</label>
                                <textarea id="article-excerpt" name="excerpt" rows="3" required></textarea>
                            </div>
                            <div class="form-group">
                                <label for="article-content">Content</label>
                                <textarea id="article-content" name="article" rows="8" required></textarea>
                            </div>
                            <div class="form-group">
                                <label for="article-author">Author</label>
                                <input type="text" id="article-author" name="author" required>
                            </div>
                            <div class="form-group">
                                <label for="article-email">Email</label>
                                <input type="email" id="article-email" name="email" required>
                            </div>
                            <div class="form-group">
                                <label for="article-link">Link (optional)</label>
                                <input type="url" id="article-link" name="link">
                            </div>
                            <button type="submit" class="btn primary">Create Article</button>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        return container;
    },
    
    init: function() {
        this.loadRecentArticles();
        this.initFormHandlers();
    },
    
    async loadRecentArticles() {
        try {
            const response = await fetch('https://skyforskning.no/api/v1/news');
            const data = await response.json();
            
            const container = document.getElementById('recent-articles');
            if (data.news && data.news.length > 0) {
                container.innerHTML = data.news.map(article => `
                    <div class="article-item">
                        <div class="article-info">
                            <h4>${article.title}</h4>
                            <p>${article.content.substring(0, 100)}...</p>
                            <small>Published: ${new Date(article.date).toLocaleDateString()}</small>
                            <span class="category">${article.category || 'General'}</span>
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<p>No articles found</p>';
            }
        } catch (error) {
            console.error('Error loading articles:', error);
            document.getElementById('recent-articles').innerHTML = '<p class="error">Failed to load articles</p>';
        }
    },
    
    initFormHandlers() {
        const form = document.getElementById('create-article-form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                const articleData = {
                    title: formData.get('title'),
                    excerpt: formData.get('excerpt'),
                    article: formData.get('article'),
                    author: formData.get('author'),
                    email: formData.get('email'),
                    link: formData.get('link') || null
                };
                
                try {
                    const response = await fetch('https://skyforskning.no/api/v1/news', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(articleData)
                    });
                    
                    if (response.ok) {
                        form.reset();
                        this.loadRecentArticles();
                        // Show success notification if available
                        if (window.ui?.showNotification) {
                            window.ui.showNotification('Article created successfully', 'success');
                        }
                    } else {
                        throw new Error('Failed to create article');
                    }
                } catch (error) {
                    console.error('Error creating article:', error);
                    if (window.ui?.showNotification) {
                        window.ui.showNotification('Failed to create article: ' + error.message, 'error');
                    }
                }
            });
        }
    }
};

// Export to global window object for UIManager
window.newsView = newsManagementView;
