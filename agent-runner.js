#!/usr/bin/env node
/**
 * 🤖 Agent Runner - Automates task processing
 * Run: node agent-runner.js
 */

const API = 'http://localhost:3001';

// Agent capabilities mapping
const AGENT_AREAS = {
  research: ['research', 'ai', 'content', 'general'],
  finance: ['finance', 'crypto', 'stock', 'market'],
  frontend: ['frontend', 'ui', 'design', 'web'],
  backend: ['backend', 'api', 'devops', 'system']
};

const AGENT_EMOJI = { research: '📚', finance: '📈', frontend: '🎨', backend: '⚙️' };
const DB_API = 'http://localhost:3001';

async function logToDB(service, level, message, details = '') {
  try {
    await fetch(DB_API + '/api/logs', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ service, level, message, details })
    });
  } catch(e) {}
}

async function log(message) {
  const ts = new Date().toISOString();
  console.log(`[${ts}] ${message}`);
  logToDB('agent-runner', 'info', message);
}

async function fetchJson(url) {
  try {
    const res = await fetch(url);
    return await res.json();
  } catch (e) {
    return null;
  }
}

async function claimTask(agentName) {
  // Get task assigned to this agent
  let tasks = await fetchJson(`${API}/api/tasks?agent=${agentName}&status=todo`);
  
  if (!tasks || tasks.length === 0) {
    // Try to get from backlog
    const next = await fetchJson(`${API}/api/agent/${agentName}/next-task`);
    
    if (next && next.from_backlog && next.task) {
      // Create the task from backlog
      await fetch(`${API}/api/tasks`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(next.task)
      });
      
      // Get it again
      tasks = await fetchJson(`${API}/api/tasks?agent=${agentName}&status=todo`);
    }
  }
  
  if (tasks && tasks.length > 0) {
    const task = tasks[0];
    
    // Claim it (move to inprogress)
    await fetch(`${API}/api/agent/${agentName}/claim/${task.id}`, { method: 'POST' });
    
    log(`${AGENT_EMOJI[agentName]} ${agentName}: Claimed task #${task.id} - "${task.title}"`);
    return task;
  }
  
  return null;
}

async function completeTask(agentName, taskId, notes = '') {
  // Generate a result comment based on the task
  const resultNotes = notes || `Tarea completada por ${agentName} el ${new Date().toISOString().split('T')[0]}`;
  
  const result = await fetch(`${API}/api/agent/${agentName}/complete/${taskId}`, { 
    method: 'POST' 
  });
  
  // Add result note
  await fetch(`${API}/api/tasks/${taskId}/result`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ result_text: resultNotes, agent: agentName })
  });
  
  log(`${AGENT_EMOJI[agentName]} ${agentName}: Completed task #${taskId}`);
  return result;
}

async function processAgent(agentName) {
  // Skip proposer agent - it only proposes, doesn't do tasks
  if (agentName === 'proposer') {
    return;
  }
  
  // First: get task assigned to this agent
  let inProgress = await fetchJson(`${API}/api/tasks?agent=${agentName}&status=todo`);
  
  // If no tasks for this specific agent, check for "general" tasks (anyone can take)
  if (!inProgress || inProgress.length === 0) {
    inProgress = await fetchJson(`${API}/api/tasks?agent=general&status=todo`);
  }
  
  if (inProgress && inProgress.length > 0) {
    const task = inProgress[0];
    await fetch(`${API}/api/agent/${agentName}/claim/${task.id}`, { method: 'POST' });
    log(`${AGENT_EMOJI[agentName]} ${agentName}: Claimed "${task.title}"`);
    await completeTask(agentName, task.id);
    return;
  }
  
  log(`${AGENT_EMOJI[agentName]} ${agentName}: No tasks assigned`);
}

async function main() {
  log('🤖 Agent Runner Started');
  
  // Run once immediately
  for (const agent of Object.keys(AGENT_AREAS)) {
    await processAgent(agent);
  }
  
  // Then run every 60 seconds
  setInterval(async () => {
    for (const agent of Object.keys(AGENT_AREAS)) {
      await processAgent(agent);
    }
  }, 30000); // Every 30 seconds
}

main();
