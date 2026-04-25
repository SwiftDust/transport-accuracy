import type { Feed } from "./types";

const BASE = import.meta.env.VITE_API_URL;

export async function getDelays(feed: Feed): Promise<any> {
  const params = new URLSearchParams({
    id: feed.id,
    rt_url: feed.rt_url,
    ...(feed.location && { location: feed.location }),
    ...(feed.provider_name && { provider_name: feed.provider_name }),
    ...(feed.feed_name && { feed_name: feed.feed_name }),
  });

  const res = await fetch(`${BASE}/delays?${params}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function search(query: string): Promise<any> {
  const res = await fetch(`${BASE}/search/${query}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getAIAnalysis(
  country: string,
  providerName: string,
  avgDelay: float,
  onTime: int,
  onTimePercentage: float,
): Promise<any> {
  const params = new URLSearchParams({
    country: country,
    provider_name: providerName,
    avg_delay: avgDelay,
    on_time: onTime,
    on_time_percentage: onTimePercentage,
  });
  const res = await fetch(`${BASE}/analysis/?${params}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
