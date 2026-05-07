/**
 * Presentation Generator
 * Creates beautiful HTML presentations from research data
 */

const fs = require('fs');
const path = require('path');

// Generate a beautiful presentation
function generatePresentation(data) {
  const { title, subtitle, sections, charts } = data;
  
  let slides = '';
  
  // Title slide
  slides += `
  <div class="slide title-slide active">
    <div class="title-content">
      <h1>${title || 'Presentación'}</h1>
      <p class="subtitle">${subtitle || ''}</p>
      <p class="date">${new Date().toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
    </div>
  </div>`;
  
  // Content slides
  if (sections) {
    sections.forEach((section, i) => {
      slides += `
  <div class="slide">
    <h2>${section.title}</h2>
    <div class="content">
      ${section.content}
    </div>
  </div>`;
    });
  }
  
  // Chart slides
  if (charts) {
    charts.forEach(chart => {
      slides += `
  <div class="slide chart-slide">
    <h2>${chart.title}</h2>
    <div class="chart-container">
      <canvas id="chart-${chart.id}"></canvas>
    </div>
  </div>`;
    });
  }
  
  // Final slide
  slides += `
  <div class="slide end-slide">
    <h1>Gracias</h1>
    <p>🤖 Generado por OpenClaw</p>
  </div>`;
  
  return slides;
}

// Full HTML template
function createPresentation(data) {
  const slides = generatePresentation(data);
  
  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${data.title || 'Presentación'}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"><\/script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
      font-family: 'Segoe UI', system-ui, sans-serif; 
      background: #0f172a; 
      color: white;
      overflow: hidden;
    }
    .slide {
      display: none;
      height: 100vh;
      padding: 60px;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    .slide.active { display: flex; }
    
    .title-slide {
      text-align: center;
      background: linear-gradient(135deg, #1e1e3f 0%, #0f172a 100%);
    }
    .title-content h1 {
      font-size: 4rem;
      background: linear-gradient(90deg, #8b5cf6, #22c55e);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 20px;
    }
    .subtitle { font-size: 1.5rem; color: #94a3b8; }
    .date { font-size: 1rem; color: #64748b; margin-top: 30px; }
    
    h2 {
      font-size: 2.5rem;
      color: #8b5cf6;
      margin-bottom: 40px;
      text-align: center;
    }
    
    .content {
      font-size: 1.3rem;
      line-height: 2;
      max-width: 900px;
      text-align: center;
    }
    
    .content ul { text-align: left; }
    .content li { margin: 15px 0; }
    
    .chart-container {
      width: 80%;
      max-width: 800px;
      height: 400px;
    }
    
    .end-slide { text-align: center; }
    .end-slide h1 { font-size: 3rem; color: #22c55e; }
    .end-slide p { font-size: 1.2rem; color: #64748b; margin-top: 20px; }
    
    .nav {
      position: fixed;
      bottom: 30px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 20px;
      z-index: 100;
    }
    .nav button {
      background: #334155;
      color: white;
      border: none;
      padding: 15px 30px;
      border-radius: 10px;
      cursor: pointer;
      font-size: 1rem;
    }
    .nav button:hover { background: #8b5cf6; }
    
    .progress {
      position: fixed;
      bottom: 0;
      left: 0;
      height: 4px;
      background: linear-gradient(90deg, #8b5cf6, #22c55e);
      transition: width 0.3s;
    }
    
    .slide-number {
      position: fixed;
      bottom: 30px;
      right: 30px;
      color: #64748b;
      font-size: 0.9rem;
    }
  </style>
</head>
<body>
  ${slides}
  
  <div class="progress" id="progress"></div>
  <div class="slide-number" id="slide-number">1 / 1</div>
  
  <div class="nav">
    <button onclick="prev()">◀ Anterior</button>
    <button onclick="next()">Siguiente ▶</button>
  </div>

  <script>
    let current = 0;
    const slides = document.querySelectorAll('.slide');
    const total = slides.length;
    
    function show() {
      slides.forEach((s, i) => s.classList.toggle('active', i === current));
      document.getElementById('progress').style.width = ((current + 1) / total * 100) + '%';
      document.getElementById('slide-number').innerText = (current + 1) + ' / ' + total;
    }
    
    function next() { current = (current + 1) % total; show(); }
    function prev() { current = (current - 1 + total) % total; show(); }
    
    document.addEventListener('keydown', e => {
      if(e.key === 'ArrowRight') next();
      if(e.key === 'ArrowLeft') prev();
    });
    
    // Render charts if any
    const charts = ${JSON.stringify(data.charts || [])};
    charts.forEach(chart => {
      if (window.Chart) {
        const ctx = document.getElementById('chart-' + chart.id);
        if (ctx) {
          new Chart(ctx, {
            type: chart.type || 'bar',
            data: chart.data,
            options: {
              responsive: true,
              plugins: { legend: { labels: { color: 'white' } } },
              scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } }
              }
            }
          });
        }
      }
    });
    
    show();
  </script>
</body>
</html>`;
}

// Save presentation
function savePresentation(data, filename) {
  const html = createPresentation(data);
  const filepath = `/root/.openclaw/workspace/ai-media-app/public/presentations/${filename}`;
  fs.writeFileSync(filepath, html);
  return filepath;
}

// CLI
const args = process.argv.slice(2);
if (args[0] === 'generate') {
  // Example usage
  const exampleData = {
    title: 'Resumen de Investigación',
    subtitle: 'IA y Machine Learning 2026',
    sections: [
      { title: 'Introducción', content: '<p>Resumen de las últimas tendencias en IA...</p>' },
      { title: 'Hallazgos Principales', content: '<ul><li>GPT-5 tiene 10x más parámetros</li><li>Claude mejora en coding</li><li>Agents son el nuevo trend</li></ul>' }
    ]
  };
  
  const filepath = savePresentation(exampleData, 'research-demo.html');
  console.log('Created:', filepath);
}

module.exports = { createPresentation, savePresentation };
