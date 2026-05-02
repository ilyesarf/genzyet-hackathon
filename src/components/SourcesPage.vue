<template>
  <div class="sources-screen">
    <div class="sources-header">
      <span class="sources-title">{{ t.sources_title }}</span>
      <button class="add-btn" @click="adding = true">
        <span style="font-size:16px;line-height:1">+</span>
        {{ t.add_source }}
      </button>
    </div>

    <div class="sources-body">
      <!-- Stats -->
      <div class="stats-row">
        <div class="stat-item" v-for="s in stats" :key="s.label">
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>

      <!-- Add form -->
      <div v-if="adding" class="add-form">
        <div class="add-form-label">NEW SOURCE</div>
        <div class="add-form-fields">
          <input v-model="newName" placeholder="Source name" class="text-input" />
          <input v-model="newUrl" placeholder="URL or @handle" class="text-input wide" />
        </div>
        <div class="add-form-actions">
          <button class="form-add-btn" @click="addSource">ADD</button>
          <button class="form-cancel-btn" @click="adding = false; newName=''; newUrl=''">CANCEL</button>
        </div>
      </div>

      <!-- Table -->
      <div class="sources-table">
        <div class="table-header">
          <span v-for="h in ['SOURCE','TYPE','CATEGORY','STATUS','']" :key="h" class="th">{{ h }}</span>
        </div>
        <div v-for="src in sources" :key="src.id" class="table-row" :class="{ inactive: !src.active }">
          <div class="src-info">
            <div class="src-name">{{ src.name }}</div>
            <div class="src-url">{{ src.url }}</div>
          </div>
          <span class="src-type" :class="src.type">{{ src.type.toUpperCase() }}</span>
          <span class="src-cat">{{ src.category }}</span>
          <button class="toggle-btn" :class="{ active: src.active }" @click="toggleSource(src.id)">
            <div class="toggle-knob" :class="{ active: src.active }"></div>
          </button>
          <button class="remove-btn" @click="removeSource(src.id)">×</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted } from 'vue';

const t = inject('t');
const SCRAPER_BASE = '/api/scraper';

const sources = ref([
  // Culture, Arts & Urban Lifestyle
  { id: 1, name: "Tunez Magazine", type: "web", active: true, category: "culture", url: "tunezmagazine.org" },
  { id: 2, name: "Misk (Cultural Media)", type: "web", active: true, category: "culture", url: "misk.tn" },
  { id: 3, name: "Highlights", type: "web", active: true, category: "culture", url: "highlights.com.tn" },
  { id: 4, name: "La Sultane", type: "web", active: true, category: "culture", url: "lasultanemag.com" },
  { id: 5, name: "1001 Tunisie", type: "web", active: true, category: "culture", url: "1001tunisie.com" },
  { id: 6, name: "Leaders (Culture/Essays)", type: "web", active: true, category: "culture", url: "leaders.com.tn" },
  
  // Tech & Innovation
  { id: 7, name: "THD (Tunisie Haut Débit)", type: "web", active: true, category: "tech", url: "thd.tn" },
  { id: 8, name: "The Dot", type: "web", active: true, category: "tech", url: "thedot.tn" },
  { id: 9, name: "TunisianStartups", type: "web", active: true, category: "tech", url: "tunisian-startups.com" },
  { id: 10, name: "Tekiano", type: "web", active: true, category: "tech", url: "tekiano.com" },
  
  // Gastronomy & Travel
  { id: 11, name: "Our Tunisian Table", type: "web", active: true, category: "lifestyle", url: "ourtunisiantable.com" },
  { id: 12, name: "Ôthentic Travel", type: "web", active: true, category: "lifestyle", url: "othentictravel.com" },
  
  // Business & Economy
  { id: 13, name: "Managers (formerly Le Manager)", type: "web", active: true, category: "economy", url: "managers.tn" },
  { id: 14, name: "Entreprises Magazine", type: "web", active: true, category: "economy", url: "entreprises-magazine.com" },
  { id: 15, name: "WebManagerCenter", type: "web", active: true, category: "economy", url: "webmanagercenter.com" },
  
  // Lifestyle & Society
  { id: 16, name: "Baya", type: "web", active: true, category: "social", url: "baya.tn" },
  { id: 17, name: "Femmes de Tunisie", type: "web", active: true, category: "social", url: "femmesdetunisie.com" },
  { id: 18, name: "Webdo (Culture/Lifestyle)", type: "web", active: true, category: "social", url: "webdo.tn" },
]);
const adding = ref(false);
const newName = ref('');
const newUrl = ref('');

const stats = computed(() => [
  { label: 'TOTAL SOURCES', value: sources.value.length },
  { label: 'ACTIVE', value: sources.value.filter(s => s.active).length },
  { label: 'WEB', value: sources.value.filter(s => s.type === 'web').length },
  { label: 'SOCIAL', value: sources.value.filter(s => s.type === 'social').length },
]);

