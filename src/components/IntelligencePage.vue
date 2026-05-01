<template>
  <div class="page intelligence-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Intelligence Hub</h1>
        <p class="page-subtitle">AI-powered analysis and trend detection across all feeds</p>
      </div>
      <div class="header-actions">
        <button class="btn-outline" @click="refreshAnalysis">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="stats-row">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-icon" :style="{ background: stat.color + '1a', color: stat.color }">
          <svg v-if="stat.icon === 'zap'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          <svg v-if="stat.icon === 'trending'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
          <svg v-if="stat.icon === 'shield'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <svg v-if="stat.icon === 'globe'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
        <span class="stat-change" :class="stat.trend">{{ stat.change }}</span>
      </div>
    </div>

    <!-- Trend Analysis -->
    <div class="intel-grid">
      <!-- Trending Topics -->
      <div class="intel-card">
        <div class="card-header">
          <h3 class="card-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
            Trending Topics
          </h3>
          <span class="card-badge">Live</span>
        </div>
        <div class="topics-list">
          <div class="topic-item" v-for="topic in trendingTopics" :key="topic.name">
            <div class="topic-bar-container">
              <div class="topic-info">
                <span class="topic-name">{{ topic.name }}</span>
                <span class="topic-count">{{ topic.mentions }} mentions</span>
              </div>
              <div class="topic-bar">
                <div class="topic-bar-fill" :style="{ width: topic.score + '%', background: topic.color }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sentiment Analysis -->
      <div class="intel-card">
        <div class="card-header">
          <h3 class="card-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            Sentiment Overview
          </h3>
        </div>
        <div class="sentiment-grid">
          <div class="sentiment-item" v-for="s in sentiments" :key="s.label">
            <div class="sentiment-ring" :style="{ '--ring-color': s.color, '--ring-pct': s.value + '%' }">
              <span class="sentiment-pct">{{ s.value }}%</span>
            </div>
            <span class="sentiment-label">{{ s.label }}</span>
            <span class="sentiment-delta" :class="s.trend">{{ s.delta }}</span>
          </div>
        </div>
      </div>

      <!-- Threat Matrix -->
      <div class="intel-card full-width">
        <div class="card-header">
          <h3 class="card-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            Active Threat Matrix
          </h3>
          <span class="card-badge alert">3 Critical</span>
        </div>
        <div class="threat-list">
          <div class="threat-item" v-for="threat in threats" :key="threat.id">
            <div class="threat-severity" :class="threat.level"></div>
            <div class="threat-content">
              <div class="threat-title">{{ threat.title }}</div>
              <div class="threat-meta">{{ threat.category }} · {{ threat.time }}</div>
            </div>
            <span class="threat-badge" :class="threat.level">{{ threat.level }}</span>
          </div>
        </div>
      </div>

      <!-- Key Insights -->
      <div class="intel-card full-width">
        <div class="card-header">
          <h3 class="card-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
            AI-Generated Insights
          </h3>
          <span class="card-meta">Updated 5 min ago</span>
        </div>
        <div class="insights-list">
          <div class="insight-item" v-for="insight in insights" :key="insight.id">
            <div class="insight-icon" :style="{ background: insight.color + '1a', color: insight.color }">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            </div>
            <div class="insight-body">
              <p class="insight-text">{{ insight.text }}</p>
              <span class="insight-confidence">{{ insight.confidence }}% confidence</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const stats = ref([
  { label: 'Active Signals', value: '1,247', icon: 'zap', color: 'var(--accent-gold)', change: '+12%', trend: 'up' },
  { label: 'Trend Shifts', value: '23', icon: 'trending', color: '#4ade80', change: '+5', trend: 'up' },
  { label: 'Threat Level', value: 'High', icon: 'shield', color: 'var(--urgency-high)', change: '↑ Elevated', trend: 'danger' },
  { label: 'Sources Active', value: '48/52', icon: 'globe', color: '#60a5fa', change: '92%', trend: 'neutral' },
]);

const trendingTopics = ref([
  { name: 'AI Regulation', mentions: 342, score: 95, color: 'var(--urgency-high)' },
  { name: 'GPT-5 Launch', mentions: 289, score: 82, color: 'var(--accent-gold)' },
  { name: 'Data Privacy', mentions: 198, score: 64, color: '#60a5fa' },
  { name: 'Edge Computing', mentions: 156, score: 51, color: '#4ade80' },
  { name: 'Quantum Security', mentions: 89, score: 30, color: 'var(--text-muted)' },
]);

const sentiments = ref([
  { label: 'Positive', value: 34, color: '#4ade80', delta: '+3%', trend: 'up' },
  { label: 'Neutral', value: 41, color: '#60a5fa', delta: '-1%', trend: 'down' },
  { label: 'Negative', value: 25, color: 'var(--urgency-high)', delta: '+4%', trend: 'danger' },
]);

const threats = ref([
  { id: 1, title: 'Supply chain vulnerability in major CDN provider', category: 'Infrastructure', time: '12 min ago', level: 'critical' },
  { id: 2, title: 'Social engineering campaign targeting C-suite executives', category: 'Social', time: '34 min ago', level: 'critical' },
  { id: 3, title: 'Regulatory deadline approaching for GDPR compliance update', category: 'Legal', time: '1h ago', level: 'critical' },
  { id: 4, title: 'Competitor patent filing in ML-assisted content generation', category: 'Market', time: '2h ago', level: 'high' },
  { id: 5, title: 'API rate limiting changes from OpenAI affecting pipelines', category: 'Technical', time: '3h ago', level: 'medium' },
]);

