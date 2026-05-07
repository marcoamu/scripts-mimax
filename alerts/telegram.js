/**
 * Telegram Alert System - Node.js version
 */

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '';
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID || '291245843';

/**
 * Send message to Telegram
 */
async function sendMessage(text, parseMode = 'Markdown') {
    if (!TELEGRAM_BOT_TOKEN) {
        console.log('⚠️ TELEGRAM_BOT_TOKEN not set');
        return false;
    }
    
    const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: TELEGRAM_CHAT_ID,
                text: text,
                parse_mode: parseMode
            })
        });
        
        const data = await response.json();
        return data.ok;
    } catch (error) {
        console.error('Telegram send error:', error.message);
        return false;
    }
}

/**
 * Alert types
 */
const alerts = {
    systemStatus: (status) => sendMessage(
        `🤖 *System Status Update*\n\n📊 Status: ${status}\n⏰ Time: ${new Date().toISOString()}`
    ),
    
    newContent: (platform, count) => sendMessage(
        `📥 *New Content Extracted*\n\nPlatform: ${platform}\nVideos: ${count}\n⏰ Time: ${new Date().toISOString()}`
    ),
    
    researchComplete: (topic) => sendMessage(
        `🔬 *Research Complete*\n\nTopic: ${topic}\n⏰ Time: ${new Date().toISOString()}`
    ),
    
    error: (error) => sendMessage(
        `⚠️ *System Error*\n\nError: ${error}\n⏰ Time: ${new Date().toISOString()}`
    ),
    
    test: () => sendMessage(
        `✅ *OpenClaw Alert System Test*\n\nAlerts are working! 🤖`
    )
};

// CLI execution
const args = process.argv.slice(2);
if (args.length > 0) {
    const command = args[0];
    const param = args[1] || '';
    
    if (alerts[command]) {
        alerts[command](param).then(success => {
            console.log(success ? '✅ Alert sent' : '❌ Failed');
            process.exit(success ? 0 : 1);
        });
    } else {
        console.log('Available commands: status, content, research, error, test');
        process.exit(1);
    }
}

module.exports = { sendMessage, alerts };
