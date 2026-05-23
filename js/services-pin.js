/**
 * Services — smaller cards, horizontal motion driven by vertical scroll (Lenis-safe)
 */

const SERVICES = [
  {
    title: "Photoshoot",
    text: "Portraits, mode et lifestyle. Direction lumière et retouches premium pour des images qui subliment votre image de marque.",
    tag: "01",
  },
  {
    title: "Publicités & films corporate",
    text: "Spots, films institutionnels et contenus brandés. De la conception à la post-production, une narration cinématographique au service de vos objectifs.",
    tag: "02",
  },
  {
    title: "Prises de vue drone",
    text: "Plans aériens cinématiques pour immobilier, événements et paysages. Certifié et autorisé, pour des images spectaculaires en toute sécurité.",
    tag: "03",
  },
  {
    title: "Mariages",
    text: "Films de mariage émotionnels et intemporels. Couverture discrète, montage raffiné, souvenirs à revivre pour toujours.",
    tag: "04",
  },
  {
    title: "Événements & soirées",
    text: "Galas, lancements, festivals. Captation dynamique et livrables rapides pour amplifier votre présence sur les réseaux.",
    tag: "05",
  },
];

function scrollY() {
  if (window.lenis && typeof window.lenis.scroll === "number") return window.lenis.scroll;
  return window.scrollY || document.documentElement.scrollTop || 0;
}

export function renderServices() {
  const root = document.getElementById("services");
  if (!root) return;

  root.innerHTML = `
    <div class="services-pin__spacer" id="services-spacer">
      <div class="services-pin__sticky">
        <header class="services-pin__head container">
          <p class="eyebrow">Services</p>
          <h2 class="display display--sm">Nos expertises</h2>
        </header>
        <div class="services-pin__rail" id="services-rail">
          <div class="services-pin__track" id="services-track">
            ${SERVICES.map(
              (s) => `
              <article class="service-card">
                <span class="service-card__tag">${s.tag}</span>
                <h3 class="service-card__title">${s.title}</h3>
                <p class="service-card__text">${s.text}</p>
                <a class="btn btn--outline service-card__cta" href="#contact">Nous contacter</a>
              </article>`
            ).join("")}
          </div>
        </div>
      </div>
    </div>`;
}

export function initServicesPin() {
  const spacer = document.getElementById("services-spacer");
  const track = document.getElementById("services-track");
  const rail = document.getElementById("services-rail");
  if (!spacer || !track || !rail) return;

  let maxShift = 0;
  let ticking = false;

  const measure = () => {
    maxShift = Math.max(track.scrollWidth - rail.clientWidth + 24, 0);
    const travel = maxShift > 0 ? maxShift + window.innerHeight * 0.35 : 0;
    spacer.style.height = `${window.innerHeight + travel}px`;
  };

  const update = () => {
    ticking = false;
    if (maxShift <= 0) {
      track.style.transform = "translate3d(0, 0, 0)";
      return;
    }

    const start = spacer.offsetTop;
    const range = spacer.offsetHeight - window.innerHeight;
    if (range <= 0) return;

    const progress = Math.min(Math.max((scrollY() - start) / range, 0), 1);
    track.style.transform = `translate3d(${-progress * maxShift}px, 0, 0)`;
  };

  const requestUpdate = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(update);
  };

  measure();
  update();

  window.addEventListener("resize", () => {
    measure();
    requestUpdate();
  }, { passive: true });

  document.addEventListener("site-scroll", requestUpdate, { passive: true });
  window.addEventListener("scroll", requestUpdate, { passive: true });

  const bindLenis = () => {
    if (!window.lenis || window.__servicesLenisBound) return;
    window.__servicesLenisBound = true;
    window.lenis.on("scroll", requestUpdate);
    measure();
    requestUpdate();
  };

  bindLenis();
  const lenisWait = setInterval(() => {
    bindLenis();
    if (window.__servicesLenisBound) clearInterval(lenisWait);
  }, 40);
  setTimeout(() => clearInterval(lenisWait), 8000);

  if (document.fonts?.ready) {
    document.fonts.ready.then(() => {
      measure();
      requestUpdate();
    });
  }

  requestAnimationFrame(() => {
    measure();
    requestUpdate();
  });
}
