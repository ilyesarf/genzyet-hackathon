import { ref, onMounted } from 'vue';

const ANALYST_BASE = '/api/analyst';

export function useAnalyst() {
  const data = ref([]);
  const tldr = ref([]);
  const loading = ref(true);
  const error = ref(null);

  const fetchIntelligence = async (window = 24, category = null) => {
    loading.value = true;
    error.value = null;
    
    try {
      const params = new URLSearchParams({ window: String(window) });
      if (category && category !== 'all') params.append('category', category);

      const res = await fetch(`${ANALYST_BASE}/analyze?${params}`);
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Analysis failed (${res.status})`);
      }

      const json = await res.json();
      const result = json.data || {};

      data.value = (result.items || []).map(item => ({
        headline: item.headline,
        source: item.source,
        date: item.date,
        why_it_matters: item.why_it_matters,
        relevance_score: item.relevance_score,
      }));

      tldr.value = result.tldr || [];
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  const refreshIntelligence = async (window = 24, category = null) => {
    loading.value = true;
    error.value = null;

    try {
      const params = new URLSearchParams({ window: String(window) });
      if (category && category !== 'all') params.append('category', category);

      const res = await fetch(`${ANALYST_BASE}/analyze/refresh?${params}`, {
        method: 'POST',
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Refresh failed (${res.status})`);
      }

      const json = await res.json();
      const result = json.data || {};

      data.value = (result.items || []).map(item => ({
        headline: item.headline,
        source: item.source,
        date: item.date,
        why_it_matters: item.why_it_matters,
        relevance_score: item.relevance_score,
      }));

      tldr.value = result.tldr || [];
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    fetchIntelligence();
  });

  return {
    data,
    tldr,
    loading,
    error,
    fetch: fetchIntelligence,
    refresh: refreshIntelligence,
  };
}
