import { readFileSync, mkdirSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import sharp from "sharp";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");
const brand = join(root, "assets", "brand");

async function rasterize(svgName, pngName, w, h = w) {
  const svg = readFileSync(join(brand, svgName));
  await sharp(svg, { density: 300 })
    .resize(w, h, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png()
    .toFile(join(brand, pngName));
  console.log("Wrote", pngName);
}

mkdirSync(join(brand, "social"), { recursive: true });

await rasterize("favicon.svg", "favicon-32x32.png", 32);
await rasterize("favicon.svg", "favicon-16x16.png", 16);
await rasterize("logo-mark-white-on-black.svg", "apple-touch-icon.png", 180);
await rasterize("social/og-image.svg", "social/og-image.png", 1200, 630);
await rasterize("social/instagram-profile.svg", "social/instagram-profile.png", 320);
