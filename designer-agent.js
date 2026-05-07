#!/usr/bin/env node
/**
 * 🎨 Designer Agent - Enhanced Presentation Generator
 */

const fs = require('fs');

const PRESENTATIONS_DIR = '/root/.openclaw/workspace/presentations';

function generatePresentation(topic, options = {}) {
  const slides = options.slides || [
    { title: topic, subtitle: 'Presentación generada por Designer Agent', type: 'title' },
    { title: 'Introducción', content: 'Puntos clave sobre el tema', type: 'content' },
    { title: 'Análisis', content: 'Datos y estadísticas relevantes', type: 'chart' },
    { title: 'Conclusiones', content: 'Resumen y próximos pasos', type: 'content' },
    { title: 'Preguntas', subtitle: 'Gracias por atención', type: 'end' }
  ];
  
  const slideHtml = slides.map((slide, i) => {
    let content = '';
    
    switch(slide.type) {
      case 'title':
        content = `<div class="slide-title"><h1>${slide.title}</h1><p class="subtitle">${slide.subtitle || ''}</p></div>`;
        break;
      case 'end':
        content = `<div class="slide-end"><h1>${slide.title}</h1><p>${slide.subtitle || ''}</p></div>`;
        break;
      case 'chart':
        content = `<div class="slide-content"><h2>${slide.title}</h2><div class="chart-container"><canvas id="chart${i}"></canvas></div></div>`;
        break;
      default:
        content = `<div class="slide-content"><h2>${slide.title}</h2><p>${slide.content || ''}</p><ul><li>Punto clave 1</li><li>Punto clave 2</li><li>Punto clave 3</li></ul></div>`;
    }
    
    return `<div class="slide active">${content}</div>`;
  }).join('\n');

  const html = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${topic}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"><\/script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: white; overflow: hidden; }
    .slide { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 60px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
    .slide-title, .slide-end { text-align: center; }
    .slide-title h1, .slide-end h1 { font-size: 4rem; margin-bottom: 20px; background: linear-gradient(90deg, #38bdf8, #8b5cf6, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .subtitle { font-size: 1.8rem; color: #94a3b8; }
    .slide-content { max-width: 1000px; width: 100%; }
    .slide-content h2 { font-size: 2.5rem; margin-bottom: 30px; color: #38bdf8; }
    .slide-content p { font-size: 1.4rem; color: #cbd5e1; margin-bottom: 20px; line-height: 1.6; }
    .slide-content ul { font-size: 1.3rem; color: #94a3b8; margin-left: 40px; }
    .slide-content li { margin-bottom: 15px; }
    .chart-container { height: 400px; background: rgba(255,255,255,0.05); border-radius: 20px; padding: 20px; }
    .nav { position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 100; }
    .nav button { background: rgba(255,255,255,0.1); border: none; color: white; padding: 12px 24px; border-radius: 30px; cursor: pointer; font-size: 1rem; backdrop-filter: blur(10px); transition: all 0.3s; }
    .nav button:hover { background: #8b5cf6; }
    .slide-counter { position: fixed; top: 30px; right: 30px; background: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 20px; font-size: 0.9rem; color: #94a3b8; }
  </style>
</head>
<body>
  ${slideHtml}
  <div class="slide-counter"><span id="current">1</span> / <span id="total">${slides.length}</span></div>
  <div class="nav">
    <button onclick="prevSlide()">← Anterior</button>
    <button onclick="nextSlide()">Siguiente →</button>
    <button onclick="window.print()">📥 PDF</button>
  </div>
  <script>
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const total = slides.length;
    document.getElementById('total').textContent = total;
    
    function showSlide(n) {
      slides.forEach(s => s.style.display = 'none');
      slides[n].style.display = 'flex';
      document.getElementById('current').textContent = n + 1;
    }
    
    function nextSlide() { if (currentSlide < total - 1) { currentSlide++; showSlide(currentSlide); } }
    function prevSlide() { if (currentSlide > 0) { currentSlide--; showSlide(currentSlide); } }
    
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
      if (e.key === 'ArrowLeft') prevSlide();
    });
    
    // Charts
    new Chart(document.getElementById('chart2'), {
      type: 'bar',
      data: {
        labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        datasets: [{ label: 'Crecimiento', data: [12, 19, 25, 32, 45, 58], backgroundColor: '#8b5cf6' }]
      },
      options: { responsive: true, plugins: { legend: { labels: { color: 'white' } } }, scales: { x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } } }
    });
  <\/script>
</body>
</html>`;

  fs.mkdirSync(PRESENTATIONS_DIR, { recursive: true });
  
  const safeName = topic.toLowerCase().replace(/[^a-z0-9]/g, '-').substring(0, 30);
  const filename = `${PRESENTATIONS_DIR}/${safeName}-${Date.now()}.html`;
  
  fs.writeFileSync(filename, html);
  
  return filename;
}

if (require.main === module) {
  const topic = process.argv.slice(2).join(' ') || 'Presentación';
  const filename = generatePresentation(topic);
  console.log('✅ Presentation created:', filename);
}

module.exports = { generatePresentation };
