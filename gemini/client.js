/**
 * Gemini AI Client for OpenClaw
 */

const https = require('https');

const API_KEY = process.env.GEMINI_API_KEY || 'AIzaSyDg8mieDLcL4gmqFOTA4ltO-krgeEM41uU';
const MODEL = 'gemini-2.0-flash-lite';

async function generateContent(prompt) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 2048
      }
    });

    const options = {
      hostname: 'generativelanguage.googleapis.com',
      path: `/v1/models/${MODEL}:generateContent?key=${API_KEY}`,
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
          if (json.error) {
            reject(new Error(json.error.message));
          } else {
            resolve(json.candidates?.[0]?.content?.parts?.[0]?.text || 'Sin respuesta');
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

// Test function
async function test() {
  try {
    console.log('Testing Gemini API...');
    const result = await generateContent('Responde solo con OK');
    console.log('✅ Gemini working:', result);
  } catch (e) {
    console.log('❌ Error:', e.message);
  }
}

module.exports = { generateContent, test };

// Run test if called directly
if (require.main === module) {
  test();
}
