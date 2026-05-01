import { createRouter, createWebHistory } from 'vue-router';

import NewsDashboard from '@/components/NewsDashboard.vue';
import IntelligencePage from '@/components/IntelligencePage.vue';
import SourcesPage from '@/components/SourcesPage.vue';
import SettingsPage from '@/components/SettingsPage.vue';

const routes = [
  { path: '/', name: 'strategy', component: IntelligencePage },
  { path: '/news', name: 'dashboard', component: NewsDashboard },
  { path: '/sources', name: 'sources', component: SourcesPage },
  { path: '/settings', name: 'settings', component: SettingsPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
