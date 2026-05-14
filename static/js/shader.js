/* ── Hero Canvas Shader ─────────────────────────────────────────── */
(function () {
  const canvas = document.getElementById('hero-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let t = 0, W = 0, H = 0;

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = canvas.offsetWidth;
    H = canvas.offsetHeight;
    canvas.width  = W * dpr;
    canvas.height = H * dpr;
    ctx.scale(dpr, dpr);
  }

  /* Orb definitions: position oscillation, radius, colour, alpha */
  const orbs = [
    { bx: 0.50, by: 0.50, ax: 0.30, ay: 0.22, fx: 0.50, fy: 0.40, r: 0.70, rgb: '249,115,22',  a: 0.22 },
    { bx: 0.25, by: 0.45, ax: 0.22, ay: 0.20, fx: 0.42, fy: 0.58, r: 0.45, rgb: '200, 55, 10',  a: 0.14 },
    { bx: 0.75, by: 0.55, ax: 0.18, ay: 0.28, fx: 0.38, fy: 0.46, r: 0.42, rgb: '255,145, 30',  a: 0.12 },
    { bx: 0.50, by: 0.20, ax: 0.35, ay: 0.18, fx: 0.60, fy: 0.55, r: 0.32, rgb: '249,115,22',   a: 0.09 },
    { bx: 0.60, by: 0.80, ax: 0.25, ay: 0.15, fx: 0.28, fy: 0.36, r: 0.28, rgb: '180, 40,  5',  a: 0.07 },
  ];

  function draw() {
    ctx.clearRect(0, 0, W, H);

    orbs.forEach((o, i) => {
      const x = (o.bx + Math.sin(t * o.fx + i) * o.ax) * W;
      const y = (o.by + Math.cos(t * o.fy + i * 1.3) * o.ay) * H;
      const r = o.r * Math.max(W, H);

      const g = ctx.createRadialGradient(x, y, 0, x, y, r);
      g.addColorStop(0,   `rgba(${o.rgb},${o.a})`);
      g.addColorStop(0.35,`rgba(${o.rgb},${(o.a * 0.45).toFixed(3)})`);
      g.addColorStop(1,   `rgba(${o.rgb},0)`);

      ctx.globalCompositeOperation = 'lighter';
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);
    });

    ctx.globalCompositeOperation = 'source-over';
  }

  function loop() {
    t += 0.005;
    draw();
    requestAnimationFrame(loop);
  }

  resize();
  window.addEventListener('resize', () => { resize(); });
  loop();
})();


/* ── Product Card Spotlight ─────────────────────────────────────── */
(function () {
  function attachSpotlight(card) {
    card.addEventListener('mousemove', e => {
      const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', ((e.clientX - r.left) / r.width  * 100).toFixed(1) + '%');
      card.style.setProperty('--my', ((e.clientY - r.top)  / r.height * 100).toFixed(1) + '%');
    });
  }

  function init() {
    document.querySelectorAll('.product-card').forEach(attachSpotlight);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();


/* ── Scroll Reveal ──────────────────────────────────────────────── */
(function () {
  function init() {
    const els = document.querySelectorAll('.reveal');
    if (!els.length) return;

    const obs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.08 });

    els.forEach(el => obs.observe(el));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
