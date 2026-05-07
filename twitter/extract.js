/**
 * Twitter/X API Script
 * 
 * TOKEN STATUS: Requires valid Bearer Token with "Read" permissions
 */

const TOKEN = process.env.TWITTER_BEARER_TOKEN || "";

async function searchTweets(query, maxResults = 10) {
  if (!TOKEN || TOKEN === "") {
    return { error: "No Twitter Bearer Token configured" };
  }
  
  const url = `https://api.twitter.com/2/tweets/search/recent?query=${encodeURIComponent(query)}&max_results=${maxResults}`;
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    return { error: `Twitter API error: ${response.status}` };
  }
  
  const data = await response.json();
  return { tweets: data.data || [], meta: data.meta };
}

const args = process.argv.slice(2);
searchTweets(args[0] || 'AI', parseInt(args[1]) || 5)
  .then(result => {
    if (result.error) {
      console.log('Error:', result.error);
    } else {
      console.log(`Found ${result.tweets.length} tweets`);
      result.tweets.forEach(t => console.log(`- ${t.text?.substring(0, 80)}`));
    }
  });
