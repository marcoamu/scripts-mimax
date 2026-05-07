/**
 * Reddit Trending Scraper
 * Extracts trending posts from subreddits
 */

const SUBREDDITS = [
  'technology',
  'ArtificialIntelligence',
  'MachineLearning',
  'programming',
  'javascript',
  'python',
  'LearnProgramming',
  'tech'
];

const REDDIT_API = 'https://www.reddit.com';

/**
 * Fetch trending posts from a subreddit
 */
async function getSubredditPosts(subreddit, limit = 10) {
  try {
    const response = await fetch(`${REDDIT_API}/r/${subreddit}/hot.json?limit=${limit}`, {
      headers: {
        'User-Agent': 'OpenClaw/1.0 (research bot)'
      }
    });
    
    const data = await response.json();
    const posts = data.data.children.map(child => ({
      id: child.data.id,
      title: child.data.title,
      author: child.data.author,
      score: child.data.score,
      num_comments: child.data.num_comments,
      subreddit: child.data.subreddit,
      url: child.data.url,
      permalink: `https://reddit.com${child.data.permalink}`,
      created_utc: child.data.created_utc,
      is_video: child.data.is_video,
      over_18: child.data.over_18
    }));
    
    return posts;
  } catch (error) {
    console.error(`Error fetching r/${subreddit}:`, error.message);
    return [];
  }
}

/**
 * Get trending from all subreddits
 */
async function getAllTrending(subreddits = SUBREDDITS, limitPerSub = 10) {
  console.log(`🔍 Fetching trending from ${subreddits.length} subreddits...\n`);
  
  const allPosts = [];
  
  for (const subreddit of subreddits) {
    const posts = await getSubredditPosts(subreddit, limitPerSub);
    console.log(`   r/${subreddit}: ${posts.length} posts`);
    allPosts.push(...posts);
  }
  
  // Sort by score
  allPosts.sort((a, b) => b.score - a.score);
  
  return allPosts;
}

/**
 * Filter posts by keywords
 */
function filterPosts(posts, keywords) {
  return posts.filter(post => {
    const text = `${post.title} ${post.subreddit}`.toLowerCase();
    return keywords.some(kw => text.includes(kw.toLowerCase()));
  });
}

/**
 * Main execution
 */
async function main() {
  const args = process.argv.slice(2);
  const subreddit = args[0] || 'all';
  const limit = parseInt(args[1]) || 10;
  
  console.log('='.repeat(50));
  console.log('📊 Reddit Trending Scraper');
  console.log('='.repeat(50));
  
  if (subreddit === 'all') {
    const posts = await getAllTrending(SUBREDDITS, limit);
    console.log(`\n✅ Total: ${posts.length} posts`);
    
    // Show top 5
    console.log('\n🔥 Top 5 Trending:');
    posts.slice(0, 5).forEach((post, i) => {
      console.log(`\n${i+1}. ${post.title}`);
      console.log(`   r/${post.subreddit} | ${post.score} upvotes | ${post.num_comments} comments`);
    });
    
    return posts;
  } else {
    const posts = await getSubredditPosts(subreddit, limit);
    console.log(`\n✅ r/${subreddit}: ${posts.length} posts`);
    
    posts.forEach((post, i) => {
      console.log(`${i+1}. ${post.title} (${post.score} 🠭)`);
    });
    
    return posts;
  }
}

// Export for use
module.exports = { getSubredditPosts, getAllTrending, filterPosts };

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}
