<template>
  <div class="strategy-container">
    <!-- Header -->
    <div class="strategy-header">
      <span class="header-title">{{ t.strategy_title }}</span>
      <div class="header-actions">
        <button v-if="phase === 'upload' && file" @click="phase = 'news-select'" class="btn-accent">
          {{ t.improve_btn }} →
        </button>
        <template v-if="phase === 'news-select'">
          <button @click="phase = 'upload'" class="btn-back">← BACK</button>
          <button @click="handleImprove" class="btn-accent">RUN AGENT →</button>
        </template>
        <button v-if="phase === 'result'" @click="reset" class="btn-back">NEW STRATEGY</button>
      </div>
    </div>

    <div class="strategy-content">
      <!-- ── UPLOAD PHASE ── -->
      <div v-if="phase === 'upload'" class="upload-phase">
        <!-- Drop zone -->
        <div
          class="drop-zone"
          :class="{ dragging: dragging, hasFile: !!file }"
          @dragover.prevent="dragging = true"
          @dragleave="dragging = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <div v-if="file" class="file-ready">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect x="6" y="3" width="20" height="26" rx="1" stroke="var(--text3)" stroke-width="1.5"/>
              <rect x="10" y="8" width="12" height="8" stroke="var(--accent)" stroke-width="1.2"/>
              <rect x="10" y="19" width="8" height="1.5" fill="var(--text3)"/>
              <rect x="10" y="22" width="12" height="1.5" fill="var(--text3)"/>
            </svg>
            <div class="file-name">{{ file.name }}</div>
            <div class="file-meta">READY · {{ (file.size / 1024).toFixed(0) }} KB</div>
            <div class="file-hint">Click to replace</div>
          </div>
          <div v-else class="drop-hint">
            <div class="icon-wrapper">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <rect x="6" y="3" width="20" height="26" rx="1" stroke="var(--text3)" stroke-width="1.5"/>
                <rect x="10" y="8" width="12" height="8" stroke="var(--accent)" stroke-width="1.2"/>
                <rect x="10" y="19" width="8" height="1.5" fill="var(--text3)"/>
                <rect x="10" y="22" width="12" height="1.5" fill="var(--text3)"/>
              </svg>
            </div>
            <div class="drop-text">{{ t.drop_ppt }}</div>
            <div class="file-types">.PPTX · .PPT · .PDF</div>
          </div>
          <input type="file" ref="fileInput" @change="handleFileChange" style="display: none" accept=".pptx,.ppt,.pdf" />
        </div>

        <button v-if="file" @click="phase = 'news-select'" class="btn-accent large">
          {{ t.improve_btn }} →
        </button>

        <!-- ── HISTORY ── -->
        <div class="history-section">
          <div class="history-header">
            <span class="history-label">PREVIOUS STRATEGIES</span>
            <!-- View toggle -->
            <div class="view-toggle">
              <button
                v-for="view in [{v:'card',icon:'▦'},{v:'list',icon:'☰'}]"
                :key="view.v"
                @click="historyView = view.v"
                :class="{ active: historyView === view.v }"
              >
                {{ view.icon }}
              </button>
            </div>
          </div>

          <!-- CARD VIEW -->
          <div v-if="historyView === 'card'" class="history-grid">
            <div
              v-for="h in HISTORY_DATA"
              :key="h.id"
              class="history-card"
              :class="{ expanded: expandedHistory === h.id }"
              @click="expandedHistory = expandedHistory === h.id ? null : h.id"
            >
              <div class="card-icon"><PptIconSmall /></div>
              <div class="card-title">{{ h.name }}</div>
              <div class="card-date">{{ h.date }}</div>
              <div class="card-improvements">{{ h.improvements }} improvements</div>
              <div v-if="expandedHistory === h.id" class="card-details">
                <div class="details-label">NEWS USED</div>
                <div v-for="(n, i) in h.newsUsed" :key="i" class="details-item">· {{ n }}</div>
                <button @click.stop="reuseStrategy(h)" class="btn-reuse">REUSE →</button>
              </div>
            </div>
          </div>

          <!-- LIST VIEW -->
          <div v-if="historyView === 'list'" class="history-list">
            <div class="list-header">
              <span>STRATEGY</span>
              <span>DATE</span>
              <span>IMPROV.</span>
              <span>NEWS USED</span>
            </div>
            <div
              v-for="h in HISTORY_DATA"
              :key="h.id"
              class="list-item-wrapper"
              @click="expandedHistory = expandedHistory === h.id ? null : h.id"
            >
              <div class="list-item" :class="{ expanded: expandedHistory === h.id }">
                <div>
                  <div class="item-name">{{ h.name }}</div>
                  <div class="item-file">{{ h.file }}</div>
                </div>
                <span class="item-date">{{ h.date }}</span>
                <span class="item-improvements">{{ h.improvements }}</span>
                <span class="item-news-count">{{ h.newsUsed.length }} items</span>
              </div>
              <div v-if="expandedHistory === h.id" class="list-details">
                <div class="details-label">NEWS USED IN THIS STRATEGY</div>
                <div class="news-chips">
                  <span v-for="(n, i) in h.newsUsed" :key="i" class="news-chip">· {{ n }}</span>
                </div>
                <button @click.stop="reuseStrategy(h)" class="btn-reuse">REUSE STRATEGY →</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── NEWS SELECTION PHASE ── -->
      <div v-if="phase === 'news-select'" class="news-select-phase">
        <div class="file-status">
          <PptIconSmall />
          <div>
            <div class="status-filename">{{ file?.name }}</div>
            <div class="status-label">LOADED · READY FOR ENRICHMENT</div>
          </div>
        </div>

        <div class="news-selection">
          <div class="selection-label">SELECT NEWS TO IMPLEMENT IN YOUR STRATEGY</div>
          <div class="selection-hint">
            Choose which news items the agent should cross-reference when generating improvements.
            <span v-if="selectedNews.length > 0" class="accent-text">{{ selectedNews.length }} selected.</span>
          </div>
          <div class="news-list">
            <div
              v-for="item in NEWS_DATA"
              :key="item.id"
              class="news-item"
              :class="{ selected: selectedNews.includes(item.id) }"
              @click="toggleNews(item.id)"
            >
              <!-- Checkbox -->
              <div class="checkbox" :class="{ active: selectedNews.includes(item.id) }">
                <span v-if="selectedNews.includes(item.id)">✓</span>
              </div>
              <!-- Cat dot -->
              <div class="cat-dot" :style="{ background: CAT_COLORS[item.cat] || 'var(--text3)' }"></div>
              <!-- Content -->
              <div class="news-main">
                <div class="news-meta">
                  <span v-if="item.tag" class="tag-pill" :style="{ borderColor: getTagColor(item.tag), color: getTagColor(item.tag) }">
                    {{ item.tag }}
                  </span>
                  <span class="news-source">{{ item.source }} · {{ item.time }}</span>
                </div>
                <div class="news-title">{{ item.title }}</div>
              </div>
              <!-- Scores -->
              <div class="news-scores">
                <div class="score-block">
                  <div class="score-label">URG</div>
                  <div class="score-value" :class="{ high: item.urgency > 80 }">{{ item.urgency }}</div>
                </div>
                <div class="score-block">
                  <div class="score-label">REL</div>
                  <div class="score-value">{{ item.relevance }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="action-footer">
          <button @click="handleImprove" :disabled="selectedNews.length === 0" class="btn-accent" :class="{ disabled: selectedNews.length === 0 }">
            RUN AGENT {{ selectedNews.length > 0 ? `(${selectedNews.length} news items)` : "" }} →
          </button>
          <button @click="handleUseBrief" class="btn-brief" :class="{ loading: briefLoading }">
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
              <rect x="3" y="4" width="10" height="8" rx="1" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="6" cy="8" r="1" fill="currentColor"/>
              <circle cx="10" cy="8" r="1" fill="currentColor"/>
              <path d="M6 2l2 2 2-2" stroke="currentColor" stroke-width="1.2" stroke-linecap="square"/>
            </svg>
            {{ briefLoading ? 'FETCHING BRIEF…' : 'USE BRIEF' }}
          </button>
          <button @click="handleImprove" class="btn-outline-mono">SKIP — USE ALL NEWS</button>
        </div>
      </div>

      <!-- ── IMPROVING PHASE ── -->
      <div v-if="phase === 'improving'" class="improving-phase">
        <div class="agent-title">COMMUNICATION STRATEGIST RUNNING</div>
        <div v-if="selectedNews.length > 0" class="cross-ref">
          <div class="cross-ref-label">CROSS-REFERENCING</div>
          <div class="cross-ref-list">
            <span v-for="n in selectedNewsItems" :key="n.id" class="cross-ref-item">
              · {{ n.title.slice(0, 40) }}…
            </span>
          </div>
        </div>
        <div class="agent-steps">
          <div v-for="(step, i) in agentSteps" :key="i" class="step-row">
            <div class="step-dot" :class="{ completed: i < improvingStep, active: i === improvingStep }"></div>
            <span class="step-text" :class="{ muted: i > improvingStep }">{{ step }}</span>
            <span v-if="i < improvingStep" class="step-check">✓</span>
          </div>
        </div>
      </div>

      <!-- ── RESULT PHASE ── -->
      <div v-if="phase === 'result'" class="result-phase">
        <!-- Status banner -->
        <div class="result-banner">
          <div class="banner-dot"></div>
          <span class="banner-text">AUDIT COMPLETE</span>
          <span v-if="selectedNews.length > 0" class="banner-sub">· {{ selectedNews.length }} news items cross-referenced</span>
        </div>

        <!-- Audit meta header -->
        <div class="audit-meta">
          <div class="meta-item">
            <span class="meta-label">MODE</span>
            <span class="meta-badge" :class="auditMode.toLowerCase()">{{ auditMode }}</span>
          </div>
          <div v-if="auditGap" class="meta-item">
            <span class="meta-label">PRIMARY GAP</span>
            <span class="meta-gap">{{ auditGap }}</span>
          </div>
        </div>

        <!-- D1-D4 Section cards -->
        <div class="audit-sections">
          <div
            v-for="(sec, key) in auditSections"
            :key="key"
            class="audit-section"
            :class="{ collapsed: collapsedSections[key] }"
          >
            <div class="section-header" @click="toggleSection(key)">
              <div class="section-tag" :class="key.toLowerCase()">{{ key }}</div>
              <span class="section-title">{{ sectionLabel(key) }}</span>
              <span class="section-toggle">{{ collapsedSections[key] ? '▸' : '▾' }}</span>
            </div>
            <div v-if="!collapsedSections[key]" class="section-body" v-html="renderMarkdown(sec)"></div>
          </div>
        </div>

        <!-- Fallback: full raw output if no sections parsed -->
        <div v-if="Object.keys(auditSections).length === 0" class="audit-raw">
          <div class="section-body" v-html="renderMarkdown(auditRaw)"></div>
        </div>

        <!-- Actions -->
        <div class="result-actions">
          <button class="btn-export" @click="exportAudit">EXPORT ↗</button>
          <button @click="reset" class="btn-back">NEW STRATEGY</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';

const SCRAPER_BASE = '/api/scraper';
const ANALYST_BASE = '/api/analyst';
const STRATEGIST_BASE = '/api/strategist';

const props = defineProps({
  t: Object,
  lang: String
});

const file = ref(null);
const dragging = ref(false);
const phase = ref('upload'); // upload | news-select | improving | result
const improvingStep = ref(0);
const auditResult = ref('');
const collapsedSections = reactive({});
const useBrief = ref(false);
const briefLoading = ref(false);
const cachedBrief = ref(null);
const historyView = ref('card'); // card | list
const selectedNews = ref([]);
const expandedHistory = ref(null);
const fileInput = ref(null);

const typeColors = { 
  REWRITE: "var(--accent)", 
  ADD: "var(--green)", 
  REFINE: "var(--blue)", 
  INSERT: "oklch(65% 0.15 290)" 
};

const agentSteps = [
  "Reading your PowerPoint…",
  "Extracting strategy objectives…",
  "Querying selected news items…",
  "Matching communication frameworks (RAG)…",
  "Generating targeted improvements…",
  "Formatting output…",
];

const CAT_COLORS = { 
  tech: "var(--blue)", 
  economy: "var(--green)", 
  politics: "var(--red)", 
  social: "var(--accent)", 
  sport: "oklch(65% 0.15 290)", 
  weather: "oklch(65% 0.12 200)" 
};

// Live article data from scraper
const NEWS_DATA = ref([]);

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

async function fetchNews() {
  try {
    const res = await fetch(`${SCRAPER_BASE}/articles?window=48`);
    if (!res.ok) throw new Error(`Scraper returned ${res.status}`);
    const json = await res.json();
    const raw = json.data || [];

    NEWS_DATA.value = raw.map((a, i) => ({
      id: i + 1,
      cat: (a.category || '').toLowerCase(),
      urgency: 50 + Math.floor(Math.random() * 40),
      relevance: 50 + Math.floor(Math.random() * 40),
      title: a.title || 'Untitled',
      source: a.source || 'Unknown',
      time: formatRelativeTime(a.published_at),
      tag: null,
    }));
  } catch (err) {
    console.error('[IntelligencePage] Failed to fetch news:', err);
  }
}

onMounted(() => {
  fetchNews();
});

const HISTORY_DATA = [
  { id: 1, name: "Q2 Brand Awareness Campaign", file: "Q2_Brand_2026.pptx", date: "Apr 28, 2026", newsUsed: ["Meta AI ad suite", "IMF growth revision"], improvements: 4, status: "done" },
  { id: 2, name: "Ramadan Social Media Push", file: "Ramadan_Strategy.pptx", date: "Apr 21, 2026", newsUsed: ["Gen Z news habits", "Ramadan brand moments"], improvements: 3, status: "done" },
  { id: 3, name: "Client Crisis Comms Draft", file: "Crisis_Comms_v2.pptx", date: "Apr 14, 2026", newsUsed: ["Tunisia dinar stabilises", "MENA governance summit"], improvements: 5, status: "done" },
  { id: 4, name: "Tech Client Launch — May", file: "TechLaunch_May.pptx", date: "Apr 10, 2026", newsUsed: ["OpenAI enterprise API", "EU digital markets vote"], improvements: 2, status: "done" },
  { id: 5, name: "Annual PR Strategy 2026", file: "Annual_PR_2026.pptx", date: "Mar 30, 2026", newsUsed: ["Champions League preview", "Bloomberg Gen Z article"], improvements: 6, status: "done" },
];



const selectedNewsItems = computed(() => {
  return NEWS_DATA.value.filter(n => selectedNews.value.includes(n.id));
});

const handleDrop = (e) => {
  dragging.value = false;
  const f = e.dataTransfer.files[0];
  if (f) file.value = f;
};

const handleFileChange = (e) => {
  const f = e.target.files[0];
  if (f) file.value = f;
};

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleImprove = async () => {
  if (!file.value) return;
  
  phase.value = 'improving';
  improvingStep.value = 0;
  auditResult.value = '';
  
  let step = 0;
  const iv = setInterval(() => {
    step++;
    improvingStep.value = Math.min(step, agentSteps.length - 2);
  }, 700);

  try {
    const formData = new FormData();
    formData.append('strategy_file', file.value);
    formData.append('mode', 'detail');
    
    if (useBrief.value && cachedBrief.value) {
      // Use the analyst agent's full brief directly
      formData.append('analyst_output', JSON.stringify(cachedBrief.value));
    } else if (selectedNewsItems.value.length > 0) {
      const analystPayload = {
        items: selectedNewsItems.value.map(n => ({
          headline: n.title,
          source: n.source,
          date: n.time,
          relevance_score: n.relevance > 80 ? 'High' : n.relevance > 60 ? 'Medium' : 'Low',
          why_it_matters: `Urgency ${n.urgency}, Relevance ${n.relevance} — ${n.cat} category.`
        })),
        tldr: selectedNewsItems.value.slice(0, 3).map(n => n.title)
      };
      formData.append('analyst_output', JSON.stringify(analystPayload));
    }

    const res = await fetch(`${STRATEGIST_BASE}/audit/upload`, {
      method: 'POST',
      body: formData
    });

    if (!res.ok) throw new Error(`API error: ${res.status}`);

    const json = await res.json();
    auditResult.value = json.data;

    clearInterval(iv);
    improvingStep.value = agentSteps.length - 1;
    setTimeout(() => {
      phase.value = 'result';
    }, 400);

  } catch (err) {
    console.error('Audit failed:', err);
    clearInterval(iv);
    alert('Audit failed. Ensure com_strategist is running.');
    phase.value = 'news-select';
    useBrief.value = false;
  }
};

const handleUseBrief = async () => {
  briefLoading.value = true;
  try {
    const res = await fetch(`${ANALYST_BASE}/analyze?window=48`);
    if (!res.ok) throw new Error(`Analyst API error: ${res.status}`);
    const json = await res.json();
    cachedBrief.value = json.data || { items: [], tldr: [] };
    useBrief.value = true;
    briefLoading.value = false;
    // Auto-run the strategist with the fetched brief
    handleImprove();
  } catch (err) {
    console.error('Failed to fetch analyst brief:', err);
    briefLoading.value = false;
    alert('Could not fetch analyst brief. Ensure analyst agent is running.');
  }
};

const toggleNews = (id) => {
  if (selectedNews.value.includes(id)) {
    selectedNews.value = selectedNews.value.filter(x => x !== id);
  } else {
    selectedNews.value.push(id);
  }
};

const reuseStrategy = (h) => {
  file.value = { name: h.file, size: 2048000 };
  phase.value = 'news-select';
};

const reset = () => {
  file.value = null;
  phase.value = 'upload';
  selectedNews.value = [];
  expandedHistory.value = null;
  useBrief.value = false;
  cachedBrief.value = null;
};

const getTagColor = (label) => {
  const colors = { BREAKING: "var(--red)", ALERT: "var(--accent)", HOT: "var(--green)" };
  return colors[label] || "var(--border2)";
};

// ── Audit result computed fields ──
const auditMode = computed(() => {
  if (!auditResult.value) return 'DETAIL';
  return auditResult.value.audit_mode || 'DETAIL';
});

const auditGap = computed(() => {
  if (!auditResult.value) return '';
  return auditResult.value.primary_gap || '';
});

const auditSections = computed(() => {
  if (!auditResult.value || !auditResult.value.sections) return {};
  return auditResult.value.sections;
});

const auditRaw = computed(() => {
  if (!auditResult.value) return '';
  if (typeof auditResult.value === 'string') return auditResult.value;
  return auditResult.value.raw_markdown || JSON.stringify(auditResult.value, null, 2);
});

function sectionLabel(key) {
  const labels = {
    D1: 'DECONSTRUCT — 6-W & Transmission Audit',
    D2: 'DIAGNOSE — Filter & Rule Audit',
    D3: 'DEVELOP — Matrix Optimization',
    D4: 'DELIVER — Improvement Log',
  };
  return labels[key] || key;
}

function toggleSection(key) {
  collapsedSections[key] = !collapsedSections[key];
}

// ── Lightweight markdown → HTML ──
function renderMarkdown(md) {
  if (!md) return '';
  let html = md
    // Escape HTML
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Horizontal rules
    .replace(/^---+$/gm, '<hr>')
    // Headers (### before ## before #)
    .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold + italic
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Unordered list items
    .replace(/^[*\-•]\s+(.+)$/gm, '<li>$1</li>')
    // Numbered list items
    .replace(/^\d+\.\s+(.+)$/gm, '<li class="ol">$1</li>')
    // Tables: header row
    .replace(/^\|(.+)\|$/gm, (match, content) => {
      const cells = content.split('|').map(c => c.trim());
      // Skip separator rows like |---|---|
      if (cells.every(c => /^[-:]+$/.test(c))) return '';
      const cellHtml = cells.map(c => `<td>${c}</td>`).join('');
      return `<tr>${cellHtml}</tr>`;
    })
    // Paragraphs: double newline
    .replace(/\n\n+/g, '</p><p>')
    // Single newlines within paragraphs
    .replace(/\n/g, '<br>');

  // Wrap consecutive <li> in <ul>
  html = html.replace(/((?:<li>.*?<\/li>(?:<br>)?)+)/g, '<ul>$1</ul>');
  html = html.replace(/((?:<li class="ol">.*?<\/li>(?:<br>)?)+)/g, '<ol>$1</ol>');
  // Wrap consecutive <tr> in <table>
  html = html.replace(/((?:<tr>.*?<\/tr>(?:<br>)?)+)/g, '<table>$1</table>');
  // Clean up stray <br> inside lists/tables
  html = html.replace(/<\/li><br>/g, '</li>');
  html = html.replace(/<\/tr><br>/g, '</tr>');
  // Remove empty paragraphs and <hr> leftovers
  html = html.replace(/<p><\/p>/g, '');
  html = html.replace(/<br><hr>/g, '<hr>');

  return `<div class="md-rendered"><p>${html}</p></div>`;
}

// ── Export audit as text file ──
function exportAudit() {
  const text = auditRaw.value || 'No audit data.';
  const blob = new Blob([text], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `straton-audit-${Date.now()}.md`;
  a.click();
  URL.revokeObjectURL(url);
}
</script>

<style scoped>
.strategy-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.strategy-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 60px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.header-title {
  font-family: var(--ff-head);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.strategy-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px 32px 32px;
}

.btn-accent {
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

.btn-accent.large {
  padding: 11px 32px;
  font-size: 13px;
  margin-top: 20px;
}

.btn-accent.disabled {
  background: var(--bg2);
  border: 1px solid var(--border);
  color: var(--text3);
  cursor: not-allowed;
}

.btn-back {
  padding: 7px 14px;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--ff-mono);
  font-size: 11px;
  cursor: pointer;
}

.btn-outline-mono {
  padding: 10px 16px;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--ff-mono);
  font-size: 11px;
  cursor: pointer;
}

.btn-brief {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: transparent;
  border: 1px solid var(--accent);
  color: var(--accent);
  font-family: var(--ff-mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-brief:hover {
  background: var(--accent);
  color: #000;
}
.btn-brief.loading {
  border-color: var(--border2);
  color: var(--text3);
  cursor: wait;
}
.btn-brief.loading svg {
  animation: spin 1s linear infinite;
}

.drop-zone {
  border: 1px dashed var(--border2);
  background: var(--bg2);
  padding: 36px 32px;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
}

.drop-zone.dragging {
  border-color: var(--accent);
  background: rgba(255, 170, 0, 0.04);
}

.drop-zone.hasFile {
  border-color: var(--green);
  background: rgba(0, 200, 100, 0.03);
}

.file-ready {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.file-name {
  font-family: var(--ff-body);
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
}

.file-meta {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--green);
}

.file-hint {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  margin-top: 4px;
}

.drop-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-text {
  font-family: var(--ff-head);
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}

.file-types {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--text3);
}

.history-section {
  margin-top: 28px;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.history-label {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.1em;
}

.view-toggle {
  display: flex;
  border: 1px solid var(--border);
  overflow: hidden;
}

.view-toggle button {
  padding: 4px 10px;
  background: transparent;
  border: none;
  border-right: 1px solid var(--border);
  color: var(--text3);
  font-family: var(--ff-mono);
  font-size: 12px;
  cursor: pointer;
}

.view-toggle button:last-child {
  border-right: none;
}

.view-toggle button.active {
  background: var(--bg3);
  color: var(--text);
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1px;
}

.history-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  padding: 18px;
  cursor: pointer;
  transition: all 0.15s;
}

.history-card.expanded {
  background: var(--bg3);
  border-color: var(--accent);
}

.card-icon {
  margin-bottom: 12px;
}

.card-title {
  font-family: var(--ff-head);
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  line-height: 1.35;
  margin-bottom: 8px;
}

.card-date {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  margin-bottom: 6px;
}

.card-improvements {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--accent);
}

.card-details {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--border);
}

