/**
 * Activity Logger
 * Tracks all changes and updates to the system
 */

const fs = require('fs');
const path = require('path');

const ACTIVITY_FILE = '/root/.openclaw/workspace/activity/activity.json';

// Ensure file exists
if (!fs.existsSync(ACTIVITY_FILE)) {
  fs.writeFileSync(ACTIVITY_FILE, JSON.stringify([], null, 2));
}

function loadActivities() {
  try {
    return JSON.parse(fs.readFileSync(ACTIVITY_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function saveActivities(activities) {
  fs.writeFileSync(ACTIVITY_FILE, JSON.stringify(activities, null, 2));
}

function addActivity(data) {
  const activities = loadActivities();
  
  const activity = {
    id: Date.now().toString(36) + Math.random().toString(36).substr(2),
    date: new Date().toISOString(),
    title: data.title,
    description: data.description || '',
    category: data.category || 'general', // automation, feature, integration, research, system
    status: data.status || 'completed', // completed, in_progress, planned
    details: data.details || [],
    dbChanges: data.dbChanges || [],
    scripts: data.scripts || [],
    endpoints: data.endpoints || [],
    files: data.files || [],
    impact: data.impact || 'medium'
  };
  
  activities.unshift(activity); // Add to beginning
  saveActivities(activities);
  
  return activity;
}

// Pre-populate with known activities
function initWithKnownActivities() {
  const existing = loadActivities();
  if (existing.length > 0) return;
  
  const activities = [
    {
      id: '1',
      date: '2026-03-09T22:00:00.000Z',
      title: '🎬 Sistema de Presentaciones',
      description: 'Generador automático de presentaciones HTML con Chart.js',
      category: 'feature',
      status: 'completed',
      details: [
        'Creado generator de presentaciones desde UI',
        'Presentaciones con navegación keyboard',
        'Soporte para gráficos Chart.js',
        'Integración con research'
      ],
      dbChanges: [],
      scripts: ['/scripts/presentation/generate.js'],
      endpoints: ['/api/presentation/generate'],
      files: ['/presentation-generator.html', '/presentations/'],
      impact: 'high'
    },
    {
      id: '2',
      date: '2026-03-09T21:00:00.000Z',
      title: '🎨 ComfyUI Prompts Manager',
      description: 'Sistema para gestionar prompts de imagen y video para ComfyUI local',
      category: 'integration',
      status: 'completed',
      details: [
        'Tabla PostgreSQL: comfyui_prompts',
        'API REST completa para CRUD',
        'Endpoint de sincronización para agente local',
        'UI para gestionar prompts',
        'Estados: pending, synced, processing, completed, failed'
      ],
      dbChanges: ['CREATE TABLE comfyui_prompts'],
      scripts: [],
      endpoints: [
        '/api/comfyui/prompts',
        '/api/comfyui/sync',
        '/api/comfyui/stats',
        '/api/comfyui/prompts/:id/status'
      ],
      files: ['/comfyui-prompts.html'],
      impact: 'high'
    },
    {
      id: '3',
      date: '2026-03-09T18:00:00.000Z',
      title: '📈 Market Prognosis',
      description: 'Pronóstico diario automático de mercados: crypto, índices, acciones',
      category: 'automation',
      status: 'completed',
      details: [
        'Script de análisis de mercado',
        'Datos de CoinGecko + Yahoo Finance',
        'Genera página HTML con precios',
        'Envío a Telegram (configurable)'
      ],
      dbChanges: [],
      scripts: ['/scripts/market/prognosis.sh'],
      endpoints: [],
      files: ['/market-prognosis.html'],
      impact: 'medium'
    },
    {
      id: '4',
      date: '2026-03-09T17:00:00.000Z',
      title: '🔄 Health Check + Auto-restart',
      description: 'Sistema de monitorización con reinicio automático',
      category: 'system',
      status: 'completed',
      details: [
        'Verificación cada 5 minutos',
        'Reinicio automático de servicios caídos',
        'Logs detallados',
        'Alertas Telegram configurables'
      ],
      dbChanges: [],
      scripts: ['/scripts/automations/health-check.sh'],
      endpoints: [],
      files: ['/health-status.html'],
      impact: 'critical'
    },
    {
      id: '5',
      date: '2026-03-09T15:00:00.000Z',
      title: '💾 Backup Automático',
      description: 'Sistema de backup diario con retención de 7 días',
      category: 'system',
      status: 'completed',
      details: [
        'Backup PostgreSQL (investigaciones)',
        'Backup SQLite (Kanban)',
        'Backup de config (MCP, skills)',
        'Limpieza automática de backups antiguos'
      ],
      dbChanges: [],
      scripts: ['/scripts/automations/backup.sh'],
      endpoints: [],
      files: [],
      impact: 'critical'
    },
    {
      id: '6',
      date: '2026-03-09T12:00:00.000Z',
      title: '📊 Trends Analysis',
      description: 'Análisis automático de tendencias del contenido',
      category: 'research',
      status: 'completed',
      details: [
        'Detección de palabras clave',
        'Top creadores por engagement',
        'Estadísticas diarias',
        'Página de visualización'
      ],
      dbChanges: [],
      scripts: ['/scripts/research/trends.sh'],
      endpoints: [],
      files: ['/trends.html'],
      impact: 'medium'
    },
    {
      id: '7',
      date: '2026-03-09T10:00:00.000Z',
      title: '🔬 Auto Research',
      description: 'Investigaciones automáticas sobre temas de IA',
      category: 'research',
      status: 'completed',
      details: [
        'Ejecución diaria a las 6 AM',
        'Búsqueda web automática',
        'Guardado en PostgreSQL',
        'Integración con Context7'
      ],
      dbChanges: [],
      scripts: ['/scripts/research/auto-research.sh'],
      endpoints: [],
      files: [],
      impact: 'medium'
    },
    {
      id: '8',
      date: '2026-03-09T08:00:00.000Z',
      title: '📥 Content Extraction',
      description: 'Extracción automática de TikTok y YouTube',
      category: 'automation',
      status: 'completed',
      details: [
        'Crons múltiples (mañana/tarde/cada 4h)',
        'Tracking configurable por creador',
        'Limite de videos personalizable',
        'Historial de extracciones'
      ],
      dbChanges: ['CREATE TABLE extraction_history'],
      scripts: ['/scripts/automations/content-extractor.sh'],
      endpoints: ['/api/tracking/extract', '/api/extraction/history'],
      files: ['/content-tracking.html', '/extraction-monitor.html'],
      impact: 'high'
    },
    {
      id: '9',
      date: '2026-03-08T22:00:00.000Z',
      title: '🤖 MCPs Adicionales',
      description: 'Instalación de nuevos Model Context Protocols',
      category: 'integration',
      status: 'completed',
      details: [
        'Context7 para documentación',
        'Filesystem MCP',
        'GitHub MCP',
        'PostgreSQL MCP',
        'Brave Search MCP',
        'Notion MCP (configurable)',
        'Sentry MCP (configurable)'
      ],
      dbChanges: [],
      scripts: [],
      endpoints: [],
      files: ['/mcp/config.json'],
      impact: 'high'
    },
    {
      id: '10',
      date: '2026-03-08T20:00:00.000Z',
      title: '📊 Analytics Dashboard',
      description: 'Dashboard completo con Chart.js',
      category: 'feature',
      status: 'completed',
      details: [
        'Estadísticas de contenido',
        'Gráficos de plataformas',
        'Top creadores',
        'Actividad reciente',
        'Auto-refresh'
      ],
      dbChanges: [],
      scripts: [],
      endpoints: [],
      files: ['/analytics.html'],
      impact: 'medium'
    },
    {
      id: '11',
      date: '2026-03-08T18:00:00.000Z',
      title: '📰 Newsletter Automático',
      description: 'Sistema de resumen diario',
      category: 'automation',
      status: 'completed',
      details: [
        'Generación HTML automática',
        'Estadísticas del sistema',
        'Top contenido',
        'Investigaciones recientes'
      ],
      dbChanges: [],
      scripts: ['/scripts/newsletter/generate.py'],
      endpoints: [],
      files: ['/newsletter.html'],
      impact: 'medium'
    },
    {
      id: '12',
      date: '2026-03-08T16:00:00.000Z',
      title: '🔍 RAG System',
      description: 'Sistema de búsqueda semántica con embeddings',
      category: 'research',
      status: 'completed',
      details: [
        'Tabla con pgvector',
        'Generador de embeddings',
        'API de búsqueda',
        'UI de búsqueda'
      ],
      dbChanges: ['CREATE TABLE document_embeddings'],
      scripts: ['/scripts/rag/generate-embeddings.py', '/scripts/rag/search.py'],
      endpoints: ['/api/rag/search', '/api/rag/rebuild'],
      files: ['/rag-search.html'],
      impact: 'high'
    },
    {
      id: '13',
      date: '2026-03-08T14:00:00.000Z',
      title: '📚 Context7 Integration',
      description: 'MCP para documentación actualizada de librerías',
      category: 'integration',
      status: 'completed',
      details: [
        'Instalado @upstash/context7-mcp',
        'Documentación sin alucinaciones',
        'Detección automática de librerías',
        'Integrado con Research Agent'
      ],
      dbChanges: [],
      scripts: ['/scripts/context7/'],
      endpoints: [],
      files: [],
      impact: 'high'
    }
  ];
  
  saveActivities(activities);
  console.log('Initialized with', activities.length, 'activities');
}

initWithKnownActivities();

module.exports = { addActivity, loadActivities };
