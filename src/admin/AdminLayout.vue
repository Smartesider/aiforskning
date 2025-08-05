<template>
  <div class="admin-layout">
    <nav>
      <router-link to="/admin/news">News Management</router-link> |
      <router-link to="/admin/llm-models">LLM Models</router-link>
    </nav>
    <main>
      <router-view />
    </main>
  </div>
</template>
<script>
import { getAuthStatus, logout } from './api';
export default {
  name: 'AdminLayout',
  data() {
    return {
      user: null,
      loading: false,
      error: ''
    };
  },
  methods: {
    async checkAuth() {
      this.loading = true;
      this.error = '';
      try {
        const res = await getAuthStatus();
        if (res.data.authenticated) {
          this.user = {
            username: res.data.username,
            role: res.data.role
          };
        } else {
          this.user = null;
        }
      } catch (e) {
        this.error = e.response?.data?.error || e.message || 'Feil ved autentisering';
        this.user = null;
      } finally {
        this.loading = false;
      }
    },
    async handleLogout() {
      this.loading = true;
      try {
        await logout();
        this.user = null;
      } catch (e) {
        this.error = e.response?.data?.error || e.message || 'Feil ved utlogging';
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.checkAuth();
  }
};
</script>
