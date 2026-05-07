#!/usr/bin/env node
/**
 * 💼 LinkedIn Agent - Popular Tech Companies
 */

const TECH_COMPANIES = [
  { slug: 'microsoft', name: 'Microsoft', industry: 'Technology' },
  { slug: 'google', name: 'Google', industry: 'Technology' },
  { slug: 'meta', name: 'Meta', industry: 'Technology' },
  { slug: 'amazon', name: 'Amazon', industry: 'E-commerce' },
  { slug: 'apple', name: 'Apple', industry: 'Technology' },
  { slug: 'nvidia', name: 'NVIDIA', industry: 'AI & Hardware' },
  { slug: 'openai', name: 'OpenAI', industry: 'AI Research' },
  { slug: 'anthropic', name: 'Anthropic', industry: 'AI Research' },
  { slug: 'tesla', name: 'Tesla', industry: 'Automotive & AI' },
  { slug: 'ibm', name: 'IBM', industry: 'Technology' },
  { slug: 'intel-corporation', name: 'Intel', industry: 'Semiconductors' },
  { slug: 'amd', name: 'AMD', industry: 'Semiconductors' },
  { slug: 'salesforce', name: 'Salesforce', industry: 'CRM' },
  { slug: 'oracle', name: 'Oracle', industry: 'Technology' },
  { slug: 'adobe', name: 'Adobe', industry: 'Software' },
  { slug: 'netflix', name: 'Netflix', industry: 'Entertainment' },
  { slug: 'spotify', name: 'Spotify', industry: 'Entertainment' },
  { slug: 'uber', name: 'Uber', industry: 'Transportation' },
  { slug: 'airbnb', name: 'Airbnb', industry: 'Travel' },
  { slug: 'linkedin', name: 'LinkedIn', industry: 'Social Network' }
];

const AI_COMPANIES = [
  { slug: 'openai', name: 'OpenAI', industry: 'AI Research' },
  { slug: 'anthropic', name: 'Anthropic', industry: 'AI Research' },
  { slug: 'google-deepmind', name: 'Google DeepMind', industry: 'AI Research' },
  { slug: 'microsoft-ai', name: 'Microsoft AI', industry: 'AI' },
  { slug: 'meta-ai', name: 'Meta AI', industry: 'AI Research' },
  { slug: 'nvidia', name: 'NVIDIA', industry: 'AI Hardware' },
  { slug: 'stability-ai', name: 'Stability AI', industry: 'AI' },
  { slug: 'hugging-face', name: 'Hugging Face', industry: 'AI Platform' },
  { slug: 'inflection', name: 'Inflection AI', industry: 'AI' },
  { slug: 'adept', name: 'Adept AI', industry: 'AI' }
];

// List all tech companies
function listCompanies() {
  return TECH_COMPANIES;
}

// List AI companies
function listAICompanies() {
  return AI_COMPANIES;
}

// Get company details
function getCompany(slug) {
  const company = TECH_COMPANIES.find(c => c.slug === slug) || 
                 AI_COMPANIES.find(c => c.slug === slug);
  if (company) {
    return {
      ...company,
      url: `https://www.linkedin.com/company/${slug}/`,
      employees: 'Visit LinkedIn for details',
      description: 'Tech industry leader'
    };
  }
  return { error: 'Company not found' };
}

// Search companies (simple filter)
function searchCompanies(query) {
  const q = query.toLowerCase();
  return [...TECH_COMPANIES, ...AI_COMPANIES]
    .filter(c => c.name.toLowerCase().includes(q) || c.industry.toLowerCase().includes(q))
    .slice(0, 10);
}

// Main
const args = process.argv.slice(2);
const command = args[0];

if (command === 'list') {
  console.log(JSON.stringify(listCompanies(), null, 2));
} else if (command === 'ai') {
  console.log(JSON.stringify(listAICompanies(), null, 2));
} else if (command === 'company') {
  console.log(JSON.stringify(getCompany(args[1]), null, 2));
} else if (command === 'search') {
  console.log(JSON.stringify(searchCompanies(args.slice(1).join(' ')), null, 2));
} else {
  console.log("💼 LinkedIn Agent");
  console.log("Usage:");
  console.log("  node linkedin-agent.js list           - List all tech companies");
  console.log("  node linkedin-agent.js ai            - List AI companies");
  console.log("  node linkedin-agent.js company <slug> - Get company details");
  console.log("  node linkedin-agent.js search <query>  - Search companies");
}