.details-label {
  font-family: var(--ff-mono);
  font-size: 8px;
  color: var(--text3);
  letter-spacing: 0.08em;
  margin-bottom: 6px;
}

.details-item {
  font-family: var(--ff-body);
  font-size: 10px;
  color: var(--text2);
  margin-bottom: 3px;
}

.btn-reuse {
  margin-top: 10px;
  padding: 5px 12px;
  background: var(--accent);
  border: none;
  color: #000;
  font-family: var(--ff-mono);
  font-size: 9px;
  cursor: pointer;
  letter-spacing: 0.06em;
}

.history-list {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border);
}

.list-header {
  display: grid;
  grid-template-columns: 1fr 120px 80px 100px;
  padding: 8px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg3);
}

.list-header span {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.08em;
}

.list-item {
  display: grid;
  grid-template-columns: 1fr 120px 80px 100px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  align-items: center;
  transition: background 0.1s;
}

.list-item.expanded {
  background: var(--bg3);
}

.item-name {
  font-family: var(--ff-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
}

.item-file {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  margin-top: 2px;
}

.item-date {
  font-family: var(--ff-mono);
  font-size: 11px;
  color: var(--text2);
}

.item-improvements {
  font-family: var(--ff-mono);
  font-size: 11px;
  color: var(--accent);
}

.item-news-count {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
}

.list-details {
  padding: 12px 16px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg3);
}

