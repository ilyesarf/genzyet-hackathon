<template>
  <div class="page settings-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Settings</h1>
        <p class="page-subtitle">Configure your intelligence platform preferences</p>
      </div>
    </div>

    <div class="settings-layout">
      <!-- Sidebar Tabs -->
      <nav class="settings-tabs">
        <button 
          v-for="tab in tabs" :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <component :is="tab.icon" />
          <span>{{ tab.label }}</span>
        </button>
      </nav>

      <!-- Content -->
      <div class="settings-content">

        <!-- Profile -->
        <div v-if="activeTab === 'profile'" class="settings-section">
          <h2 class="section-title">Profile Information</h2>
          <p class="section-desc">Manage your analyst identity and contact details</p>
          
          <div class="profile-card">
            <div class="profile-avatar">SA</div>
            <div class="profile-meta">
              <span class="profile-name">Son of Anton</span>
              <span class="profile-email">anton@khaberni.ai</span>
            </div>
            <button class="btn-outline-sm">Change Photo</button>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Full Name</label>
              <input type="text" class="form-input" value="Son of Anton" />
            </div>
            <div class="form-group">
              <label class="form-label">Email</label>
              <input type="email" class="form-input" value="anton@khaberni.ai" />
            </div>
            <div class="form-group">
              <label class="form-label">Role</label>
              <input type="text" class="form-input" value="Lead Analyst" disabled />
            </div>
            <div class="form-group">
              <label class="form-label">Timezone</label>
              <select class="form-input">
                <option>UTC+0 — London</option>
                <option selected>UTC+1 — Algiers</option>
                <option>UTC+2 — Cairo</option>
                <option>UTC+3 — Riyadh</option>
              </select>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn-primary">Save Changes</button>
          </div>
        </div>

        <!-- API Keys -->
        <div v-if="activeTab === 'api'" class="settings-section">
          <h2 class="section-title">API Configuration</h2>
          <p class="section-desc">Manage your AI provider keys and integration endpoints</p>

          <div class="api-list">
            <div class="api-card" v-for="api in apiKeys" :key="api.name">
              <div class="api-top">
                <div class="api-icon" :style="{ background: api.color + '1a', color: api.color }">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>
                </div>
                <div class="api-info">
                  <span class="api-name">{{ api.name }}</span>
                  <span class="api-status" :class="api.connected ? 'connected' : 'disconnected'">
                    {{ api.connected ? 'Connected' : 'Disconnected' }}
                  </span>
                </div>
              </div>
              <div class="api-key-field">
                <input 
                  :type="api.visible ? 'text' : 'password'" 
                  class="form-input mono" 
                  :value="api.key" 
                  readonly 
                />
                <button class="key-toggle" @click="api.visible = !api.visible">
                  <svg v-if="!api.visible" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
              <div class="api-footer">
                <span class="api-usage">{{ api.usage }} calls this month</span>
                <button class="btn-outline-sm">Rotate Key</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Notifications -->
        <div v-if="activeTab === 'notifications'" class="settings-section">
          <h2 class="section-title">Notification Preferences</h2>
          <p class="section-desc">Control how and when you receive intelligence alerts</p>

          <div class="toggle-list">
            <div class="toggle-item" v-for="n in notifications" :key="n.id">
              <div class="toggle-info">
                <span class="toggle-label">{{ n.label }}</span>
                <span class="toggle-desc">{{ n.desc }}</span>
              </div>
              <button 
                class="toggle-switch" 
                :class="{ on: n.enabled }" 
                @click="n.enabled = !n.enabled"
              >
                <span class="toggle-thumb"></span>
              </button>
            </div>
          </div>
        </div>

        <!-- Appearance -->
        <div v-if="activeTab === 'appearance'" class="settings-section">
          <h2 class="section-title">Appearance</h2>
          <p class="section-desc">Customize the look and feel of your dashboard</p>

          <label class="form-label" style="margin-bottom: 10px;">Theme</label>
          <div class="theme-picker">
            <div 
              class="theme-option" 
              v-for="theme in themeList" :key="theme.id"
              :class="{ selected: activeTheme === theme.id }"
              @click="activeTheme = theme.id"
            >
              <div class="theme-preview" :style="{ background: theme.bg }">
                <div class="theme-sidebar-preview" :style="{ background: theme.sidebar }"></div>
                <div class="theme-accent-preview" :style="{ background: theme.accent }"></div>
              </div>
              <span class="theme-name">{{ theme.name }}</span>
            </div>
          </div>

          <div class="form-grid" style="margin-top: 24px;">
            <div class="form-group">
              <label class="form-label">Font Size</label>
              <select class="form-input" v-model="fontSize">
                <option v-for="fs in fontSizes" :key="fs" :value="fs">{{ fs }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Feed Density</label>
              <select class="form-input" v-model="feedDensity">
                <option v-for="d in densities" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
          </div>

          <div class="applied-toast" v-if="showApplied">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
            Theme applied
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, h, watch } from 'vue';
import { useTheme } from '@/composables/useTheme.js';

