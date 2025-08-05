// Main entry point for Vue.js admin application
import { createApp } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
import { UIManager } from '/js/admin/ui-manager.js'
import { AuthService } from '/js/admin/auth.js'
import { ApiClient } from '/js/admin/api-client.js'
import { config } from '/js/admin/config.js'

// Initialize services
const apiClient = new ApiClient(config)
const authService = new AuthService(apiClient)
const uiManager = new UIManager(authService)

// Vue.js admin application
const AdminApp = {
  data() {
    return {
      isAuthenticated: false,
      currentView: 'login',
      user: null,
      loading: true
    }
  },
  
  async mounted() {
    // Check authentication status
    this.isAuthenticated = await authService.checkAuth()
    if (this.isAuthenticated) {
      this.user = authService.getCurrentUser()
      this.currentView = 'dashboard'
    }
    this.loading = false
  },
  
  methods: {
    async login(credentials) {
      try {
        const success = await authService.login(credentials)
        if (success) {
          this.isAuthenticated = true
          this.user = authService.getCurrentUser()
          this.currentView = 'dashboard'
        }
      } catch (error) {
        console.error('Login failed:', error)
      }
    },
    
    logout() {
      authService.logout()
      this.isAuthenticated = false
      this.user = null
      this.currentView = 'login'
    },
    
    switchView(viewName) {
      this.currentView = viewName
      uiManager.loadView(viewName)
    }
  },
  
  template: `
    <div class="admin-app">
      <div v-if="loading" class="loading">
        <p>Loading...</p>
      </div>
      
      <div v-else-if="!isAuthenticated" class="login-container">
        <h2>Admin Login</h2>
        <form @submit.prevent="login({username: $refs.username.value, password: $refs.password.value})">
          <div>
            <label>Username:</label>
            <input type="text" ref="username" required>
          </div>
          <div>
            <label>Password:</label>
            <input type="password" ref="password" required>
          </div>
          <button type="submit">Login</button>
        </form>
      </div>
      
      <div v-else class="admin-dashboard">
        <header class="admin-header">
          <h1>AI Ethics Admin</h1>
          <nav>
            <button @click="switchView('dashboard')">Dashboard</button>
            <button @click="switchView('llms')">LLMs</button>
            <button @click="switchView('news')">News</button>
            <button @click="switchView('settings')">Settings</button>
            <button @click="logout()">Logout</button>
          </nav>
        </header>
        
        <main class="admin-content">
          <div id="dynamic-view">
            <!-- Dynamic content loaded here -->
          </div>
        </main>
      </div>
    </div>
  `
}

// Mount the application
createApp(AdminApp).mount('#vue-admin-app')
