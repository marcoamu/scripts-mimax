const { chromium } = require('playwright');
const fs = require('fs');

const CEGID_URL = 'https://ghr.pn.cegid.cloud/sse_generico/generico_login.jsp';
const USER = 'GBESRAGUILAR';
const PASS = 'BCD123|@#';

async function executeAction(action) {
    const browser = await chromium.launch({ 
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        console.log('🔐 Logging in...');
        await page.goto(CEGID_URL, { waitUntil: 'networkidle', timeout: 45000 });
        await page.waitForTimeout(2000);
        
        await page.evaluate((val) => {
            const el = document.querySelector('#userlogin');
            if (el) { el.value = val; el.dispatchEvent(new Event('input', { bubbles: true })); }
        }, USER);
        
        await page.evaluate((val) => {
            const el = document.querySelector('#pwdlogin');
            if (el) { el.value = val; el.dispatchEvent(new Event('input', { bubbles: true })); }
        }, PASS);
        
        await page.waitForTimeout(500);
        
        await page.evaluate(() => {
            const btn = document.querySelector('#buttonenter');
            if (btn) btn.click();
        });
        
        await page.waitForTimeout(15000);
        
        console.log('📄 Logged in');
        
        // Get all frames and find the GTA frame
        const frames = page.frames();
        let gtaFrame = null;
        for (const f of frames) {
            if (f.url().includes('sse_g4_gta_virtual_c')) {
                gtaFrame = f;
                break;
            }
        }
        
        if (!gtaFrame) {
            return { success: false, error: 'GTA frame not found' };
        }
        
        await gtaFrame.waitForLoadState('networkidle').catch(() => {});
        await gtaFrame.waitForTimeout(5000);
        
        // Get current button state
        const buttonInfo = await gtaFrame.evaluate(() => {
            const btn = document.querySelector('.clockOutButton, .clockInButton, #tableClockInOut');
            if (!btn) return null;
            
            const textEl = document.querySelector('#textClock');
            const buttonText = textEl ? textEl.textContent : '';
            const isOut = btn.classList.contains('clockOutButton');
            const isIn = btn.classList.contains('clockInButton');
            
            return {
                buttonText: buttonText,
                isClockOut: isOut,
                isClockIn: isIn
            };
        });
        
        console.log('📋 Current button state:', JSON.stringify(buttonInfo));
        
        // Determine current status and action needed
        // If button says "Salir" (clockOutButton) -> user is CLOCKED IN (inside)
        // If button says "Entrar" (clockInButton) -> user is CLOCKED OUT (outside)
        
        let currentStatus = 'unknown';
        let desiredAction = action;
        
        if (buttonInfo.buttonText.toLowerCase().includes('salir')) {
            currentStatus = 'INSIDE';
            console.log('📋 Current status: INSIDE (marked ENTRAR)');
        } else if (buttonInfo.buttonText.toLowerCase().includes('entrar')) {
            currentStatus = 'OUTSIDE';
            console.log('📋 Current status: OUTSIDE (marked SALIR)');
        }
        
        // Determine what the user WANTS to do
        // ENTRAR = mark that you're entering work (you were outside)
        // SALIR = mark that you're leaving work (you were inside)
        
        // Click the button
        console.log(`🖱️ Clicking clocking button for action: ${action}...`);
        
        await gtaFrame.evaluate(() => {
            const btn = document.querySelector('.clockOutButton, .clockInButton, #tableClockInOut');
            if (btn && btn.click) {
                btn.click();
            } else if (typeof clockInOut === 'function') {
                clockInOut(0.00000000);
            }
        });
        
        await page.waitForTimeout(5000);
        
        // Get new state after clicking
        const newButtonInfo = await gtaFrame.evaluate(() => {
            const btn = document.querySelector('.clockOutButton, .clockInButton, #tableClockInOut');
            if (!btn) return null;
            
            const textEl = document.querySelector('#textClock');
            return {
                buttonText: textEl ? textEl.textContent : '',
                isClockOut: btn.classList.contains('clockOutButton'),
                isClockIn: btn.classList.contains('clockInButton')
            };
        });
        
        console.log('📋 New button state:', JSON.stringify(newButtonInfo));
        
        // Save session
        const sessionDir = '/root/.openclaw/workspace/data/cegid';
        fs.mkdirSync(sessionDir, { recursive: true });
        
        const newStatus = newButtonInfo.buttonText.toLowerCase().includes('salir') ? 'INSIDE' : 'OUTSIDE';
        
        const sessionData = {
            current_state: newStatus === 'INSIDE' ? 'ENTRAR' : 'SALIR',
            last_action: new Date().toISOString(),
            last_check: new Date().toISOString(),
            success: true,
            button_state: newButtonInfo
        };
        
        fs.writeFileSync(`${sessionDir}/session.json`, JSON.stringify(sessionData, null, 2));
        console.log('💾 Session saved');
        
        return {
            success: true,
            action: action,
            previous_state: currentStatus,
            new_state: newStatus,
            button_text: newButtonInfo.buttonText,
            message: `${action} executed - now ${newStatus}`
        };
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        return { success: false, error: error.message };
    } finally {
        await browser.close();
    }
}

const args = process.argv.slice(2);
const action = args[1] || 'ENTRAR';

console.log(`🚀 Executing ${action}...`);
executeAction(action).then(result => {
    console.log('\n📊 Result:', JSON.stringify(result, null, 2));
    process.exit(result.success ? 0 : 1);
});
