#!/usr/bin/env node
/**
 * 🎵 TikTok Profile Photo Extractor
 * Gets profile photos from TikTok creators
 */

const { execSync } = require('child_process');

function getTikTokProfile(username) {
  try {
    // Get profile page and extract avatar
    const output = execSync(
      `curl -s "https://www.tiktok.com/api/uniqueid/?appId=1233&language=en&uniqueId=${username}" 2>/dev/null | head -50`,
      { encoding: 'utf8', timeout: 15 }
    );
    
    // Try to extract avatar URL from response
    const avatarMatch = output.match(/"avatarUrl":"([^"]+)"/);
    if (avatarMatch) {
      return avatarMatch[1].replace(/\\u002F/g, '/');
    }
    
    // Alternative: try to get from page
    const pageOutput = execSync(
      `curl -s "https://www.tiktok.com/@${username}" 2>/dev/null | grep -oP 'avatar.*?url.*?"([^"]+)"' | head -1`,
      { encoding: 'utf8', timeout: 15 }
    );
    
    return null;
  } catch(e) {
    return null;
  }
}

// Test with a creator
const test = getTikTokProfile('rileybrown.ai');
console.log('Avatar:', test || 'Not found, using placeholder');
