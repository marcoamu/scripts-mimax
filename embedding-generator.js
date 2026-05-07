#!/usr/bin/env node
/**
 * 🔢 Embedding Generator
 * Uses Xenova Transformers for embeddings
 */

const { pipeline } = require('@xenova/transformers');

// Cache the model
let embeddingPipeline = null;

async function getEmbedding(text) {
  if (!embeddingPipeline) {
    console.log("📥 Loading embedding model...");
    embeddingPipeline = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
  }
  
  const output = await embeddingPipeline(text, { pooling: 'mean', normalize: true });
  return Array.from(output.data); // Convert to regular array
}

async function generateEmbedding(text) {
  try {
    const embedding = await getEmbedding(text);
    return embedding;
  } catch(e) {
    console.error("Error generating embedding:", e.message);
    // Return null vector as fallback
    return null;
  }
}

// CLI usage
const text = process.argv.slice(2).join(" ");
if (text) {
  generateEmbedding(text).then(emb => {
    if (emb) {
      console.log(`✅ Embedding generated: ${emb.length} dimensions`);
      console.log("First 5 values:", emb.slice(0, 5));
    }
  });
}

module.exports = { generateEmbedding };
