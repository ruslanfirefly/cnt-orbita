#!/usr/bin/env bash
set -euo pipefail

echo "============================================="
echo "🏗 Запуск сборки и проверки сайта СНТ «Орбита»"
echo "============================================="

if git rev-parse --show-toplevel >/dev/null 2>&1; then
    PROJECT_DIR="$(git rev-parse --show-toplevel)"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
fi

cd "$PROJECT_DIR"

# 1. Поиск бинарника Hugo
HUGO_BIN="/opt/homebrew/bin/hugo"
if [ ! -x "$HUGO_BIN" ]; then
    HUGO_BIN="$(command -v hugo || echo "")"
fi

if [ -z "$HUGO_BIN" ]; then
    echo "❌ Ошибка: бинарник hugo не найден!" >&2
    exit 1
fi

# 2. Чистовая сборка с очисткой каталога назначения и минификацией
echo "⚙️ Сборка: hugo build --cleanDestinationDir --minify..."
"$HUGO_BIN" build --cleanDestinationDir --minify

# 3. Валидация главной страницы (Quality Gate)
echo "🔍 Проверка главной страницы (public/index.html)..."

if [ ! -f "public/index.html" ]; then
    echo "❌ КРИТИЧЕСКАЯ ОШИБКА: public/index.html не сформирован!" >&2
    exit 1
fi

# Подсчет статей
ARTICLE_COUNT=$(grep -o '<article' public/index.html | wc -l | tr -d ' ')
echo "   Найдено статей в ленте главной страницы: $ARTICLE_COUNT"

if [ "$ARTICLE_COUNT" -lt 1 ]; then
    echo "❌ КРИТИЧЕСКАЯ ОШИБКА: Главная страница сгенерирована БЕЗ статей!" >&2
    echo "   Проверьте, не помечены ли последние статьи как draft: true или датой в будущем." >&2
    exit 1
fi

# Проверка размера index.html
FILE_SIZE=$(wc -c < "public/index.html" | tr -d ' ')
if [ "$FILE_SIZE" -lt 5000 ]; then
    echo "⚠️ ВНИМАНИЕ: Размер public/index.html подозрительно мал ($FILE_SIZE байт)!" >&2
fi

echo "✅ Проверка пройдена успешно! Сгенерировано $ARTICLE_COUNT статей на главной странице."
