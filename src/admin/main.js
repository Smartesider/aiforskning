import { createApp } from 'vue';
import AdminLayout from './AdminLayout.vue';
import router from './router';

const app = createApp(AdminLayout);
app.use(router);
app.mount('#vue-admin-app');