const { activeTheme, fontSize, feedDensity, themes: themeList, fontSizes, densities } = useTheme();

const activeTab = ref('profile');
const showApplied = ref(false);

// Flash a "Theme applied" toast when any appearance setting changes
let toastTimer = null;
watch([activeTheme, fontSize, feedDensity], () => {
  showApplied.value = true;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { showApplied.value = false; }, 1800);
});

const SvgUser = { render() { return h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, innerHTML: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>' }); } };
const SvgKey = { render() { return h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, innerHTML: '<path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>' }); } };
const SvgBell = { render() { return h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, innerHTML: '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>' }); } };
const SvgPalette = { render() { return h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, innerHTML: '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="8" r="1.5" fill="currentColor"/><circle cx="8" cy="12" r="1.5" fill="currentColor"/><circle cx="16" cy="12" r="1.5" fill="currentColor"/><circle cx="12" cy="16" r="1.5" fill="currentColor"/>' }); } };

const tabs = [
  { key: 'profile', label: 'Profile', icon: SvgUser },
  { key: 'api', label: 'API Keys', icon: SvgKey },
  { key: 'notifications', label: 'Notifications', icon: SvgBell },
  { key: 'appearance', label: 'Appearance', icon: SvgPalette },
];

const apiKeys = ref([
  { name: 'Groq API', key: 'gsk_Uv4Qhm1v•••••••••q0gzAW', color: '#f97316', connected: true, visible: false, usage: '2,847' },
  { name: 'Gemini API', key: 'AIzaSyDzrET•••••••••YvKL4', color: '#60a5fa', connected: true, visible: false, usage: '1,203' },
]);

const notifications = ref([
  { id: 1, label: 'Critical Alerts', desc: 'Receive immediate notifications for high-urgency intelligence', enabled: true },
  { id: 2, label: 'Daily Digest', desc: 'Summary of top stories delivered every morning at 08:00', enabled: true },
  { id: 3, label: 'Source Outages', desc: 'Alert when a monitored source becomes unreachable', enabled: true },
  { id: 4, label: 'Trend Shifts', desc: 'Notify when significant sentiment changes are detected', enabled: false },
  { id: 5, label: 'Weekly Report', desc: 'Comprehensive weekly analysis report via email', enabled: false },
]);
</script>

