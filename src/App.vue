<template>
  <div class="app-shell">
    <aside class="sidebar">
      <!-- Logo -->
      <div class="logo-block">
        <svg width="32" height="32" viewBox="0 0 40 40" fill="none">
          <rect width="40" height="40" fill="var(--accent)" />
          <text x="20" y="27" text-anchor="middle" font-family="Noto Sans Arabic" font-size="18" font-weight="700" fill="#000">خ</text>
        </svg>
        <div class="logo-text">
          <span class="brand-name">khaberni</span>
          <span class="brand-arabic">خبرني</span>
        </div>
      </div>

      <!-- Nav -->
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-link" exact-active-class="active">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <path d="M2 14l4-4 3 2 5-8" stroke="currentColor" stroke-width="1.5" stroke-linecap="square"/>
            <circle cx="14" cy="4" r="1.5" fill="currentColor"/>
          </svg>
          <span>{{ t.nav_strategy }}</span>
        </router-link>
        <router-link to="/news" class="nav-link" active-class="active">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <rect x="2" y="3" width="12" height="1.5" fill="currentColor"/>
            <rect x="2" y="7" width="8" height="1.5" fill="currentColor"/>
            <rect x="2" y="11" width="10" height="1.5" fill="currentColor"/>
          </svg>
          <span>{{ t.nav_news }}</span>
        </router-link>
        <router-link to="/sources" class="nav-link" active-class="active">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="5" stroke="currentColor" stroke-width="1.5"/>
            <path d="M8 3c-2 0-3 2.5-3 5s1 5 3 5" stroke="currentColor" stroke-width="1.2"/>
            <path d="M8 3c2 0 3 2.5 3 5s-1 5-3 5" stroke="currentColor" stroke-width="1.2"/>
            <path d="M3 8h10" stroke="currentColor" stroke-width="1.2"/>
          </svg>
          <span>{{ t.nav_sources }}</span>
        </router-link>
        <router-link to="/settings" class="nav-link" active-class="active">
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.5"/>
            <path d="M8 2v1M8 13v1M2 8h1M13 8h1M3.5 3.5l.7.7M11.8 11.8l.7.7M3.5 12.5l.7-.7M11.8 4.2l.7-.7" stroke="currentColor" stroke-width="1.2" stroke-linecap="square"/>
          </svg>
          <span>{{ t.nav_settings }}</span>
        </router-link>
      </nav>

      <!-- Language switcher -->
      <div class="lang-block">
        <div class="lang-label">LANGUAGE</div>
        <div class="lang-btns">
          <button
            v-for="l in ['en','fr','ar']"
            :key="l"
            class="lang-btn"
            :class="{ active: lang === l }"
            @click="setLang(l)"
          >{{ l.toUpperCase() }}</button>
        </div>
      </div>

      <!-- Agency footer -->
      <div class="sidebar-footer">
        <div class="agency-name">3SG COMMUNICATIONS</div>
        <div class="agency-plan">ENTERPRISE · PLAN PRO</div>
      </div>
    </aside>

    <main class="main-area">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" :t="t" :lang="lang" :set-lang="setLang" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, provide } from 'vue';

