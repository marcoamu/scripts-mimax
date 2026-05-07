/**
 * Webhook Receiver - Receive and process external events
 */

const fs = require('fs');

// Webhook log storage
const WEBHOOK_LOG_FILE = '/root/.openclaw/workspace/data/webhooks.json';

// Ensure data directory exists
const dataDir = '/root/.openclaw/workspace/data';
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Initialize webhook log
function initWebhookLog() {
  if (!fs.existsSync(WEBHOOK_LOG_FILE)) {
    fs.writeFileSync(WEBHOOK_LOG_FILE, JSON.stringify([]));
  }
}

// Log incoming webhook
function logWebhook(source, event, data) {
  initWebhookLog();
  const logs = JSON.parse(fs.readFileSync(WEBHOOK_LOG_FILE, 'utf8'));
  
  logs.unshift({
    id: Date.now(),
    source,
    event,
    data,
    timestamp: new Date().toISOString()
  });
  
  // Keep only last 100 webhooks
  fs.writeFileSync(WEBHOOK_LOG_FILE, JSON.stringify(logs.slice(0, 100), null, 2));
  
  return { success: true, id: logs[0].id };
}

// Get webhook logs
function getWebhookLogs(limit = 50) {
  initWebhookLog();
  const logs = JSON.parse(fs.readFileSync(WEBHOOK_LOG_FILE, 'utf8'));
  return logs.slice(0, limit);
}

// Process webhook based on source
async function processWebhook(source, event, data) {
  logWebhook(source, event, data);
  
  // Process specific webhooks
  switch (source) {
    case 'github':
      if (event === 'push') {
        return { action: 'GitHub push received', data };
      }
      break;
      
    case 'telegram':
      if (event === 'message') {
        return { action: 'Telegram message', data };
      }
      break;
      
    case ' IFTTT':
      return { action: 'IFTTT trigger', data };
      
    case 'zapier':
      return { action: 'Zapier trigger', data };
      
    default:
      return { action: 'Unknown source', data };
  }
  
  return { action: 'processed' };
}

// Get webhook endpoints (URLs to receive webhooks)
function getWebhookEndpoints() {
  return {
    github: 'http://212.227.107.120:3001/api/webhooks/github',
    telegram: 'http://212.227.107.120:3001/api/webhooks/telegram',
    generic: 'http://212.227.107.120:3001/api/webhooks/receive',
    ifttt: 'http://212.227.107.120:3001/api/webhooks/ifttt',
    zapier: 'http://212.227.107.120:3001/api/webhooks/zapier'
  };
}

module.exports = {
  logWebhook,
  getWebhookLogs,
  processWebhook,
  getWebhookEndpoints
};
