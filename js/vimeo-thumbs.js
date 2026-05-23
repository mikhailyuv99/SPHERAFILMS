/**
 * Reliable Vimeo poster URLs (vimeocdn) — vumbnail.com often fails on mobile.
 */
const cache = new Map();

export async function resolveVimeoThumbs(ids) {
  const unique = [...new Set((ids || []).filter(Boolean))];
  const map = {};
  await Promise.all(
    unique.map(async (id) => {
      map[id] = await resolveVimeoThumb(id);
    })
  );
  return map;
}

export async function resolveVimeoThumb(id) {
  if (cache.has(id)) return cache.get(id);

  let url = null;
  try {
    const ctrl = new AbortController();
    const timer = window.setTimeout(() => ctrl.abort(), 8000);
    const res = await fetch(`https://vimeo.com/api/v2/video/${id}.json`, { signal: ctrl.signal });
    window.clearTimeout(timer);
    if (res.ok) {
      const data = await res.json();
      const v = data?.[0];
      url = v?.thumbnail_large || v?.thumbnail_medium || v?.thumbnail_small || null;
    }
  } catch (_) {
    /* network / timeout */
  }

  if (!url) url = `https://vumbnail.com/${id}.jpg`;
  cache.set(id, url);
  return url;
}
