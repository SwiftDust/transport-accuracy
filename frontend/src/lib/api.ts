const BASE = import.meta.env.VITE_API_URL;

export async function getCountryDelays(country: string): Promise<any> {
  const res = await fetch(`${BASE}/delays/country/${country}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function search(query: string): Promise<any> {
  const res = await fetch(`${BASE}/search/${query}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
