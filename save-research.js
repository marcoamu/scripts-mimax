#!/usr/bin/env node
/**
 * 💾 Research Saver - Save research to PostgreSQL
 */

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

const pgPool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'knowledge_base',
  user: 'postgres',
  password: 'postgres'
});

async function generateEmbedding(text) {
  try {
    const { pipeline } = require('@xenova/transformors');
    const extractor = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
    const output = await extractor(text, { pooling: 'mean', normalize: true });
    return Array.from(output.data);
  } catch(e) {
    console.log("Embedding error:", e.message);
    return null;
  }
}

async function saveResearch(research) {
  const client = await pgPool.connect();
  
  try {
    await client.query('BEGIN');
    
    // 1. Save investigacion
    const invResult = await client.query(`
      INSERT INTO investigaciones (tema, dominio, hipotesis, resumen, conclusion, score_calidad, estado)
      VALUES ($1, $2, $3, $4, $5, $6, 'completada')
      RETURNING id
    `, [
      research.investigacion.tema,
      research.investigacion.dominio,
      research.investigacion.hipotesis,
      research.investigacion.resumen,
      research.investigacion.conclusion,
      research.investigacion.score_calidad
    ]);
    
    const investigacionId = invResult.rows[0].id;
    console.log("✅ Investigación guardada:", investigacionId);
    
    // 2. Save fuentes
    for (const fuente of research.fuentes) {
      const fuenteResult = await client.query(`
        INSERT INTO fuentes (url, titulo, dominio, autoridad_score, fecha_publicacion, tipo)
        VALUES ($1, $2, $3, $4, $5, 'article')
        RETURNING id
      `, [fuente.url, fuente.titulo || fuente.dominio, fuente.dominio, fuente.autoridad_score, fuente.fecha_publicacion]);
      
      const fuenteId = fuenteResult.rows[0].id;
      
      // Link to investigacion
      await client.query(`
        INSERT INTO investigacion_fuentes (investigacion_id, fuente_id, relevancia)
        VALUES ($1, $2, $3)
      `, [investigacionId, fuenteId, 1.0]);
    }
    console.log("✅ Fuentes guardadas:", research.fuentes.length);
    
    await client.query('COMMIT');
    console.log("\n🎉 Investigación completa guardada!");
    
    return investigacionId;
    
  } catch(e) {
    await client.query('ROLLBACK');
    console.error("Error:", e.message);
    throw e;
  } finally {
    client.release();
  }
}

// CLI - read file directly
const researchFile = process.argv[2];
if (!researchFile) {
  console.log("Uso: node save-research.js <archivo.json>");
  process.exit(1);
}

const research = JSON.parse(fs.readFileSync(researchFile, 'utf8'));
saveResearch(research).then(id => console.log("ID:", id));
