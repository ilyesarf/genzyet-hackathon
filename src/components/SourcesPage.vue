<template>
  <div class="page sources-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">News Sources</h1>
        <p class="page-subtitle">Monitor and manage your intelligence feed providers</p>
      </div>
      <button class="btn-primary" @click="showAddModal = true">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Add Source
      </button>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <button 
        v-for="f in filters" :key="f.key"
        class="filter-btn" 
        :class="{ active: activeFilter === f.key }"
        @click="activeFilter = f.key"
      >
        {{ f.label }}
        <span class="filter-count">{{ f.count }}</span>
      </button>
    </div>

    <!-- Sources Grid -->
    <div class="sources-grid">
      <div 
        v-for="source in filteredSources" :key="source.id" 
        class="source-card"
        :class="{ inactive: !source.active }"
      >
        <div class="source-top">
          <div class="source-avatar" :style="{ background: source.color }">
            {{ source.name.charAt(0) }}
          </div>
          <div class="source-info">
            <h3 class="source-name">{{ source.name }}</h3>
            <span class="source-type">{{ source.type }}</span>
          </div>
          <div class="source-status" :class="source.active ? 'online' : 'offline'">
            {{ source.active ? 'Active' : 'Paused' }}
          </div>
        </div>

        <div class="source-stats">
          <div class="source-stat">
            <span class="source-stat-val">{{ source.articles }}</span>
            <span class="source-stat-lbl">Articles</span>
          </div>
          <div class="source-stat">
            <span class="source-stat-val">{{ source.reliability }}%</span>
            <span class="source-stat-lbl">Reliability</span>
          </div>
          <div class="source-stat">
            <span class="source-stat-val">{{ source.latency }}</span>
            <span class="source-stat-lbl">Latency</span>
          </div>
        </div>

        <div class="source-bar-section">
          <div class="source-bar-header">
            <span class="source-bar-label">Coverage</span>
            <span class="source-bar-value">{{ source.coverage }}%</span>
          </div>
          <div class="source-bar-track">
            <div class="source-bar-fill" :style="{ width: source.coverage + '%', background: source.color }"></div>
          </div>
        </div>

        <div class="source-footer">
          <span class="source-updated">Updated {{ source.lastUpdate }}</span>
          <div class="source-actions">
            <button class="action-btn" title="Configure">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
            </button>
            <button class="action-btn" :class="{ toggled: source.active }" @click="source.active = !source.active" :title="source.active ? 'Pause' : 'Activate'">
              <svg v-if="source.active" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
              <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Source Modal Overlay -->
    <Transition name="modal">
      <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Add New Source</h3>
            <button class="modal-close" @click="showAddModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <label class="form-label">Source Name</label>
            <input type="text" class="form-input" placeholder="e.g. Bloomberg Terminal" />
            <label class="form-label">Feed URL</label>
            <input type="text" class="form-input" placeholder="https://..." />
            <label class="form-label">Category</label>
            <select class="form-input">
              <option>News Wire</option>
              <option>Tech Press</option>
              <option>Government</option>
              <option>Social Intelligence</option>
              <option>Custom RSS</option>
            </select>
          </div>
          <div class="modal-footer">
            <button class="btn-outline" @click="showAddModal = false">Cancel</button>
            <button class="btn-primary" @click="showAddModal = false">Add Source</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const showAddModal = ref(false);
const activeFilter = ref('all');

const sources = ref([
  { id: 1, name: 'Reuters', type: 'News Wire', color: '#f97316', articles: '12.4K', reliability: 98, latency: '1.2s', coverage: 94, lastUpdate: '2 min ago', active: true },
  { id: 2, name: 'TechPulse', type: 'Tech Press', color: '#60a5fa', articles: '3.8K', reliability: 91, latency: '2.1s', coverage: 78, lastUpdate: '5 min ago', active: true },
  { id: 3, name: 'MarketWatch', type: 'Financial', color: '#4ade80', articles: '8.1K', reliability: 95, latency: '1.5s', coverage: 88, lastUpdate: '1 min ago', active: true },
  { id: 4, name: 'Securly', type: 'Cybersecurity', color: 'var(--urgency-high)', articles: '2.1K', reliability: 93, latency: '3.4s', coverage: 65, lastUpdate: '12 min ago', active: true },
  { id: 5, name: 'The Verge', type: 'Tech Press', color: '#a78bfa', articles: '5.6K', reliability: 89, latency: '1.8s', coverage: 72, lastUpdate: '8 min ago', active: true },
  { id: 6, name: 'Gov.UK', type: 'Government', color: '#facc15', articles: '890', reliability: 99, latency: '4.2s', coverage: 42, lastUpdate: '1h ago', active: false },
  { id: 7, name: 'Al Jazeera', type: 'News Wire', color: 'var(--accent-gold)', articles: '9.2K', reliability: 92, latency: '2.0s', coverage: 81, lastUpdate: '3 min ago', active: true },
  { id: 8, name: 'Ars Technica', type: 'Tech Press', color: '#f472b6', articles: '4.3K', reliability: 90, latency: '2.5s', coverage: 69, lastUpdate: '20 min ago', active: false },
]);

