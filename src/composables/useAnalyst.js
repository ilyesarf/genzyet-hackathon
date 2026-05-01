import { ref, onMounted } from 'vue';

export function useAnalyst() {
  const data = ref([]);
  const loading = ref(true);
  const error = ref(null);

  const fetchIntelligence = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      // Simulating network delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      data.value = [
        {
          title: "Neural Engine Breakthrough: Apple's M4 Chip benchmarks leaked",
          source: "TechPulse",
          category: "Hardware",
          urgency_score: 85,
          timestamp: new Date().toISOString(),
          summary: "Newly leaked benchmarks indicate a 40% jump in NPU performance, potentially reshaping the competitive landscape for edge AI marketing campaigns."
        },
        {
          title: "European Union finalizes landmark AI Act regulations",
          source: "Reuters",
          category: "Regulatory",
          urgency_score: 92,
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          summary: "The final text introduces strict transparency requirements for generative models. Marketing firms must audit their automated content pipelines immediately."
        },
        {
          title: "Consumer sentiment shifts toward 'Human-Made' branding",
          source: "MarketWatch",
          category: "Consumer Trends",
          urgency_score: 45,
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          summary: "Recent survey data suggests a growing premium on human-verified content. Brands should pivot their messaging to emphasize creative authenticity."
        },
        {
          title: "OpenAI announces GPT-5 developer preview",
          source: "The Verge",
          category: "AI Software",
          urgency_score: 98,
          timestamp: new Date(Date.now() - 1800000).toISOString(),
          summary: "The next generation of LLMs is here. Early access shows significant improvements in complex reasoning and multi-modal integration for automated analysts."
        },
        {
          title: "Cybersecurity Alert: New phishing wave targets marketing VPs",
          source: "Securly",
          category: "Security",
          urgency_score: 72,
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          summary: "Highly targeted campaigns are using deepfake audio to bypass traditional auth. Immediate staff training on verification protocols is required."
        }
      ];
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
    loading,
    error,
    refresh: fetchIntelligence
  };
}
