/**
 * Translation Service - Multiple Free Providers
 */

const https = require('https');

// 1. MyMemory (free, 1000 words/day)
function translateMyMemory(text, from = 'en', to = 'es') {
  return new Promise((resolve, reject) => {
    const encodedText = encodeURIComponent(text);
    const url = `https://api.mymemory.translated.net/get?q=${encodedText}&langpair=${from}|${to}`;
    
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (json.responseStatus === 200) {
            resolve(json.responseData.translatedText);
          } else {
            reject(new Error(json.responseDetails));
          }
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

function translate(text, from = 'en', to = 'es') {
  return translateMyMemory(text, from, to);
}

function test() {
  return translateMyMemory('Hello world', 'en', 'es')
    .then(result => console.log('✅ Translation:', result))
    .catch(e => console.log('❌ Error:', e.message));
}

module.exports = { translate, translateMyMemory, test };

if (require.main === module) test();
