<template>
  <div class="admin-news">
    <h1>Admin News Management</h1>
    <button @click="showAddForm = true">Add News Article</button>
    <div v-if="showAddForm">
      <admin-news-form @saved="onNewsSaved" @cancel="showAddForm = false" />
    </div>
    <ul>
      <li v-for="article in news" :key="article.id">
        <strong>{{ article.title }}</strong> ({{ article.category }})
        <button @click="editNews(article)">Edit</button>
        <button @click="deleteNews(article.id)">Delete</button>
      </li>
    </ul>
    <div v-if="editing">
      <admin-news-form :news="editing" @saved="onNewsSaved" @cancel="cancelEdit" />
    </div>
  </div>
</template>

<script>
import AdminNewsForm from '../components/AdminNewsForm.vue';
import axios from 'axios';

<script>
import { fetchNews, deleteNews } from '../api';
export default {
  name: 'AdminNews',
  data() {
    return {
      newsList: [],
      selectedNews: null,
      showForm: false,
      loading: false,
      error: ''
    };
  },
  methods: {
    openForm(news) {
      this.selectedNews = news || {};
      this.showForm = true;
    },
    closeForm() {
      this.selectedNews = null;
      this.showForm = false;
    },
    async fetchNews() {
      this.loading = true;
      this.error = '';
      try {
        const res = await fetchNews();
        this.newsList = res.data.news || [];
      } catch (e) {
        this.error = e.response?.data?.error || e.message || 'Feil ved henting av nyheter';
      } finally {
        this.loading = false;
      }
    },
    async deleteNews(id) {
      this.loading = true;
      try {
        await deleteNews(id);
        this.fetchNews();
      } catch (e) {
        this.error = e.response?.data?.error || e.message || 'Feil ved sletting';
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchNews();
  }
};
</script>