<style scoped>
.page { padding: 24px; flex: 1; overflow-y: auto; }
.page-header { margin-bottom: 24px; }
.page-title { font-family: 'Outfit', sans-serif; font-size: 22px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.page-subtitle { font-size: 13px; color: var(--text-secondary); }

.settings-layout { display: flex; gap: 24px; }

/* Tabs */
.settings-tabs { width: 200px; flex-shrink: 0; display: flex; flex-direction: column; gap: 2px; }
.tab-btn { display: flex; align-items: center; gap: 10px; padding: 10px 14px; background: transparent; border: none; border-radius: 6px; color: var(--text-secondary); font-size: 13px; font-weight: 500; cursor: pointer; font-family: inherit; transition: all 0.15s ease; text-align: left; }
.tab-btn:hover { background: var(--bg-hover); color: var(--text-primary); }
.tab-btn.active { background: var(--accent-gold-dim); color: var(--accent-gold); }

/* Content */
.settings-content { flex: 1; min-width: 0; }
.settings-section { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 24px; }
.section-title { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.section-desc { font-size: 13px; color: var(--text-muted); margin-bottom: 24px; }

/* Profile Card */
.profile-card { display: flex; align-items: center; gap: 14px; padding: 16px; background: var(--bg-input); border-radius: 8px; margin-bottom: 24px; }
.profile-avatar { width: 48px; height: 48px; background: linear-gradient(135deg, var(--accent-gold), #d4a040); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; color: #000; flex-shrink: 0; }
.profile-meta { flex: 1; display: flex; flex-direction: column; }
.profile-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.profile-email { font-size: 12px; color: var(--text-muted); }

/* Forms */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; }
.form-input { background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 9px 12px; color: var(--text-primary); font-size: 13px; font-family: inherit; outline: none; transition: border-color 0.15s ease; }
.form-input:focus { border-color: var(--accent-gold-muted); }
.form-input:disabled { opacity: 0.5; cursor: not-allowed; }
.form-input.mono { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; letter-spacing: 0.02em; }
.form-actions { margin-top: 20px; display: flex; justify-content: flex-end; }

.btn-primary { display: flex; align-items: center; gap: 6px; background: var(--accent-gold); color: #000; border: none; padding: 8px 20px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; transition: background 0.15s ease; }
.btn-primary:hover { background: var(--accent-gold-hover); }
.btn-outline-sm { background: transparent; border: 1px solid var(--border-subtle); color: var(--text-secondary); padding: 5px 12px; border-radius: 5px; font-size: 11px; font-weight: 600; cursor: pointer; font-family: inherit; transition: all 0.15s ease; }
.btn-outline-sm:hover { border-color: var(--accent-gold-muted); color: var(--accent-gold); }

/* API Cards */
.api-list { display: flex; flex-direction: column; gap: 16px; }
.api-card { background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 16px; }
.api-top { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.api-icon { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.api-info { flex: 1; }
.api-name { display: block; font-size: 14px; font-weight: 600; color: var(--text-primary); }
.api-status { font-size: 11px; font-weight: 600; }
.api-status.connected { color: #4ade80; }
.api-status.disconnected { color: var(--urgency-high); }
.api-key-field { display: flex; gap: 8px; margin-bottom: 12px; }
.api-key-field .form-input { flex: 1; }
.key-toggle { background: transparent; border: 1px solid var(--border-subtle); color: var(--text-muted); width: 36px; border-radius: 6px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.12s ease; }
.key-toggle:hover { color: var(--text-primary); border-color: var(--border-muted); }
.api-footer { display: flex; align-items: center; justify-content: space-between; }
.api-usage { font-size: 11px; color: var(--text-muted); }

/* Toggle */
.toggle-list { display: flex; flex-direction: column; gap: 0; }
.toggle-item { display: flex; align-items: center; justify-content: space-between; padding: 14px 0; border-bottom: 1px solid var(--border-subtle); }
.toggle-item:last-child { border-bottom: none; }
.toggle-info { flex: 1; }
.toggle-label { display: block; font-size: 13.5px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.toggle-desc { font-size: 12px; color: var(--text-muted); }
.toggle-switch { width: 40px; height: 22px; border-radius: 11px; background: var(--border-muted); border: none; cursor: pointer; position: relative; transition: background 0.2s ease; flex-shrink: 0; }
.toggle-switch.on { background: var(--accent-gold); }
.toggle-thumb { position: absolute; top: 3px; left: 3px; width: 16px; height: 16px; border-radius: 50%; background: #fff; transition: transform 0.2s ease; }
.toggle-switch.on .toggle-thumb { transform: translateX(18px); }

/* Themes */
.theme-picker { display: flex; gap: 16px; flex-wrap: wrap; }
.theme-option { cursor: pointer; text-align: center; }
.theme-preview { width: 100px; height: 68px; border-radius: 8px; border: 2px solid var(--border-subtle); position: relative; overflow: hidden; transition: border-color 0.15s ease; }
.theme-option.selected .theme-preview { border-color: var(--accent-gold); }
.theme-option:hover .theme-preview { border-color: var(--border-muted); }
.theme-sidebar-preview { position: absolute; top: 0; left: 0; width: 24px; height: 100%; }
.theme-accent-preview { position: absolute; top: 8px; right: 8px; width: 20px; height: 8px; border-radius: 3px; }
.theme-name { display: block; margin-top: 6px; font-size: 11px; color: var(--text-secondary); font-weight: 500; }
.theme-option.selected .theme-name { color: var(--accent-gold); }

/* Toast */
.applied-toast {
  display: flex; align-items: center; gap: 8px;
  margin-top: 16px; padding: 10px 16px;
  background: rgba(74, 222, 128, 0.12);
  border: 1px solid rgba(74, 222, 128, 0.3);
  border-radius: 6px;
  color: #4ade80;
  font-size: 12.5px; font-weight: 600;
  animation: fadeInUp 0.25s ease;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .settings-layout { flex-direction: column; }
  .settings-tabs { width: 100%; flex-direction: row; overflow-x: auto; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>
