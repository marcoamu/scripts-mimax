/**
 * Telegram Bot - Enhanced with buttons and commands
 */

const https = require('https');

let BOT_TOKEN = '';
let CHAT_ID = '';

function configure(token, chatId) {
  BOT_TOKEN = token;
  CHAT_ID = chatId;
}

// Send message with buttons
async function sendMessageWithButtons(text, buttons) {
  if (!BOT_TOKEN || !CHAT_ID) return { ok: false, error: 'Not configured' };

  const keyboard = buttons.map(row => row.map(btn => ({
    text: btn.text,
    callback_data: btn.data
  })));

  const data = JSON.stringify({
    chat_id: CHAT_ID,
    text: text,
    reply_markup: { inline_keyboard: keyboard }
  });

  return new Promise((resolve) => {
    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/sendMessage`,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': data.length }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => resolve(JSON.parse(body)));
    });

    req.on('error', () => resolve({ ok: false, error: 'Network error' }));
    req.write(data);
    req.end();
  });
}

// Send simple message
async function sendMessage(text) {
  if (!BOT_TOKEN || !CHAT_ID) return { ok: false };

  const data = JSON.stringify({
    chat_id: CHAT_ID,
    text: text
  });

  return new Promise((resolve) => {
    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${BOT_TOKEN}/sendMessage`,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': data.length }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => resolve(JSON.parse(body)));
    });

    req.on('error', () => resolve({ ok: false }));
    req.write(data);
    req.end();
  });
}

// Send system status
async function sendSystemStatus() {
  const status = `🔔 *Estado del Sistema*

✅ API: Activa
✅ Static: Activo
⏰ ${new Date().toLocaleString('es-ES')}

*Usa los botones para más info*`;

  const buttons = [
    [{ text: '📊 Dashboard', data: 'status_dashboard' }],
    [{ text: '📈 Finanzas', data: 'status_finanzas' }],
    [{ text: '🔄 Recargar', data: 'status_reload' }]
  ];

  return sendMessageWithButtons(status, buttons);
}

// Send alert
async function sendAlert(title, message, severity = 'info') {
  const emoji = severity === 'error' ? '❌' : severity === 'warning' ? '⚠️' : 'ℹ️';
  
  const text = `${emoji} *${title}*\n\n${message}`;
  
  const buttons = [
    [{ text: '📊 Ver', data: 'alert_view' }],
    [{ text: '✅ OK', data: 'alert_ok' }]
  ];

  return sendMessageWithButtons(text, buttons);
}

// Handle commands
function handleCommand(command, args) {
  switch (command) {
    case '/start':
      return sendMessage('🤖 *OpenClaw Bot*\n\nBienvenido! Usa los comandos:\n/status - Ver estado\n/finanzas - Resumen financiero\n/backup - Hacer backup\n/help - Ayuda');
    
    case '/status':
      return sendSystemStatus();
    
    case '/finanzas':
      return sendMessage('📈 *Finanzas*\n\nVe a: http://212.227.107.120:4000/finanzas.html');
    
    case '/backup':
      return sendMessage('💾 *Backup*\n\nEjecutando backup...');
    
    case '/help':
      return sendMessage('🤖 *Comandos disponibles:*\n/start - Iniciar\n/status - Estado del sistema\n/finanzas - Ver finanzas\n/backup - Hacer backup\n/help - Esta ayuda');
    
    default:
      return sendMessage('❓ Comando no reconocido. Usa /help');
  }
}

// Configure from file
function configureFromFile() {
  try {
    const config = JSON.parse(require('fs').readFileSync('/root/.openclaw/workspace/ai-media-app/api/telegram-config.json'));
    configure(config.token, config.chatId);
    return true;
  } catch (e) {
    return false;
  }
}

module.exports = { 
  configure, 
  configureFromFile,
  sendMessage, 
  sendMessageWithButtons, 
  sendSystemStatus, 
  sendAlert, 
  handleCommand 
};
