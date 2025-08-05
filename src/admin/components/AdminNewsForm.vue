<template>
  <form @submit.prevent="save">
    <div>
      <label for="news-title">Title</label>
      <input id="news-title" v-model="form.title" required />
    </div>
    <div>
      <label for="news-content">Content</label>
      <textarea id="news-content" v-model="form.content" required></textarea>
    </div>
    <div>
      <label for="news-category">Category</label>
      <input id="news-category" v-model="form.category" />
    </div>
    <div>
      <label for="news-visible">Visible</label>
      <input id="news-visible" type="checkbox" v-model="form.visible" />
    </div>
    <button type="submit">Save</button>
    <button type="button" @click="$emit('cancel')">Cancel</button>
  </form>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    news: Object
  },
  data() {
    return {
      form: {
        title: '',
        content: '',
<script>
import { addNews, updateNews } from '../api';
export default {
  name: 'AdminNewsForm',
  props: {
    news: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      form: {
        title: this.news.title || '',
        content: this.news.content || '',
        category: this.news.category || '',
        visible: this.news.visible !== undefined ? this.news.visible : true
      },
      loading: false,
      error: ''
    };
  },
  methods: {
    async submit() {
      this.loading = true;
      this.error = '';
      try {
        if (this.news.id) {
          await updateNews(this.news.id, this.form);
        } else {
          await addNews(this.form);
        }
        this.$emit('saved');
      } catch (e) {
        this.error = e.response?.data?.error || e.message || 'Feil ved lagring';
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
