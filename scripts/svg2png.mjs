import { readFileSync } from "fs";
import sharp from "sharp";

const [svgPath, pngPath, w, h, bgHex = "transparent"] = process.argv.slice(2);
const svg = readFileSync(svgPath);
const bg =
  bgHex === "transparent"
    ? { r: 0, g: 0, b: 0, alpha: 0 }
    : { r: 255, g: 255, b: 255, alpha: 1 };

await sharp(svg, { density: 600 })
  .resize(Number(w), Number(h), { fit: "fill", background: bg, kernel: sharp.kernel.lanczos3 })
  .png()
  .toFile(pngPath);
