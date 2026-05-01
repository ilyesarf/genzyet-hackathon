<template>
  <div class="app-shell">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="logo-block">
        <span class="logo-arabic">خ</span>
        <div class="logo-text">
          <span class="brand-name">Khaberni</span>
          <span class="brand-tagline">خبرني</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/" class="nav-link" active-class="active" exact-active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/intelligence" class="nav-link" active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <span>Intelligence</span>
        </router-link>
        <router-link to="/sources" class="nav-link" active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
          <span>Sources</span>
        </router-link>
        <router-link to="/settings" class="nav-link" active-class="active">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          <span>Settings</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-badge">
          <div class="user-avatar">SA</div>
          <div class="user-meta">
            <span class="user-name">Son of Anton</span>
            <span class="user-role">Lead Analyst</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="main-area">
      <!-- Top Bar -->
      <header class="topbar">
        <div class="search-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" placeholder="Search intelligence feeds..." class="search-input" />
        </div>
        <button class="btn-primary" @click="$router.push('/')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New Brief
        </button>
      </header>

      <!-- Router View with transition -->
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup>
import { useTheme } from '@/composables/useTheme.js';
// Initialize theme on app load — restores from localStorage
useTheme();
</script>

<style>
/* ═══ App Shell ═══ */
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--bg-root);
}

/* ═══ Sidebar ═══ */
.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 20;
  padding: 0;
}

.logo-block {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.logo-arabic {
  width: 42px;
  height: 42px;
  background: var(--accent-gold);
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Noto Naskh Arabic', serif;
  font-size: 22px;
  font-weight: 700;
  border-radius: 6px;
  flex-shrink: 0;
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 0;
  line-height: 1.2;
}

.brand-name {
  font-family: 'Outfit', sans-serif;
  font-weight: 700;
  font-size: 16px;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

.brand-tagline {
  font-family: 'Noto Naskh Arabic', serif;
  font-size: 11px;
  color: var(--text-secondary);
  direction: rtl;
}

/* Nav */
.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 6px;
  font-size: 13.5px;
  font-weight: 500;
  transition: all 0.15s ease;
}

.nav-link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-link.active {
  background: var(--accent-gold-dim);
  color: var(--accent-gold);
}

.nav-link svg {
  flex-shrink: 0;
  opacity: 0.7;
}

.nav-link.active svg {
  opacity: 1;
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-subtle);
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, var(--accent-gold), #d4a040);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
  color: #000;
  flex-shrink: 0;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.user-role {
  font-size: 11px;
  color: var(--text-secondary);
}

/* ═══ Main Area ═══ */
.main-area {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ═══ Top Bar ═══ */
.topbar {
  height: var(--topbar-height);
  background: var(--bg-topbar);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  padding: 0 12px;
  width: 320px;
  transition: border-color 0.15s ease;
}

.search-box:focus-within {
  border-color: var(--accent-gold-muted);
}

.search-box svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.search-input {
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 13px;
  padding: 8px 0;
  width: 100%;
  font-family: inherit;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--accent-gold);
  color: #000;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s ease;
}

.btn-primary:hover {
  background: var(--accent-gold-hover);
}

.btn-primary svg {
  flex-shrink: 0;
}

/* ═══ Page Transitions ═══ */
.page-enter-active { transition: all 0.2s ease-out; }
.page-leave-active { transition: all 0.15s ease-in; }
.page-enter-from { opacity: 0; transform: translateY(6px); }
.page-leave-to { opacity: 0; transform: translateY(-4px); }

/* ═══ Responsive ═══ */
@media (max-width: 1024px) {
  .sidebar {
    width: 64px;
    overflow: hidden;
  }
  .logo-text,
  .nav-link span,
  .user-meta {
    display: none;
  }
  .logo-block {
    justify-content: center;
    padding: 16px 8px 20px;
  }
  .sidebar-nav {
    padding: 16px 8px;
  }
  .nav-link {
    justify-content: center;
    padding: 10px;
  }
  .main-area {
    margin-left: 64px;
  }
  .search-box {
    width: 200px;
  }
}
</style>
