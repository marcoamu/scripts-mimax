/**
 * Google Drive Backup - Upload files to Google Drive
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

let CONFIG = {
  clientId: '',
  clientSecret: '',
  refreshToken: '',
  folderId: ''
};

function configure(clientId, clientSecret, refreshToken, folderId) {
  CONFIG = { clientId, clientSecret, refreshToken, folderId };
}

// Get access token from refresh token
function getAccessToken() {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      client_id: CONFIG.clientId,
      client_secret: CONFIG.clientSecret,
      refresh_token: CONFIG.refreshToken,
      grant_type: 'refresh_token'
    });

    const options = {
      hostname: 'oauth2.googleapis.com',
      path: '/token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(body);
          if (json.access_token) {
            resolve(json.access_token);
          } else {
            reject(new Error('No access token'));
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// Upload file to Google Drive
async function uploadFile(filePath, fileName) {
  const accessToken = await getAccessToken();
  const fileContent = fs.readFileSync(filePath);
  
  const boundary = '-------314159265358979323846';
  const delimiter = '\r\n--' + boundary + '\r\n';
  const closeDelimiter = '\r\n--' + boundary + '--';

  const metadata = {
    name: fileName || path.basename(filePath),
    parents: CONFIG.folderId ? [CONFIG.folderId] : []
  };

  const multipartRequestBody =
    delimiter +
    'Content-Type: application/json; charset=UTF-8\r\n\r\n' +
    JSON.stringify(metadata) +
    delimiter +
    'Content-Type: application/octet-stream\r\n\r\n' +
    fileContent +
    closeDelimiter;

  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'www.googleapis.com',
      path: '/upload/drive/v3/files?uploadType=multipart',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'multipart/related; boundary="' + boundary + '"',
        'Content-Length': Buffer.byteLength(multipartRequestBody)
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(multipartRequestBody);
    req.end();
  });
}

// Backup databases to Google Drive
async function backupDatabases() {
  const results = { success: [], failed: [] };
  const timestamp = new Date().toISOString().split('T')[0];
  
  const backups = [
    { name: 'knowledge_base.sql', path: '/root/.openclaw/workspace/backups/knowledge_base.sql' },
    { name: 'kanban.db', path: '/root/.openclaw/workspace/ai-media-app/api/media.db' }
  ];

  for (const backup of backups) {
    try {
      if (fs.existsSync(backup.path)) {
        const result = await uploadFile(backup.path, `${backup.name}-${timestamp}`);
        results.success.push(backup.name);
      }
    } catch (e) {
      results.failed.push({ name: backup.name, error: e.message });
    }
  }

  return results;
}

function configureFromFile() {
  try {
    const configPath = '/root/.openclaw/workspace/ai-media-app/api/backup-config.json';
    if (fs.existsSync(configPath)) {
      const data = JSON.parse(fs.readFileSync(configPath));
      configure(data.clientId, data.clientSecret, data.refreshToken, data.folderId);
      return true;
    }
  } catch (e) {}
  return false;
}

module.exports = { configure, uploadFile, backupDatabases, configureFromFile };
