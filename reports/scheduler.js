/**
 * Scheduled Reports - Automatic report generation
 */

const fs = require('fs');

// Report types
const REPORT_TYPES = {
  daily: 'Resumen diario',
  weekly: 'Resumen semanal', 
  monthly: 'Resumen mensual',
  finance: 'Informe financiero'
};

// Generate report data
async function generateReport(type) {
  const { Pool } = require('pg');
  const pool = new Pool({ connectionString: 'postgresql://postgres:postgres@localhost:5432/knowledge_base' });
  
  let report = {
    type: type,
    generated: new Date().toISOString(),
    sections: []
  };
  
  switch (type) {
    case 'finance':
      const ingresos = await pool.query("SELECT COALESCE(SUM(monto), 0) as total FROM transacciones WHERE tipo = 'ingreso'");
      const gastos = await pool.query("SELECT COALESCE(SUM(monto), 0) as total FROM transacciones WHERE tipo = 'egreso'");
      const porCategoria = await pool.query(`
        SELECT categoria, SUM(monto) as total 
        FROM transacciones 
        WHERE tipo = 'egreso' AND fecha >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY categoria ORDER BY total DESC LIMIT 5
      `);
      
      report.sections.push({
        title: 'Resumen Financiero',
        content: `Ingresos: €${ingresos.rows[0].total}\nGastos: €${gastos.rows[0].total}\nBalance: €${ingresos.rows[0].total - gastos.rows[0].total}`
      });
      report.sections.push({
        title: 'Top Gastos',
        content: porCategoria.rows.map(r => `${r.categoria}: €${r.total}`).join('\n')
      });
      break;
      
    case 'daily':
      const investigaciones = await pool.query("SELECT COUNT(*) as total FROM investigaciones WHERE fecha >= CURRENT_DATE - INTERVAL '24 hours'");
      report.sections.push({
        title: 'Investigaciones',
        content: `Nuevas: ${investigaciones.rows[0].total}`
      });
      break;
  }
  
  await pool.end();
  return report;
}

// Save report to file
async function saveReport(report) {
  const filename = `/root/.openclaw/workspace/reports/${report.type}-${new Date().toISOString().split('T')[0]}.json`;
  fs.writeFileSync(filename, JSON.stringify(report, null, 2));
  return filename;
}

// Get recent reports
function getRecentReports() {
  const dir = '/root/.openclaw/workspace/reports/';
  if (!fs.existsSync(dir)) return [];
  
  return fs.readdirSync(dir)
    .filter(f => f.endsWith('.json'))
    .sort()
    .reverse()
    .slice(0, 10)
    .map(f => ({
      name: f,
      path: dir + f,
      date: fs.statSync(dir + f).mtime
    }));
}

module.exports = { generateReport, saveReport, getRecentReports, REPORT_TYPES };
