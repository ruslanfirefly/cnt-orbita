#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Валидация и сборка
"$SCRIPT_DIR/validate_and_build.sh"

if git rev-parse --show-toplevel >/dev/null 2>&1; then
    PROJECT_DIR="$(git rev-parse --show-toplevel)"
else
    PROJECT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
fi
cd "$PROJECT_DIR"

CONFIG_FILE="$PROJECT_DIR/.deploy_config"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "⚠️ Файл конфигурации сервера (.deploy_config) не найден!"
    echo "   Создайте его на основе deploy_config.example с вашими данными доступа."
    exit 1
fi

# Загрузка переменных окружения
# shellcheck disable=SC1090
source "$CONFIG_FILE"

echo "============================================="
echo "🚀 Синхронизация с сервером $REMOTE_HOST..."
echo "============================================="

DEPLOY_METHOD="${DEPLOY_METHOD:-ftp}"

case "$DEPLOY_METHOD" in
    ftp)
        python3 "$SCRIPT_DIR/ftp_sync.py"
        ;;

    rsync)
        REMOTE_PORT="${REMOTE_PORT:-22}"
        if [ -n "${REMOTE_PASSWORD:-}" ]; then
            if ! command -v sshpass >/dev/null 2>&1; then
                echo "⚠️ Для передачи пароля в rsync требуется утилита sshpass (brew install hudochenkov/sshpass/sshpass)."
                echo "   Или используйте DEPLOY_METHOD=ftp"
                exit 1
            fi
            export SSHPASS="$REMOTE_PASSWORD"
            sshpass -e rsync -avz --delete -e "ssh -o StrictHostKeyChecking=no -p $REMOTE_PORT" public/ "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
        else
            rsync -avz --delete -e "ssh -o StrictHostKeyChecking=no -p $REMOTE_PORT" public/ "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
        fi
        ;;

    *)
        echo "❌ Неизвестный метод деплоя: $DEPLOY_METHOD (поддерживаются ftp или rsync)"
        exit 1
        ;;
esac

echo "============================================="
echo "🎉 Сайт успешно обновлен на сервере!"
echo "============================================="
