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
        <!-- Strategic Context Fields -->
        <div class="context-fields">
          <div class="context-label">STRATEGIC CONTEXT</div>
          <div class="field-grid">
            <div class="field-item">
              <label>BRAND NAME</label>
              <input v-model="brandName" placeholder="e.g. Khaberni" class="ctx-input" />
            </div>
            <div class="field-item">
              <label>SLOGAN</label>
              <input v-model="slogan" placeholder="Brand tagline" class="ctx-input" />
            </div>
            <div class="field-item">
              <label>BRAND DESCRIPTION</label>
              <textarea v-model="brandDesc" placeholder="What is the brand about?" class="ctx-textarea"></textarea>
            </div>
            <div class="field-item">
              <label>REASON OF EXISTENCE (RAISON D'ÊTRE)</label>
              <textarea v-model="raisonDetre" placeholder="Why does this brand exist?" class="ctx-textarea"></textarea>
            </div>
            <div class="field-item">
              <label>PRODUCT / CAMPAIGN</label>
              <input v-model="productName" placeholder="e.g. Summer Launch" class="ctx-input" />
            </div>
            <div class="field-item">
              <label>PRODUCT DESCRIPTION</label>
              <textarea v-model="productDesc" placeholder="Details about the product/campaign..." class="ctx-textarea"></textarea>
            </div>
          </div>
        </div>

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
            <div class="drop-text">{{ t.drop_file }}</div>
            <div class="file-types">.PPTX · .PDF · .DOCX · .TXT</div>
          </div>
          <input type="file" ref="fileInput" @change="handleFileChange" style="display: none" accept=".pptx,.ppt,.pdf,.docx,.doc,.txt" />
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
              v-for="h in historyItems"
              :key="h.id"
              class="history-card"
              :class="{ expanded: expandedHistory === h.id }"
              @click="expandedHistory = expandedHistory === h.id ? null : h.id"
            >
              <div class="card-icon">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <rect x="3" y="2" width="14" height="16" rx="1" stroke="var(--text3)" stroke-width="1.2"/>
                  <rect x="6" y="5" width="8" height="5" stroke="var(--accent)" stroke-width="1"/>
                  <rect x="6" y="12" width="5" height="1" fill="var(--text3)"/>
                  <rect x="6" y="14" width="8" height="1" fill="var(--text3)"/>
                </svg>
              </div>
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
              v-for="h in historyItems"
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
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <rect x="3" y="2" width="14" height="16" rx="1" stroke="var(--text3)" stroke-width="1.2"/>
            <rect x="6" y="5" width="8" height="5" stroke="var(--accent)" stroke-width="1"/>
            <rect x="6" y="12" width="5" height="1" fill="var(--text3)"/>
            <rect x="6" y="14" width="8" height="1" fill="var(--text3)"/>
          </svg>
          <div>
            <div class="status-filename">{{ file?.name }}</div>
            <div class="status-label">LOADED · READY FOR ENRICHMENT</div>
          </div>
        </div>

        <!-- Quick actions — USE BRIEF / SKIP -->
        <div class="quick-actions">
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

        <div class="news-selection">
          <div class="selection-label">OR SELECT NEWS MANUALLY</div>
          <div class="selection-hint">
            Pick specific news items the agent should cross-reference.
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
            <span :id="'step-text-' + i" class="step-text" :class="{ muted: i > improvingStep }">{{ i < improvingStep ? step : (i === improvingStep ? '' : step) }}</span>
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

        <!-- Missing Context (High priority flag) -->
        <div v-if="auditMissingHtml" class="audit-missing-context">
          <div class="section-body" v-html="renderMarkdown(auditMissingHtml)"></div>
        </div>

        <!-- Brand Context Snapshot -->
        <div v-if="auditBrandHtml" class="audit-brand-context">
          <div class="section-body" v-html="renderMarkdown(auditBrandHtml)"></div>
        </div>

        <!-- ── SMART Recommendations Visual Grid ── -->
        <div v-if="auditRecommendations.length" class="recs-visual">
          <div class="recs-visual-label">SMART IMPROVEMENT RECOMMENDATIONS</div>
          <div class="recs-grid">
            <div
              v-for="rec in auditRecommendations"
              :key="rec.number"
              class="rec-card"
              :class="`prio-${prioKey(rec.priority)}`"
            >
              <!-- compact view (always visible) -->
              <div class="rec-head">
                <span class="rec-num">#{{ rec.number }}</span>
                <span class="rec-badge">{{ rec.priority }}</span>
              </div>
              <div class="rec-gap">{{ rec.gap_identified }}</div>

              <!-- expanded view (CSS hover) -->
              <div class="rec-expand">
                <div class="rec-divider"></div>
                <div v-if="rec.brief_signal" class="rec-field">
                  <div class="rec-field-label">SIGNAL</div>
                  <div class="rec-field-val">{{ rec.brief_signal }}</div>
                </div>
                <div class="rec-field">
                  <div class="rec-field-label">SMART RECOMMENDATION</div>
                  <div class="rec-field-val">{{ rec.smart_recommendation }}</div>
                </div>
                <div v-if="rec.feasibility_note" class="rec-field">
                  <div class="rec-field-label">FEASIBILITY</div>
                  <div class="rec-field-val">{{ rec.feasibility_note }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Rest of audit report (brand context, strengths, next steps) -->
        <div v-if="auditRaw" class="audit-raw">
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
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue';
import { useAnimation } from '@/composables/useAnimation';
import { useNewsLogic } from '@/composables/useNewsLogic';
import { marked } from 'marked';

const { entrance, staggerList, magneticHover, typewriter, gsap } = useAnimation();
const { autoCategorize, calculateScores } = useNewsLogic();

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

// Context fields
const brandName = ref('');
const slogan = ref('');
const brandDesc = ref('');
const raisonDetre = ref('');
const productName = ref('');
const productDesc = ref('');

const agentSteps = [
  "Reading your strategy file…",
  "Extracting objectives & context…",
  "Querying selected news items…",
  "Matching communication frameworks (RAG)…",
  "Generating targeted improvements…",
  "Finalizing audit output…",
];

const CAT_COLORS = { 
  tech: "var(--blue)", 
  economy: "var(--green)", 
  politics: "var(--red)", 
  social: "var(--accent)", 
  sport: "oklch(65% 0.15 290)", 
  weather: "oklch(65% 0.12 200)",
  culture: "oklch(70% 0.15 320)",
  lifestyle: "oklch(65% 0.18 65)"
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

    NEWS_DATA.value = raw.map((a, i) => {
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
        tag: scores.tag,
      };
    });
  } catch (err) {
    console.error('[IntelligencePage] Failed to fetch news:', err);
  }
}

