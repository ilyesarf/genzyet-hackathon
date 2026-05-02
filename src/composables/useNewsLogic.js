export function useNewsLogic() {
  function autoCategorize(title, body = '') {
    const content = (title + ' ' + body).toLowerCase();
    
    const mapping = {
      tech: ['ai', 'intelligence artificielle', 'startup', 'digital', 'data', 'api', 'software', 'robot', 'cyber', 'meta', 'google', 'apple', 'microsoft'],
      economy: ['bourse', 'dinar', 'imf', 'fmi', 'growth', 'inflation', 'banque', 'bank', 'finance', 'business', 'entreprises', 'marché'],
      politics: ['gouvernement', 'parlement', 'vote', 'élection', 'ministre', 'policy', 'summit', 'sommet', 'democratie', 'onu', 'un'],
      culture: ['art', 'cinéma', 'film', 'musique', 'music', 'exhibition', 'expo', 'festival', 'urban', 'lifestyle', 'théâtre', 'misk'],
      lifestyle: ['food', 'cuisine', 'travel', 'gastronomy', 'voyage', 'restaurant', 'table', 'gastronomie'],
      sport: ['football', 'champions league', 'psg', 'bayern', 'match', 'score', 'sport', 'tennis', 'atp'],
      weather: ['météo', 'pluie', 'soleil', 'température', 'climat', 'weather', 'rain', 'forecast'],
      social: ['société', 'gen z', 'jeunes', 'social media', 'trends', 'tendances', 'communauté', 'femme', 'women']
    };

    for (const [cat, keywords] of Object.entries(mapping)) {
      if (keywords.some(k => content.includes(k))) return cat;
    }
    
    return 'culture'; // Default
  }

  function calculateScores(title, body = '', publishedAt) {
    const content = (title + ' ' + body).toLowerCase();
    
    let urgency = 40;
    let relevance = 40;
    
    // Recency factor (up to +40)
    if (publishedAt) {
      const hoursOld = (Date.now() - new Date(publishedAt).getTime()) / 3600000;
      if (hoursOld < 1) urgency += 40;
      else if (hoursOld < 3) urgency += 30;
      else if (hoursOld < 8) urgency += 20;
      else if (hoursOld < 24) urgency += 10;
    }
    
    // Breaking keywords (up to +30)
    const urgentWords = ['breaking', 'urgent', 'alert', 'crisis', 'live', 'now', 'today', 'alerte', 'direct', 'عاجل', 'حصري'];
    const urgentMatches = urgentWords.filter(w => content.includes(w)).length;
    urgency += Math.min(urgentMatches * 15, 30);
    
    // Length factor for relevance (up to +25)
    const length = content.length;
    if (length > 2000) relevance += 25;
    else if (length > 1000) relevance += 18;
    else if (length > 500) relevance += 10;
    else if (length > 200) relevance += 5;
    
    // Strategic keywords (up to +30)
    const strategicWords = ['report', 'study', 'analysis', 'data', 'revenue', 'market', 'trend', 'strategy', 'rapport', 'étude', 'analyse', 'données', 'marché', 'stratégie', 'تقرير', 'دراسة', 'تحليل', 'بيانات', 'سوق', 'استراتيجية'];
    const strategicMatches = strategicWords.filter(w => content.includes(w)).length;
    relevance += Math.min(strategicMatches * 15, 30);

    // Deterministic variance so not everything is identical
    let hash = 0;
    for (let i = 0; i < title.length; i++) hash = (hash << 5) - hash + title.charCodeAt(i);
    hash = Math.abs(hash);
    
    urgency += (hash % 15);
    relevance += ((hash >> 4) % 15);
    
    // Cap at 99
    urgency = Math.min(Math.max(Math.floor(urgency), 10), 99);
    relevance = Math.min(Math.max(Math.floor(relevance), 10), 99);
    
    // Tag generation
    let tag = null;
    if (urgency > 85) tag = 'BREAKING';
    else if (urgency > 70) tag = 'ALERT';
    else if (relevance > 80 && urgency > 60) tag = 'HOT';
    
    return { urgency, relevance, tag };
  }

  return { autoCategorize, calculateScores };
}
