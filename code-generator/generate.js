#!/usr/bin/env node
/**
 * Code Generator Agent
 * Generates code from research/requirements
 */

const fs = require('fs');
const path = require('path');

// Templates for common patterns
const TEMPLATES = {
    'api': `const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Add your routes here

app.listen(PORT, () => {
  console.log(\`Server running on port \${PORT}\`);
});`,

    'react-component': `import React, { useState, useEffect } from 'react';

export function MyComponent({ title }) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // Fetch data
  }, []);
  
  return (
    <div className="component">
      <h1>{title}</h1>
      {data ? <p>{data}</p> : <p>Loading...</p>}
    </div>
  );
}`,

    'python-api': `from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)`,

    'docker-compose': `version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret
    volumes:
      - db-data:/data

volumes:
  db-data:`,

    'database': `-- PostgreSQL Schema
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);`
};

/**
 * Generate code from template
 */
function generate(template, name) {
    const code = TEMPLATES[template] || '// Template not found';
    return code;
}

/**
 * CLI
 */
const args = process.argv.slice(2);
const template = args[0] || 'api';
const name = args[1] || 'output';

if (TEMPLATES[template]) {
    const code = generate(template, name);
    console.log(`Generated ${template} code:\n`);
    console.log(code);
} else {
    console.log('Available templates:');
    Object.keys(TEMPLATES).forEach(t => console.log(`  - ${t}`));
}

module.exports = { generate, TEMPLATES };