onMounted(() => {
  fetchNews();
  fetchHistory();
  
  // Initial entrance animations
  entrance('.context-fields', { delay: 0.2 });
  entrance('.drop-zone', { delay: 0.4 });
  entrance('.history-section', { delay: 0.6 });

  // Magnetic buttons
  setTimeout(() => {
    const btns = document.querySelectorAll('.btn-accent, .btn-brief, .btn-reuse');
    btns.forEach(b => magneticHover(b, 0.15));
  }, 1000);

  // Load persisted context
  const saved = localStorage.getItem('khaberni_strategy_ctx');
  if (saved) {
    try {
      const data = JSON.parse(saved);
      brandName.value = data.brandName || '';
      slogan.value = data.slogan || '';
      brandDesc.value = data.brandDesc || '';
      raisonDetre.value = data.raisonDetre || '';
      productName.value = data.productName || '';
      productDesc.value = data.productDesc || '';
    } catch (e) {
      console.error('Failed to parse saved strategy context', e);
    }
  }
});

// Save context on change
watch([brandName, slogan, brandDesc, raisonDetre, productName, productDesc], () => {
  const data = {
    brandName: brandName.value,
    slogan: slogan.value,
    brandDesc: brandDesc.value,
    raisonDetre: raisonDetre.value,
    productName: productName.value,
    productDesc: productDesc.value
  };
  localStorage.setItem('khaberni_strategy_ctx', JSON.stringify(data));
}, { deep: true });

