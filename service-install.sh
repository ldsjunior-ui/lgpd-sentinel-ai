#!/bin/bash
# LGPD Sentinel AI — Gerenciador de serviço macOS (launchd)
# Uso: ./service-install.sh [install|uninstall|start|stop|status|logs]

PLIST_NAME="com.lgpdsentinel"
PLIST_SRC="$(cd "$(dirname "$0")" && pwd)/${PLIST_NAME}.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[LGPD Sentinel Service]${NC} $1"; }
warn() { echo -e "${YELLOW}[LGPD Sentinel Service]${NC} $1"; }
err()  { echo -e "${RED}[LGPD Sentinel Service]${NC} $1"; }

case "${1:-help}" in

  install)
    log "Instalando serviço de auto-inicialização..."
    mkdir -p "$HOME/Library/LaunchAgents"
    cp "$PLIST_SRC" "$PLIST_DEST"
    launchctl load "$PLIST_DEST"
    log "✅ Serviço instalado! O LGPD Sentinel AI vai iniciar automaticamente no próximo boot."
    log "   Para iniciar agora: $0 start"
    ;;

  uninstall)
    log "Removendo serviço de auto-inicialização..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
    rm -f "$PLIST_DEST"
    log "✅ Serviço removido."
    ;;

  start)
    log "Iniciando serviço..."
    launchctl start "$PLIST_NAME"
    sleep 2
    $0 status
    ;;

  stop)
    log "Parando serviço..."
    launchctl stop "$PLIST_NAME"
    pkill -f 'uvicorn src.main' 2>/dev/null || true
    pkill -f 'streamlit run'   2>/dev/null || true
    log "✅ Serviço parado."
    ;;

  status)
    echo ""
    log "=== Status do serviço ==="
    if launchctl list | grep -q "$PLIST_NAME"; then
      log "launchd: ativo (registrado)"
    else
      warn "launchd: não registrado. Execute: $0 install"
    fi

    API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
    FE_STATUS=$(curl -s  -o /dev/null -w "%{http_code}" http://localhost:8501     2>/dev/null || echo "000")

    [ "$API_STATUS" = "200" ] \
      && log "✅ API:      http://localhost:8000 (status $API_STATUS)" \
      || err "❌ API:      não responde (status $API_STATUS)"

    [ "$FE_STATUS" = "200" ] \
      && log "✅ Frontend: http://localhost:8501 (status $FE_STATUS)" \
      || err "❌ Frontend: não responde (status $FE_STATUS)"
    echo ""
    ;;

  logs)
    log "=== Logs do serviço (Ctrl+C para sair) ==="
    tail -f /tmp/lgpd-sentinel-service.log /tmp/lgpd-sentinel-service-error.log \
            /tmp/lgpd-api.log /tmp/lgpd-frontend.log /tmp/lgpd-ollama.log 2>/dev/null
    ;;

  *)
    echo ""
    echo "Uso: $0 <comando>"
    echo ""
    echo "  install    Instala o serviço (inicia no boot + reinicia se crashar)"
    echo "  uninstall  Remove o serviço"
    echo "  start      Inicia o serviço manualmente"
    echo "  stop       Para o serviço"
    echo "  status     Verifica se os serviços estão rodando"
    echo "  logs       Mostra logs em tempo real"
    echo ""
    ;;
esac
