#!/bin/bash
# sync_edge.sh
# Simula sincronização de dados da borda para o ambiente central
# Executado após reconexão com o cluster principal

BUFFER_DIR="/data/buffer"
CENTRAL_URL="${CENTRAL_URL:-http://servico-dados.cloudnative.svc.cluster.local:5000}"
LOG_FILE="/data/buffer/sync.log"
TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%S")

echo "[$TIMESTAMP] Iniciando sincronização edge → central..." | tee -a "$LOG_FILE"

# Verifica conectividade com o cluster central
check_connectivity() {
  curl -sf --max-time 5 "$CENTRAL_URL/health" > /dev/null 2>&1
  return $?
}

# Aguarda conexão ficar disponível
MAX_RETRIES=10
RETRY=0
while ! check_connectivity; do
  RETRY=$((RETRY + 1))
  echo "[$TIMESTAMP] Tentativa $RETRY/$MAX_RETRIES — central indisponível. Aguardando 10s..." | tee -a "$LOG_FILE"
  sleep 10
  if [ "$RETRY" -ge "$MAX_RETRIES" ]; then
    echo "[$TIMESTAMP] ERRO: Central não acessível após $MAX_RETRIES tentativas. Sync abortado." | tee -a "$LOG_FILE"
    exit 1
  fi
done

echo "[$TIMESTAMP] Conectividade restaurada. Iniciando envio de dados em buffer..." | tee -a "$LOG_FILE"

# Envia arquivos em buffer para o central
SYNCED=0
FAILED=0
for FILE in "$BUFFER_DIR"/*.json; do
  [ -f "$FILE" ] || continue
  RESPONSE=$(curl -sf --max-time 10 -X POST "$CENTRAL_URL/sync" \
    -H "Content-Type: application/json" \
    -d @"$FILE" 2>&1)
  if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] ✓ Sincronizado: $(basename $FILE)" | tee -a "$LOG_FILE"
    rm -f "$FILE"
    SYNCED=$((SYNCED + 1))
  else
    echo "[$TIMESTAMP] ✗ Falha ao sincronizar: $(basename $FILE) — $RESPONSE" | tee -a "$LOG_FILE"
    FAILED=$((FAILED + 1))
  fi
done

echo "[$TIMESTAMP] Sincronização concluída. Sucesso: $SYNCED | Falhas: $FAILED" | tee -a "$LOG_FILE"
exit 0
