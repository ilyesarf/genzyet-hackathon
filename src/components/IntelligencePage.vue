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
        <div class="result-banner">
          <div class="banner-dot"></div>
          <span class="banner-text">STRATEGY IMPROVEMENTS READY</span>
          <span v-if="selectedNews.length > 0" class="banner-sub">· based on {{ selectedNews.length }} news items</span>
        </div>
        <div class="improvements-list">
          <div v-for="(imp, i) in STRATEGY_IMPROVEMENTS" :key="i" class="improvement-card">
            <div class="improvement-header">
              <span class="improvement-type" :style="{ borderColor: typeColors[imp.type], color: typeColors[imp.type] }">
                {{ imp.type }}
              </span>
              <span class="improvement-section">{{ imp.section }}</span>
            </div>
            <p class="improvement-text">{{ imp.text }}</p>
          </div>
        </div>
        <div class="result-actions">
          <button class="btn-export">EXPORT ↗</button>
          <button @click="reset" class="btn-back">NEW STRATEGY</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  t: Object,
  lang: String
});

const file = ref(null);
const dragging = ref(false);
const phase = ref('upload'); // upload | news-select | improving | result
const improvingStep = ref(0);
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

const NEWS_DATA = [
  { id: 1, cat: "tech", urgency: 92, relevance: 88, title: "Meta launches AI-powered ad personalisation suite for agencies", source: "TechCrunch", time: "2h ago", tag: "BREAKING" },
  { id: 2, cat: "economy", urgency: 85, relevance: 91, title: "IMF revises global growth forecast downward amid trade tensions", source: "Reuters", time: "3h ago", tag: "ALERT" },
  { id: 3, cat: "politics", urgency: 78, relevance: 72, title: "European Parliament votes on new digital markets regulation", source: "Le Monde", time: "4h ago", tag: null },
  { id: 4, cat: "social", urgency: 65, relevance: 80, title: "Gen Z abandons traditional news for short-video summaries", source: "Bloomberg", time: "5h ago", tag: null },
  { id: 5, cat: "tech", urgency: 88, relevance: 94, title: "OpenAI announces enterprise API with custom model fine-tuning", source: "The Verge", time: "6h ago", tag: "HOT" },
  { id: 6, cat: "sport", urgency: 55, relevance: 60, title: "Champions League: PSG vs Bayern preview — tactical breakdown", source: "L'Équipe", time: "7h ago", tag: null },
  { id: 7, cat: "economy", urgency: 74, relevance: 76, title: "Tunisian dinar stabilises as central bank raises interest rates", source: "TAP", time: "8h ago", tag: null },
  { id: 8, cat: "tech", urgency: 70, relevance: 85, title: "Anthropic releases Claude 4.5 with extended context window", source: "Wired", time: "9h ago", tag: null },
  { id: 9, cat: "social", urgency: 60, relevance: 70, title: "Ramadan social media trends: brands missing key moments", source: "Social Media Today", time: "10h ago", tag: null },
  { id: 10, cat: "politics", urgency: 82, relevance: 68, title: "Tunisia to host MENA digital governance summit next month", source: "TAP", time: "11h ago", tag: null },
];

const HISTORY_DATA = [
  { id: 1, name: "Q2 Brand Awareness Campaign", file: "Q2_Brand_2026.pptx", date: "Apr 28, 2026", newsUsed: ["Meta AI ad suite", "IMF growth revision"], improvements: 4, status: "done" },
  { id: 2, name: "Ramadan Social Media Push", file: "Ramadan_Strategy.pptx", date: "Apr 21, 2026", newsUsed: ["Gen Z news habits", "Ramadan brand moments"], improvements: 3, status: "done" },
  { id: 3, name: "Client Crisis Comms Draft", file: "Crisis_Comms_v2.pptx", date: "Apr 14, 2026", newsUsed: ["Tunisia dinar stabilises", "MENA governance summit"], improvements: 5, status: "done" },
  { id: 4, name: "Tech Client Launch — May", file: "TechLaunch_May.pptx", date: "Apr 10, 2026", newsUsed: ["OpenAI enterprise API", "EU digital markets vote"], improvements: 2, status: "done" },
  { id: 5, name: "Annual PR Strategy 2026", file: "Annual_PR_2026.pptx", date: "Mar 30, 2026", newsUsed: ["Champions League preview", "Bloomberg Gen Z article"], improvements: 6, status: "done" },
];

const STRATEGY_IMPROVEMENTS = [
  { section: "Executive Summary", type: "REWRITE", text: "Lead with AI disruption narrative — high urgency score (88) in tech this week makes this immediately relevant to your client's stakeholders." },
  { section: "Media Channels", type: "ADD", text: "Include short-video distribution (TikTok, Reels) targeting Gen Z. Data shows 34% shift away from traditional news channels in your demographic." },
  { section: "Messaging Tone", type: "REFINE", text: "Adjust economic framing to be cautiously optimistic — IMF downgrade creates a sensitive window; avoid overcommitting on growth projections." },
  { section: "Timeline", type: "INSERT", text: "Add a 48h reactive window for AI-related news. OpenAI & Meta announcements create opportunities for thought-leadership content." },
];

const selectedNewsItems = computed(() => {
  return NEWS_DATA.filter(n => selectedNews.value.includes(n.id));
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

const handleImprove = () => {
  phase.value = 'improving';
  improvingStep.value = 0;
  let step = 0;
  const iv = setInterval(() => {
    step++;
    improvingStep.value = Math.min(step - 1, agentSteps.length - 1);
    if (step >= agentSteps.length) {
      clearInterval(iv);
      setTimeout(() => {
        phase.value = 'result';
      }, 400);
    }
  }, 700);
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
};

const getTagColor = (label) => {
  const colors = { BREAKING: "var(--red)", ALERT: "var(--accent)", HOT: "var(--green)" };
  return colors[label] || "var(--border2)";
};
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

/* Result Phase */
.result-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.banner-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--green);
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

.improvements-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.improvement-card {
  background: var(--bg2);
  border: 1px solid var(--border);
  padding: 20px;
}

.improvement-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.improvement-type {
  font-family: var(--ff-mono);
  font-size: 9px;
  padding: 3px 8px;
  border: 1px solid;
}

.improvement-section {
  font-family: var(--ff-head);
  font-size: 13px;
  font-weight: 600;
}

.improvement-text {
  font-family: var(--ff-body);
  font-size: 12px;
  color: var(--text2);
  line-height: 1.75;
}

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
}
</style>
