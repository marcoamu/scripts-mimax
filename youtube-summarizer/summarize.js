#!/usr/bin/env node
/**
 * YouTube Video Summarizer
 * Uses transcripts + AI to summarize videos
 */

const https = require('https');
const fs = require('fs');
const { execSync } = require('child_process');

const API_KEY = process.env.YOUTUBE_API_KEY || 'AIzaSyAO5VLoXf9d5DYo-30MKH2uYCs7Pofq1_4';

/**
 * Get video transcript
 */
async function getTranscript(videoId) {
    console.log(`📥 Getting transcript for: ${videoId}`);
    
    // Use yt-dlp to get transcript
    try {
        const output = execSync(
            `yt-dlp --write-subs --write-auto-subs --sub-lang en,es --skip-download -o /tmp/transcript https://youtube.com/watch?v=${videoId}`,
            { encoding: 'utf8' }
        );
        console.log('Transcript downloaded');
        
        // Find the transcript file
        const files = fs.readdirSync('/tmp').filter(f => f.includes(videoId) && f.endsWith('.vtt'));
        if (files.length > 0) {
            const transcript = fs.readFileSync(`/tmp/${files[0]}`, 'utf8');
            // Clean VTT to plain text
            return transcript
                .replace(/<[^>]+>/g, '')
                .replace(/^\d+\.\d+\s*$/gm, '')
                .trim()
                .substring(0, 5000); // Limit length
        }
    } catch (e) {
        console.log('Could not get transcript:', e.message);
    }
    
    return null;
}

/**
 * Generate summary using simple extraction
 */
function generateSummary(transcript) {
    if (!transcript) return 'No transcript available';
    
    // Simple extractive summarization - take first few sentences
    const sentences = transcript.split(/[.!?]+/).filter(s => s.trim().length > 20);
    const summary = sentences.slice(0, 5).join('. ') + '.';
    
    return summary;
}

/**
 * Get video info
 */
async function getVideoInfo(videoId) {
    const url = `https://www.googleapis.com/youtube/v3/videos?id=${videoId}&key=${API_KEY}&part=snippet,statistics`;
    
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    if (json.items && json.items[0]) {
                        resolve(json.items[0]);
                    }
                    resolve(null);
                } catch(e) {
                    reject(e);
                }
            });
        }).on('error', reject);
    });
}

/**
 * Main
 */
async function main() {
    const videoId = process.argv[2] || 'dQw4w9WgXcQ';
    
    console.log('='.repeat(50));
    console.log('📺 YouTube Video Summarizer');
    console.log('='.repeat(50));
    console.log(`Video ID: ${videoId}`);
    
    // Get video info
    const info = await getVideoInfo(videoId);
    if (info) {
        console.log(`\n📌 Title: ${info.snippet.title}`);
        console.log(`👤 Channel: ${info.snippet.channelTitle}`);
        console.log(`👁️ Views: ${parseInt(info.statistics.viewCount).toLocaleString()}`);
    }
    
    // Get transcript
    const transcript = await getTranscript(videoId);
    
    if (transcript) {
        console.log(`\n📝 Transcript length: ${transcript.length} chars`);
        
        // Generate summary
        const summary = generateSummary(transcript);
        console.log(`\n📋 Summary:\n${summary}\n`);
    } else {
        console.log('\n⚠️ No transcript available');
        console.log('Use: yt-dlp --write-subs https://youtube.com/watch?v=VIDEO_ID');
    }
}

main().catch(console.error);