.news-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.news-chip {
  font-family: var(--ff-body);
  font-size: 10px;
  color: var(--text2);
  padding: 3px 8px;
  border: 1px solid var(--border2);
}

/* News Selection Phase */
.file-status {
  background: var(--bg2);
  border: 1px solid var(--border);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-filename {
  font-family: var(--ff-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
}

.status-label {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  margin-top: 2px;
}

.news-selection {
  margin-top: 20px;
}

.selection-label {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.1em;
  margin-bottom: 4px;
}

.selection-hint {
  font-family: var(--ff-body);
  font-size: 11px;
  color: var(--text3);
  margin-bottom: 16px;
}

.accent-text {
  color: var(--accent);
}

.news-list {
  display: flex;
  flex-direction: column;
}

.news-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 13px 16px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.12s;
}

.news-item.selected {
  background: rgba(255, 170, 0, 0.05);
}

.checkbox {
  width: 16px;
  height: 16px;
  border: 1.5px solid var(--border2);
  flex-shrink: 0;
  margin-top: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.12s;
}

.checkbox.active {
  border-color: var(--accent);
  background: var(--accent);
}

.checkbox span {
  font-size: 9px;
  color: #000;
  line-height: 1;
  font-weight: 700;
}

.cat-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}

.news-main {
  flex: 1;
  min-width: 0;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.tag-pill {
  font-family: var(--ff-mono);
  font-size: 9px;
  font-weight: 500;
  padding: 2px 6px;
  border: 1px solid;
  letter-spacing: 0.08em;
}

.news-source {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
}

.news-title {
  font-family: var(--ff-body);
  font-size: 12px;
  font-weight: 500;
  color: var(--text);
  line-height: 1.4;
}

.news-scores {
  display: flex;
  gap: 14px;
  flex-shrink: 0;
}

.score-block {
  text-align: right;
}

.score-label {
  font-family: var(--ff-mono);
  font-size: 8px;
  color: var(--text3);
  margin-bottom: 2px;
}

.score-value {
  font-family: var(--ff-mono);
  font-size: 12px;
  color: var(--text2);
}

.score-value.high {
  color: var(--red);
}

.action-footer {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

/* Improving Phase */
.improving-phase {
  max-width: 480px;
}

.agent-title {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--accent);
  letter-spacing: 0.1em;
  margin-bottom: 20px;
}

.cross-ref {
  margin-bottom: 20px;
  padding: 10px 14px;
  background: var(--bg2);
  border: 1px solid var(--border);
}

.cross-ref-label {
  font-family: var(--ff-mono);
  font-size: 8px;
  color: var(--text3);
  letter-spacing: 0.08em;
  margin-bottom: 8px;
}

.cross-ref-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.cross-ref-item {
  font-family: var(--ff-body);
  font-size: 10px;
  color: var(--text2);
  padding: 2px 8px;
  border: 1px solid var(--border2);
}

.agent-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
  background: var(--border2);
}

