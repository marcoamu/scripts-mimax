/**
 * TikTok AI Trends Intelligence - Scraper
 * Captures trending videos from TikTok related to AI
 */

const { chromium } = require('playwright');

const CONFIG = {
    targetHashtags: [
        'AI', 'ArtificialIntelligence', 'ChatGPT', 'GPT',
        'Agent', 'Agents', 'MachineLearning', 'DeepLearning',
        'OpenAI', 'AGI', 'NeuralNetwork', 'Robotics',
        'AIAgent', 'LLM', 'GenerativeAI', 'Midjourney',
        'Claude', 'Gemini', 'Copilot', 'Sora', 'StableDiffusion'
    ],
    headless: true,
    viewport: { width: 1920, height: 1080 },
    userAgents: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ],
    maxVideosPerHashtag: 50,
    scrollDelay: 2000,
    maxScrolls: 10
};

class TikTokScraper {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
        this.results = [];
    }

    async init() {
        console.log('🚀 Initializing TikTok scraper...');
        
        const userAgent = CONFIG.userAgents[Math.floor(Math.random() * CONFIG.userAgents.length)];
        
        this.browser = await chromium.launch({
            headless: CONFIG.headless,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        });

        this.context = await this.browser.newContext({
            userAgent,
            viewport: CONFIG.viewport,
            locale: 'en-US'
        });

        this.page = await this.context.newPage();
        
        // Block images to speed up
        await this.page.route('**/*.{jpg,jpeg,png,gif,svg,webp}', route => route.abort());
        
        console.log('✅ Browser initialized');
    }

    async scrapeHashtag(hashtag) {
        console.log(`\n📊 Scraping hashtag: #${hashtag}`);
        
        const hashtagUrl = `https://www.tiktok.com/tag/${hashtag}?lang=en`;
        
        try {
            await this.page.goto(hashtagUrl, { 
                waitUntil: 'networkidle', 
                timeout: 60000 
            });
            
            // Wait for videos to load
            await this.page.waitForSelector('[data-e2e="search-card-container"]', { timeout: 10000 }).catch(() => {});
            await this.waitAndScroll();
            
            const videos = await this.extractVideos(hashtag);
            console.log(`   ✅ Found ${videos.length} videos`);
            
            return videos;
            
        } catch (error) {
            console.error(`   ❌ Error scraping #${hashtag}:`, error.message);
            return [];
        }
    }

    async waitAndScroll() {
        let scrolls = 0;
        
        while (scrolls < CONFIG.maxScrolls) {
            await this.page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
            await this.page.waitForTimeout(CONFIG.scrollDelay);
            scrolls++;
        }
    }

    async extractVideos(hashtag) {
        return await this.page.evaluate((config) => {
            const videos = [];
            
            // Find video containers - TikTok uses different selectors
            const videoCards = document.querySelectorAll('[data-e2e="search-card-container"], .tiktok-search-item');
            
            videoCards.forEach(card => {
                try {
                    // Extract basic info
                    const titleEl = card.querySelector('[data-e2e="search-card-video-title"], .title');
                    const authorEl = card.querySelector('[data-e2e="search-card-author-link"], .author');
                    const descEl = card.querySelector('[data-e2e="search-card-desc"], .desc');
                    
                    // Extract metrics
                    const viewsEl = card.querySelector('[data-e2e="search-card-like-count"], .views');
                    const likesEl = card.querySelector('.like-count, [data-e2e="search-like-count"]');
                    const commentsEl = card.querySelector('.comment-count, [data-e2e="search-comment-count"]');
                    const sharesEl = card.querySelector('.share-count, [data-e2e="search-share-count"]');
                    
                    // Extract links
                    const linkEl = card.querySelector('a[href*="/video/"]');
                    const videoLink = linkEl ? `https://www.tiktok.com${linkEl.getAttribute('href')}` : '';
                    const videoIdMatch = videoLink.match(/\/video\/(\d+)/);
                    const videoId = videoIdMatch ? videoIdMatch[1] : null;
                    
                    // Extract hashtags from description
                    const hashtagsInDesc = descEl ? 
                        Array.from(descEl.querySelectorAll('a')).map(a => a.textContent).filter(t => t.startsWith('#')) : [];
                    
                    // Parse numbers (1.2M, 500K, etc)
                    const parseNumber = (str) => {
                        if (!str) return 0;
                        str = str.replace(/,/g, '');
                        if (str.includes('M')) return parseFloat(str) * 1000000;
                        if (str.includes('K')) return parseFloat(str) * 1000;
                        return parseInt(str) || 0;
                    };
                    
                    const views = parseNumber(viewsEl?.textContent);
                    const likes = parseNumber(likesEl?.textContent);
                    const comments = parseNumber(commentsEl?.textContent);
                    const shares = parseNumber(sharesEl?.textContent);
                    
                    // Calculate engagement rate
                    const engagementRate = views > 0 ? ((likes + comments + shares) / views * 100) : 0;
                    
                    // Calculate trend score based on engagement
                    const trendScore = Math.min(100, (engagementRate * 10) + (views / 1000000 * 20));
                    
                    if (videoId) {
                        videos.push({
                            video_id: videoId,
                            title: titleEl?.textContent?.trim() || '',
                            description: descEl?.textContent?.trim() || '',
                            author_name: authorEl?.textContent?.trim() || '',
                            author_id: '',
                            views,
                            likes,
                            comments,
                            shares,
                            engagement_rate: engagementRate.toFixed(2),
                            hashtags: hashtagsInDesc,
                            video_url: videoLink,
                            trend_score: trendScore.toFixed(2),
                            captured_at: new Date().toISOString(),
                            source_hashtag: config.targetHashtag
                        });
                    }
                } catch (e) {
                    // Skip malformed cards
                }
            });
            
            return videos;
            
        }, { targetHashtag: hashtag });
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
            console.log('\n🔒 Browser closed');
        }
    }

    async run() {
        try {
            await this.init();
            
            for (const hashtag of CONFIG.targetHashtags) {
                const videos = await this.scrapeHashtag(hashtag);
                this.results.push(...videos);
                
                // Random delay between hashtags
                await this.page.waitForTimeout(Math.random() * 3000 + 2000);
            }
            
            console.log(`\n📊 Total videos captured: ${this.results.length}`);
            
            return {
                success: true,
                total: this.results.length,
                hashtags_scraped: CONFIG.targetHashtags.length,
                data: this.results
            };
            
        } catch (error) {
            console.error('❌ Scraping failed:', error);
            return {
                success: false,
                error: error.message
            };
        } finally {
            await this.close();
        }
    }
}

// Run if executed directly
if (require.main === module) {
    (async () => {
        const scraper = new TikTokScraper();
        const result = await scraper.run();
        console.log('\n📊 Result:', JSON.stringify(result, null, 2));
        process.exit(result.success ? 0 : 1);
    })();
}

module.exports = { TikTokScraper };
