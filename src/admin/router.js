// Admin router for news and LLM management
import { createRouter, createWebHistory } from 'vue-router';
import AdminNews from './views/AdminNews.vue';
import AdminLLM from './views/AdminLLM.vue';

// Dummy admin guard (replace with real auth logic)
function adminGuard(to, from, next) {
  // Replace with your real admin check
  const isAdmin = true; // TODO: implement real check
  if (isAdmin) {
    next();
  } else {
    next('/login');
  }
}

const routes = [
  {
    path: '/admin/news',
    component: AdminNews,
    beforeEnter: adminGuard
  },
  {
    path: '/admin/llm-models',
    component: AdminLLM,
    beforeEnter: adminGuard
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
