<template>
  <div class="news-screen">
    <!-- Top bar with pane toggles -->
    <div class="news-topbar">
      <div class="pane-toggles">
        <button class="pane-toggle" :class="{ collapsed: newsCollapsed }" @click="toggleNews">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
            <rect x="2" y="3" width="12" height="1.5" fill="currentColor"/>
            <rect x="2" y="7" width="8" height="1.5" fill="currentColor"/>
            <rect x="2" y="11" width="10" height="1.5" fill="currentColor"/>
          </svg>
          {{ t.nav_news }}
          <span class="toggle-arrow">{{ newsCollapsed ? '▶' : '◀' }}</span>
        </button>
        <span class="sep">|</span>
        <button class="pane-toggle" :class="{ collapsed: analysisCollapsed }" @click="toggleAnalysis">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
            <rect x="2" y="10" width="2" height="4" fill="currentColor"/>
            <rect x="6" y="7" width="2" height="7" fill="currentColor"/>
            <rect x="10" y="4" width="2" height="10" fill="currentColor"/>
            <rect x="14" y="2" width="2" height="12" fill="currentColor" opacity="0.4"/>
          </svg>
          AGENT ANALYSIS
          <span class="toggle-arrow">{{ analysisCollapsed ? '▶' : '◀' }}</span>
        </button>
      </div>
      <div class="topbar-actions">
        <button
          v-if="!analysisCollapsed && phase !== 'running'"
          class="run-btn"
          @click="runAnalysis"
        >
          <svg width="11" height="11" viewBox="0 0 16 16" fill="none">
            <rect x="3" y="4" width="10" height="8" rx="1" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="6" cy="8" r="1" fill="currentColor"/>
            <circle cx="10" cy="8" r="1" fill="currentColor"/>
            <path d="M6 2l2 2 2-2" stroke="currentColor" stroke-width="1.2" stroke-linecap="square"/>
          </svg>
          {{ t.run_agent }}
        </button>
      </div>
    </div>

    <!-- Split body -->
    <div class="split-body" ref="containerRef">
      <!-- News pane -->
      <div
        v-if="!newsCollapsed"
        class="news-pane"
        :style="{ width: newsWidth }"
      >
        <!-- Controls -->
        <div class="pane-controls">
          <div class="controls-left">
            <span class="pane-title">{{ t.headlines }}</span>
            <span class="last-update">{{ lastUpdate }}</span>
          </div>
          <div class="controls-right">
            <div class="time-toggle">
              <button
                v-for="w in ['24','48','72']"
                :key="w"
                class="time-btn"
                :class="{ active: timeWindow === w }"
                @click="timeWindow = w"
              >{{ w }}h</button>
            </div>
            <button class="update-btn" :class="{ updating }" @click="handleUpdate" :disabled="updating">
              <span v-if="updating" class="spinner"></span>
              <svg v-else width="11" height="11" viewBox="0 0 14 14" fill="none">
                <path d="M12 7A5 5 0 1 1 7 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="square"/>
                <path d="M7 2l2.5 2.5L7 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="square" stroke-linejoin="miter"/>
              </svg>
              {{ updating ? t.updating : t.update }}
            </button>
          </div>
        </div>

        <!-- Category filter -->
        <div class="cat-bar">
          <button
            v-for="c in categories"
            :key="c.id"
            class="cat-btn"
            :class="{ active: category === c.id }"
            @click="category = c.id"
          >{{ c.label }}</button>
        </div>

        <!-- Sort bar -->
        <div class="sort-bar">
          <span class="sort-hint">SORT BY:</span>
          <div class="sort-btns">
            <button
              v-for="s in ['urgency', 'relevance', 'newest']"
              :key="s"
              class="sort-btn"
              :class="{ active: sortBy === s }"
              @click="sortBy = s"
            >{{ s.toUpperCase() }}</button>
          </div>
        </div>

        <!-- News list -->
        <div class="news-list" ref="listRef">
          <div class="sort-label">↑ {{ sortBy.toUpperCase() }}</div>
          <div
            v-for="(item, idx) in sortedNews"
            :key="item.id"
            class="news-row"
            :class="{ expanded: expandedId === item.id }"
            @click="expandedId = expandedId === item.id ? null : item.id"
          >
            <div class="row-main">
              <span class="row-idx">{{ String(idx + 1).padStart(2, '0') }}</span>
              <div class="cat-dot" :style="{ background: CAT_COLORS[item.cat] || 'var(--text3)' }"></div>
              <div class="row-content">
                <div class="row-meta">
                  <span v-if="item.tag" class="tag-pill" :class="item.tag.toLowerCase()">{{ item.tag }}</span>
                  <span class="row-source">{{ item.source }} · {{ item.time }}</span>
                </div>
                <div class="row-title">{{ item.title }}</div>
                <div v-if="expandedId === item.id" class="row-expanded">
                  <p class="row-desc">{{ item.body ? item.body.slice(0, 300) : 'No body content available for this article.' }}</p>

                  <div class="score-row">
                    <div class="score-item">
                      <div class="score-label">{{ t.urgency }}</div>
                      <div class="score-bar">
                        <div class="score-fill" :style="{ width: item.urgency + '%', background: 'var(--red)' }"></div>
                      </div>
                      <span class="score-val" style="color:var(--red)">{{ item.urgency }}</span>
                    </div>
                    <div class="score-item">
                      <div class="score-label">{{ t.relevance }}</div>
                      <div class="score-bar">
                        <div class="score-fill" :style="{ width: item.relevance + '%', background: 'var(--accent)' }"></div>
                      </div>
                      <span class="score-val">{{ item.relevance }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="expandedId !== item.id" class="row-scores">
                <div class="score-compact">
                  <div class="sc-label">URG</div>
                  <div class="sc-val" :class="item.urgency > 80 ? 'high' : item.urgency > 65 ? 'mid' : ''">{{ item.urgency }}</div>
                </div>
                <div class="score-compact">
                  <div class="sc-label">REL</div>
                  <div class="sc-val">{{ item.relevance }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Drag handle -->
      <div
        v-if="!newsCollapsed && !analysisCollapsed"
        class="drag-handle"
        @mousedown="startDrag"
      >
        <div class="drag-grip"></div>
      </div>

      <!-- Analysis pane -->
      <div
        v-if="!analysisCollapsed"
        class="analysis-pane"
        :style="{ width: analysisWidth }"
      >
        <div class="analysis-header">
          <span class="analysis-label">AGENT ANALYSIS</span>
          <div v-if="phase === 'done'" class="status-done">
            <div class="status-dot green"></div>
            <span>COMPLETE</span>
          </div>
          <span v-else-if="phase === 'running'" class="status-running">RUNNING…</span>
        </div>

        <div class="analysis-body">
          <!-- Idle -->
          <div v-if="phase === 'idle'" class="analysis-idle">
            <div class="idle-icon">
              <svg width="28" height="28" viewBox="0 0 16 16" fill="none">
                <rect x="3" y="4" width="10" height="8" rx="1" stroke="var(--text3)" stroke-width="1.5"/>
                <circle cx="6" cy="8" r="1" fill="var(--text3)"/>
                <circle cx="10" cy="8" r="1" fill="var(--text3)"/>
                <path d="M6 2l2 2 2-2" stroke="var(--text3)" stroke-width="1.2" stroke-linecap="square"/>
              </svg>
            </div>
            <p class="idle-desc">Reads all active sources and returns a structured intelligence brief.</p>
          </div>

          <!-- Running -->
          <div v-else-if="phase === 'running'" class="agent-steps">
            <div v-for="(step, i) in agentSteps" :key="i" class="agent-step">
              <div class="step-dot" :class="i < stepIdx ? 'done' : i === stepIdx ? 'active' : 'pending'"></div>
              <span :id="'agent-step-' + i" class="step-text" :class="i < stepIdx ? 'done' : i === stepIdx ? 'active' : 'pending'">
                {{ i < stepIdx ? step : (i === stepIdx ? '' : step) }}
              </span>
              <span v-if="i < stepIdx" class="step-check">✓</span>
            </div>
          </div>

          <!-- Done -->
          <div v-else-if="phase === 'done'" class="analysis-results">
            <div class="result-card">
              <div class="result-card-label">SUMMARY</div>
              <p class="result-summary">{{ RESULT_SUMMARY }}</p>
            </div>

            <div>
              <div class="result-card-label">CLUSTERS</div>
              <div class="clusters">
                <div v-for="(c, i) in RESULT_CLUSTERS" :key="i" class="cluster-item">
                  <div class="cluster-top">
                    <span class="cluster-theme">{{ c.theme }}</span>
                    <span class="cluster-urg" :class="c.urgency > 80 ? 'high' : ''">URG {{ c.urgency }}</span>
                  </div>
                  <div class="cluster-articles">
                    <span v-for="(a, j) in c.articles" :key="j" class="cluster-article">· {{ a }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <div class="result-card-label">STRATEGIC SIGNALS</div>
              <div class="signals">
                <div v-for="(rec, i) in RESULT_RECS" :key="i" class="signal-item">
                  <span class="signal-arrow">→</span>
                  <span class="signal-text">{{ rec }}</span>
                </div>
              </div>
            </div>

            <button class="rerun-btn" @click="runAnalysis">↺ RE-RUN</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useAnimation } from '@/composables/useAnimation';
import { useNewsLogic } from '@/composables/useNewsLogic';

const t = inject('t');
const { entrance, staggerList, magneticHover, typewriter, wordReveal, scrollReveal, gsap } = useAnimation();
const { autoCategorize, calculateScores } = useNewsLogic();

const SCRAPER_BASE = '/api/scraper';
const ANALYST_BASE = '/api/analyst';

const CAT_COLORS = {
  tech: 'var(--blue)',
  economy: 'var(--green)',
  politics: 'var(--red)',
  social: 'var(--accent)',
  sport: 'oklch(65% 0.15 290)',
  weather: 'oklch(65% 0.12 200)',
  culture: 'oklch(70% 0.15 320)',
  lifestyle: 'oklch(65% 0.18 65)'
};

// ── State ──────────────────────────────────────────────────────────────────
const timeWindow = ref('24');
const category = ref('all');
const updating = ref(false);
const lastUpdate = ref('—');
const expandedId = ref(null);
const newsCollapsed = ref(false);
const analysisCollapsed = ref(false);
const phase = ref('idle');
const sortBy = ref('urgency');
const stepIdx = ref(0);
const listRef = ref(null);

// Live data
const articles = ref([]);
const analysisItems = ref([]);
const analysisTldr = ref([]);
const analysisSummary = ref('');
const analysisError = ref(null);

const agentSteps = [
  'Connecting to scraper API…',
  'Fetching articles…',
  'Sending to LLM analyst…',
  'Parsing structured results…',
  'Rendering output…',
];

// ── Split pane ─────────────────────────────────────────────────────────────
const _initSplit = (() => {
  try { const v = localStorage.getItem('khaberni_split'); return v ? parseFloat(v) : 55; } catch { return 55; }
})();
const splitSize = ref(_initSplit);
const containerRef = ref(null);
let dragging = false;

const categories = computed(() => [
  { id:'all', label: t.value.all },
  { id:'culture', label: t.value.culture },
  { id:'tech', label: t.value.tech },
  { id:'economy', label: t.value.economy },
  { id:'social', label: t.value.social },
  { id:'lifestyle', label: t.value.lifestyle },
  { id:'sport', label: t.value.sport },
  { id:'politics', label: t.value.politics },
  { id:'weather', label: t.value.weather },
]);

const sortedNews = computed(() => {
  let list = [...articles.value];
  if (category.value && category.value !== 'all') {
    list = list.filter(a => a.cat === category.value);
  }
  
  return list.sort((a, b) => {
    if (sortBy.value === 'urgency') return (b.urgency || 0) - (a.urgency || 0);
    if (sortBy.value === 'relevance') return (b.relevance || 0) - (a.relevance || 0);
    if (sortBy.value === 'newest') {
      const da = new Date(a.raw_date || 0);
      const db = new Date(b.raw_date || 0);
      return db - da;
    }
    return 0;
  });
});

const bothVisible = computed(() => !newsCollapsed.value && !analysisCollapsed.value);
const newsWidth = computed(() => {
  if (newsCollapsed.value) return '0%';
  if (analysisCollapsed.value) return '100%';
  return splitSize.value + '%';
});
const analysisWidth = computed(() => {
  if (analysisCollapsed.value) return '0%';
  if (newsCollapsed.value) return '100%';
  return (100 - splitSize.value) + '%';
});

// ── Derived analysis display data ──────────────────────────────────────────
const RESULT_SUMMARY = computed(() => {
  if (analysisTldr.value.length > 0) {
    return analysisTldr.value.join(' ');
  }
  return analysisSummary.value || 'No analysis available yet. Click "Run Analysis" to generate an intelligence brief.';
});

const RESULT_CLUSTERS = computed(() => {
  const items = analysisItems.value;
  if (!items.length) return [];

  const highItems = items.filter(i => i.relevance_score >= 70);
  const medItems = items.filter(i => i.relevance_score >= 40 && i.relevance_score < 70);
  const lowItems = items.filter(i => i.relevance_score < 40);

  const clusters = [];
  if (highItems.length) clusters.push({ theme: 'High Priority', urgency: 90, articles: highItems.map(i => i.headline) });
  if (medItems.length) clusters.push({ theme: 'Medium Priority', urgency: 60, articles: medItems.map(i => i.headline) });
  if (lowItems.length) clusters.push({ theme: 'Lower Priority', urgency: 30, articles: lowItems.map(i => i.headline) });
  return clusters;
});

const RESULT_RECS = computed(() => {
  return analysisTldr.value.length > 0
    ? analysisTldr.value
    : ['Run the agent to get strategic recommendations.'];
});



/**
 * Heuristic automated categorization
 */
function autoCategorize(title, body = '') {
  const content = (title + ' ' + body).toLowerCase();
  
  const mapping = {
    tech: ['ai', 'intelligence artificielle', 'startup', 'digital', 'data', 'api', 'software', 'robot', 'cyber', 'meta', 'google', 'apple', 'microsoft'],
    economy: ['bourse', 'dinar', 'imf', 'fmi', 'growth', 'inflation', 'banque', 'bank', 'finance', 'business', 'entreprises', 'marché'],
    politics: ['gouvernement', 'parlement', 'vote', 'élection', 'ministre', 'policy', 'summit', 'sommet', 'democratie', 'onu', 'un'],
    culture: ['art', 'cinéma', 'film', 'musique', 'music', 'exhibition', 'expo', 'festival', 'urban', 'lifestyle', 'théâtre', 'misk'],
    lifestyle: ['food', 'cuisine', 'travel', 'gastronomy', 'voyage', 'restaurant', 'table', 'gastronomie'],
    sport: ['football', 'champions league', 'psg', 'bayern', 'match', 'score', 'sport', 'tennis', 'atp'],
    weather: ['météo', 'pluie', 'soleil', 'température', 'climat', 'weather', 'rain', 'forecast'],
    social: ['société', 'gen z', 'jeunes', 'social media', 'trends', 'tendances', 'communauté', 'femme', 'women']
  };

  for (const [cat, keywords] of Object.entries(mapping)) {
    if (keywords.some(k => content.includes(k))) return cat;
  }
  
  return 'culture'; // Default to culture/urban for editorial feel if no match
}

// ── API calls ──────────────────────────────────────────────────────────────
async function fetchArticles() {
  try {
    const params = new URLSearchParams({ window: timeWindow.value });
    const res = await fetch(`${SCRAPER_BASE}/articles?${params}`);
    if (!res.ok) throw new Error(`Scraper returned ${res.status}`);
    const json = await res.json();
    const raw = json.data || [];

    articles.value = raw.map((a, i) => {
      const initialCat = a.category ? a.category.toLowerCase() : autoCategorize(a.title, a.body);
      const scores = calculateScores(a.title, a.body, a.published_at);
      
      return {
        id: i + 1,
        cat: initialCat,
        urgency: scores.urgency,
        relevance: scores.relevance,
        title: a.title || 'Untitled',
        source: a.source || 'Unknown',
        time: formatRelativeTime(a.published_at),
        raw_date: a.published_at,
        tag: scores.tag,
        body: a.body || '',
        url: a.url || '',
      };
    });

    const now = new Date();
    lastUpdate.value = `Today, ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
    
    // Staggered entrance for news rows
    nextTick(() => {
      staggerList('.news-row', { 
        delay: 0.1, 
        y: 15,
        onComplete: () => {
          document.querySelectorAll('.news-row').forEach(row => scrollReveal(row));
        }
      });
    });
  } catch (err) {
    console.error('[NewsDashboard] Failed to fetch articles:', err);
  }
}

function formatRelativeTime(dateStr) {
  if (!dateStr) return 'unknown';
  try {
    const d = new Date(dateStr);
    const diffMs = Date.now() - d.getTime();
    const diffH = Math.floor(diffMs / 3600000);
    if (diffH < 1) return 'just now';
    if (diffH < 24) return `${diffH}h ago`;
    const diffD = Math.floor(diffH / 24);
    return `${diffD}d ago`;
  } catch {
    return dateStr;
  }
}

async function triggerScrape() {
  const res = await fetch(`${SCRAPER_BASE}/scrape`, { method: 'POST' });
  if (!res.ok) throw new Error(`Scrape failed (${res.status})`);
}

// ── Handlers ───────────────────────────────────────────────────────────────
function toggleNews() {
  if (!newsCollapsed.value && analysisCollapsed.value) analysisCollapsed.value = false;
  newsCollapsed.value = !newsCollapsed.value;
}
function toggleAnalysis() {
  if (!analysisCollapsed.value && newsCollapsed.value) newsCollapsed.value = false;
  analysisCollapsed.value = !analysisCollapsed.value;
}

async function handleUpdate() {
  updating.value = true;
  try {
    await triggerScrape();
    await fetchArticles();
  } catch (err) {
    console.error('[NewsDashboard] Update failed:', err);
  } finally {
    updating.value = false;
  }
}

async function runAnalysis() {
  phase.value = 'running';
  stepIdx.value = 0;
  analysisError.value = null;

  // Run typewriter for first step
  nextTick(() => {
    typewriter('#agent-step-0', agentSteps[0]);
  });

  const runVisualSteps = async () => {
    for (let i = 0; i < agentSteps.length - 1; i++) {
      stepIdx.value = i;
      await new Promise(r => setTimeout(r, 1000));
      if (i + 1 < agentSteps.length) {
        typewriter(`#agent-step-${i+1}`, agentSteps[i+1]);
      }
    }
  };
  
  const stepPromise = runVisualSteps();

  try {
    const params = new URLSearchParams({ window: timeWindow.value });
    const res = await fetch(`${ANALYST_BASE}/analyze?${params}`);
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `Agent returned ${res.status}`);
    }
    const json = await res.json();
    const result = json.data || {};

    analysisItems.value = result.items || [];
    analysisTldr.value = result.tldr || [];

    analysisItems.value.forEach(item => {
      const target = articles.value.find(a => a.id === item.id);
      if (target) {
        target.cat = item.category;
        target.urgency = item.urgency_score;
        target.relevance = item.relevance_score;
        target.why_it_matters = item.why_it_matters;
        if (item.headline && item.headline !== 'N/A') {
          target.title = item.headline;
        }
      }
    });

    if (analysisItems.value.length > 0) {
      const topItems = analysisItems.value.slice(0, 3);
      analysisSummary.value = topItems
        .map(i => i.why_it_matters)
        .filter(Boolean)
        .join(' ');
      
      // Animate summary reveal
      nextTick(() => {
        wordReveal('.result-summary');
      });
    }
  } catch (err) {
    analysisError.value = err.message;
    console.error('[NewsDashboard] Analysis failed:', err);
  } finally {
    await stepPromise;
    stepIdx.value = agentSteps.length;
    setTimeout(() => {
      phase.value = analysisError.value ? 'idle' : 'done';
    }, 400);
  }
}