async function fetchSources() {
  try {
    const res = await fetch(`${SCRAPER_BASE}/sources`);
    if (!res.ok) throw new Error(`Failed to fetch sources: ${res.status}`);
    const json = await res.json();
    const data = json.data || [];
    
    sources.value = data.map((s, idx) => ({
      id: idx + 1,
      name: s.name,
      type: s.type === 'rss' || s.type === 'html' ? 'web' : 'social',
      active: s.enabled,
      category: s.category || 'tech',
      url: s.url.replace(/^https?:\/\/(www\.)?/, '')
    }));
  } catch (err) {
    console.error('[SourcesPage] Error fetching sources:', err);
  }
}

onMounted(() => {
  fetchSources();
});

function toggleSource(id) {
  // UI only for now — no backend endpoint to save config changes yet
  sources.value = sources.value.map(s => s.id === id ? { ...s, active: !s.active } : s);
}
function removeSource(id) {
  // UI only
  sources.value = sources.value.filter(s => s.id !== id);
}
function addSource() {
  if (!newName.value || !newUrl.value) return;
  sources.value = [...sources.value, { id: Date.now(), name: newName.value, type: 'web', active: true, category: 'tech', url: newUrl.value }];
  newName.value = ''; newUrl.value = ''; adding.value = false;
}
</script>

<style scoped>
.sources-screen {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.sources-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 60px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.sources-title {
  font-family: var(--ff-head);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 18px;
  background: var(--accent);
  border: none;
  color: #000;
  font-family: var(--ff-head);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.05em;
  cursor: pointer;
}

.sources-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-row { display: flex; gap: 1px; }
.stat-item {
  flex: 1;
  padding: 16px 20px;
  background: var(--bg2);
  border-right: 1px solid var(--border);
}
.stat-item:last-child { border-right: none; }
.stat-value { font-family: var(--ff-mono); font-size: 22px; font-weight: 500; color: var(--text); margin-bottom: 4px; }
.stat-label { font-family: var(--ff-mono); font-size: 9px; color: var(--text3); letter-spacing: 0.1em; }

.add-form { background: var(--bg2); border: 1px solid var(--border); padding: 20px; }
.add-form-label { font-family: var(--ff-mono); font-size: 10px; color: var(--accent); letter-spacing: 0.08em; margin-bottom: 14px; }
.add-form-fields { display: flex; gap: 10px; margin-bottom: 10px; }
.text-input {
  flex: 1; padding: 8px 12px; background: var(--bg3); border: 1px solid var(--border2);
  color: var(--text); font-family: var(--ff-body); font-size: 12px; outline: none; color-scheme: dark;
}
.text-input.wide { flex: 2; }
.text-input::placeholder { color: var(--text3); }
.add-form-actions { display: flex; gap: 8px; }
.form-add-btn { padding: 7px 16px; background: var(--accent); border: none; color: #000; font-family: var(--ff-mono); font-size: 11px; font-weight: 500; cursor: pointer; }
.form-cancel-btn { padding: 7px 16px; background: transparent; border: 1px solid var(--border); color: var(--text2); font-family: var(--ff-mono); font-size: 11px; cursor: pointer; }

.sources-table { display: flex; flex-direction: column; }
.table-header { display: grid; grid-template-columns: 1fr 80px 80px 80px 40px; padding: 8px 16px; border-bottom: 1px solid var(--border); }
.th { font-family: var(--ff-mono); font-size: 9px; color: var(--text3); letter-spacing: 0.1em; }

.table-row {
  display: grid; grid-template-columns: 1fr 80px 80px 80px 40px;
  padding: 13px 16px; border-bottom: 1px solid var(--border); align-items: center; transition: background 0.15s;
}
.table-row.inactive { background: var(--bg2); }

.src-name { font-family: var(--ff-body); font-size: 13px; font-weight: 500; color: var(--text); }
.table-row.inactive .src-name { color: var(--text3); }
.src-url { font-family: var(--ff-mono); font-size: 9px; color: var(--text3); margin-top: 2px; }

.src-type { font-family: var(--ff-mono); font-size: 9px; letter-spacing: 0.06em; }
.src-type.web { color: var(--blue); }
.src-type.social { color: var(--green); }
.src-cat { font-family: var(--ff-mono); font-size: 9px; color: var(--text2); }

.toggle-btn { width: 40px; height: 20px; border-radius: 10px; border: none; cursor: pointer; background: var(--border2); position: relative; transition: background 0.2s; }
.toggle-btn.active { background: var(--accent); }
.toggle-knob { position: absolute; top: 2px; left: 2px; width: 16px; height: 16px; border-radius: 50%; background: var(--text3); transition: left 0.2s, background 0.2s; }
.toggle-knob.active { left: 22px; background: #000; }

.remove-btn { background: transparent; border: none; color: var(--text3); cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; transition: color 0.15s; }
.remove-btn:hover { color: var(--red); }
</style>
