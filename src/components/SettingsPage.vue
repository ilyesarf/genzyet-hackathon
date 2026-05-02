<template>
  <div class="settings-screen">
    <div class="settings-header">
      <span class="settings-title">{{ t.settings_title }}</span>
    </div>

    <div class="settings-body">
      <div class="settings-layout">
        <!-- Sidebar Tabs -->
        <nav class="settings-tabs">
          <button
            v-for="tab in tabs" :key="tab.key"
            class="tab-btn"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >{{ tab.label }}</button>
        </nav>

        <!-- Content -->
        <div class="settings-content">

          <!-- Profile / Account -->
          <div v-if="activeTab === 'account'" class="tab-panel">
            <div class="section-label">ACCOUNT</div>
            <div class="section-body">
              <div class="setting-row"><span class="setting-key">Agency</span><span class="setting-val">3SG Communications</span></div>
              <div class="setting-row"><span class="setting-key">Plan</span><span class="setting-val accent">Enterprise Pro</span></div>
              <div class="setting-row"><span class="setting-key">Seats used</span><span class="setting-val">3 / 10</span></div>
            </div>

            <div class="section-label" style="margin-top:16px">SCRAPER</div>
            <div class="section-body">
              <div class="setting-row">
                <span class="setting-key">Daily scrape time</span>
                <input type="time" v-model="scrapeTime" class="time-input" />
              </div>
              <div class="setting-row"><span class="setting-key">Data retention</span><span class="setting-val accent">72 hours</span></div>
              <div class="setting-row"><span class="setting-key">Engine</span><span class="setting-val">feedparser + custom</span></div>
            </div>
          </div>

          <!-- API Keys -->
          <div v-if="activeTab === 'api'" class="tab-panel">
            <div class="section-label">API KEYS</div>
            <div class="section-body">
              <div class="api-card" v-for="api in apiKeys" :key="api.name">
                <div class="api-top">
                  <div class="api-dot" :style="{ background: api.color }"></div>
                  <div class="api-info">
                    <span class="api-name">{{ api.name }}</span>
                    <span class="api-status" :class="api.connected ? 'on' : 'off'">{{ api.connected ? 'Connected' : 'Disconnected' }}</span>
                  </div>
                </div>
                <div class="api-key-row">
                  <input
                    :type="api.visible ? 'text' : 'password'"
                    class="key-input"
                    :value="api.key"
                    readonly
                  />
                  <button class="key-toggle" @click="api.visible = !api.visible">
                    {{ api.visible ? 'HIDE' : 'SHOW' }}
                  </button>
                </div>
                <div class="api-footer">
                  <span class="api-usage">{{ api.usage }} calls this month</span>
                  <button class="action-btn">Rotate Key</button>
                </div>
              </div>
            </div>

            <div class="section-label" style="margin-top:16px">ADD NEW KEY</div>
            <div class="section-body">
              <div class="add-key-form">
                <input type="text" class="key-input" placeholder="Provider name" v-model="newKeyName" />
                <input type="text" class="key-input" placeholder="API key" v-model="newKeyValue" />
                <button class="action-btn accent-btn">Add Key</button>
              </div>
            </div>
          </div>

          <!-- Notifications -->
          <div v-if="activeTab === 'notifications'" class="tab-panel">
            <div class="section-label">ALERTS</div>
            <div class="section-body">
              <div class="setting-row" v-for="n in notifSettings" :key="n.id">
                <div class="notif-info">
                  <span class="setting-key">{{ n.label }}</span>
                  <span class="notif-desc">{{ n.desc }}</span>
                </div>
                <button class="toggle-btn" :class="{ active: n.enabled }" @click="n.enabled = !n.enabled">
                  <div class="toggle-knob" :class="{ active: n.enabled }"></div>
                </button>
              </div>
            </div>
          </div>

          <!-- Appearance -->
          <div v-if="activeTab === 'appearance'" class="tab-panel">
            <div class="section-label">THEME</div>
            <div class="theme-picker">
              <div
                v-for="theme in themeList"
                :key="theme.id"
                class="theme-option"
                :class="{ selected: activeTheme === theme.id }"
                @click="activeTheme = theme.id"
              >
                <div class="theme-preview" :style="{ background: theme.bg }">
                  <div class="theme-sidebar-bar" :style="{ background: theme.sidebar }"></div>
                  <div class="theme-accent-bar" :style="{ background: theme.accent }"></div>
                </div>
                <span class="theme-name">{{ theme.name }}</span>
              </div>
            </div>

            <div v-if="showThemeToast" class="applied-toast">✓ Theme applied</div>

            <div class="section-label" style="margin-top:16px">LANGUAGE & REGION</div>
            <div class="section-body">
              <div class="lang-setting">
                <div class="setting-key" style="margin-bottom:12px">Interface language</div>
                <div class="lang-options">
                  <button
                    v-for="l in langOptions"
                    :key="l.code"
                    class="lang-option-btn"
                    :class="{ active: lang === l.code }"
                    @click="setLang(l.code)"
                    :style="l.code === 'ar' ? { fontFamily: 'var(--ff-arabic)' } : {}"
                  >{{ l.label }}</button>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, watch } from 'vue';