.step-dot.completed {
  background: var(--green);
}

.step-dot.active {
  background: var(--accent);
}

.step-text {
  font-family: var(--ff-mono);
  font-size: 11px;
  color: var(--text);
}

.step-text.muted {
  color: var(--text3);
}

.step-check {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--green);
}

/* ═══════════════════════════════════════════════════════════════════
   RESULT PHASE — Straton Audit Output
   ═══════════════════════════════════════════════════════════════════ */

.result-phase {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

.result-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}
.banner-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 6px var(--green);
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%, 100% { box-shadow: 0 0 4px var(--green); }
  50% { box-shadow: 0 0 12px var(--green); }
}
.banner-text {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--green);
  letter-spacing: 0.08em;
}
.banner-sub {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
}

/* ── Audit Meta ── */
.audit-meta {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 14px 20px;
  background: var(--bg2);
  border: 1px solid var(--border);
  margin-bottom: 16px;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.meta-label {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.1em;
}
.meta-badge {
  font-family: var(--ff-mono);
  font-size: 10px;
  font-weight: 600;
  padding: 3px 10px;
  border: 1px solid;
  letter-spacing: 0.06em;
}
.meta-badge.detail {
  border-color: var(--accent);
  color: var(--accent);
}
.meta-badge.basic {
  border-color: var(--blue);
  color: var(--blue);
}
.meta-gap {
  font-family: var(--ff-body);
  font-size: 12px;
  color: var(--text);
  font-weight: 500;
}

/* ── Section Cards ── */
.audit-sections {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.audit-section {
  background: var(--bg2);
  border: 1px solid var(--border);
  transition: all 0.2s;
}
.audit-section:hover {
  border-color: var(--border2);
}
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  user-select: none;
}
.section-tag {
  font-family: var(--ff-mono);
  font-size: 10px;
  font-weight: 700;
  padding: 3px 10px;
  letter-spacing: 0.06em;
  flex-shrink: 0;
}
.section-tag.d1 { background: rgba(255,170,0,0.12); color: var(--accent); }
.section-tag.d2 { background: rgba(255,80,80,0.12); color: var(--red); }
.section-tag.d3 { background: rgba(80,180,255,0.12); color: var(--blue); }
.section-tag.d4 { background: rgba(0,200,100,0.12); color: var(--green); }

.section-title {
  font-family: var(--ff-head);
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  flex: 1;
}
.section-toggle {
  font-size: 12px;
  color: var(--text3);
  flex-shrink: 0;
}

.section-body {
  padding: 0 20px 20px;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}

/* ── Raw fallback ── */
.audit-raw {
  background: var(--bg2);
  border: 1px solid var(--border);
  padding: 20px;
  margin-bottom: 8px;
}

/* ── Markdown rendered content ── */
.section-body :deep(.md-rendered) {
  font-family: var(--ff-body);
  font-size: 13px;
  line-height: 1.8;
  color: var(--text2);
}

.section-body :deep(h1),
.section-body :deep(h2),
.section-body :deep(h3),
.section-body :deep(h4) {
  font-family: var(--ff-head);
  color: var(--text);
  margin-top: 16px;
  margin-bottom: 8px;
  line-height: 1.3;
}
.section-body :deep(h1) { font-size: 18px; font-weight: 700; }
.section-body :deep(h2) { font-size: 15px; font-weight: 700; }
.section-body :deep(h3) { font-size: 13px; font-weight: 700; letter-spacing: 0.01em; }
.section-body :deep(h4) { font-size: 12px; font-weight: 600; color: var(--text2); }

.section-body :deep(strong) {
  color: var(--text);
  font-weight: 600;
}
.section-body :deep(em) {
  color: var(--accent);
  font-style: italic;
}
.section-body :deep(code) {
  font-family: var(--ff-mono);
  font-size: 11px;
  background: var(--bg3);
  padding: 2px 6px;
  border: 1px solid var(--border);
  color: var(--accent);
}

.section-body :deep(ul),
.section-body :deep(ol) {
  padding-left: 0;
  margin: 8px 0;
  list-style: none;
}
.section-body :deep(li) {
  position: relative;
  padding: 6px 0 6px 20px;
  border-bottom: 1px solid var(--border);
  font-size: 12px;
  line-height: 1.7;
}
.section-body :deep(li):last-child {
  border-bottom: none;
}
.section-body :deep(li)::before {
  content: '→';
  position: absolute;
  left: 0;
  color: var(--accent);
  font-family: var(--ff-mono);
  font-size: 11px;
}
.section-body :deep(li.ol)::before {
  content: counter(li-counter);
  counter-increment: li-counter;
  color: var(--text3);
  font-size: 10px;
}
.section-body :deep(ol) {
  counter-reset: li-counter;
}

.section-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 11px;
}
.section-body :deep(tr) {
  border-bottom: 1px solid var(--border);
}
.section-body :deep(tr:first-child) {
  border-bottom: 2px solid var(--border2);
}
.section-body :deep(tr:first-child td) {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.section-body :deep(td) {
  padding: 8px 12px;
  font-family: var(--ff-body);
  color: var(--text2);
  line-height: 1.5;
}
.section-body :deep(td:first-child) {
  font-weight: 500;
  color: var(--text);
}

.section-body :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 16px 0;
}

.section-body :deep(p) {
  margin: 0;
}

/* ── Result Actions ── */
.result-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}
.btn-export {
  padding: 9px 20px;
  background: transparent;
  border: 1px solid var(--accent);
  color: var(--accent);
  font-family: var(--ff-mono);
  font-size: 11px;
  cursor: pointer;
  letter-spacing: 0.06em;
  transition: all 0.15s;
}
.btn-export:hover {
  background: var(--accent);
  color: #000;
}
</style>
