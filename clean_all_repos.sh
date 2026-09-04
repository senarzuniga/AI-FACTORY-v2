#!/bin/bash
# ============================================================================
# LIMPIEZA MASIVA DE SECRETOS - TODOS LOS REPOSITORIOS
# Ejecutar desde cualquier directorio. Procesa TODOS los repos en GitHub.
# ============================================================================

# Configuración
REPOS_BASE="/c/Users/Inaki Senar/Documents/GitHub"
BACKUP_DIR="/c/Users/Inaki Senar/Desktop/secret_backup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$BACKUP_DIR/cleanup_all.log"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"
touch "$LOG_FILE"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║              🛡️  LIMPIEZA MASIVA DE SECRETOS - TODOS LOS REPOS               ║"
echo "║              🎯 Eliminando .env de TODO el historial Git                     ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Directorio base: $REPOS_BASE"
echo "💾 Backups guardados en: $BACKUP_DIR"
echo "📋 Log: $LOG_FILE"
echo ""

# Función de logging
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] OK: $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARN: $1" >> "$LOG_FILE"
}

# Instalar git-filter-repo si no está
if ! command -v git-filter-repo &> /dev/null; then
    log "Instalando git-filter-repo..."
    pip install git-filter-repo --quiet
fi

# Contar repositorios
REPO_LIST=()
while IFS= read -r -d '' dir; do
    if [ -d "$dir/.git" ]; then
        REPO_LIST+=("$dir")
    fi
done < <(find "$REPOS_BASE" -maxdepth 1 -type d -print0)

TOTAL_REPOS=${#REPO_LIST[@]}
log "Encontrados $TOTAL_REPOS repositorios Git"
echo ""

# Procesar cada repositorio
SUCCESS=0
FAILED=0

for repo_path in "${REPO_LIST[@]}"; do
    repo_name=$(basename "$repo_path")
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log "Procesando: $repo_name"
    
    cd "$repo_path" || {
        log_error "No se pudo acceder a $repo_path"
        ((FAILED++))
        continue
    }
    
    # Backup de .env si existe
    if [ -f ".env" ]; then
        cp ".env" "$BACKUP_DIR/${repo_name}_env_backup.txt"
        log_success "Backup de .env guardado"
    else
        log_warning "No hay archivo .env en $repo_name"
    fi
    
    # Verificar si .env está en el historial
    if git log --all --full-history -- .env 2>/dev/null | grep -q "diff --git"; then
        log "Eliminando .env del historial de $repo_name..."
        if git filter-repo --path .env --invert-paths --force; then
            log_success ".env eliminado del historial"
        else
            log_error "Error en filter-repo para $repo_name"
            ((FAILED++))
            continue
        fi
    else
        log_warning ".env no está en el historial de $repo_name"
    fi
    
    # Actualizar .gitignore
    if [ -f ".gitignore" ]; then
        for pattern in ".env" ".env.backup" ".env.local" ".env.*.local" "secrets.json" "*.key"; do
            if ! grep -q "^$pattern$" .gitignore; then
                echo "$pattern" >> .gitignore
            fi
        done
    else
        echo -e ".env\n.env.backup\n.env.local\n.env.*.local\nsecrets.json\n*.key" > .gitignore
        log "Creado .gitignore"
    fi
    
    # Crear .env.example (plantilla sin secretos)
    if [ ! -f ".env.example" ]; then
        cat > .env.example << 'EOF'
# === CONFIGURACIÓN REQUERIDA ===
# Copia este archivo a .env y completa tus claves

# API Keys
OPENAI_API_KEY=sk-your-key-here
OPENROUTER_API_KEY=sk-or-v1-your-key

# Supabase (si aplica)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key

# Email (si aplica)
SMTP_SERVER=smtp.ionos.es
SMTP_PORT=587
SMTP_USER=your-email@ingecart.es
SMTP_PASSWORD=your-password
EOF
        log_success "Creado .env.example"
    fi
    
    # Commit de los cambios de seguridad
    git add .gitignore .env.example 2>/dev/null
    if git diff --cached --quiet; then
        log_warning "No hay cambios para commitear en $repo_name"
    else
        git commit -m "chore(security): remove .env from history, add .gitignore and .env.example"
        log_success "Commit de seguridad realizado"
    fi
    
    # Obtener rama actual (main o master)
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
    if [ -z "$CURRENT_BRANCH" ]; then
        CURRENT_BRANCH="main"
        if ! git show-ref --verify refs/heads/main &>/dev/null; then
            CURRENT_BRANCH="master"
        fi
    fi
    log "Rama actual: $CURRENT_BRANCH"
    
    # Push forzado
    if git push origin "$CURRENT_BRANCH" --force; then
        log_success "Push forzado completado para $repo_name"
        ((SUCCESS++))
    else
        log_error "Fallo en push forzado para $repo_name"
        ((FAILED++))
    fi
    
    echo ""
done

# ============================================================================
# RESUMEN FINAL
# ============================================================================

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                              📊 RESUMEN FINAL                                ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Repositorios limpiados con éxito: $SUCCESS"
echo "❌ Repositorios con errores: $FAILED"
echo ""
echo "💾 Backups guardados en: $BACKUP_DIR"
echo "📋 Log completo: $LOG_FILE"
echo ""
echo "⚠️  IMPORTANTE: Ahora debes ROTAR (cambiar) todas tus claves expuestas:"
echo "   🔑 OpenAI:      https://platform.openai.com/api-keys"
echo "   🔑 Supabase:    https://app.supabase.com/project/_/settings/api"
echo "   🔑 OpenRouter:  https://openrouter.ai/keys"
echo ""
echo "🔐 Para restaurar tu .env local (con NUEVAS claves) en cada repo:"
echo "   cp $BACKUP_DIR/[repo]_env_backup.txt [ruta_repo]/.env"
echo "   Luego edita el .env y reemplaza las claves con las nuevas."
echo ""

# Abrir carpeta de backups en Windows
explorer "$BACKUP_DIR" 2>/dev/null || echo "📁 Backups en: $BACKUP_DIR"