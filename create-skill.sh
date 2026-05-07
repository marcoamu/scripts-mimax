#!/bin/bash
# Script para crear nuevas skills

if [ -z "$1" ]; then
    echo "Uso: ./create-skill.sh <nombre-skill> <descripcion>"
    exit 1
fi

NAME="$1"
DESC="$2"
SKILL_DIR="/root/.openclaw/workspace/skills/$NAME"

# Crear directorio
mkdir -p "$SKILL_DIR"

# Crear SKILL.md
cat > "$SKILL_DIR/SKILL.md" << EOT
---
name: $NAME
description: $DESC
---

# $NAME Skill

## Cuándo usarla
Cuando el usuario necesite $DESC.

## Pasos
1. Entender el objetivo
2. Ejecutar las acciones necesarias
3. Devolver el resultado

## Ejemplos
- El usuario pide $DESC
EOT

echo "✅ Skill '$NAME' creada en $SKILL_DIR"
echo "Edita $SKILL_DIR/SKILL.md para customize"
