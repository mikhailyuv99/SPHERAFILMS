import { readFileSync, mkdirSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import sharp from "sharp";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const branding = join(root, "branding");

async function rasterize(svgName, pngName, w, h = w, bg = null) {
  const svg = readFileSync(join(branding, svgName));
  const bgOpt = bg ?? { r: 0, g: 0, b: 0, alpha: 0 };
  await sharp(svg, { density: 300 })
    .resize(w, h, { fit: "fill", background: bgOpt })
    .png()
    .toFile(join(branding, pngName));
  console.log("Wrote", pngName);
}

mkdirSync(branding, { recursive: true });

await rasterize("favicon.svg", "favicon-16x16.png", 16);
await rasterize("favicon.svg", "favicon-32x32.png", 32);
await rasterize("favicon.svg", "favicon-48x48.png", 48);
await rasterize("logo-mark-black-on-white.svg", "apple-touch-icon.png", 180, 180, {
  r: 255,
  g: 255,
  b: 255,
  alpha: 1,
});
await rasterize("logo-mark-white-on-black.svg", "apple-touch-icon-dark.png", 180, 180, {
  r: 0,
  g: 0,
  b: 0,
  alpha: 1,
});
await rasterize("logo-mark-black-on-white.svg", "instagram-profile.png", 320, 320, {
  r: 255,
  g: 255,
  b: 255,
  alpha: 1,
});
await rasterize("logo-mark-white-on-black.svg", "instagram-profile-dark.png", 320, 320, {
  r: 0,
  g: 0,
  b: 0,
  alpha: 1,
});
