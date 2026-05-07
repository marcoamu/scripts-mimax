#!/bin/bash
###############################################################################
# Database Backup Script
# Backs up PostgreSQL and SQLite databases
###############################################################################

BACKUP_DIR="/root/.openclaw/workspace/backups"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/root/.openclaw/workspace/logs/backup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

mkdir -p "$BACKUP_DIR"

log "=== Starting Backup ==="

# PostgreSQL backup
log "📦 Backing up PostgreSQL..."
pg_dump -h localhost -U postgres knowledge_base > "$BACKUP_DIR/postgres_$DATE.sql"
if [ $? -eq 0 ]; then
    log "✅ PostgreSQL backed up: postgres_$DATE.sql"
else
    log "❌ PostgreSQL backup failed"
fi

# SQLite backup (Kanban)
log "📦 Backing up SQLite..."
cp /root/.openclaw/workspace/ai-media-app/api/media.db "$BACKUP_DIR/media_$DATE.db"
if [ $? -eq 0 ]; then
    log "✅ SQLite backed up: media_$DATE.db"
else
    log "❌ SQLite backup failed"
fi

# Backup workspace (important files only)
log "📦 Backing up workspace config..."
tar -czf "$BACKUP_DIR/workspace_$DATE.tar.gz" \
    /root/.openclaw/workspace/mcp \
    /root/.openclaw/workspace/skills \
    /root/.openclaw/workspace/agents \
    2>/dev/null

if [ $? -eq 0 ]; then
    log "✅ Workspace backed up: workspace_$DATE.tar.gz"
fi

# Cleanup old backups (keep last 7)
log "🧹 Cleaning old backups..."
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete 2>/dev/null
find "$BACKUP_DIR" -name "*.db" -mtime +7 -delete 2>/dev/null
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete 2>/dev/null

# Show backup count
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" | wc -l)
log "📊 Total backups: $BACKUP_COUNT"

log "=== Backup Complete ==="