const filters = computed(() => [
  { key: 'all', label: 'All', count: sources.value.length },
  { key: 'active', label: 'Active', count: sources.value.filter(s => s.active).length },
  { key: 'paused', label: 'Paused', count: sources.value.filter(s => !s.active).length },
]);

const filteredSources = computed(() => {
  if (activeFilter.value === 'active') return sources.value.filter(s => s.active);
  if (activeFilter.value === 'paused') return sources.value.filter(s => !s.active);
  return sources.value;
});
</script>

<style scoped>
.page { padding: 24px; flex: 1; overflow-y: auto; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-family: 'Outfit', sans-serif; font-size: 22px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.page-subtitle { font-size: 13px; color: var(--text-secondary); }

.btn-primary { display: flex; align-items: center; gap: 6px; background: var(--accent-gold); color: #000; border: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; transition: background 0.15s ease; }
.btn-primary:hover { background: var(--accent-gold-hover); }
.btn-outline { display: flex; align-items: center; gap: 6px; background: transparent; border: 1px solid var(--border-subtle); color: var(--text-secondary); padding: 7px 14px; border-radius: 6px; font-size: 12.5px; font-weight: 600; cursor: pointer; font-family: inherit; transition: all 0.15s ease; }
.btn-outline:hover { border-color: var(--accent-gold-muted); color: var(--accent-gold); }

/* Filter */
.filter-bar { display: flex; gap: 6px; margin-bottom: 20px; }
.filter-btn { background: transparent; border: 1px solid var(--border-subtle); color: var(--text-secondary); padding: 6px 14px; border-radius: 6px; font-size: 12.5px; font-weight: 600; cursor: pointer; font-family: inherit; display: flex; align-items: center; gap: 6px; transition: all 0.15s ease; }
.filter-btn:hover { border-color: var(--accent-gold-muted); color: var(--text-primary); }
.filter-btn.active { background: var(--accent-gold-dim); border-color: var(--accent-gold-muted); color: var(--accent-gold); }
.filter-count { font-size: 10px; background: var(--bg-input); padding: 1px 6px; border-radius: 10px; }
.filter-btn.active .filter-count { background: var(--accent-gold); color: #000; }

/* Grid */
.sources-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.source-card { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 18px; transition: all 0.15s ease; }
.source-card:hover { border-color: var(--border-muted); }
.source-card.inactive { opacity: 0.55; }

.source-top { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.source-avatar { width: 38px; height: 38px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; color: #000; flex-shrink: 0; }
.source-info { flex: 1; }
.source-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.source-type { font-size: 11px; color: var(--text-muted); }
.source-status { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 3px 8px; border-radius: 4px; }
.source-status.online { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
.source-status.offline { background: var(--bg-input); color: var(--text-muted); }

.source-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
.source-stat { text-align: center; }
.source-stat-val { display: block; font-size: 15px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; }
.source-stat-lbl { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }

.source-bar-section { margin-bottom: 14px; }
.source-bar-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.source-bar-label { font-size: 11px; color: var(--text-muted); }
.source-bar-value { font-size: 11px; font-weight: 600; color: var(--text-secondary); }
.source-bar-track { height: 4px; background: var(--border-muted); border-radius: 2px; overflow: hidden; }
.source-bar-fill { height: 100%; border-radius: 2px; transition: width 0.5s ease; }

.source-footer { display: flex; align-items: center; justify-content: space-between; padding-top: 12px; border-top: 1px solid var(--border-subtle); }
.source-updated { font-size: 11px; color: var(--text-muted); }
.source-actions { display: flex; gap: 4px; }
.action-btn { width: 30px; height: 30px; border: 1px solid var(--border-subtle); background: transparent; border-radius: 6px; display: flex; align-items: center; justify-content: center; cursor: pointer; color: var(--text-muted); transition: all 0.12s ease; }
.action-btn:hover { color: var(--text-primary); border-color: var(--border-muted); }
.action-btn.toggled { color: var(--accent-gold); border-color: var(--accent-gold-muted); }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-content { background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: 12px; width: 440px; max-width: 90vw; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--border-subtle); }
.modal-header h3 { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.modal-close { background: none; border: none; color: var(--text-muted); font-size: 20px; cursor: pointer; padding: 0 4px; }
.modal-close:hover { color: var(--text-primary); }
.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.form-label { font-size: 12px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
.form-input { background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: 6px; padding: 9px 12px; color: var(--text-primary); font-size: 13px; font-family: inherit; outline: none; transition: border-color 0.15s ease; }
.form-input:focus { border-color: var(--accent-gold-muted); }
.modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 14px 20px; border-top: 1px solid var(--border-subtle); }

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

@media (max-width: 768px) {
  .sources-grid { grid-template-columns: 1fr; }
}
</style>
