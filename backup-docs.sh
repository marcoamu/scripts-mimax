#!/bin/bash
# ============================================
# Backup Documentación a GitHub
# ============================================

GITHUB_USER="marcoamu"
GITHUB_TOKEN="<GITHUB_TOKEN>"
DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP_DIR="/tmp/backup-docs"

# Docs a respaldar
SOURCE_DIRS=(
    "/root/.openclaw/workspace/docs/sistema"
    "/root/.openclaw/workspace/BACKLOG.md"
)

mkdir -p $BACKUP_DIR

echo "🔄 Backup documentación - $DATE"

# Clonar repo existente
cd $BACKUP_DIR
if [ -d "docs-mimax" ]; then
    cd docs-mimax
    git pull origin main 2>/dev/null
else
    git clone https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/docs-mimax.git
    cd docs-mimax
fi

# Sincronizar archivos
rsync -av --exclude='.git' /root/.openclaw/workspace/docs/sistema/ ./docs/
cp /root/.openclaw/workspace/BACKLOG.md ./BACKLOG.md

# Commit y push
git add .
git commit -m "Backup $DATE" || echo "No changes to commit"
git push origin main

echo "✅ Backup completado - https://github.com/${GITHUB_USER}/docs-mimax"
