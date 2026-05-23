from pathlib import Path
import re

p = Path(__file__).resolve().parents[1] / "index.html"
t = p.read_text(encoding="utf-8")

new_block = """        <figure class="founders__hero" data-aos="fade-up">
          <div class="founders__photo" id="founders-photo"></div>
          <figcaption class="founders__caption">
            <h3>Enzo Da Silva &amp; Lani Giacinti</h3>
            <p id="founders-intro-text"></p>
          </figcaption>
        </figure>
        <motion></motion>
        <div class="founders__bios">
          <article class="founder-bio" data-aos="fade-up">
            <h4>Enzo Da Silva</h4>
            <p id="founders-enzo-text"></p>
          </article>
          <article class="founder-bio" data-aos="fade-up" data-aos-delay="80">
            <h4>Lani Giacinti</h4>
            <p id="founders-lani-text"></p>
          </article>
        </div>"""

pat = r'        <div class="founders__grid">.*?</motion></motion></motion></div>\s*        <p class="founders__together"'
if "founders__grid" not in t:
    pat = r'        <div class="founders__grid">.*?</motion></div>\s*        <p class="founders__together"'
if "founders__grid" in t and not re.search(pat, t, re.S):
    pat = r'        <motion></motion>\s*<div class="founders__grid">.*?</div>\s*        <p class="founders__together"'
if not re.search(pat, t, re.S):
    pat = r'        <div class="founders__grid">.*?</motion></div>\s*        <p class="founders__together"'
if not re.search(pat, t, re.S):
    pat = r'        <div class="founders__grid">[\s\S]*?</div>\s*        <p class="founders__together"'

t2, n = re.subn(pat, new_block + "\n        <p class=\"founders__together\"", t, count=1)
t2 = re.sub(r"</?motion>", "", t2)
p.write_text(t2, encoding="utf-8")
print("replaced", n)
