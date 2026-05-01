<template>
  <div class="dashboard">
    <!-- Error State -->
    <div v-if="error" class="state-box error-state">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <p>Failed to load intelligence data.</p>
    </div>

    <!-- Loading State -->
    <div v-else-if="loading" class="split-layout">
      <div class="feed-panel">
        <div class="panel-header">
          <h2 class="panel-title">Feed</h2>
        </div>
        <div class="feed-list">
          <div v-for="i in 5" :key="i" class="feed-item skeleton-item">
            <div class="skel skel-badge"></div>
            <div class="skel skel-title"></div>
            <div class="skel skel-meta"></div>
            <div class="skel skel-body"></div>
            <div class="skel skel-body short"></div>
          </div>
        </div>
      </div>
      <div class="divider"></div>
      <div class="analysis-panel">
        <div class="panel-header">
          <h2 class="panel-title">Analysis</h2>
        </div>
        <div class="analysis-empty">
          <p>Select an item to view analysis</p>
        </div>
      </div>
    </div>

    <!-- Data State -->
    <div v-else class="split-layout">
      <!-- Left: News Feed -->
      <div class="feed-panel">
        <div class="panel-header">
          <h2 class="panel-title">Feed</h2>
          <div class="sort-toggle" @click="toggleSort">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path v-if="sortOrder === 'desc'" d="M12 5v14M5 12l7 7 7-7"/>
              <path v-else d="M12 19V5M5 12l7-7 7 7"/>
            </svg>
            <span>Urgency</span>
          </div>
        </div>
        <div class="feed-list">
          <TransitionGroup name="feed">
            <div
              v-for="item in sortedData"
              :key="item.title"
              class="feed-item"
              :class="{ 'is-selected': selectedItem?.title === item.title }"
              @click="selectItem(item)"
            >
              <div class="feed-item-top">
                <span class="source-badge">{{ item.source }}</span>
                <span 
                  class="urgency-dot"
                  :style="{ background: getUrgencyColor(item.urgency_score) }"
                ></span>
                <span class="urgency-val" :style="{ color: getUrgencyColor(item.urgency_score) }">{{ item.urgency_score }}</span>
              </div>
              <h3 class="feed-title">{{ item.title }}</h3>
              <div class="feed-meta">
                <span class="category">{{ item.category }}</span>
                <span class="dot">·</span>
                <span class="time">{{ formatTimestamp(item.timestamp) }}</span>
              </div>
              <p class="feed-excerpt">{{ item.summary }}</p>
            </div>
          </TransitionGroup>
        </div>
      </div>

      <!-- Divider -->
      <div class="divider"></div>

      <!-- Right: Analysis Panel -->
      <div class="analysis-panel">
        <div class="panel-header">
          <h2 class="panel-title">Analysis</h2>
        </div>

        <div v-if="!selectedItem" class="analysis-empty">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
          <p>Select an item to view analysis</p>
        </div>

        <Transition name="slide" mode="out-in">
          <div v-if="selectedItem" :key="selectedItem.title" class="analysis-content">
            <!-- Summary Card -->
            <div class="analysis-card">
              <div class="analysis-card-header">
                <span class="source-badge">{{ selectedItem.source }}</span>
                <span class="time">{{ formatTimestamp(selectedItem.timestamp) }}</span>
              </div>
              <h3 class="analysis-title">{{ selectedItem.title }}</h3>
              <p class="analysis-body">{{ selectedItem.summary }}</p>
            </div>

            <!-- Urgency Assessment -->
            <div class="analysis-card urgency-card">
              <div class="urgency-header">
                <span class="urgency-label">Urgency Assessment</span>
                <span 
                  class="urgency-score-badge"
                  :style="{ 
                    background: getUrgencyColor(selectedItem.urgency_score) + '1a',
                    color: getUrgencyColor(selectedItem.urgency_score)
                  }"
                >{{ getUrgencyLevel(selectedItem.urgency_score) }} · {{ selectedItem.urgency_score }}/100</span>
              </div>
              <div class="urgency-bar-track">
                <div 
                  class="urgency-bar-fill"
                  :style="{ 
                    width: selectedItem.urgency_score + '%',
                    background: getUrgencyColor(selectedItem.urgency_score)
                  }"
                ></div>
              </div>
            </div>

            <!-- Key Info -->
            <div class="analysis-card">
              <span class="analysis-card-label">Category</span>
              <span class="category-tag">{{ selectedItem.category }}</span>
            </div>

            <!-- Action -->
            <button class="btn-action" @click="$emit('item-selected', selectedItem)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
              Open Full Report
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAnalyst } from '@/composables/useAnalyst';

const { data, loading, error } = useAnalyst();

defineEmits(['item-selected']);

const sortOrder = ref('desc');
const selectedItem = ref(null);

