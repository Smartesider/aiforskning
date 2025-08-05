<template>
  <form @submit.prevent="save">
    <div>
      <label for="llm-name">Name</label>
      <input id="llm-name" v-model="form.name" required />
    </div>
    <div>
      <label for="llm-provider">Provider</label>
      <input id="llm-provider" v-model="form.provider" required />
    </div>
    <div>
      <label for="llm-status">Status</label>
      <select id="llm-status" v-model="form.status">
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>
    <button type="submit">Save</button>
    <button type="button" @click="$emit('cancel')">Cancel</button>
  </form>
</template>

<script>
import axios from 'axios';

export default {
  props: {
<script>
import { addLLM, updateLLM } from '../api';
export default {
  name: 'AdminLLMForm',
  props: {
    model: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      form: {
        name: this.model.name || '',
        provider: this.model.provider || '',
        status: this.model.status || 'inactive'
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
        if (this.model.id) {
          await updateLLM(this.model.id, this.form);
        } else {
          await addLLM(this.form);
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