const TRANSLATIONS = {
  en: {
    nav_news: 'News Feed', nav_sources: 'Sources', nav_strategy: 'Strategy', nav_settings: 'Settings',
    update: 'Update', updating: 'Updating...', headlines: 'Top Headlines',
    all: 'All', tech: 'Tech', sport: 'Sport', social: 'Social', weather: 'Weather', politics: 'Politics', economy: 'Economy',
    urgency: 'Urgency', relevance: 'Relevance',
    run_agent: 'Run Analysis',
    sources_title: 'Manage Sources', add_source: 'Add Source',
    strategy_title: 'Strategy Workshop', drop_ppt: 'Drop your PowerPoint here', improve_btn: 'Improve My Strategy',
    settings_title: 'Settings',
  },
  fr: {
    nav_news: 'Actualités', nav_sources: 'Sources', nav_strategy: 'Stratégie', nav_settings: 'Paramètres',
    update: 'Actualiser', updating: 'Actualisation…', headlines: 'À la une',
    all: 'Tout', tech: 'Tech', sport: 'Sport', social: 'Social', weather: 'Météo', politics: 'Politique', economy: 'Économie',
    urgency: 'Urgence', relevance: 'Pertinence',
    run_agent: "Lancer l'Analyse",
    sources_title: 'Gérer les Sources', add_source: 'Ajouter une Source',
    strategy_title: 'Atelier Stratégie', drop_ppt: 'Déposez votre PowerPoint ici', improve_btn: 'Améliorer Ma Stratégie',
    settings_title: 'Paramètres',
  },
  ar: {
    nav_news: 'موجز الأخبار', nav_sources: 'المصادر', nav_strategy: 'الاستراتيجية', nav_settings: 'الإعدادات',
    update: 'تحديث', updating: 'جارٍ التحديث…', headlines: 'أبرز العناوين',
    all: 'الكل', tech: 'تقنية', sport: 'رياضة', social: 'اجتماعي', weather: 'طقس', politics: 'سياسة', economy: 'اقتصاد',
    urgency: 'الإلحاح', relevance: 'الصلة',
    run_agent: 'تشغيل التحليل',
    sources_title: 'إدارة المصادر', add_source: 'إضافة مصدر',
    strategy_title: 'ورشة الاستراتيجية', drop_ppt: 'أسقط ملف PowerPoint هنا', improve_btn: 'تحسين استراتيجيتي',
    settings_title: 'الإعدادات',
  },
};

const lang = ref('en');
const t = ref(TRANSLATIONS['en']);

function setLang(l) {
  lang.value = l;
  t.value = TRANSLATIONS[l] || TRANSLATIONS.en;
  document.documentElement.dir = l === 'ar' ? 'rtl' : 'ltr';
  document.documentElement.lang = l;
}

provide('lang', lang);
provide('t', t);
provide('setLang', setLang);
</script>

<style>
.app-shell {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: var(--bg);
}

/* ── Sidebar ── */
.sidebar {
  width: 220px;
  background: var(--bg);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100%;
}

.logo-block {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 28px 20px 24px;
  border-bottom: 1px solid var(--border);
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1;
  gap: 3px;
}

.brand-name {
  font-family: var(--ff-head);
  font-weight: 800;
  font-size: 15px;
  letter-spacing: -0.02em;
  color: var(--text);
}

.brand-arabic {
  font-family: var(--ff-arabic);
  font-weight: 600;
  font-size: 11px;
  color: var(--accent);
  direction: rtl;
}

/* Nav */
.sidebar-nav {
  flex: 1;
  padding: 12px 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 11px 20px;
  background: transparent;
  border-left: 2px solid transparent;
  color: var(--text2);
  font-family: var(--ff-body);
  font-size: 13px;
  font-weight: 400;
  text-decoration: none;
  transition: all 0.15s;
}

.nav-link:hover {
  color: var(--text);
  background: var(--bg2);
}

.nav-link.active {
  background: var(--bg2);
  border-left-color: var(--accent);
  color: var(--text);
  font-weight: 500;
}

.nav-link.active svg {
  color: var(--accent);
}

/* Language */
.lang-block {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
}

.lang-label {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.lang-btns {
  display: flex;
  gap: 4px;
}

.lang-btn {
  flex: 1;
  padding: 5px 0;
  background: var(--bg2);
  border: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--ff-mono);
  font-size: 10px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.lang-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #000;
}

/* Footer */
.sidebar-footer {
  padding: 12px 20px 20px;
  border-top: 1px solid var(--border);
}

.agency-name {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  letter-spacing: 0.08em;
}

.agency-plan {
  font-family: var(--ff-mono);
  font-size: 9px;
  color: var(--text3);
  margin-top: 2px;
}

/* Main */
.main-area {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Page transitions */
.page-enter-active { transition: opacity 0.15s ease-out; }
.page-leave-active { transition: opacity 0.1s ease-in; }
.page-enter-from, .page-leave-to { opacity: 0; }

@keyframes spin { to { transform: rotate(360deg); } }
</style>