const historyItems = ref([]);

const fetchHistory = async () => {
  try {
    const res = await fetch(`${STRATEGIST_BASE}/history`);
    if (!res.ok) return;
    const json = await res.json();
    historyItems.value = (json.data || []).map(h => ({
      ...h,
      newsUsed: h.news_used ?? [],
    }));
  } catch (err) {
    console.error('Failed to fetch strategy history:', err);
  }
};

const saveToHistory = async (auditData, analystData, filename) => {
  const newsUsed = analystData?.tldr?.length
    ? analystData.tldr.slice(0, 5)
    : (analystData?.items || []).slice(0, 5).map(i => i.headline || i.title || '');

  const improvements = Array.isArray(auditData?.recommendations)
    ? auditData.recommendations.length
    : 0;

  const name = filename.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' ');

  try {
    await fetch(`${STRATEGIST_BASE}/history`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, file: filename, news_used: newsUsed, improvements }),
    });
    await fetchHistory();
  } catch (err) {
    console.error('Failed to save history:', err);
  }
};



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
  
  // Run typewriter for first step
  nextTick(() => {
    typewriter(`#step-text-0`, agentSteps[0]);
  });

  const runSteps = async () => {
    for (let i = 0; i < agentSteps.length - 1; i++) {
      improvingStep.value = i;
      await new Promise(r => setTimeout(r, 1200));
      if (i + 1 < agentSteps.length) {
        typewriter(`#step-text-${i+1}`, agentSteps[i+1]);
      }
    }
  };
  
  const stepPromise = runSteps();

  try {
    const formData = new FormData();
    formData.append('strategy_file', file.value);
    formData.append('mode', 'detail');
    
    // Add strategic context
    formData.append('brand_name', brandName.value);
    formData.append('slogan', slogan.value);
    formData.append('brand_desc', brandDesc.value);
    formData.append('raison_detre', raisonDetre.value);
    formData.append('product_name', productName.value);
    formData.append('product_desc', productDesc.value);
    
    if (useBrief.value && cachedBrief.value) {
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

    const usedAnalyst = (useBrief.value && cachedBrief.value)
      ? cachedBrief.value
      : { tldr: selectedNewsItems.value.slice(0, 5).map(n => n.title) };
    saveToHistory(json.data, usedAnalyst, file.value.name);

    await stepPromise;
    improvingStep.value = agentSteps.length - 1;
    setTimeout(() => {
      phase.value = 'result';
    }, 600);

  } catch (err) {
    console.error('Audit failed:', err);
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
  
  brandName.value = '';
  slogan.value = '';
  brandDesc.value = '';
  raisonDetre.value = '';
  productName.value = '';
  productDesc.value = '';

  nextTick(() => {
    entrance('.context-fields, .drop-zone, .history-section', { delay: 0.1 });
  });
};

const getTagColor = (label) => {
  const colors = { BREAKING: "var(--red)", ALERT: "var(--accent)", HOT: "var(--green)" };
  return colors[label] || "var(--border2)";
};

// Phase watcher for animations
watch(phase, (newPhase) => {
  if (newPhase === 'result') {
    nextTick(() => {
      entrance('.audit-meta, .audit-section', { stagger: 0.12, y: 30, duration: 0.8 });
    });
  } else if (newPhase === 'news-select') {
    nextTick(() => {
      entrance('.file-status, .quick-actions, .news-selection', { stagger: 0.1, duration: 0.6 });
      staggerList('.news-item', { delay: 0.3 });
    });
  }
});

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

// Missing context section — rendered at the very top if present
const auditMissingHtml = computed(() => {
  if (!auditResult.value) return '';
  return auditResult.value.html_missing_context || '';
});

// Brand context section — rendered above the SMART cards
const auditBrandHtml = computed(() => {
  if (!auditResult.value) return '';
  return auditResult.value.html_brand_context || '';
});

// Everything except brand context and SMART table — rendered below the cards
const auditRaw = computed(() => {
  if (!auditResult.value) return '';
  if (typeof auditResult.value === 'string') return auditResult.value;
  return auditResult.value.html_rest || auditResult.value.html_body || auditResult.value.html_output || auditResult.value.raw_markdown || '';
});

const auditRecommendations = computed(() => {
  if (!auditResult.value || !Array.isArray(auditResult.value.recommendations)) return [];
  return auditResult.value.recommendations.filter(
    r => r.number && r.number !== '#' && r.gap_identified && r.gap_identified.trim()
  );
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

function prioKey(priority) {
  const p = (priority || '').toLowerCase();
  if (p.includes('critical')) return 'critical';
  if (p.includes('high')) return 'high';
  if (p.includes('medium')) return 'medium';
  return 'low';
}

// ── Render markdown or pass through pre-built HTML from backend ──
function renderMarkdown(md) {
  if (!md) return '';
  // Backend now returns html_output (already HTML); detect by leading tag
  const isHtml = typeof md === 'string' && md.trimStart().startsWith('<');
  const html = isHtml ? md : marked.parse(md);
  return `<div class="md-rendered">${html}</div>`;
}

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
  font-size: var(--text-lg);
  font-weight: 800;
  letter-spacing: var(--letter-spacing-display);
  text-transform: uppercase;
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
  transition: transform 0.2s;
}
.btn-accent:active { transform: scale(0.95); }

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

/* ── Context Fields ── */
.context-fields {
  margin-bottom: 24px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
}
.context-label {
  font-family: var(--ff-mono);
  font-size: var(--text-xs);
  color: var(--text3);
  letter-spacing: 0.15em;
  margin-bottom: 20px;
}
.field-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.field-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.field-item label {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--text2);
  letter-spacing: 0.1em;
}
.ctx-input, .ctx-textarea {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border2);
  color: var(--text);
  padding: 10px 14px;
  font-family: var(--ff-body);
  font-size: var(--text-sm);
  transition: all 0.2s ease;
}
.ctx-input:focus, .ctx-textarea:focus {
  outline: none;
  border-color: var(--accent);
  background: rgba(255, 170, 0, 0.02);
  box-shadow: 0 0 15px rgba(255, 170, 0, 0.05);
}
.ctx-textarea {
  resize: vertical;
  min-height: 80px;
}

