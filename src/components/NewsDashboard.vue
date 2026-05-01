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

        <!-- News list -->
        <div class="news-list">
          <div class="sort-label">↑ URGENCY</div>
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
                  <p class="row-desc">This article has been flagged as relevant to your current communication strategy. The data analyst agent identified key themes: market positioning, stakeholder impact, and timeline sensitivity. Consider reviewing your messaging around this topic within the next 4–6 hours for maximum relevance.</p>
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
            <button class="agent-run-btn" @click="runAnalysis">{{ t.run_agent }}</button>
          </div>

          <!-- Running -->
          <div v-else-if="phase === 'running'" class="agent-steps">
            <div v-for="(step, i) in agentSteps" :key="i" class="agent-step">
              <div class="step-dot" :class="i < stepIdx ? 'done' : i === stepIdx ? 'active' : 'pending'"></div>
              <span class="step-text" :class="i < stepIdx ? 'done' : i === stepIdx ? 'active' : 'pending'">{{ step }}</span>
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
import { ref, computed, inject, onMounted, onUnmounted } from 'vue';

const t = inject('t');

const CAT_COLORS = {
  tech: 'var(--blue)',
  economy: 'var(--green)',
  politics: 'var(--red)',
  social: 'var(--accent)',
  sport: 'oklch(65% 0.15 290)',
  weather: 'oklch(65% 0.12 200)',
};

const NEWS_DATA = [
  { id:1, cat:'tech', urgency:92, relevance:88, title:'Meta launches AI-powered ad personalisation suite for agencies', source:'TechCrunch', time:'2h ago', tag:'BREAKING' },
  { id:2, cat:'economy', urgency:85, relevance:91, title:'IMF revises global growth forecast downward amid trade tensions', source:'Reuters', time:'3h ago', tag:'ALERT' },
  { id:3, cat:'politics', urgency:78, relevance:72, title:'European Parliament votes on new digital markets regulation', source:'Le Monde', time:'4h ago', tag:null },
  { id:4, cat:'social', urgency:65, relevance:80, title:'Gen Z abandons traditional news for short-video summaries', source:'Bloomberg', time:'5h ago', tag:null },
  { id:5, cat:'tech', urgency:88, relevance:94, title:'OpenAI announces enterprise API with custom model fine-tuning', source:'The Verge', time:'6h ago', tag:'HOT' },
  { id:6, cat:'sport', urgency:55, relevance:60, title:'Champions League: PSG vs Bayern preview — tactical breakdown', source:"L'Équipe", time:'7h ago', tag:null },
  { id:7, cat:'economy', urgency:74, relevance:76, title:'Tunisian dinar stabilises as central bank raises interest rates', source:'TAP', time:'8h ago', tag:null },
  { id:8, cat:'tech', urgency:70, relevance:85, title:'Anthropic releases Claude 4.5 with extended context window', source:'Wired', time:'9h ago', tag:null },
  { id:9, cat:'social', urgency:60, relevance:70, title:'Ramadan social media trends: brands missing key moments', source:'Social Media Today', time:'10h ago', tag:null },
  { id:10, cat:'politics', urgency:82, relevance:68, title:'Tunisia to host MENA digital governance summit next month', source:'TAP', time:'11h ago', tag:null },
];

const RESULT_CLUSTERS = [
  { theme:'AI & Tech', count:4, urgency:88, articles:['Meta AI ad suite','OpenAI enterprise API','Claude 4.5 release','EU digital markets vote'] },
  { theme:'Economy', count:2, urgency:80, articles:['IMF growth revision','Tunisian dinar stabilises'] },
  { theme:'Social', count:2, urgency:63, articles:['Gen Z news habits','Ramadan brand moments'] },
  { theme:'Politics', count:2, urgency:80, articles:['EU Parliament vote','MENA governance summit'] },
];
const RESULT_RECS = [
  'Prioritise AI-themed content in client comms this week — tech narrative dominates.',
  'Prepare reactive messaging for economic uncertainty — IMF data may fuel client concerns.',
  'Review social media distribution for younger segments; video-first is critical.',
];
const RESULT_SUMMARY = 'AI infrastructure acceleration dominates the past 24h, with Meta and OpenAI making key enterprise announcements. Economic signals are mixed. Social listening reveals a generational shift in news consumption that directly impacts PR distribution strategy.';