const sortedData = computed(() => {
  if (!data.value) return [];
  return [...data.value].sort((a, b) => {
    return sortOrder.value === 'desc'
      ? b.urgency_score - a.urgency_score
      : a.urgency_score - b.urgency_score;
  });
});

const toggleSort = () => {
  sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc';
};

const selectItem = (item) => {
  selectedItem.value = item;
};

const getUrgencyColor = (score) => {
  if (score >= 70) return 'var(--urgency-high)';
  if (score >= 40) return 'var(--urgency-medium)';
  return 'var(--urgency-low)';
};

const getUrgencyLevel = (score) => {
  if (score >= 70) return 'HIGH';
  if (score >= 40) return 'MEDIUM';
  return 'LOW';
};

const formatTimestamp = (ts) => {
  const date = new Date(ts);
  const now = new Date();
  const diff = now - date;
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
};
</script>

<style scoped>
/* ═══ Dashboard Shell ═══ */
.dashboard {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - var(--topbar-height));
}

/* ═══ Split Layout ═══ */
.split-layout {
  display: flex;
  flex: 1;
  min-height: 0;
}

.feed-panel {
  flex: 0 0 58%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.divider {
  width: 1px;
  background: var(--border-subtle);
  flex-shrink: 0;
}

.analysis-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* ═══ Panel Headers ═══ */
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.sort-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.15s ease;
  user-select: none;
}

.sort-toggle:hover {
  color: var(--accent-gold);
  background: var(--accent-gold-dim);
}

/* ═══ Feed List ═══ */
.feed-list {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.feed-item {
  padding: var(--feed-density, 14px) 24px;
  border-bottom: 1px solid var(--border-subtle);
  cursor: pointer;
  transition: background 0.15s ease;
}

.feed-item:hover {
  background: var(--bg-hover);
}

.feed-item.is-selected {
  background: var(--accent-gold-dim);
  border-left: 3px solid var(--accent-gold);
  padding-left: 21px;
}

.feed-item-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.source-badge {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--accent-gold);
  background: var(--accent-gold-dim);
  padding: 2px 8px;
  border-radius: 3px;
}

.urgency-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-left: auto;
  flex-shrink: 0;
}

.urgency-val {
  font-size: 12px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.feed-title {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.feed-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.dot {
  opacity: 0.4;
}

.feed-excerpt {
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ═══ Analysis Panel ═══ */
.analysis-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-muted);
  font-size: 13px;
}

.analysis-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.analysis-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 16px;
}

.analysis-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.analysis-card-header .time {
  font-size: 12px;
  color: var(--text-muted);
}

.analysis-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.45;
  margin-bottom: 12px;
}

.analysis-body {
  font-size: 13.5px;
  line-height: 1.65;
  color: var(--text-secondary);
}

/* Urgency Card */
.urgency-card {
  border-color: var(--border-subtle);
}

.urgency-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.urgency-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.urgency-score-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 4px;
  letter-spacing: 0.04em;
}

.urgency-bar-track {
  height: 4px;
  background: var(--border-muted);
  border-radius: 2px;
  overflow: hidden;
}

.urgency-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}

.analysis-card-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  display: block;
  margin-bottom: 8px;
}

.category-tag {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* Action Button */
.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--accent-gold);
  font-size: 13px;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s ease;
}

.btn-action:hover {
  background: var(--accent-gold-dim);
  border-color: var(--accent-gold-muted);
}

/* ═══ Skeleton ═══ */
.skeleton-item {
  cursor: default;
  pointer-events: none;
}

.skel {
  border-radius: 4px;
  background: var(--border-muted);
  position: relative;
  overflow: hidden;
}

.skel::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
  animation: shimmer 1.5s infinite;
}

.skel-badge { width: 60px; height: 16px; margin-bottom: 10px; }
.skel-title { width: 80%; height: 14px; margin-bottom: 8px; }
.skel-meta { width: 40%; height: 10px; margin-bottom: 8px; }
.skel-body { width: 100%; height: 10px; margin-bottom: 4px; }
.skel-body.short { width: 65%; }

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

/* ═══ Transitions ═══ */
.feed-move,
.feed-enter-active,
.feed-leave-active {
  transition: all 0.3s ease;
}
.feed-enter-from,
.feed-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}

.slide-enter-active { transition: all 0.25s ease-out; }
.slide-leave-active { transition: all 0.15s ease-in; }
.slide-enter-from { opacity: 0; transform: translateY(8px); }
.slide-leave-to { opacity: 0; transform: translateY(-4px); }

/* ═══ Error ═══ */
.state-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-muted);
  padding: 48px;
}

.error-state svg {
  color: var(--urgency-high);
}

/* ═══ Responsive ═══ */
@media (max-width: 900px) {
  .split-layout {
    flex-direction: column;
  }
  .feed-panel {
    flex: none;
    max-height: 50vh;
  }
  .divider {
    width: 100%;
    height: 1px;
  }
  .analysis-panel {
    flex: 1;
  }
}
</style>
