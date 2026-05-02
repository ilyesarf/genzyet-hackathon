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
            <div class="view-toggle">
              <button class="view-btn" :class="{ active: viewMode === 'graph' }" @click="viewMode = 'graph'" title="Graph View">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><circle cx="4" cy="4" r="2.5" stroke="currentColor" stroke-width="1.2"/><circle cx="12" cy="6" r="2" stroke="currentColor" stroke-width="1.2"/><circle cx="6" cy="12" r="1.8" stroke="currentColor" stroke-width="1.2"/><line x1="6" y1="5" x2="10" y2="5.5" stroke="currentColor" stroke-width="0.8" opacity="0.5"/><line x1="5" y1="6" x2="6" y2="10" stroke="currentColor" stroke-width="0.8" opacity="0.5"/></svg>
              </button>
              <button class="view-btn" :class="{ active: viewMode === 'list' }" @click="viewMode = 'list'" title="List View">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="2" y="3" width="12" height="1.5" fill="currentColor"/><rect x="2" y="7" width="8" height="1.5" fill="currentColor"/><rect x="2" y="11" width="10" height="1.5" fill="currentColor"/></svg>
              </button>
            </div>
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

        <!-- Sort bar (list view only) -->
        <div v-if="viewMode === 'list'" class="sort-bar">
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

        <!-- Graph view -->
        <div v-if="viewMode === 'graph'" class="graph-container" ref="graphContainerRef">
          <canvas ref="graphCanvasRef"></canvas>
          <div v-if="hoveredNode" class="graph-tooltip" :style="{ left: tooltipPos.x + 'px', top: tooltipPos.y + 'px' }">
            <div class="tooltip-tag" v-if="hoveredNode.tag">{{ hoveredNode.tag }}</div>
            <div class="tooltip-title">{{ hoveredNode.title }}</div>
            <div class="tooltip-meta">{{ hoveredNode.source }} · {{ hoveredNode.time }}</div>
            <div class="tooltip-scores">
              <span class="tooltip-urg">URG {{ hoveredNode.urgency }}</span>
              <span class="tooltip-rel">REL {{ hoveredNode.relevance }}</span>
            </div>
          </div>
        </div>

        <!-- News list -->
        <div v-if="viewMode === 'list'" class="news-list" ref="listRef">
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
                        <div class="score-fill" :style="{ width: item.urgency + '%', background: urgencyColor(item.urgency) }"></div>
                      </div>
                      <span class="score-val" :style="{ color: urgencyColor(item.urgency) }">{{ item.urgency }}</span>
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
                  <div class="sc-val" :style="{ color: urgencyColor(item.urgency) }">{{ item.urgency }}</div>
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
              <div class="result-summary md-rendered" v-html="renderMarkdown(RESULT_SUMMARY)"></div>
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
                  <div class="signal-text md-rendered" v-html="renderMarkdown(rec)"></div>
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
import { marked } from 'marked';
import { useAnimation } from '@/composables/useAnimation';
import { useNewsLogic } from '@/composables/useNewsLogic';

const t = inject('t');
const { entrance, staggerList, magneticHover, typewriter, wordReveal, scrollReveal, gsap } = useAnimation();
const { autoCategorize, calculateScores } = useNewsLogic();

const SCRAPER_BASE = '/api/scraper';
const ANALYST_BASE = '/api/analyst';

// ── State ──────────────────────────────────────────────────────────────────
const timeWindow = ref('24');
const viewMode = ref('graph');
const updating = ref(false);
const lastUpdate = ref('—');
const expandedId = ref(null);
const newsCollapsed = ref(false);
const analysisCollapsed = ref(true);
const phase = ref('idle');
const sortBy = ref('urgency');
const stepIdx = ref(0);
const listRef = ref(null);

// Graph state
const graphCanvasRef = ref(null);
const graphContainerRef = ref(null);
const hoveredNode = ref(null);
const tooltipPos = ref({ x: 0, y: 0 });
let graphNodes = [];
let graphAnimId = null;

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

