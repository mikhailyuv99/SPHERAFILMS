import re
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "index.html"
t = p.read_text(encoding="utf-8")

manifesto = """    <section class="section manifesto" id="manifesto">
      <motion></motion>
      <div class="container manifesto__wrap">
        <div class="manifesto__panel" data-aos="fade-up">
          <p class="eyebrow">L'art en image</p>
          <blockquote class="manifesto__quote">Façonner la lumière, capturer l'instant, révéler l'âme d'une vision.</blockquote>
          <p class="manifesto__intro" id="intro-text"></p>
        </div>
        <div class="manifesto__services" data-aos="fade-up" data-aos-delay="100">
          <article class="service-card">
            <span class="service-card__num">01</span>
            <p id="service1-text"></p>
          </article>
          <article class="service-card">
            <span class="service-card__num">02</span>
            <p id="service2-text"></p>
          </article>
        </div>
      </div>
    </section>"""

t, n = re.subn(
    r'    <section class="section manifesto" id="manifesto">.*?</section>',
    manifesto,
    t,
    count=1,
    flags=re.S,
)
t = re.sub(
    r'<div class="brands__row" id="marquee-track"></motion></div>',
    '<div class="marquee"><div class="marquee__track" id="marquee-track"></div></div>',
    t,
)
t = re.sub(r'<div class="brands__row" id="marquee-track"></div>',
    '<div class="marquee"><div class="marquee__track" id="marquee-track"></div></motion></motion></motion></div>',
    t)
t = re.sub(r"</?motion>", "", t)
p.write_text(t, encoding="utf-8")
print("manifesto replaced", n)
