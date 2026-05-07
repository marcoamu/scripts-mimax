#!/usr/bin/env node
/**
 * ✍️ Writer Agent - Content creation
 */

const API = 'http://localhost:3001';

async function runWriter(task) {
  const title = task.title || task.description || '';
  console.log(`✍️ Writer: Creating content for "${title}"`);
  
  // Get context from research if needed
  const research = await fetch(`${API}/api/investigaciones?limit=5`).then(r => r.json());
  
  const content = `
# ${title}

## Resumen
${task.description || 'Contenido generado por el Writer Agent.'}

## Puntos Clave
${research.map((r, i) => `${i+1}. ${r.tema || r.resumen}`).join('\n')}

---
*Generado por Writer Agent*
  `.trim();
  
  return { success: true, content };
}

// Run if called directly
if (require.main === module) {
  const args = process.argv.slice(2);
  const task = { title: args[0] || 'Test', description: args[1] || '' };
  runWriter(task).then(r => console.log(r)).catch(e => console.error(e));
}

module.exports = { runWriter };
