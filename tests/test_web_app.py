import os
import pytest
from flask import Flask
from src.web_app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = False
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# --- Helper for admin auth (mock or token) ---
def admin_headers():
    # Adjust as needed for your auth system
    return {'Authorization': 'Bearer test_admin_token'}

# --- News CRUD ---
def test_news_crud(client):
    # Create news (admin)
    resp = client.post('/api/news', json={
        'title': 'Test News', 'content': 'Test Content', 'category': 'General', 'visible': True
    }, headers=admin_headers())
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success']

    # Get news (public)
    resp = client.get('/api/news')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'news' in data

# --- LLM CRUD ---
def test_llm_crud(client):
    # Create LLM (admin)
    resp = client.post('/api/llm-models', json={
        'name': 'Test LLM', 'provider': 'openai', 'status': 'active'
    }, headers=admin_headers())
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success']

# --- API Key Management ---
def test_api_key_management(client):
    # Save API key (admin)
    resp = client.post('/api/admin/api-keys-config', json={
        'provider': 'openai', 'api_key': 'sk-test'
    }, headers=admin_headers())
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'message' in data

# --- Log Endpoints (admin) ---
def test_logs_admin(client):
    resp = client.get('/api/logs', headers=admin_headers())
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'logs' in data

# --- Public Analytics Endpoints ---
def test_public_endpoints(client):
    for url in ['/api/chart-data', '/api/stats', '/api/news']:
        resp = client.get(url)
        assert resp.status_code == 200

# --- Auth Required ---
def test_admin_required(client):
    # Should fail without admin headers
    resp = client.post('/api/news', json={
        'title': 'No Auth', 'content': 'No Auth', 'category': 'General', 'visible': True
    })
    assert resp.status_code in (401, 403)

# --- Error Handling ---
def test_news_missing_fields(client):
    resp = client.post('/api/news', json={'title': ''}, headers=admin_headers())
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'error' in data