// ── Drag to resize ─────────────────────────────────────────────────────────
function startDrag(e) {
  e.preventDefault();
  dragging = true;
  document.body.style.cursor = 'col-resize';
  document.body.style.userSelect = 'none';
  window.addEventListener('mousemove', onDragMove);
  window.addEventListener('mouseup', stopDrag);
}
function onDragMove(e) {
  if (!dragging || !containerRef.value) return;
  const rect = containerRef.value.getBoundingClientRect();
  const pct = ((e.clientX - rect.left) / rect.width) * 100;
  splitSize.value = Math.max(18, Math.min(82, pct));
  try { localStorage.setItem('khaberni_split', splitSize.value); } catch {}
}
function stopDrag() {
  dragging = false;
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  window.removeEventListener('mousemove', onDragMove);
  window.removeEventListener('mouseup', stopDrag);
}

// ── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => {
  fetchArticles();

  // Magnetic pills
  setTimeout(() => {
    document.querySelectorAll('.cat-btn, .time-btn, .run-btn').forEach(el => magneticHover(el, 0.2));
  }, 1000);
});

watch([timeWindow, category], () => {
  fetchArticles();
});

watch(phase, (p) => {
  if (p === 'done') {
    nextTick(() => {
      entrance('.result-card, .cluster-item, .signal-item', { stagger: 0.1, y: 20 });
      wordReveal('.result-summary');
    });
  }
});

