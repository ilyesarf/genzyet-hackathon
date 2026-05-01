import { createRouter, createWebHistory } from 'vue-router';

import NewsDashboard from '@/components/NewsDashboard.vue';
import IntelligencePage from '@/components/IntelligencePage.vue';
import SourcesPage from '@/components/SourcesPage.vue';
import SettingsPage from '@/components/SettingsPage.vue';

const routes = [
  { path: '/', name: 'dashboard', component: NewsDashboard },
  { path: '/intelligence', name: 'intelligence', component: IntelligencePage },
  { path: '/sources', name: 'sources', component: SourcesPage },
  { path: '/settings', name: 'settings', component: SettingsPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