const agentSteps = ['Triggering scraper…','Fetching 9 active sources…','Reading 147 articles…','Computing urgency scores…','Building semantic clusters…','Synthesising summary…'];

// State
const timeWindow = ref('24');
const category = ref('all');
const updating = ref(false);
const lastUpdate = ref('Today, 09:14');
const expandedId = ref(null);
const newsCollapsed = ref(false);
const analysisCollapsed = ref(false);
const phase = ref('idle');
const stepIdx = ref(0);

// Split pane
const _initSplit = (() => {
  try { const v = localStorage.getItem('khaberni_split'); return v ? parseFloat(v) : 55; } catch { return 55; }
})();
const splitSize = ref(_initSplit);
const containerRef = ref(null);
let dragging = false;

const categories = computed(() => [
  { id:'all', label: t.value.all },
  { id:'tech', label: t.value.tech },
  { id:'sport', label: t.value.sport },
  { id:'social', label: t.value.social },
  { id:'weather', label: t.value.weather },
  { id:'politics', label: t.value.politics },
  { id:'economy', label: t.value.economy },
]);

const sortedNews = computed(() => {
  const filtered = NEWS_DATA.filter(n => category.value === 'all' || n.cat === category.value);
  return [...filtered].sort((a, b) => b.urgency - a.urgency);
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

function toggleNews() {
  if (!newsCollapsed.value && analysisCollapsed.value) analysisCollapsed.value = false;
  newsCollapsed.value = !newsCollapsed.value;
}
function toggleAnalysis() {
  if (!analysisCollapsed.value && newsCollapsed.value) newsCollapsed.value = false;
  analysisCollapsed.value = !analysisCollapsed.value;
}

function handleUpdate() {
  updating.value = true;
  setTimeout(() => {
    updating.value = false;
    const now = new Date();
    lastUpdate.value = `Today, ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
  }, 2200);
}

function runAnalysis() {
  phase.value = 'running'; stepIdx.value = 0;
  let step = 0;
  const iv = setInterval(() => {
    step++;
    stepIdx.value = Math.min(step - 1, agentSteps.length - 1);
    if (step >= agentSteps.length) { clearInterval(iv); setTimeout(() => { phase.value = 'done'; }, 300); }
  }, 600);
}

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
onUnmounted(() => { window.removeEventListener('mousemove', onDragMove); window.removeEventListener('mouseup', stopDrag); });
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
  padding: 0 20px;
  height: 52px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  gap: 8px;
}

.pane-toggles {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sep { color: var(--border2); font-size: 12px; }

.pane-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: var(--bg2);
  border: 1px solid var(--border2);
  color: var(--text);
  font-family: var(--ff-mono);
  font-size: 10px;
  cursor: pointer;
  letter-spacing: 0.04em;
  transition: all 0.15s;
}

.pane-toggle.collapsed {
  background: transparent;
  border-color: var(--border);
  color: var(--text3);
}

.toggle-arrow { color: var(--text2); font-size: 9px; }
.pane-toggle.collapsed .toggle-arrow { color: var(--text3); }

.topbar-actions { display: flex; align-items: center; gap: 8px; }

.run-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--ff-mono);
  font-size: 10px;
  cursor: pointer;
  transition: all 0.15s;
}
.run-btn:hover { border-color: var(--accent); color: var(--accent); }

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
  padding: 0 20px;
  height: 48px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.controls-left { display: flex; align-items: center; gap: 12px; }
.pane-title { font-family: var(--ff-head); font-size: 14px; font-weight: 700; letter-spacing: -0.02em; }
.last-update { font-family: var(--ff-mono); font-size: 9px; color: var(--text3); }

.controls-right { display: flex; align-items: center; gap: 8px; }

.time-toggle {
  display: flex;
  border: 1px solid var(--border);
  overflow: hidden;
}
.time-btn {
  padding: 4px 10px;
  background: transparent;
  border: none;
  border-right: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--ff-mono);
  font-size: 10px;
  font-weight: 500;
  cursor: pointer;
}
.time-btn:last-child { border-right: none; }
.time-btn.active { background: var(--accent); color: #000; }

.update-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  background: var(--accent);
  border: 1px solid var(--accent);
  color: #000;
  font-family: var(--ff-head);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: all 0.2s;
}
.update-btn.updating {
  background: var(--bg2);
  border-color: var(--border);
  color: var(--text2);
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 10px;
  height: 10px;
  border: 1.5px solid rgba(0,0,0,0.3);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* Category bar */
.cat-bar {
  display: flex;
  gap: 0;
  padding: 0 20px;
  height: 36px;
  align-items: center;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  overflow-x: auto;
}

.cat-btn {
  padding: 3px 10px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text2);
  font-family: var(--ff-body);
  font-size: 11px;
  font-weight: 400;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
  margin-bottom: -1px;
}
.cat-btn.active { border-bottom-color: var(--accent); color: var(--text); font-weight: 500; }

/* News list */
.news-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px 24px;
}

.sort-label {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.1em;
  padding: 12px 0 8px;
}

.news-row {
  border-bottom: 1px solid var(--border);
  padding: 16px 0;
  cursor: pointer;
  transition: background 0.15s;
}
.news-row.expanded {
  background: var(--bg2);
  margin: 0 -20px;
  padding: 16px 20px;
}

.row-main { display: flex; align-items: flex-start; gap: 16px; }

.row-idx { font-family: var(--ff-mono); font-size: 10px; color: var(--text3); min-width: 20px; padding-top: 2px; }

.cat-dot { width: 6px; height: 6px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }

.row-content { flex: 1; min-width: 0; }

.row-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }

.tag-pill {
  font-family: var(--ff-mono);
  font-size: 9px;
  font-weight: 500;
  padding: 2px 6px;
  border: 1px solid;
  letter-spacing: 0.08em;
}
.tag-pill.breaking { border-color: var(--red); color: var(--red); }
.tag-pill.alert { border-color: var(--accent); color: var(--accent); }
.tag-pill.hot { border-color: var(--green); color: var(--green); }

.row-source { font-family: var(--ff-mono); font-size: 9px; color: var(--text3); }

.row-title {
  font-family: var(--ff-head);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.35;
  color: var(--text);
}

.row-expanded { margin-top: 12px; }

.row-desc {
  font-family: var(--ff-body);
  font-size: 12px;
  color: var(--text2);
  line-height: 1.7;
  margin-bottom: 16px;
}

.score-row { display: flex; gap: 24px; }
.score-item { flex: 1; }
.score-label { font-family: var(--ff-mono); font-size: 9px; color: var(--text3); letter-spacing: 0.08em; margin-bottom: 6px; }
.score-bar { flex: 1; height: 2px; background: var(--border2); position: relative; margin-bottom: 0; display: flex; align-items: center; }
.score-fill { position: absolute; left: 0; top: 0; height: 100%; transition: width 0.5s; }
.score-val { font-family: var(--ff-mono); font-size: 10px; color: var(--accent); min-width: 28px; display: block; margin-top: 4px; }

.row-scores { display: flex; gap: 16px; flex-shrink: 0; }
.score-compact { text-align: right; min-width: 40px; }
.sc-label { font-family: var(--ff-mono); font-size: 8px; color: var(--text3); letter-spacing: 0.06em; margin-bottom: 4px; }
.sc-val { font-family: var(--ff-mono); font-size: 13px; color: var(--text2); font-weight: 500; }
.sc-val.high { color: var(--red); }
.sc-val.mid { color: var(--accent); }

/* Drag handle */
.drag-handle {
  width: 5px;
  flex-shrink: 0;
  cursor: col-resize;
  background: var(--border);
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}
.drag-handle:hover { background: var(--border2); }
.drag-grip {
  width: 3px;
  height: 32px;
  border-radius: 2px;
  background: var(--border2);
}

/* Analysis pane */
.analysis-pane {
  min-width: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.analysis-header {
  padding: 0 20px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.analysis-label { font-family: var(--ff-mono); font-size: 10px; color: var(--text3); letter-spacing: 0.1em; }

.status-done { display: flex; align-items: center; gap: 6px; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; }
.status-dot.green { background: var(--green); }
.status-done span { font-family: var(--ff-mono); font-size: 9px; color: var(--green); }
.status-running { font-family: var(--ff-mono); font-size: 9px; color: var(--accent); }

.analysis-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px 24px;
}

/* Idle */
.analysis-idle {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 14px;
}

.idle-icon {
  width: 56px;
  height: 56px;
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
}

.idle-desc { font-family: var(--ff-body); font-size: 12px; color: var(--text3); text-align: center; max-width: 260px; line-height: 1.6; }

.agent-run-btn {
  padding: 8px 24px;
  background: var(--accent);
  border: none;
  color: #000;
  font-family: var(--ff-head);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

/* Steps */
.agent-steps { display: flex; flex-direction: column; gap: 10px; padding-top: 8px; }
.agent-step { display: flex; align-items: center; gap: 10px; }
.step-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.step-dot.done { background: var(--green); }
.step-dot.active { background: var(--accent); }
.step-dot.pending { background: var(--border2); }
.step-text { font-family: var(--ff-mono); font-size: 11px; }
.step-text.done, .step-text.active { color: var(--text); }
.step-text.pending { color: var(--text3); }
.step-check { font-family: var(--ff-mono); font-size: 9px; color: var(--green); }

/* Results */
.analysis-results { display: flex; flex-direction: column; gap: 16px; }

.result-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  padding: 16px;
}

.result-card-label {
  font-family: var(--ff-mono);
  font-size: 8px;
  color: var(--text3);
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.result-summary { font-family: var(--ff-body); font-size: 12px; color: var(--text); line-height: 1.75; }

.clusters { display: flex; flex-direction: column; gap: 1px; }
.cluster-item {
  background: var(--bg2);
  border: 1px solid var(--border);
  padding: 12px 16px;
}
.cluster-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.cluster-theme { font-family: var(--ff-head); font-size: 12px; font-weight: 600; }
.cluster-urg { font-family: var(--ff-mono); font-size: 9px; color: var(--accent); }
.cluster-urg.high { color: var(--red); }
.cluster-articles { display: flex; flex-wrap: wrap; gap: 4px 12px; }
.cluster-article { font-family: var(--ff-body); font-size: 10px; color: var(--text2); }

.signals { display: flex; flex-direction: column; gap: 1px; }
.signal-item {
  display: flex;
  gap: 12px;
  padding: 10px 14px;
  background: var(--bg2);
  border: 1px solid var(--border);
}
.signal-arrow { font-family: var(--ff-mono); font-size: 10px; color: var(--accent); }
.signal-text { font-family: var(--ff-body); font-size: 11px; color: var(--text2); line-height: 1.6; }

.rerun-btn {
  padding: 7px 16px;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text3);
  font-family: var(--ff-mono);
  font-size: 10px;
  cursor: pointer;
  align-self: flex-start;
}
.rerun-btn:hover { border-color: var(--border2); color: var(--text2); }
</style>
