/**
 * Gallery — single source of truth, strict dedupe (no duplicate images ever)
 */

const MAP = "assets/media-map";

/** UI / non-photo assets — never show in gallery or home mosaic */
export const GALLERY_EXCLUDE = new Set([
  "f09e28130786425c25ceaa9561def661",
  "10f9a07b05780c7691c41a3bba7f817d",
  "e1f78e667dbffb6298b1859dcb1092af",
  "0bee10adc0a548861f7ce9fa2aa929e1",
  "0b15a29edb41617b26d8e9fd1cc1c12d",
  "40988032d76b9fba43f7ea7f5179c871",
  "240d11b28e54454182e86f7293b631f7",
  "15430ce4c716dcf666cc4d22e3a41eb4",
  "88c84b8adc504d0c6bc888ad132eb388",
  "fec4c46f59d2687154e3f364f3b1cff0",
  "fea1775c265beea9b248f4fa76d938d0",
  "founders",
  "test",
]);

export function stem(path) {
  if (!path) return "";
  const file = String(path).split("/").pop().split("?")[0];
  return file.replace(/\.[^.]+$/, "").toLowerCase();
}

export function isGalleryPhoto(path, extraExclude = new Set()) {
  const id = stem(path);
  if (!id || GALLERY_EXCLUDE.has(id) || extraExclude.has(id)) return false;
  if (!/\.(jpe?g|webp)$/i.test(path)) return false;
  if (/\.png$/i.test(path)) return false;
  return true;
}

async function loadJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed ${path}`);
  return res.json();
}

let visualSkipStems = null;

/** Stems of near-duplicate photos (see scripts/rebuild_gallery_deduped.py) */
async function loadVisualSkipStems() {
  if (visualSkipStems) return visualSkipStems;
  try {
    const data = await loadJson(`${MAP}/gallery-visual-skip.json`);
    visualSkipStems = new Set(
      (data.skip || []).map((name) => stem(name)).filter(Boolean)
    );
  } catch {
    visualSkipStems = new Set();
  }
  return visualSkipStems;
}

function mergeExclude(extraExclude = new Set()) {
  const out = new Set(extraExclude);
  if (visualSkipStems) {
    for (const id of visualSkipStems) out.add(id);
  }
  return out;
}

/** One canonical src per image — local file only */
export function normalizeGalleryItem(item, extraExclude = new Set()) {
  const name = (item.name || item.path || item.src || "").split("/").pop().split("?")[0];
  if (!name || !isGalleryPhoto(name, extraExclude)) return null;

  const id = stem(name);
  if (!id || GALLERY_EXCLUDE.has(id) || extraExclude.has(id)) return null;

  const src = `assets/media/${name}`;
  return { id, name, path: src, src };
}

/** Strict dedupe by image id and src */
export function uniqueGalleryItems(items, extraExclude = new Set()) {
  const seenId = new Set();
  const seenSrc = new Set();
  const out = [];

  for (const raw of items) {
    const item = normalizeGalleryItem(raw, extraExclude);
    if (!item) continue;
    if (seenId.has(item.id) || seenSrc.has(item.src)) continue;
    seenId.add(item.id);
    seenSrc.add(item.src);
    out.push(item);
  }

  return out;
}

/** Evenly spaced picks for home mosaic — each image at most once */
export function pickShowcaseItems(items, count, extraExclude = new Set()) {
  const unique = uniqueGalleryItems(items, extraExclude);
  if (unique.length <= count) return unique;

  const picked = [];
  const used = new Set();
  const step = unique.length / count;

  for (let n = 0; n < count; n++) {
    const idx = Math.min(unique.length - 1, Math.floor(n * step + step * 0.5));
    let i = idx;
    while (i < unique.length && used.has(unique[i].id)) i += 1;
    if (i >= unique.length) {
      i = unique.findIndex((x) => !used.has(x.id));
    }
    if (i < 0) break;
    used.add(unique[i].id);
    picked.push(unique[i]);
  }

  return picked;
}

/** Split unique items into disjoint row pools (no image in two rows) */
export function partitionForRows(items, rowCount, extraExclude = new Set()) {
  const unique = uniqueGalleryItems(items, extraExclude);
  if (!rowCount || !unique.length) return [];

  const size = Math.ceil(unique.length / rowCount);
  const rows = [];
  for (let r = 0; r < rowCount; r++) {
    rows.push(unique.slice(r * size, (r + 1) * size));
  }
  return rows;
}

export async function loadGalleryPageOrder(extraExclude = new Set()) {
  try {
    await loadVisualSkipStems();
    const exclude = mergeExclude(extraExclude);
    const data = await loadJson(`${MAP}/gallery-page-order.json`);
    return uniqueGalleryItems(data.order || [], exclude);
  } catch {
    return [];
  }
}