import { useTheme } from '@/composables/useTheme.js';

const t = inject('t');
const lang = inject('lang');
const setLang = inject('setLang');

const { activeTheme, themes: themeList } = useTheme();

const activeTab = ref('account');
const scrapeTime = ref('06:00');
const newKeyName = ref('');
const newKeyValue = ref('');

const tabs = [
  { key: 'account', label: 'Account' },
  { key: 'api', label: 'API Keys' },
  { key: 'notifications', label: 'Notifications' },
  { key: 'appearance', label: 'Appearance' },
];

const apiKeys = ref([
  { name: 'Groq API', key: 'gsk_Uv4Qhm1v•••••••••q0gzAW', color: '#f97316', connected: true, visible: false, usage: '2,847' },
  { name: 'Gemini API', key: 'AIzaSyDzrET•••••••••YvKL4', color: '#60a5fa', connected: true, visible: false, usage: '1,203' },
]);

const notifSettings = ref([
  { id: 1, label: 'Breaking news alerts', desc: 'Immediate push for high-urgency items', enabled: true },
  { id: 2, label: 'Daily digest', desc: 'Summary email every morning at 08:00', enabled: true },
  { id: 3, label: 'Source outages', desc: 'Alert when a feed becomes unreachable', enabled: true },
  { id: 4, label: 'Auto-score on update', desc: 'Run urgency scoring after each scrape', enabled: true },
  { id: 5, label: 'Trend shift alerts', desc: 'Notify when sentiment changes significantly', enabled: false },
]);

const langOptions = [
  { code: 'en', label: 'English' },
  { code: 'fr', label: 'Français' },
  { code: 'ar', label: 'العربية' },
];

// Theme applied toast
const showThemeToast = ref(false);
let toastTimer = null;
watch(activeTheme, () => {
  showThemeToast.value = true;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { showThemeToast.value = false; }, 1800);
});
</script>

