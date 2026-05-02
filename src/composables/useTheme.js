import { ref, watch } from 'vue';

// Theme definitions using the current CSS variable names
const THEME_DEFS = {
  'dark-gold': {
    '--bg': '#080808',
    '--bg2': '#111111',
    '--bg3': '#181818',
    '--border': '#222222',
    '--border2': '#2a2a2a',
    '--text': '#f0ede6',
    '--text2': '#888880',
    '--text3': '#555550',
    '--accent': 'oklch(75% 0.18 65)',
    '--accent2': 'oklch(65% 0.16 65)',
    '--red': 'oklch(65% 0.2 25)',
    '--green': 'oklch(65% 0.15 145)',
    '--blue': 'oklch(65% 0.15 245)',
  },
  'dark-blue': {
    '--bg': '#0a0e1a',
    '--bg2': '#0f1525',
    '--bg3': '#151d30',
    '--border': '#1c2640',
    '--border2': '#253050',
    '--text': '#e2e8f0',
    '--text2': '#7b8ba5',
    '--text3': '#4a5568',
    '--accent': '#60a5fa',
    '--accent2': '#3b82f6',
    '--red': '#f87171',
    '--green': '#34d399',
    '--blue': '#60a5fa',
  },
  'dark-green': {
    '--bg': '#060d06',
    '--bg2': '#0b150b',
    '--bg3': '#122012',
    '--border': '#1a2e1a',
    '--border2': '#234023',
    '--text': '#e2f0e2',
    '--text2': '#7ba57b',
    '--text3': '#4a6b4a',
    '--accent': '#4ade80',
    '--accent2': '#22c55e',
    '--red': '#f87171',
    '--green': '#4ade80',
    '--blue': '#60a5fa',
  },
  'dark-purple': {
    '--bg': '#0c0815',
    '--bg2': '#110d1a',
    '--bg3': '#1a1428',
    '--border': '#251d3a',
    '--border2': '#302548',
    '--text': '#e8e2f0',
    '--text2': '#9888b5',
    '--text3': '#5a4a72',
    '--accent': '#a78bfa',
    '--accent2': '#8b5cf6',
    '--red': '#f87171',
    '--green': '#34d399',
    '--blue': '#60a5fa',
  },
  'light': {
    '--bg': '#fafaf8',
    '--bg2': '#f0ede6',
    '--bg3': '#e8e4dc',
    '--border': '#d0cdc6',
    '--border2': '#b8b5ae',
    '--text': '#1a1814',
    '--text2': '#5a5650',
    '--text3': '#9a9690',
    '--accent': 'oklch(48% 0.18 65)',
    '--accent2': 'oklch(40% 0.16 65)',
    '--red': 'oklch(50% 0.2 25)',
    '--green': 'oklch(45% 0.15 145)',
    '--blue': 'oklch(50% 0.15 245)',
  },
};

// Singleton reactive state
const activeTheme = ref('dark-gold');

function loadFromStorage() {
  try {
    const saved = localStorage.getItem('khaberni-theme');
    if (saved && THEME_DEFS[saved]) activeTheme.value = saved;
  } catch { /* ignore */ }
}

function saveToStorage() {
  try { localStorage.setItem('khaberni-theme', activeTheme.value); } catch { /* ignore */ }
}

function applyTheme() {
  const root = document.documentElement;
  const vars = THEME_DEFS[activeTheme.value];
  if (!vars) return;
  for (const [prop, val] of Object.entries(vars)) {
    root.style.setProperty(prop, val);
  }
  const isLight = activeTheme.value === 'light';
  root.setAttribute('data-theme', activeTheme.value);
  root.style.colorScheme = isLight ? 'light' : 'dark';
  saveToStorage();
}

export function useTheme() {
  loadFromStorage();
  watch(activeTheme, applyTheme, { immediate: true });

  const NAMES = {
    'dark-gold': 'Dark Gold',
    'dark-blue': 'Midnight Blue',
    'dark-green': 'Forest',
    'dark-purple': 'Amethyst',
    'light': 'Light',
  };

  return {
    activeTheme,
    themes: Object.keys(THEME_DEFS).map(id => {
      const d = THEME_DEFS[id];
      return {
        id,
        name: NAMES[id] || id,
        bg: d['--bg'],
        sidebar: d['--bg2'],
        accent: d['--accent'],
      };
    }),
    applyTheme,
  };
}