.quick-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 16px;
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

.drop-zone {
  border: 1px dashed var(--border2);
  background: rgba(255, 255, 255, 0.01);
  padding: 48px 32px;
  cursor: pointer;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drop-zone.dragging {
  border-color: var(--accent);
  background: rgba(255, 170, 0, 0.04);
  transform: scale(1.01);
}

.drop-zone.hasFile {
  border-color: var(--green);
  background: rgba(0, 200, 100, 0.03);
}

.drop-text {
  font-family: var(--ff-head);
  font-size: var(--text-md);
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.01em;
}

/* History */
.history-section {
  margin-top: 32px;
}
.history-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.history-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border2);
  transform: translateY(-2px);
}
.history-card.expanded {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--accent);
}

/* Improving Phase */
.improving-phase {
  max-width: 520px;
  margin: 40px auto;
}
.agent-title {
  font-family: var(--ff-mono);
  font-size: var(--text-xs);
  color: var(--accent);
  letter-spacing: 0.15em;
  margin-bottom: 32px;
  text-align: center;
}
.agent-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.step-row {
  display: flex;
  align-items: center;
  gap: 16px;
}
.step-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--border2);
  transition: all 0.3s;
}
.step-dot.active { background: var(--accent); box-shadow: 0 0 10px var(--accent); }
.step-dot.completed { background: var(--green); }
.step-text {
  font-family: var(--ff-mono);
  font-size: var(--text-sm);
  color: var(--text);
  min-height: 1.5em;
}

