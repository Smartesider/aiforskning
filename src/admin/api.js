// API client for admin Vue.js app
import axios from 'axios';

const API_BASE = '/api';

// Auth
export function login(username, password) {
  return axios.post(`${API_BASE}/v1/auth/login`, { username, password });
}
export function getAuthStatus() {
  return axios.get(`${API_BASE}/v1/auth/status`);
}
export function logout() {
  return axios.get('/logout');
}

// News CRUD
export function fetchNews() {
  return axios.get(`${API_BASE}/news`);
}
export function addNews(news) {
  return axios.post(`${API_BASE}/news`, news);
}
export function updateNews(id, news) {
  return axios.put(`${API_BASE}/news/${id}`, news);
}
export function deleteNews(id) {
  return axios.delete(`${API_BASE}/news/${id}`);
}

// LLM Models CRUD
export function fetchLLMs() {
  return axios.get(`${API_BASE}/llm-models`);
}
export function addLLM(model) {
  return axios.post(`${API_BASE}/llm-models`, model);
}
export function updateLLM(id, model) {
  return axios.put(`${API_BASE}/llm-models/${id}`, model);
}
export function deleteLLM(id) {
  return axios.delete(`${API_BASE}/llm-models/${id}`);
}