onUnmounted(() => {
  window.removeEventListener('mousemove', onDragMove);
  window.removeEventListener('mouseup', stopDrag);
});
</script>

<style scoped>
.news-screen {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* Top bar */
.news-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  background: var(--bg);
}

.pane-toggles {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sep { color: var(--border2); font-size: 14px; opacity: 0.5; }

.pane-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border2);
  color: var(--text);
  font-family: var(--ff-mono);
  font-size: 11px;
  cursor: pointer;
  letter-spacing: 0.06em;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.pane-toggle:hover { background: rgba(255, 255, 255, 0.08); border-color: var(--text3); }

.pane-toggle.collapsed {
  background: transparent;
  border-color: var(--border);
  color: var(--text3);
}

.toggle-arrow { color: var(--text2); font-size: 10px; opacity: 0.7; }

.run-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: transparent;
  border: 1px solid var(--accent);
  color: var(--accent);
  font-family: var(--ff-mono);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.run-btn:hover { background: var(--accent); color: #000; }

/* Split body */
.split-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* News pane */
.news-pane {
  min-width: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.pane-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.controls-left { display: flex; align-items: center; gap: 16px; }
.pane-title { font-family: var(--ff-head); font-size: var(--text-base); font-weight: 800; letter-spacing: var(--letter-spacing-display); text-transform: uppercase; }
.last-update { font-family: var(--ff-mono); font-size: 10px; color: var(--text3); }

.controls-right { display: flex; align-items: center; gap: 12px; }

.time-toggle {
  display: flex;
  border: 1px solid var(--border);
  overflow: hidden;
}
.time-btn {
  padding: 5px 12px;
  background: transparent;
  border: none;
  border-right: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--ff-mono);
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.time-btn:last-child { border-right: none; }
.time-btn.active { background: var(--bg3); color: var(--accent); }

.update-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: var(--accent);
  border: none;
  color: #000;
  font-family: var(--ff-head);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s;
}
.update-btn.updating { background: var(--bg2); color: var(--text3); }

/* Sort Bar */
.sort-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 24px;
  height: 40px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.sort-hint {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.1em;
}
.sort-btns {
  display: flex;
  gap: 8px;
}
.sort-btn {
  padding: 2px 8px;
  background: transparent;
  border: 1px solid transparent;
  color: var(--text2);
  font-family: var(--ff-mono);
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.sort-btn:hover { color: var(--text); }
.sort-btn.active {
  background: var(--bg3);
  border-color: var(--border2);
  color: var(--accent);
}

/* Category bar */
.cat-bar {
  display: flex;
  gap: 4px;
  padding: 0 24px;
  height: 44px;
  align-items: center;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  overflow-x: auto;
}

.cat-btn {
  padding: 4px 12px;
  background: transparent;
  border: 1px solid transparent;
  color: var(--text2);
  font-family: var(--ff-body);
  font-size: var(--text-sm);
  font-weight: 400;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.cat-btn:hover { color: var(--text); }
.cat-btn.active { border-color: var(--accent); color: var(--accent); font-weight: 600; }

/* News list */
.news-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 24px 32px;
}

.sort-label {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--text3);
  letter-spacing: 0.15em;
  padding: 20px 0 12px;
}

.news-row {
  border-bottom: 1px solid var(--border);
  padding: 20px 0;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform, opacity;
}
.news-row:hover { background: rgba(255, 255, 255, 0.01); transform: translateX(4px); }
.news-row.expanded {
  background: rgba(255, 255, 255, 0.02);
  margin: 0 -24px;
  padding: 24px;
  border-left: 4px solid var(--accent);
}

.row-main { display: flex; align-items: flex-start; gap: 20px; }

.row-idx { font-family: var(--ff-mono); font-size: 11px; color: var(--text3); min-width: 24px; padding-top: 4px; opacity: 0.5; }

.cat-dot { width: 6px; height: 6px; border-radius: 50%; margin-top: 8px; flex-shrink: 0; }

.row-content { flex: 1; min-width: 0; }

.row-meta { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }

.tag-pill {
  font-family: var(--ff-mono);
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border: 1px solid;
  letter-spacing: 0.08em;
}

.row-source { font-family: var(--ff-mono); font-size: 10px; color: var(--text3); }

.row-title {
  font-family: var(--ff-head);
  font-size: var(--text-md);
  font-weight: 700;
  line-height: 1.3;
  color: var(--text);
  letter-spacing: -0.01em;
}

.row-expanded { margin-top: 16px; }

.row-desc {
  font-family: var(--ff-body);
  font-size: var(--text-sm);
  color: var(--text2);
  line-height: 1.8;
  margin-bottom: 24px;
}

.score-compact { text-align: right; min-width: 48px; }
.sc-label { font-family: var(--ff-mono); font-size: 9px; color: var(--text3); letter-spacing: 0.1em; margin-bottom: 4px; }
.sc-val { font-family: var(--ff-mono); font-size: 14px; font-weight: 600; }

/* Drag handle */
.drag-handle {
  width: 1px;
  flex-shrink: 0;
  cursor: col-resize;
  background: var(--border);
  position: relative;
  z-index: 10;
  transition: background 0.3s;
}
.drag-handle:hover { background: var(--accent); }
.drag-handle::after {
  content: '';
  position: absolute;
  inset: 0 -4px;
}

/* Analysis pane */
.analysis-pane {
  min-width: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.01);
}

.analysis-header {
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.analysis-label { font-family: var(--ff-mono); font-size: 11px; color: var(--text3); letter-spacing: 0.15em; font-weight: 600; }

.status-done span { font-family: var(--ff-mono); font-size: 10px; color: var(--green); font-weight: 700; }

.analysis-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.result-card-label {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--text3);
  letter-spacing: 0.15em;
  margin-bottom: 12px;
  text-transform: uppercase;
}

.result-summary { font-family: var(--ff-body); font-size: var(--text-sm); color: var(--text); line-height: 1.8; }

.cluster-item {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  padding: 16px 20px;
  margin-bottom: 2px;
  transition: all 0.3s ease;
}
.cluster-item:hover { background: rgba(255, 255, 255, 0.04); border-color: var(--border2); }

.cluster-theme { font-family: var(--ff-head); font-size: 14px; font-weight: 700; color: var(--text); }

.signal-item {
  display: flex;
  gap: 16px;
  padding: 14px 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  margin-bottom: 2px;
}

.signal-text { font-family: var(--ff-body); font-size: 13px; color: var(--text2); line-height: 1.7; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