/* Result Phase */
.result-phase {
  will-change: transform, opacity;
}
.audit-meta {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
}
.audit-section {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.audit-section:hover {
  border-color: var(--border2);
  background: rgba(255, 255, 255, 0.04);
  transform: translateX(4px);
}
.section-title {
  font-family: var(--ff-head);
  font-size: var(--text-base);
  font-weight: 700;
}

.btn-export {
  padding: 10px 24px;
  background: transparent;
  border: 1.5px solid var(--accent);
  color: var(--accent);
  font-family: var(--ff-mono);
  font-size: var(--text-xs);
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 0.06em;
  transition: all 0.2s;
}
.btn-export:hover {
  background: var(--accent);
  color: #000;
  transform: translateY(-2px);
}

/* ── Cross-Ref List ── */
.cross-ref {
  margin-bottom: 24px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  border-radius: 4px;
}

.cross-ref-label {
  font-family: var(--ff-mono);
  font-size: var(--text-xs);
  color: var(--text3);
  letter-spacing: 0.1em;
  margin-bottom: 12px;
}

.cross-ref-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cross-ref-item {
  font-family: var(--ff-body);
  font-size: var(--text-sm);
  color: var(--text2);
}

/* ── Markdown Rendered Output ── */
.md-rendered { font-family: var(--ff-body); font-size: var(--text-sm); color: var(--text2); line-height: 1.8; }
.md-rendered p { margin: 0 0 10px; }
.md-rendered p:last-child { margin-bottom: 0; }
.md-rendered strong { color: var(--text); font-weight: 700; }
.md-rendered em { color: var(--text2); font-style: italic; }
.md-rendered ul, .md-rendered ol { padding-left: 20px; margin: 8px 0; }
.md-rendered li { margin-bottom: 6px; }
.md-rendered code { font-family: var(--ff-mono); font-size: 11px; background: rgba(255,255,255,0.06); padding: 1px 5px; border-radius: 2px; }
.md-rendered h1, .md-rendered h2, .md-rendered h3 { font-family: var(--ff-head); font-weight: 700; color: var(--text); margin: 14px 0 8px; letter-spacing: var(--letter-spacing-display); }
.md-rendered h1 { font-size: var(--text-lg); }
.md-rendered h2 { font-size: var(--text-md); }
.md-rendered h3 { font-size: var(--text-base); }
.md-rendered blockquote { border-left: 3px solid var(--accent); padding-left: 16px; margin: 10px 0; color: var(--text3); }

/* ── Markdown Rendered Tables ── */
.md-rendered table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  font-family: var(--ff-body);
  font-size: var(--text-sm);
  border: 1.5px solid var(--border2);
  display: block;
  overflow-x: auto;
}

.md-rendered th {
  padding: 14px 20px;
  text-align: left;
  background: rgba(255, 255, 255, 0.06);
  font-family: var(--ff-mono);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text);
  border-bottom: 1.5px solid var(--border2);
  border-right: 1px solid var(--border2);
  white-space: nowrap;
}

.md-rendered th:last-child {
  border-right: none;
}

.md-rendered td {
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  border-right: 1px solid var(--border);
  color: var(--text2);
  line-height: 1.6;
  vertical-align: top;
}

.md-rendered td:last-child {
  border-right: none;
}

.md-rendered tr:last-child td {
  border-bottom: none;
}

.md-rendered tr:nth-child(even) td {
  background: rgba(255, 255, 255, 0.02);
}

.md-rendered tr:hover td {
  background: rgba(255, 255, 255, 0.04);
}


/* ── News Selection ── */
.news-selection {
  margin-top: 24px;
}

.selection-label {
  font-family: var(--ff-mono);
  font-size: var(--text-xs);
  color: var(--text3);
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.selection-hint {
  font-family: var(--ff-body);
  font-size: var(--text-sm);
  color: var(--text2);
  margin-bottom: 16px;
}

.accent-text { color: var(--accent); }

.news-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.news-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.2s ease;
}

.news-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.news-item.selected {
  background: rgba(255, 170, 0, 0.05);
  border-color: var(--accent);
}

.checkbox {
  width: 18px;
  height: 18px;
  border: 1.5px solid var(--border2);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  margin-top: 2px;
}

.checkbox.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #000;
}