const insights = ref([
  { id: 1, text: 'Market sentiment is shifting negatively toward AI-generated content. Brands emphasizing human creativity are seeing 18% higher engagement.', confidence: 89, color: 'var(--accent-gold)' },
  { id: 2, text: 'The EU AI Act will require compliance changes in at least 3 of your active content pipelines within the next 90 days.', confidence: 94, color: 'var(--urgency-high)' },
  { id: 3, text: 'Competitors in the DTC space are increasing ad spend on short-form video by 40% this quarter — consider reallocating budget.', confidence: 76, color: '#60a5fa' },
]);

const refreshAnalysis = () => {
  // would trigger re-analysis
};
</script>

<style scoped>
.page { padding: 24px; flex: 1; overflow-y: auto; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; }
.page-title { font-family: 'Outfit', sans-serif; font-size: 22px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.page-subtitle { font-size: 13px; color: var(--text-secondary); }
.header-actions { display: flex; gap: 8px; }

.btn-outline {
  display: flex; align-items: center; gap: 6px;
  background: transparent; border: 1px solid var(--border-subtle);
  color: var(--text-secondary); padding: 7px 14px; border-radius: 6px;
  font-size: 12.5px; font-weight: 600; cursor: pointer; font-family: inherit;
  transition: all 0.15s ease;
}
.btn-outline:hover { border-color: var(--accent-gold-muted); color: var(--accent-gold); }

/* Stats */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card {
  background: var(--bg-surface); border: 1px solid var(--border-subtle);
  border-radius: 10px; padding: 16px; display: flex; align-items: center; gap: 12px;
}
.stat-icon { width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-info { flex: 1; display: flex; flex-direction: column; }
.stat-value { font-size: 18px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; }
.stat-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; }
.stat-change { font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.stat-change.up { color: #4ade80; background: rgba(74, 222, 128, 0.1); }
.stat-change.danger { color: var(--urgency-high); background: rgba(229, 69, 69, 0.1); }
.stat-change.neutral { color: var(--text-muted); background: var(--bg-input); }

/* Grid */
.intel-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.intel-card {
  background: var(--bg-surface); border: 1px solid var(--border-subtle);
  border-radius: 10px; padding: 0; overflow: hidden;
}
.intel-card.full-width { grid-column: 1 / -1; }
.card-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px; border-bottom: 1px solid var(--border-subtle);
}
.card-title { font-size: 13px; font-weight: 600; color: var(--text-secondary); display: flex; align-items: center; gap: 8px; text-transform: uppercase; letter-spacing: 0.05em; }
.card-badge { font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px; background: rgba(74, 222, 128, 0.15); color: #4ade80; text-transform: uppercase; letter-spacing: 0.06em; }
.card-badge.alert { background: rgba(229, 69, 69, 0.15); color: var(--urgency-high); }
.card-meta { font-size: 11px; color: var(--text-muted); }

/* Topics */
.topics-list { padding: 14px 18px; display: flex; flex-direction: column; gap: 14px; }
.topic-item { }
.topic-info { display: flex; justify-content: space-between; margin-bottom: 6px; }
.topic-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.topic-count { font-size: 11px; color: var(--text-muted); }
.topic-bar { height: 4px; background: var(--border-muted); border-radius: 2px; overflow: hidden; }
.topic-bar-fill { height: 100%; border-radius: 2px; transition: width 0.6s ease; }

/* Sentiment */
.sentiment-grid { padding: 20px 18px; display: flex; justify-content: space-around; }
.sentiment-item { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.sentiment-ring {
  width: 72px; height: 72px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  background: conic-gradient(var(--ring-color) var(--ring-pct), var(--border-muted) 0);
  position: relative;
}
.sentiment-ring::after {
  content: ''; position: absolute; inset: 6px; border-radius: 50%; background: var(--bg-surface);
}
.sentiment-pct { font-size: 14px; font-weight: 700; color: var(--text-primary); position: relative; z-index: 1; }
.sentiment-label { font-size: 12px; color: var(--text-secondary); }
.sentiment-delta { font-size: 11px; font-weight: 600; }
.sentiment-delta.up { color: #4ade80; }
.sentiment-delta.down { color: #60a5fa; }
.sentiment-delta.danger { color: var(--urgency-high); }

/* Threats */
.threat-list { padding: 0; }
.threat-item { display: flex; align-items: center; gap: 12px; padding: 12px 18px; border-bottom: 1px solid var(--border-subtle); transition: background 0.12s ease; }
.threat-item:last-child { border-bottom: none; }
.threat-item:hover { background: var(--bg-hover); }
.threat-severity { width: 4px; height: 32px; border-radius: 2px; flex-shrink: 0; }
.threat-severity.critical { background: var(--urgency-high); }
.threat-severity.high { background: var(--accent-gold); }
.threat-severity.medium { background: #60a5fa; }
.threat-content { flex: 1; }
.threat-title { font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.threat-meta { font-size: 11px; color: var(--text-muted); }
.threat-badge { font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.04em; }
.threat-badge.critical { background: rgba(229, 69, 69, 0.15); color: var(--urgency-high); }
.threat-badge.high { background: var(--accent-gold-dim); color: var(--accent-gold); }
.threat-badge.medium { background: rgba(96, 165, 250, 0.15); color: #60a5fa; }

/* Insights */
.insights-list { padding: 14px 18px; display: flex; flex-direction: column; gap: 14px; }
.insight-item { display: flex; gap: 12px; align-items: flex-start; }
.insight-icon { width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.insight-body { flex: 1; }
.insight-text { font-size: 13px; line-height: 1.6; color: var(--text-secondary); margin-bottom: 4px; }
.insight-confidence { font-size: 11px; font-weight: 600; color: var(--accent-gold); }

/* Responsive */
@media (max-width: 900px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .intel-grid { grid-template-columns: 1fr; }
  .intel-card.full-width { grid-column: 1; }
}
</style>
