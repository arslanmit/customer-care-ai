import supabase from './supabaseClient';

// Log a single conversation event to the database
export const logEvent = async (event) => {
  if (!supabase) return;
  try {
    await supabase.from('conversation_events').insert([event]);
  } catch (error) {
    // Silently fail – analytics should never break the app UI
    console.error('Analytics logEvent error:', error);
  }
};

// Submit user feedback (rating/comment)
export const submitFeedback = async (feedback) => {
  if (!supabase) return;
  try {
    await supabase.from('feedback').insert([feedback]);
  } catch (error) {
    console.error('Analytics submitFeedback error:', error);
  }
};

// Fetch aggregated analytics from the backend. First tries an RPC function for
// server-side aggregation, and falls back to client-side aggregation if that
// isnt available.
export const fetchAggregatedStats = async () => {
  if (!supabase) return null;

  // 1. Prefer an RPC (Postgres function) if it exists
  const { data: rpcData, error: rpcError } = await supabase.rpc('get_aggregated_analytics');
  if (!rpcError && rpcData) {
    return rpcData;
  }

  console.warn('get_aggregated_analytics RPC unavailable – falling back to client aggregation');

  // 2. Fallback – fetch raw events and aggregate in the client
  const { data: events, error } = await supabase
    .from('conversation_events')
    .select('sender,intent,timestamp')
    .limit(10000); // safety cap – adjust to your needs

  if (error || !events) return null;

  const stats = {
    userCount: 0,
    botCount: 0,
    avgResponseTime: 0,
    intentDistribution: {},
  };

  let lastUserTime = null;
  const responseTimes = [];

  events.forEach((ev) => {
    if (ev.sender === 'user') {
      stats.userCount += 1;
      lastUserTime = new Date(ev.timestamp);
    } else if (ev.sender === 'bot') {
      stats.botCount += 1;
      if (ev.intent) {
        stats.intentDistribution[ev.intent] = (stats.intentDistribution[ev.intent] || 0) + 1;
      }
      if (lastUserTime) {
        responseTimes.push(new Date(ev.timestamp) - lastUserTime);
        lastUserTime = null;
      }
    }
  });

  stats.avgResponseTime = responseTimes.length
    ? Math.round(responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length)
    : 0;

  return stats;
};
