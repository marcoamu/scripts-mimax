#!/usr/bin/env node
/**
 * 📸 Instagram Agent - Search and extract Instagram content
 */

const { execSync } = require('child_process');

const INSTAGRAM_DIR = '/root/.openclaw/workspace/instagram';

// Search Instagram for profiles
function searchProfiles(query) {
  try {
    // Use yt-dlp to get profile info
    const output = execSync(
      `yt-dlp --flat-playlist "https://www.instagram.com/explore/search/grid/?q=${encodeURIComponent(query)}" --print "%(uploader)s|%(title)s|%(view_count)s|%(like_count)s|%(upload_date)s" 2>/dev/null | head -20`,
      { encoding: 'utf8', timeout: 30, shell: '/bin/bash' }
    );
    
    const profiles = output.split('\n')
      .filter(l => l.includes('|'))
      .map(l => {
        const [user, title, views, likes, date] = l.split('|');
        return { user: user?.trim(), title: title?.trim(), views, likes, date };
      })
      .filter(p => p.user);
    
    return profiles;
  } catch(e) {
    console.log("Search error:", e.message);
    return [];
  }
}

// Get user profile info
function getProfile(username) {
  try {
    const output = execSync(
      `yt-dlp --flat-playlist "https://www.instagram.com/${username}/" --print "%(uploader)s|%(description)s|%(channel_follower_count)s|%(upload_date)s" 2>/dev/null | head -5`,
      { encoding: 'utf8', timeout: 30, shell: '/bin/bash' }
    );
    
    const [user, desc, followers, date] = output.split('|');
    
    return {
      username,
      description: desc?.trim() || '',
      followers: parseInt(followers) || 0,
      lastPost: date?.trim()
    };
  } catch(e) {
    console.log("Profile error:", e.message);
    return null;
  }
}

// Get recent posts from profile
function getPosts(username, limit = 10) {
  try {
    const output = execSync(
      `yt-dlp --flat-playlist --playlist-end ${limit} "https://www.instagram.com/${username}/" --print "%(title)s|%(description)s|%(view_count)s|%(like_count)s|%(upload_date)s|%(id)s" 2>/dev/null`,
      { encoding: 'utf8', timeout: 60, shell: '/bin/bash' }
    );
    
    const posts = output.split('\n')
      .filter(l => l.includes('|'))
      .map(l => {
        const [title, desc, views, likes, date, id] = l.split('|');
        return {
          id: id?.trim(),
          title: title?.trim(),
          caption: desc?.trim() || title?.trim(),
          views: parseInt(views) || 0,
          likes: parseInt(likes) || 0,
          date: date?.trim()
        };
      })
      .filter(p => p.id);
    
    return posts;
  } catch(e) {
    console.log("Posts error:", e.message);
    return [];
  }
}

// Download post media
function downloadMedia(username, postId) {
  try {
    const output = execSync(
      `yt-dlp "https://www.instagram.com/reel/${postId}/" -o "${INSTAGRAM_DIR}/%(id)s.%%(ext)s" 2>/dev/null`,
      { encoding: 'utf8', timeout: 60, shell: '/bin/bash' }
    );
    return true;
  } catch(e) {
    console.log("Download error:", e.message);
    return false;
  }
}

// Main
const args = process.argv.slice(2);
const command = args[0];

if (command === 'search') {
  const query = args.slice(1).join(' ');
  const results = searchProfiles(query);
  console.log(JSON.stringify(results, null, 2));
} else if (command === 'profile') {
  const profile = getProfile(args[1]);
  console.log(JSON.stringify(profile, null, 2));
} else if (command === 'posts') {
  const posts = getPosts(args[1], parseInt(args[2]) || 10);
  console.log(JSON.stringify(posts, null, 2));
} else {
  console.log("Usage:");
  console.log("  node instagram-agent.js search <query>");
  console.log("  node instagram-agent.js profile <username>");
  console.log("  node instagram-agent.js posts <username> [limit]");
}
