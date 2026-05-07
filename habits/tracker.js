/**
 * Habit Tracker - Track daily habits
 */

const fs = require('fs');

const HABITS_FILE = '/root/.openclaw/workspace/data/habits.json';

// Default habits
const DEFAULT_HABITS = [
  { id: 1, name: '💪 Ejercicio', icon: '💪', color: '#22c55e' },
  { id: 2, name: '📚 Lectura', icon: '📚', color: '#3b82f6' },
  { id: 3, name: '🧘 Meditación', icon: '🧘', color: '#8b5cf6' },
  { id: 4, name: '💰 Ahorro', icon: '💰', color: '#f59e0b' },
  { id: 5, name: '😴 Dormir 8h', icon: '😴', color: '#06b6d4' },
  { id: 6, name: '💧 Agua 2L', icon: '💧', color: '#0ea5e9' },
  { id: 7, name: '🍎 Comida sana', icon: '🍎', color: '#ef4444' },
  { id: 8, name: '🎯 Productivity', icon: '🎯', color: '#ec4899' }
];

// Initialize habits file
function initHabits() {
  if (!fs.existsSync(HABITS_FILE)) {
    const data = {
      habits: DEFAULT_HABITS,
      logs: []
    };
    fs.writeFileSync(HABITS_FILE, JSON.stringify(data, null, 2));
  }
}

// Get all habits
function getHabits() {
  initHabits();
  const data = JSON.parse(fs.readFileSync(HABITS_FILE, 'utf8'));
  return data.habits;
}

// Toggle habit for today
function toggleHabit(habitId) {
  initHabits();
  const data = JSON.parse(fs.readFileSync(HABITS_FILE, 'utf8'));
  
  const today = new Date().toISOString().split('T')[0];
  const existingIndex = data.logs.findIndex(l => l.habitId === habitId && l.date === today);
  
  if (existingIndex >= 0) {
    data.logs.splice(existingIndex, 1);
  } else {
    data.logs.push({ habitId, date: today, completed: true });
  }
  
  fs.writeFileSync(HABITS_FILE, JSON.stringify(data, null, 2));
  return data.logs;
}

// Get logs for date range
function getLogs(days = 7) {
  initHabits();
  const data = JSON.parse(fs.readFileSync(HABITS_FILE, 'utf8'));
  
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  const startStr = startDate.toISOString().split('T')[0];
  
  return data.logs.filter(l => l.date >= startStr);
}

// Get streak for habit
function getStreak(habitId) {
  initHabits();
  const data = JSON.parse(fs.readFileSync(HABITS_FILE, 'utf8'));
  
  const habitLogs = data.logs.filter(l => l.habitId === habitId).sort((a, b) => b.date.localeCompare(a.date));
  
  if (habitLogs.length === 0) return 0;
  
  let streak = 0;
  let currentDate = new Date();
  
  for (const log of habitLogs) {
    const logDate = log.date;
    const expectedDate = currentDate.toISOString().split('T')[0];
    
    if (logDate === expectedDate) {
      streak++;
      currentDate.setDate(currentDate.getDate() - 1);
    } else {
      break;
    }
  }
  
  return streak;
}

// Get stats
function getStats() {
  initHabits();
  const data = JSON.parse(fs.readFileSync(HABITS_FILE, 'utf8'));
  
  const today = new Date().toISOString().split('T')[0];
  const todayLogs = data.logs.filter(l => l.date === today);
  
  return {
    totalHabits: data.habits.length,
    completedToday: todayLogs.length,
    totalLogs: data.logs.length,
    completionRate: data.habits.length > 0 ? Math.round((todayLogs.length / data.habits.length) * 100) : 0
  };
}

module.exports = {
  getHabits,
  toggleHabit,
  getLogs,
  getStreak,
  getStats,
  DEFAULT_HABITS
};