.cat-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-top: 8px;
  flex-shrink: 0;
}

.news-main { flex: 1; min-width: 0; }

.news-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.tag-pill {
  font-family: var(--ff-mono);
  font-size: 9px;
  padding: 2px 6px;
  border: 1px solid;
  letter-spacing: 0.1em;
  font-weight: 600;
}

.news-source {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--text3);
}

.news-title {
  font-family: var(--ff-head);
  font-size: var(--text-md);
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
}

.news-scores {
  display: flex;
  gap: 16px;
  flex-shrink: 0;
}

.score-block { text-align: right; }

.score-label {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.1em;
  margin-bottom: 4px;
}

.score-value {
  font-family: var(--ff-mono);
  font-size: 14px;
  font-weight: 600;
  color: var(--text2);
}

.score-value.high { color: var(--red); }

.action-footer {
  margin-top: 32px;
  display: flex;
  justify-content: flex-end;
}

/* ── Brand Context Snapshot ── */
.audit-brand-context {
  margin-bottom: 24px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
}

/* ── Missing Context Section ── */
.audit-missing-context {
  margin-bottom: 24px;
  padding: 20px 24px;
  background: rgba(192, 96, 96, 0.04);
  border: 1px solid rgba(192, 96, 96, 0.2);
  border-left: 3px solid #c06060;
}

/* ── SMART Recommendations Visual Grid ── */
.recs-visual {
  margin: 20px 0 28px;
}

.recs-visual-label {
  font-family: var(--ff-head);
  font-size: var(--text-lg);
  font-weight: 800;
  letter-spacing: var(--letter-spacing-display);
  margin-bottom: 24px;
  color: var(--accent);
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.recs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
  gap: 10px;
}

/* Priority color variables */
.rec-card.prio-critical { --pc: #c06060; --pc-bg: rgba(192, 96, 96, 0.06); }
.rec-card.prio-high     { --pc: #c09050; --pc-bg: rgba(192, 144, 80, 0.06); }
.rec-card.prio-medium   { --pc: #5090c0; --pc-bg: rgba(80, 144, 192, 0.06); }
.rec-card.prio-low      { --pc: #50a87a; --pc-bg: rgba(80, 168, 122, 0.06); }

.rec-card {
  position: relative;
  background: var(--pc-bg);
  border: 1px solid var(--border);
  border-left: 3px solid var(--pc, var(--border2));
  padding: 14px 16px;
  cursor: default;
  transition: background 0.2s, border-color 0.15s, box-shadow 0.2s;
}

.rec-card:hover {
  background: var(--pc-bg);
  border-color: var(--pc);
  box-shadow: 0 0 20px color-mix(in srgb, var(--pc) 20%, transparent);
}

.rec-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.rec-num {
  font-family: var(--ff-mono);
  font-size: 10px;
  color: var(--text3);
  letter-spacing: 0.06em;
}

.rec-badge {
  font-family: var(--ff-mono);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--pc);
  border: 1px solid var(--pc);
  padding: 2px 7px;
}

.rec-gap {
  font-family: var(--ff-head);
  font-size: var(--text-base);
  font-weight: 700;
  color: var(--text);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: all 0.2s;
}

/* Expanded panel — hidden by default, revealed on hover via max-height */
.rec-expand {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.rec-card:hover .rec-gap {
  -webkit-line-clamp: unset;
  overflow: visible;
  display: block;
}

.rec-card:hover .rec-expand {
  max-height: 640px;
}

.rec-divider {
  height: 1px;
  background: var(--pc);
  opacity: 0.25;
  margin: 12px 0;
}

.rec-field {
  margin-bottom: 12px;
}

.rec-field:last-child {
  margin-bottom: 0;
}

.rec-field-label {
  font-family: var(--ff-mono);
  font-size: 10px;
  font-weight: 600;
  color: var(--text3);
  letter-spacing: 0.12em;
  margin-bottom: 5px;
}

.rec-field-val {
  font-family: var(--ff-body);
  font-size: var(--text-sm);
  color: var(--text2);
  line-height: 1.65;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
