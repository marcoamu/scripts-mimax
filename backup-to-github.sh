#!/bin/bash
# ============================================
# Backup Script - Subir proyectos a GitHub
# ============================================

GITHUB_USER="monmax"  # Cambiar por tu usuario
BACKUP_DIR="/root/.openclaw/workspace/backups"
DATE=$(date +%Y-%m-%d_%H-%M)

# Proyectos a backup
PROJECTS=(
    "/root/.openclaw/workspace/docs:docs-mimax"
    "/root/.openclaw/workspace/scripts:scripts-mimax"
)

mkdir -p $BACKUP_DIR

echo "🔄 Iniciando backup - $DATE"

for project in "${PROJECTS[@]}"; do
    SOURCE=$(echo $project | cut -d: -f1)
    REPO=$(echo $project | cut -d: -f2)
    
    if [ ! -d "$SOURCE" ]; then
        echo "⚠️ Skip $REPO (no existe)"
        continue
    fi
    
    echo "📦 Backup $REPO..."
    
    cd $BACKUP_DIR
    
    # Si no existe el repo local, clonar o crear
    if [ ! -d "$REPO" ]; then
        # Crear repo desde cero
        mkdir -p $REPO
        cd $REPO
        git init
        git remote add origin "https://github.com/$GITHUB_USER/$REPO.git" 2>/dev/null || true
    else
        cd $REPO
        git remote -v | grep fetch
    fi
    
    # Copiar archivos (excepto .git y archivos sensibles)
    rsync -av --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
          --exclude='*.pyc' --exclude='.env' \
          "$SOURCE/" .
    
    # Commit y push
    git add -A
    git commit -m "Backup $DATE" 2>/dev/null
    
    # Intentar push (puede fallar si no hay token configurado)
    # git push origin main 2>/dev/null || echo "   (push omitido - configurar token)"
    
    echo "✅ $REPO listo para subir"
done

echo ""
echo "📋 Para subir a GitHub manualmente:"
echo "   cd $BACKUP_DIR/<repo>"
echo "   git push origin main"
echo ""
echo "💡 Para push automático, necesitas:"
echo "   git remote set-url origin https://<TOKEN>@github.com/$GITHUB_USER/<repo>.git"
