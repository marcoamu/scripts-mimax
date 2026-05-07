/**
 * Notion Sync - Export research to Notion
 */

const https = require('https');

let NOTION_KEY = process.env.NOTION_API_KEY || '';
let NOTION_DB_ID = process.env.NOTION_DB_ID || '';

function configure(apiKey, dbId) {
  NOTION_KEY = apiKey;
  NOTION_DB_ID = dbId;
}

// Search for pages in Notion
async function searchPages(query = '') {
  return new Promise((resolve, reject) => {
    if (!NOTION_KEY) {
      return reject(new Error('NOTION_API_KEY not configured'));
    }

    const data = JSON.stringify({
      query: query,
      page_size: 10
    });

    const options = {
      hostname: 'api.notion.com',
      path: '/v1/search',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${NOTION_KEY}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json',
        'Content-Length': data.length
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
    req.write(data);
    req.end();
  });
}

// Create a page in Notion
async function createPage(properties) {
  return new Promise((resolve, reject) => {
    if (!NOTION_KEY || !NOTION_DB_ID) {
      return reject(new Error('NOTION_API_KEY or NOTION_DB_ID not configured'));
    }

    const data = JSON.stringify({
      parent: { database_id: NOTION_DB_ID },
      properties: {
        'Name': { title: [{ text: { content: properties.title || 'Sin título' } }] },
        'Description': { rich_text: [{ text: { content: (properties.description || '').substring(0, 2000) } }] },
        'Tags': { multi_select: (properties.tags || ['OpenClaw']).map(t => ({ name: t.substring(0, 30) })) },
        'Source': { select: { name: properties.source || 'OpenClaw' } }
      }
    });

    const options = {
      hostname: 'api.notion.com',
      path: '/v1/pages',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${NOTION_KEY}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json',
        'Content-Length': data.length
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
    req.write(data);
    req.end();
  });
}

module.exports = { configure, searchPages, createPage };
