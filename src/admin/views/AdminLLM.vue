<template>
  <div class="admin-llm">
    <h1>Admin LLM Model Management</h1>
    <button @click="showAddForm = true">Add LLM Model</button>
    <div v-if="showAddForm">
      <admin-llm-form @saved="onLLMSaved" @cancel="showAddForm = false" />
    </div>
    <ul>
      <li v-for="model in llms" :key="model.id">
        <strong>{{ model.name }}</strong> ({{ model.provider }})
        <button @click="editLLM(model)">Edit</button>
        <button @click="deleteLLM(model.id)">Delete</button>
      </li>
    </ul>
    <div v-if="editing">
      <admin-llm-form :llm="editing" @saved="onLLMSaved" @cancel="cancelEdit" />
    </div>
  </div>
</template>

<script>
import AdminLLMForm from '../components/AdminLLMForm.vue';
import axios from 'axios';

<script>
import { fetchLLMs, deleteLLM } from '../api';
export default {
  name: 'AdminLLM',
  data() {
    return {
      llmList: [],
      selectedLLM: null,
      showForm: false,
      loading: false,
      error: ''
    };
  },
  methods: {
    openForm(model) {
      this.selectedLLM = model || {};
      this.showForm = true;
    },
    closeForm() {
      this.selectedLLM = null;
      this.showForm = false;
    },
    async fetchLLMs() {
      this.loading = true;
      this.error = '';
      try {
        const res = await fetchLLMs();
        this.llmList = res.data.llms || res.data || [];
      } catch (e) {
        this.error = e.response?.data?.error || e.message || 'Feil ved henting av modeller';
      } finally {
        this.loading = false;
      }
    },
    async deleteLLM(id) {
      this.loading = true;
      try {
        await deleteLLM(id);
        this.fetchLLMs();
      } catch (e) {
        this.error = e.response?.data?.error || e.message || 'Feil ved sletting';
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchLLMs();
  }
};
</script>
