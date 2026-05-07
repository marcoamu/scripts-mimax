/**
 * OCR Service - Using Tesseract (free, local)
 */

const { exec } = require('child_process');
const fs = require('fs');

function extractText(imagePath) {
  return new Promise((resolve, reject) => {
    exec(`tesseract ${imagePath} stdout -l spa+eng`, (error, stdout, stderr) => {
      if (error) {
        reject(error);
      } else {
        resolve(stdout.trim());
      }
    });
  });
}

function test() {
  console.log('Tesseract OCR ready');
}

module.exports = { extractText, test };

if (require.main === module) test();