<style scoped>
.settings-screen {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.settings-header {
  padding: 0 32px;
  height: 52px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.settings-title {
  font-family: var(--ff-head);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.settings-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
}

/* Layout */
.settings-layout {
  display: flex;
  gap: 24px;
  max-width: 820px;
}

/* Tabs */
.settings-tabs {
  width: 160px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.tab-btn {
  text-align: left;
  padding: 9px 14px;
  background: transparent;
  border: none;
  border-left: 2px solid transparent;
  color: var(--text2);
  font-family: var(--ff-body);
  font-size: 13px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.15s;
}
.tab-btn:hover { color: var(--text); background: var(--bg2); }
.tab-btn.active { border-left-color: var(--accent); color: var(--text); background: var(--bg2); font-weight: 500; }

/* Content */
.settings-content { flex: 1; min-width: 0; }
.tab-panel { display: flex; flex-direction: column; gap: 0; }

/* Section */
.section-label {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.1em;
  padding: 8px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--bg3);
}

.section-body {
  border: 1px solid var(--border);
  border-top: none;
}

/* Rows */
.setting-row {
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.setting-row:last-child { border-bottom: none; }

.setting-key { font-family: var(--ff-body); font-size: 13px; color: var(--text); }
.setting-val { font-family: var(--ff-mono); font-size: 12px; color: var(--text2); }
.setting-val.accent { color: var(--accent); }

.time-input {
  background: var(--bg3);
  border: 1px solid var(--border2);
  color: var(--text);
  font-family: var(--ff-mono);
  font-size: 13px;
  padding: 4px 10px;
  outline: none;
  color-scheme: inherit;
}

/* API Cards */
.api-card {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}
.api-card:last-child { border-bottom: none; }

.api-top { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.api-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.api-info { flex: 1; }
.api-name { font-family: var(--ff-head); font-size: 13px; font-weight: 600; color: var(--text); display: block; }
.api-status { font-family: var(--ff-mono); font-size: 9px; letter-spacing: 0.05em; }
.api-status.on { color: var(--green); }
.api-status.off { color: var(--red); }

.api-key-row { display: flex; gap: 6px; margin-bottom: 10px; }

.key-input {
  flex: 1;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text);
  font-family: var(--ff-mono);
  font-size: 11px;
  padding: 7px 12px;
  outline: none;
  letter-spacing: 0.02em;
}
.key-input:focus { border-color: var(--border2); }

.key-toggle {
  background: var(--bg3);
  border: 1px solid var(--border);
  color: var(--text3);
  font-family: var(--ff-mono);
  font-size: 9px;
  padding: 0 12px;
  cursor: pointer;
  letter-spacing: 0.06em;
  transition: all 0.15s;
}
.key-toggle:hover { color: var(--text2); border-color: var(--border2); }

.api-footer { display: flex; align-items: center; justify-content: space-between; }
.api-usage { font-family: var(--ff-mono); font-size: 10px; color: var(--text3); }

.action-btn {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--ff-mono);
  font-size: 10px;
  padding: 5px 14px;
  cursor: pointer;
  letter-spacing: 0.04em;
  transition: all 0.15s;
}
.action-btn:hover { border-color: var(--border2); color: var(--text); }
.accent-btn { border-color: var(--accent); color: var(--accent); }
.accent-btn:hover { background: var(--accent); color: #000; }

.add-key-form {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Notifications */
.notif-info { flex: 1; }
.notif-desc { display: block; font-family: var(--ff-body); font-size: 11px; color: var(--text3); margin-top: 2px; }

.toggle-btn {
  width: 40px; height: 20px; border-radius: 10px; border: none; cursor: pointer;
  background: var(--border2); position: relative; transition: background 0.2s;
  flex-shrink: 0;
}
.toggle-btn.active { background: var(--accent); }
.toggle-knob {
  position: absolute; top: 2px; left: 2px; width: 16px; height: 16px;
  border-radius: 50%; background: var(--text3); transition: left 0.2s, background 0.2s;
}
.toggle-knob.active { left: 22px; background: #000; }

/* Theme picker */
.theme-picker {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border: 1px solid var(--border);
  border-top: none;
  flex-wrap: wrap;
}

.theme-option { cursor: pointer; text-align: center; }
.theme-preview {
  width: 90px; height: 58px; border-radius: 0; position: relative;
  border: 1px solid var(--border); overflow: hidden;
  transition: border-color 0.15s;
}
.theme-option.selected .theme-preview { border-color: var(--accent); }
.theme-option:hover .theme-preview { border-color: var(--border2); }
.theme-sidebar-bar { position: absolute; top: 0; left: 0; width: 20px; height: 100%; }
.theme-accent-bar { position: absolute; top: 6px; right: 6px; width: 16px; height: 6px; }
.theme-name { display: block; margin-top: 6px; font-family: var(--ff-mono); font-size: 9px; color: var(--text3); letter-spacing: 0.04em; }
.theme-option.selected .theme-name { color: var(--accent); }

/* Toast */
.applied-toast {
  padding: 8px 20px;
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--green);
  border: 1px solid var(--border);
  border-top: none;
  animation: fadeIn 0.2s ease;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Language */
.lang-setting { padding: 16px 20px; }
.lang-options { display: flex; gap: 4px; }
.lang-option-btn {
  padding: 7px 16px;
  background: var(--bg3);
  border: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--ff-body);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.lang-option-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #000;
}

/* Responsive */
@media (max-width: 768px) {
  .settings-layout { flex-direction: column; }
  .settings-tabs { width: 100%; flex-direction: row; overflow-x: auto; }
  .tab-btn { border-left: none; border-bottom: 2px solid transparent; white-space: nowrap; }
  .tab-btn.active { border-left-color: transparent; border-bottom-color: var(--accent); }
}
</style>
