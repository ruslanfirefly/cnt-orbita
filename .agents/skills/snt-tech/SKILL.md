---
name: snt-tech
description: >-
  Технический специалист и Hugo-разработчик сайта СНТ «Орбита».
  Используйте этот скил для настройки конфигурации Hugo (hugo.yaml), работы с шаблонами (layouts),
  стилями SCSS (assets/scss/custom.scss), меню страниц, тестирования сборки и устранения багов верстки.
---

# Hugo-разработчик сайта СНТ «Орбита» (snt-tech)

Скил отвечает за техническое сопровождение сайта на базе **Hugo Extended** и темы **Hugo Theme Stack**.

---

## 🏗 Архитектура проекта и особенности темы Stack

* **Git Submodule темы**: тема подключена в `themes/hugo-theme-stack/`.
  ⚠️ **Строго запрещено напрямую редактировать файлы в папке `themes/`**.
  Все изменения производятся путем переопределения (override) в корневой структуре проекта:
  * Шаблоны и шорткоды: `layouts/`
  * Стили и ассеты: `assets/`
  * Статика: `static/`
  * Переводы: `i18n/ru.yaml`

* **Управление главным меню (`menu.main`)**:
  В данной конфигурации пункты меню задаются **в Front Matter страниц** в каталоге `content/page/*/index.md`, а не в `hugo.yaml`.
  *Пример из `content/page/contacts/index.md`:*
  ```yaml
  menu:
    main:
      weight: -80
      params:
        icon: address-book # иконка из assets/icons/ или темы
  ```

---

## 📁 Ключевые файлы кастомизации

1. **[`hugo.yaml`](file:///Users/firefly/Documents/works/cnt-orbita/hugo.yaml)**:
   * Глобальные параметры сайта (`baseURL`, `params.description`, `params.sidebar`, `params.widgets`).
   * Правила разметки (`markup.goldmark.renderer.unsafe: true` для шорткодов).
   * Пагинация и пермалинки (`/p/:slug/` для постов, `/:slug/` для страниц).

2. **[`assets/scss/custom.scss`](file:///Users/firefly/Documents/works/cnt-orbita/assets/scss/custom.scss)**:
   * Стили компонентов `.alert` (`.alert-info`, `.alert-warning`, `.alert-danger`, `.alert-success`).
   * Стили колонок `.columns-container` и `.column` с медиа-запросом для мобильных (<=768px).
   * SEO-стили футера (`.footer-seo-links`).

3. **[`layouts/shortcodes/`](file:///Users/firefly/Documents/works/cnt-orbita/layouts/shortcodes)**:
   * `alert.html` — плашки с SVG-иконками.
   * `columns.html` — верстка на Flexbox с разделителем `<--->`.
   * `figure.html` — адаптивные теги `<picture>` с автоматическим сжатием картинок в WebP (1024px).

4. **[`layouts/partials/`](file:///Users/firefly/Documents/works/cnt-orbita/layouts/partials)**:
   * `head/custom.html` — микроразметка Schema.org (Organization), Open Graph, фавиконки.
   * `footer/custom.html` — кастомные ссылки и копирайты.

---

## 🚀 Команды для сборки и диагностики

* На машине установлен Hugo через Homebrew: `/opt/homebrew/bin/hugo`.

* **Тестовая сборка сайта (проверка на ошибки)**:
  ```bash
  /opt/homebrew/bin/hugo --minify
  ```

* **Сборка с учетом черновиков**:
  ```bash
  /opt/homebrew/bin/hugo --buildDrafts
  ```

* **Локальный dev-сервер**:
  ```bash
  /opt/homebrew/bin/hugo server -D
  ```

---

## 🔍 Чеклист диагностики неполадок
1. **Ошибка сборки SCSS**: проверить синтаксис `assets/scss/custom.scss` (переменные, незакрытые скобки).
2. **Не отображается картинка**: проверить, лежит ли она в той же папке поста (`Page Bundle`) и верно ли указан относительный путь в `figure src="..."`.
3. **Пункт меню не на своем месте**: проверить значение `weight` в `content/page/<имя>/index.md` (меньшие отрицательные значения идут выше).
