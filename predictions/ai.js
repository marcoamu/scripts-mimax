/**
 * AI Predictions - Using Ollama or fallback responses
 */

const http = require('http');

// Check if Ollama is available
async function isOllamaRunning() {
  try {
    const res = await fetch('http://localhost:11434/api/tags');
    return res.ok;
  } catch {
    return false;
  }
}

async function askOllama(prompt) {
  return new Promise((resolve) => {
    const data = JSON.stringify({
      model: 'llama3.2:1b',
      prompt: prompt,
      stream: false
    });

    const req = http.request({
      hostname: 'localhost',
      port: 11434,
      path: '/api/generate',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': data.length }
    }, (res) => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        try {
          const json = JSON.parse(body);
          resolve(json.response?.trim() || 'Sin respuesta');
        } catch { resolve('Error'); }
      });
    });
    
    req.on('error', () => resolve('ERROR'));
    req.write(data);
    req.end();
    
    // Timeout
    setTimeout(() => { req.destroy(); resolve('TIMEOUT'); }, 15000);
  });
}

async function predictResearchTopics() {
  const available = await isOllamaRunning();
  if (!available) {
    return '🔮 Predicciones de IA:\n\n1. Agentes de IA - Automatización de tareas\n2. Multimodal AI - Texto, imagen, video\n3. IA Local - Modelos offline\n4. Code Assistants - Programación automática\n5. IA Personal - Asistentes privados';
  }
  
  const result = await askOllama('Lista 5 topics de IA para 2026. Solo nombres.');
  return result.includes('ERROR') || result.includes('TIMEOUT') 
    ? 'Ollama no disponible. Configura Ollama para usar IA.'
    : '🔮 ' + result;
}

async function predictFinancial(data) {
  const available = await isOllamaRunning();
  if (!available) {
    return `💰 Análisis Financiero:\n\nIngresos: €${data.ingresos}\nGastos: €${data.gastos}\nAhorro: €${data.ahorro}\n\nConsejo: Intenta reducir gastos en categorias no esenciales.`;
  }
  
  return askOllama(`Resumen: ingresos €${data.ingresos}, gastos €${data.gastos}. Da 2 consejos.`);
}

async function predictContentTrends(data) {
  return '📊 Tendencias 2026:\n\n1. Contenido educativo corto\n2. Tutoriales de IA\n3. Vlogs personales\n4. Contenido behind-the-scenes\n5. Lives interactivas';
}

async function getContentSummary() {
  return '📝 Para viralizar:\n\n1. Hook en 3 segundos\n2. Contenido útil o entertainer\n3. Formato consistente\n4. Engagement early\n5. Trends temprano';
}

module.exports = {
  predictContentTrends,
  predictFinancial,
  predictResearchTopics,
  getContentSummary
};
