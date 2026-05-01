import { ref, watch, onMounted } from 'vue';

// Full theme definitions — every CSS variable mapped per theme
const THEME_DEFS = {
  'dark-gold': {
    '--bg-root': '#080808',
    '--bg-sidebar': '#111111',
    '--bg-topbar': '#111111',
    '--bg-surface': '#111111',
    '--bg-input': '#1e1e1e',
    '--bg-hover': '#1a1a1a',
    '--border-subtle': '#222222',
    '--border-muted': '#2a2a2a',
    '--text-primary': '#e8e8e8',
    '--text-secondary': '#888888',
    '--text-muted': '#555555',
    '--accent-gold': '#c98a2a',
    '--accent-gold-hover': '#d99a3a',
    '--accent-gold-dim': 'rgba(201, 138, 42, 0.15)',
    '--accent-gold-muted': 'rgba(201, 138, 42, 0.6)',
    '--urgency-high': '#e54545',
    '--urgency-medium': '#c98a2a',
    '--urgency-low': '#3a8a5c',
  },
  'dark-blue': {
    '--bg-root': '#0a0e1a',
    '--bg-sidebar': '#0f1525',
    '--bg-topbar': '#0f1525',
    '--bg-surface': '#0f1525',
    '--bg-input': '#151d30',
    '--bg-hover': '#131b2c',
    '--border-subtle': '#1c2640',
    '--border-muted': '#253050',
    '--text-primary': '#e2e8f0',
    '--text-secondary': '#7b8ba5',
    '--text-muted': '#4a5568',
    '--accent-gold': '#60a5fa',
    '--accent-gold-hover': '#7ab8ff',
    '--accent-gold-dim': 'rgba(96, 165, 250, 0.15)',
    '--accent-gold-muted': 'rgba(96, 165, 250, 0.6)',
    '--urgency-high': '#f87171',
    '--urgency-medium': '#60a5fa',
    '--urgency-low': '#34d399',
  },
  'dark-green': {
    '--bg-root': '#060d06',
    '--bg-sidebar': '#0b150b',
    '--bg-topbar': '#0b150b',
    '--bg-surface': '#0b150b',
    '--bg-input': '#122012',
    '--bg-hover': '#0f1a0f',
    '--border-subtle': '#1a2e1a',
    '--border-muted': '#234023',
    '--text-primary': '#e2f0e2',
    '--text-secondary': '#7ba57b',
    '--text-muted': '#4a6b4a',
    '--accent-gold': '#4ade80',
    '--accent-gold-hover': '#6fee9a',
    '--accent-gold-dim': 'rgba(74, 222, 128, 0.15)',
    '--accent-gold-muted': 'rgba(74, 222, 128, 0.6)',
    '--urgency-high': '#f87171',
    '--urgency-medium': '#4ade80',
    '--urgency-low': '#34d399',
  },
  'dark-purple': {
    '--bg-root': '#0c0815',
    '--bg-sidebar': '#110d1a',
    '--bg-topbar': '#110d1a',
    '--bg-surface': '#110d1a',
    '--bg-input': '#1a1428',
    '--bg-hover': '#161020',
    '--border-subtle': '#251d3a',
    '--border-muted': '#302548',
    '--text-primary': '#e8e2f0',
    '--text-secondary': '#9888b5',
    '--text-muted': '#5a4a72',
    '--accent-gold': '#a78bfa',
    '--accent-gold-hover': '#bfa4ff',
    '--accent-gold-dim': 'rgba(167, 139, 250, 0.15)',
    '--accent-gold-muted': 'rgba(167, 139, 250, 0.6)',
    '--urgency-high': '#f87171',
    '--urgency-medium': '#a78bfa',
    '--urgency-low': '#34d399',
  },
};

const FONT_SIZES = {
  Small: '12px',
  Default: '13px',
  Large: '15px',
};

const DENSITY_PADDING = {
  Compact: '8px',
  Comfortable: '14px',
  Spacious: '20px',
};

// Singleton state — shared across all components that import this
const activeTheme = ref('dark-gold');
const fontSize = ref('Default');
const feedDensity = ref('Comfortable');

// Load saved preferences from localStorage
function loadFromStorage() {
  try {
    const saved = localStorage.getItem('khaberni-appearance');
    if (saved) {
      const parsed = JSON.parse(saved);
      if (parsed.theme && THEME_DEFS[parsed.theme]) activeTheme.value = parsed.theme;
      if (parsed.fontSize && FONT_SIZES[parsed.fontSize]) fontSize.value = parsed.fontSize;
      if (parsed.density && DENSITY_PADDING[parsed.density]) feedDensity.value = parsed.density;
    }
  } catch {
    // Ignore corrupt storage
  }
}

function saveToStorage() {
  localStorage.setItem('khaberni-appearance', JSON.stringify({
    theme: activeTheme.value,
    fontSize: fontSize.value,
    density: feedDensity.value,
  }));
}

function applyTheme() {
  const root = document.documentElement;
  const vars = THEME_DEFS[activeTheme.value];
  if (!vars) return;

  // Apply all CSS variables
  for (const [prop, val] of Object.entries(vars)) {
    root.style.setProperty(prop, val);
  }

  // Apply font size
  root.style.setProperty('--base-font-size', FONT_SIZES[fontSize.value] || '13px');
  root.style.fontSize = FONT_SIZES[fontSize.value] || '13px';

  // Apply feed density
  root.style.setProperty('--feed-density', DENSITY_PADDING[feedDensity.value] || '14px');

  saveToStorage();
}

export function useTheme() {
  // Load from storage on first call
  loadFromStorage();

  // Watch for changes and apply
  watch([activeTheme, fontSize, feedDensity], applyTheme, { immediate: true });

  return {
    activeTheme,
    fontSize,
    feedDensity,
    themes: Object.keys(THEME_DEFS).map(id => {
      const d = THEME_DEFS[id];
      return {
        id,
        name: id === 'dark-gold' ? 'Dark Gold' : id === 'dark-blue' ? 'Midnight Blue' : id === 'dark-green' ? 'Forest' : 'Amethyst',
        bg: d['--bg-root'],
        sidebar: d['--bg-sidebar'],
        accent: d['--accent-gold'],
      };
    }),
    fontSizes: Object.keys(FONT_SIZES),
    densities: Object.keys(DENSITY_PADDING),
    applyTheme,
  };
}