const sortedNews = computed(() => {
  let list = [...articles.value];
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

// ── Urgency color helper (red → orange → yellow → grey) ───────────────────
function urgencyColor(urgency) {
  const t = Math.max(0, Math.min(1, (urgency - 10) / 89));
  if (t > 0.7) {
    // High urgency: red
    return `rgba(220, 50, 47, ${0.7 + (t - 0.7) * 1})`;
  } else if (t > 0.4) {
    // Medium-high: orange
    const s = (t - 0.4) / 0.3;
    const r = Math.round(230 + s * -10);
    const g = Math.round(140 - s * 90);
    return `rgba(${r}, ${g}, 30, ${0.55 + s * 0.25})`;
  } else if (t > 0.15) {
    // Medium-low: yellow
    const s = (t - 0.15) / 0.25;
    const r = Math.round(180 + s * 50);
    const g = Math.round(170 - s * 30);
    return `rgba(${r}, ${g}, 40, ${0.4 + s * 0.15})`;
  } else {
    // Low urgency: grey
    return `rgba(120, 120, 115, ${0.25 + t * 1})`;
  }
}

function urgencyGlow(urgency) {
  const t = Math.max(0, Math.min(1, (urgency - 10) / 89));
  if (t > 0.7) return `rgba(220, 50, 47, ${0.2 + (t - 0.7) * 0.6})`;
  if (t > 0.4) return `rgba(230, 120, 30, ${0.1 + (t - 0.4) * 0.3})`;
  if (t > 0.15) return `rgba(200, 180, 40, ${0.05 + (t - 0.15) * 0.15})`;
  return 'transparent';
}

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
    
    // Animate based on current view
    nextTick(() => {
      if (viewMode.value === 'list') {
        staggerList('.news-row', { 
          delay: 0.1, 
          y: 15,
          onComplete: () => {
            document.querySelectorAll('.news-row').forEach(row => scrollReveal(row));
          }
        });
      } else {
        initGraph();
      }
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

// ── Graph rendering (static layout) ────────────────────────────────────────
function initGraph() {
  const canvas = graphCanvasRef.value;
  const container = graphContainerRef.value;
  if (!canvas || !container) return;

  destroyGraph();

  const rect = container.getBoundingClientRect();
  const W = rect.width;
  const H = rect.height;
  if (W < 10 || H < 10) return;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = W * dpr;
  canvas.height = H * dpr;
  canvas.style.width = W + 'px';
  canvas.style.height = H + 'px';
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  const cx = W / 2;
  const cy = H / 2;
  const data = articles.value;
  if (!data.length) return;

  // Static layout: place nodes in a spiral, high-urgency closer to center
  const sorted = [...data].sort((a, b) => b.urgency - a.urgency).slice(0, 25);
  const pad = 30;
  graphNodes = sorted.map((a, i) => {
    const r = 28 + (a.urgency / 99) * 32;
    const goldenAngle = Math.PI * (3 - Math.sqrt(5));
    const angle = i * goldenAngle;
    const maxR = Math.min(W, H) / 2 - pad - r;
    const frac = Math.sqrt(i / Math.max(1, sorted.length - 1));
    const dist = 20 + frac * maxR;
    return {
      ...a,
      x: cx + Math.cos(angle) * dist,
      y: cy + Math.sin(angle) * dist,
      r,
    };
  });

  // Resolve overlaps with a few iterations of push-apart
  for (let iter = 0; iter < 80; iter++) {
    for (let i = 0; i < graphNodes.length; i++) {
      for (let j = i + 1; j < graphNodes.length; j++) {
        const a = graphNodes[i], b = graphNodes[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const minD = a.r + b.r + 24;
        if (dist < minD) {
          const push = (minD - dist) / 2;
          const nx = dx / dist, ny = dy / dist;
          a.x += nx * push; a.y += ny * push;
          b.x -= nx * push; b.y -= ny * push;
        }
      }
      // Keep inside bounds
      const n = graphNodes[i];
      n.x = Math.max(n.r + pad, Math.min(W - n.r - pad, n.x));
      n.y = Math.max(n.r + pad, Math.min(H - n.r - pad, n.y));
    }
  }

  // Draw function
  function draw() {
    ctx.clearRect(0, 0, W, H);

    // Connection lines between nearby nodes
    for (let i = 0; i < graphNodes.length; i++) {
      for (let j = i + 1; j < graphNodes.length; j++) {
        const a = graphNodes[i], b = graphNodes[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const maxDist = 160;
        if (dist < maxDist) {
          const alpha = (1 - dist / maxDist) * 0.1;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(255, 255, 255, ${alpha})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }

    // Draw nodes
    for (const n of graphNodes) {
      const isHovered = hoveredNode.value && hoveredNode.value.id === n.id;
      const color = urgencyColor(n.urgency);
      const glow = urgencyGlow(n.urgency);

      // Glow
      if (glow !== 'transparent' || isHovered) {
        ctx.beginPath();
        const gr = ctx.createRadialGradient(n.x, n.y, n.r * 0.3, n.x, n.y, n.r * (isHovered ? 3 : 2.2));
        gr.addColorStop(0, isHovered ? urgencyGlow(Math.min(99, n.urgency + 20)) : glow);
        gr.addColorStop(1, 'transparent');
        ctx.fillStyle = gr;
        ctx.arc(n.x, n.y, n.r * (isHovered ? 3 : 2.2), 0, Math.PI * 2);
        ctx.fill();
      }

      // Circle
      ctx.beginPath();
      ctx.arc(n.x, n.y, isHovered ? n.r * 1.15 : n.r, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();

      // Border
      ctx.strokeStyle = isHovered ? 'rgba(255,255,255,0.6)' : 'rgba(255,255,255,0.06)';
      ctx.lineWidth = isHovered ? 1.5 : 0.5;
      ctx.stroke();

      // Headline text
      const drawR = isHovered ? n.r * 1.15 : n.r;
      const fontSize = Math.max(8, drawR * 0.28);
      ctx.fillStyle = n.urgency > 60 ? 'rgba(255,255,255,0.92)' : 'rgba(255,255,255,0.65)';
      ctx.font = `600 ${fontSize}px 'DM Sans', sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const maxW = drawR * 1.5;
      const words = n.title.split(' ');
      const lines = [];
      let cur = '';
      for (const w of words) {
        const test = cur ? cur + ' ' + w : w;
        if (ctx.measureText(test).width > maxW && cur) {
          lines.push(cur);
          cur = w;
        } else {
          cur = test;
        }
      }
      if (cur) lines.push(cur);
      const maxLines = Math.max(2, Math.floor(drawR / (fontSize * 1.15)));
      const visible = lines.slice(0, maxLines);
      if (lines.length > maxLines) {
        visible[visible.length - 1] = visible[visible.length - 1].slice(0, -1) + '…';
      }
      const lh = fontSize * 1.2;
      const startY = n.y - ((visible.length - 1) * lh) / 2;
      for (let li = 0; li < visible.length; li++) {
        ctx.fillText(visible[li], n.x, startY + li * lh, maxW);
      }
    }
  }

  // Mouse interaction - just redraw on hover changes
  const onMove = (e) => {
    const cr = canvas.getBoundingClientRect();
    const mx = e.clientX - cr.left;
    const my = e.clientY - cr.top;
    let found = null;
    for (const n of graphNodes) {
      const dx = mx - n.x;
      const dy = my - n.y;
      if (Math.sqrt(dx * dx + dy * dy) < n.r + 4) { found = n; break; }
    }
    const prev = hoveredNode.value;
    hoveredNode.value = found;
    if (found) {
      tooltipPos.value = { x: found.x + found.r + 12, y: found.y - 20 };
      canvas.style.cursor = 'pointer';
    } else {
      canvas.style.cursor = 'default';
    }
    if (prev !== found) draw();
  };
  canvas.addEventListener('mousemove', onMove);

  const onClick = () => {
    if (hoveredNode.value && hoveredNode.value.url) {
      window.open(hoveredNode.value.url, '_blank');
    }
  };
  canvas.addEventListener('click', onClick);

  // Initial draw
  draw();
}

function destroyGraph() {
  if (graphAnimId) { cancelAnimationFrame(graphAnimId); graphAnimId = null; }
  hoveredNode.value = null;
}

// ── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => {
  fetchArticles();

  // Magnetic pills
  setTimeout(() => {
    document.querySelectorAll('.time-btn, .run-btn, .view-btn').forEach(el => magneticHover(el, 0.2));
  }, 1000);
});

watch(timeWindow, () => {
  fetchArticles();
});

watch(viewMode, (mode) => {
  nextTick(() => {
    if (mode === 'graph') {
      initGraph();
    } else {
      destroyGraph();
      staggerList('.news-row', { delay: 0.1, y: 15 });
    }
  });
});

watch(() => articles.value.length, () => {
  if (viewMode.value === 'graph') {
    nextTick(() => initGraph());
  }
});

watch(analysisCollapsed, () => {
  if (viewMode.value === 'graph') {
    nextTick(() => setTimeout(() => initGraph(), 50));
  }
});

watch(phase, (p) => {
  if (p === 'done') {
    nextTick(() => {
      entrance('.result-card, .cluster-item, .signal-item', { stagger: 0.1, y: 20 });
      wordReveal('.result-summary');
      if (viewMode.value === 'graph') initGraph();
    });
  }
});

function renderMarkdown(md) {
  if (!md) return '';
  return marked.parse(String(md));
}

onUnmounted(() => {
  destroyGraph();
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

/* View toggle */
.view-toggle {
  display: flex;
  border: 1px solid var(--border);
  overflow: hidden;
}
.view-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 30px;
  background: transparent;
  border: none;
  border-right: 1px solid var(--border);
  color: var(--text3);
  cursor: pointer;
  transition: all 0.2s;
}
.view-btn:last-child { border-right: none; }
.view-btn:hover { color: var(--text); background: rgba(255,255,255,0.03); }
.view-btn.active { background: var(--bg3); color: var(--accent); }

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

/* ── Markdown rendered output ── */
.md-rendered { font-family: var(--ff-body); font-size: var(--text-sm); color: var(--text2); line-height: 1.8; }
.md-rendered p { margin: 0 0 8px; }
.md-rendered p:last-child { margin-bottom: 0; }
.md-rendered strong { color: var(--text); font-weight: 700; }
.md-rendered em { color: var(--text2); font-style: italic; }
.md-rendered ul, .md-rendered ol { padding-left: 20px; margin: 6px 0; }
.md-rendered li { margin-bottom: 4px; }
.md-rendered code { font-family: var(--ff-mono); font-size: 11px; background: rgba(255,255,255,0.06); padding: 1px 5px; border-radius: 2px; }
.md-rendered h1, .md-rendered h2, .md-rendered h3 { font-family: var(--ff-head); font-weight: 700; color: var(--text); margin: 10px 0 6px; letter-spacing: var(--letter-spacing-display); }
.md-rendered h3 { font-size: var(--text-base); }

/* Graph view */
.graph-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: radial-gradient(ellipse at center, rgba(20,10,10,0.3) 0%, transparent 70%);
}
.graph-container canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.graph-tooltip {
  position: absolute;
  pointer-events: none;
  background: rgba(8, 8, 8, 0.92);
  border: 1px solid var(--border2);
  padding: 12px 16px;
  max-width: 280px;
  z-index: 20;
  backdrop-filter: blur(8px);
  animation: tooltipIn 0.15s ease-out;
}
@keyframes tooltipIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
.tooltip-tag {
  font-family: var(--ff-mono);
  font-size: 9px;
  font-weight: 700;
  color: var(--red);
  letter-spacing: 0.1em;
  margin-bottom: 4px;
}
.tooltip-title {
  font-family: var(--ff-head);
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
  margin-bottom: 6px;
}
.tooltip-meta {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--text3);
  margin-bottom: 8px;
}
.tooltip-scores {
  display: flex;
  gap: 12px;
  font-family: var(--ff-mono);
  font-size: 10px;
  font-weight: 600;
}
.tooltip-urg { color: var(--red); }
.tooltip-rel { color: var(--accent); }
</style>
