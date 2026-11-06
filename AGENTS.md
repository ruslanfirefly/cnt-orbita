# Инструкции для ИИ-агентов — СНТ «Орбита» (cnt-orbita.ru)

Этот репозиторий содержит исходный код официального портала **СНТ «Орбита»** (https://cnt-orbita.ru/, Ленинградская область, Ломоносовский район, д. Малое Карлино, 383 участка).

📖 **Обязательно прочитайте [`README.md`](./README.md) в корне проекта** — там приведена полная документация:
1. Карта проекта и команды сборки (`/opt/homebrew/bin/hugo --cleanDestinationDir --minify`).
2. Управление модулями главной страницы в `hugo.yaml`:
   - как включать/выключать сезонный баннер `params.heroBanner` (`enabled: true/false`, автоскрытие `expiresAt`, шкала `showProgress`),
   - из каких элементов состоит `heroBanner` и готовые YAML-пресеты для собраний, взносов и дорожных объявлений,
   - настройка `statusBar`, `emergencyStrip`, `requisites`.
3. Полный стандарт создания новостей и протоколов в `content/post/<slug>/index.md` (Frontmatter, 7 канонических рубрик, вложения `attachments`, шорткоды `callout`, `alert`, `doc`, `requisites`, `columns`, `figure`).
4. Справочник UI-компонентов дизайн-системы **Navy & Cyan** (`assets/scss/main.scss` + интерактивные триггеры `assets/js/main.js`) и устройство всех справочных страниц (`layouts/page/*.html`).

## Ключевые технические инварианты
- **Автономная тема**: сайт использует собственную вёрстку в `layouts/` и `assets/` без внешних тем и без git-подмодулей.
- **Dart Sass (`dartsass`)**: компиляция `assets/scss/main.scss` в `layouts/_default/baseof.html` выполняется через `css.Sass (dict "transpiler" "dartsass" ...)` (бинарник `sass` из пакета `dart-sass`). Не используйте устаревший `toCSS` / `libsass`.
- **Никакого сырого HTML в статьях**: в `content/post/**/index.md` используется только чистый Markdown и шорткоды.
- **Две темы и режим «А+»**: всегда используйте CSS-переменные (`var(--card)`, `var(--ink)`, `var(--cyan)`, и т.д.), чтобы верстка корректно работала в светлой и тёмной темах (`data-theme="light|dark"`) и в режиме увеличенного шрифта (`data-font="large"`).
