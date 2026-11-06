# Техническое задание и архитектурные рекомендации по разработке темы Hugo для СНТ «Орбита» (`cnt-orbita.ru`)

Документ предназначен для верстальщика / разработчика Hugo, который переносит редизайн сайта СНТ «Орбита» на движок **Hugo** (взамен текущей стандартной темы `hugo-theme-stack`).

---

## 1. Состав передаваемого комплекта макетов и маппинг на шаблоны Hugo

Все 5 макетов выполнены в единой дизайн-системе (Navy Ink `#17233b` + Cyan Accent `#06b6d4`, светлая и тёмная темы, режим увеличенного шрифта **`А+`** для пожилых садоводов 60–85 лет, высокий контраст на солнце, адаптивность `320px–1920px`):

| Файл прототипа | Шаблон в теме Hugo | Назначение и какие URL закрывает |
|---|---|---|
| `orbita-redesign.html` | `layouts/index.html` | **Главная страница портала**: экстренная плашка связи с Правлением, условный Hero-баннер общего собрания, сводка статуса и тарифов, сетка сервисов 3×2, реквизиты СНТ в 1 клик + модалка с QR-кодом СБП, главная новость + хронологическая лента, рубрики и архив по годам. |
| `orbita-article.html` | `layouts/_default/single.html` | **Страница отдельной новости / протокола / объявления** (`/p/:slug/`): хлебные крошки, чипы рубрик, крупный лид, дата и номер протокола, блоки выносок (`callout`), карточки кандидатов, адаптивные таблицы, карточки скачивания вложений PDF/DOCX, кнопки «Поделиться» и «Распечатать» (`@media print`), перелинковка «Предыдущая / Следующая запись», липкая правая колонка с оглавлением (`TableOfContents`) и виджетами. |
| `orbita-news-list.html` | `layouts/_default/list.html`, `layouts/_default/taxonomy.html`, `layouts/page/archives.html` | **Список новостей, страница рубрики/тега и архив по годам** (`/post/`, `/categories/:slug/`, `/tags/:slug/`, `/archives/`): шапка со статистикой, фильтр по рубрикам и годам, группировка публикаций по годам (`2026`, `2025`, `2024–2023`), поддержка закреплённых (`pinned`) и срочных (`urgent`) карточек, бейджи вложений (`PDF`), пагинация. |
| `orbita-search.html` | `layouts/page/search.html` + `layouts/index.searchindex.json` | **Страница умного живого поиска** (`/search/`): мгновенный поиск по заголовкам, текстам, тегам и PDF-документам, чипы частых запросов садоводов (`реквизиты`, `тариф`, `доверенность`, `устав`, `дорога`), фильтрация по типу результата (`Новости`, `Документы PDF`, `Разделы`), подсветка совпадений `<mark>`. |
| `orbita-documents.html` | `layouts/_default/page.html` / `layouts/page/documents.html` | **Справочно-сервисные статические страницы** (`/documents/`, `/electro/`, `/pravlenie/`, `/komfort/`, `/contacts/`): карточки официальных документов с размером и форматом (`PDF`, `DOCX`), карточки тарифов АО «ПСК» на электроэнергию, состав Правления и Ревизионной комиссии, блок онлайн-обращений. |
| `orbita-mobile-check.html` | Инструмент контроля качества (QA) | **Интерактивный стенд проверки адаптивности**: позволяет переключать все 5 шаблонов в верхнем селекторе и тестировать их на ширинах `320px`, `390px`, `768px`, `1024px`, `1200px`, `1920px`, в светлой/тёмной теме и в режиме крупного шрифта **`А+`**. |

---

## 2. Архитектура шаблонов Hugo (`layouts/`)

Рекомендуемая структура каталога `layouts/` новой темы:

```text
layouts/
├── _default/
│   ├── baseof.html          # Общий каркас: <head>, шапка, каталог разделов, футер, мобильный таб-бар, модалка QR
│   ├── single.html          # Шаблон новости / статьи (из orbita-article.html)
│   ├── list.html            # Шаблон списка новостей / рубрики / тега (из orbita-news-list.html)
│   └── page.html            # Шаблон статических страниц (из orbita-documents.html)
├── page/
│   ├── archives.html        # Шаблон архива по годам (/archives/)
│   ├── search.html          # Шаблон умного поиска (/search/)
│   └── documents.html       # Специализированный шаблон справочника документов
├── partials/
│   ├── header.html          # Шапка + выпадающий каталог всех разделов (#mobileMenu) + строка поиска
│   ├── emergency-strip.html # Экстренная плашка телефонов Правления и Ленэнерго
│   ├── hero-banner.html     # Условный баннер общего собрания / важного события
│   ├── status-bar.html      # 4-карточная сводка инфраструктуры и тарифов
│   ├── quick-grid.html      # Сетка быстрых сервисов (3x2) из data/services.yaml или params
│   ├── payment-card.html    # Блок реквизитов СНТ в 1 клик + модальное окно #qrModal
│   ├── article-aside.html   # Правая колонка статьи (Оглавление, виджет собрания, контакты)
│   ├── doc-attachments.html # Блок карточек прикреплённых файлов PDF/DOCX в конце статьи
│   └── footer.html          # Футер + нижний мобильный таб-бар (.bottomnav)
├── shortcodes/
│   ├── callout.html         # Шорткод важных выносок (info / warn / danger)
│   ├── doc.html             # Шорткод карточки скачивания документа PDF/DOCX
│   ├── candidates.html      # Шорткод карточек кандидатов / членов Правления
│   └── requisites.html      # Шорткод реквизитов с кнопками копирования
├── index.html               # Главная страница (из orbita-redesign.html)
└── index.searchindex.json   # Генератор JSON-индекса для живого поиска
```

---

## 3. Как включать и выключать баннеры и блоки через `hugo.yaml` (`params`)

Одно из главных требований — чтобы председатель или администратор сайта мог **включать и отключать сезонные баннеры (например, баннер Общего собрания, сбор на дорогу или экстренное оповещение)** без правки HTML-кода, просто меняя флаги в конфигурационном файле `config/_default/params.yaml` (или `hugo.yaml`).

### 3.1. Пример конфигурации `params.yaml`

```yaml
# Общие реквизиты и контакты СНТ (используются в шапке, плашках, реквизитах и футере)
snt:
  name: 'СНТ «Орбита»'
  location: 'д. Малое Карлино, Ломоносовский р-н'
  fullAddress: '188508, Ленинградская обл., Ломоносовский р-н, Виллозское ГП, д. Малое Карлино, тер. СНТ «Орбита»'
  chairman: 'Витер Андрей Дмитриевич'
  plotsCount: 334
  phoneDisplay: '+7 (921) 967-06-42'
  phoneTel: '+79219670642'
  receptionHours: 'Сб 12:00–14:00'
  email: 'sntorbita56@yandex.ru'
  newsEmail: 'news@cnt-orbita.ru'
  maxChannelUrl: 'https://max.ru/id4720008674_biz'
  lenenergoPhone: '8 (800) 220-02-20'
  pskPhone: '8 (812) 678-96-00'
  pskCabinetUrl: 'https://ikus.pesc.ru/auth/login'

# Банковские реквизиты (для блока «Реквизиты в 1 клик» и модального окна QR)
requisites:
  enabled: true
  inn: '4720008674'
  kpp: '472501001'
  account: '40703810155240000156'
  bank: 'Северо-Западный банк ПАО Сбербанк'
  bik: '044030653'
  corrAccount: '30101810500000000653'
  purposeTemplate: 'Целевой и членский взнос за 20__ год, участок № ___'
  paymentTableUrl: 'https://docs.google.com/spreadsheets/d/1zhGuLnfFQLzfv22SANlKMt_76mLHWN2umiCzYl9Nk64/edit?usp=sharing'
  qrImageUrl: '/vznosy/qr-oplata.png'

# 1. Экстренная верхняя полоса для планшетов и мобильных (.emergency-strip)
emergencyStrip:
  enabled: true
  mode: 'normal' # 'normal' (зелёный индикатор) или 'alert' (янтарный/красный при ЧП или отключении света)
  title: 'Правление СНТ «Орбита» · Приём: Сб 12:00–14:00'
  subtitle: 'Аварийная «Ленэнерго»: 8 (800) 220-02-20 · Показания ПСК: 8 (812) 678-96-00'

# 2. Главный Hero-баннер на главной странице (.hero-banner)
heroBanner:
  enabled: true
  # Необязательная дата автоматического скрытия баннера (ISO 8601):
  # после этой даты баннер сам перестанет отображаться при сборке или через JS
  expiresAt: '2026-07-05T23:59:59+03:00'
  tag: 'Общее собрание 2026'
  datesLabel: 'Заочно: 20 июня – 3 июля (до 20:00) · Очно: 4 июля в 12:00'
  title: 'Очередное общее собрание членов СНТ «Орбита» (очно-заочное голосование)'
  description: 'Выборы Председателя, членов Правления (5 кандидатов) и Ревизионной комиссии, утверждение отчётов и сметы. Бюллетени выдаются в здании Правления по субботам с 12:00 до 14:00 и у волонтёров.'
  # Прогресс-индикатор (можно выключить showProgress: false)
  showProgress: true
  progressLeftLabel: 'Территория СНТ: 334 участка (д. Малое Карлино)'
  progressRightLabel: 'Бюллетени: в Правлении Сб 12:00–14:00'
  progressPercent: 68
  primaryBtn:
    text: 'Порядок голосования 2026'
    url: '/p/nachalo-golosovaniya-2026/'
  secondaryBtn:
    text: 'Список кандидатов (Протокол №31)'
    url: '/p/utverzhden-spisok-kandidatov-2026/'

# 3. Оперативная сводка инфраструктуры и тарифов (.status-bar)
statusBar:
  enabled: true
  items:
    - dot: 'ok'   # 'ok' (зелёный), 'info' (голубой), 'warn' (янтарный)
      label: 'Тарифы АО «ПСК» (до 1500 кВт·ч)'
      value: 'День 7,25 ₽ · Ночь 3,95 ₽ · Единый 6,59 ₽'
    - dot: 'ok'
      label: 'Передача показаний света'
      value: 'С 1 по 25 число · 8 (812) 678-96-00'
    - dot: 'info'
      label: 'Аварийная «Ленэнерго»'
      value: 'Отключение света: 8 (800) 220-02-20'
    - dot: 'info'
      label: 'Приём в доме Правления'
      value: 'Суббота 12:00–14:00 · Витер А.Д.'
```

### 3.2. Шаблон условного вывода Hero-баннера (`layouts/partials/hero-banner.html`)

Ниже показан код для Hugo, который проверяет:
1. Включён ли баннер (`site.Params.heroBanner.enabled`).
2. Не истёк ли срок действия `expiresAt` (сравнение с текущим временем сборки `now` + атрибут `data-expires` для клиентской проверки в браузере, если статический сайт пересобирается редко):

```go-html-template
{{- $hb := site.Params.heroBanner -}}
{{- if $hb.enabled -}}
  {{- $notExpired := true -}}
  {{- with $hb.expiresAt -}}
    {{- if lt (time.AsTime .) now -}}
      {{- $notExpired = false -}}
    {{- end -}}
  {{- end -}}

  {{- if $notExpired -}}
  <section class="hero-banner" aria-labelledby="heroHeading" {{ with $hb.expiresAt }}data-expires="{{ . }}"{{ end }}>
    <div class="hero-body">
      <div class="hero-top">
        {{- with $hb.tag -}}
        <span class="hero-tag">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="m3 11 18-5v12L3 13v-2z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/></svg>
          {{ . }}
        </span>
        {{- end -}}
        {{- with $hb.datesLabel -}}
        <span class="hero-exp">{{ . }}</span>
        {{- end -}}
      </div>

      <h1 class="hero-title" id="heroHeading">{{ $hb.title }}</h1>
      {{- with $hb.description -}}
      <p class="hero-desc">{{ . }}</p>
      {{- end -}}

      {{- if $hb.showProgress -}}
      <div class="quorum-box" role="group" aria-label="Информация о проведении голосования">
        <div class="quorum-head">
          <span>{{ $hb.progressLeftLabel | safeHTML }}</span>
          <span>{{ $hb.progressRightLabel | safeHTML }}</span>
        </div>
        <div class="quorum-bar" aria-hidden="true">
          <div class="quorum-fill" style="width: {{ default 68 $hb.progressPercent }}%"></div>
        </div>
      </div>
      {{- end -}}
    </div>

    <div class="hero-cta">
      {{- with $hb.primaryBtn -}}
      <a class="hero-btn-primary" href="{{ .url | relURL }}">{{ .text }}</a>
      {{- end -}}
      {{- with $hb.secondaryBtn -}}
      <a class="hero-btn-secondary" href="{{ .url | relURL }}">{{ .text }}</a>
      {{- end -}}
    </div>
  </section>
  {{- end -}}
{{- end -}}
```

А в общем JS-скрипте достаточно добавить 5 строк, чтобы баннер автоматически скрывался после `data-expires` даже без пересборки Hugo:

```javascript
var heroBanner = document.querySelector('.hero-banner[data-expires]');
if (heroBanner) {
  var exp = Date.parse(heroBanner.getAttribute('data-expires'));
  if (!isNaN(exp) && Date.now() > exp) {
    heroBanner.style.display = 'none';
  }
}
```

---

## 4. Условия генерации во Frontmatter новостей и страниц

Каждая публикация в `content/post/.../index.md` может управлять своим внешним видом на главной странице, в списке новостей (`orbita-news-list.html`) и внутри самой статьи (`orbita-article.html`) через поля Frontmatter:

### 4.1. Рекомендуемый шаблон Frontmatter (`archetypes/post.md`)

```yaml
---
title: "Утверждён список кандидатов в органы управления СНТ «Орбита» на 2026 год"
slug: "utverzhden-spisok-kandidatov-2026"
date: 2026-06-05T12:00:00+03:00
description: "По итогам заседания Правления СНТ «Орбита» (Протокол №31 от 05.06.2026) сформирован итоговый список кандидатов."

# Рубрика (одна из 7 нормализованных рубрик) и теги
categories:
  - "sobraniya"        # Собрания и выборы
tags:
  - "Протокол №31"
  - "Выборы 2026"
  - "Кандидаты"

# Флаги отображения карточки в ленте и на главной:
featured: true         # Сделать главной большой карточкой слева в блоке новостей на главной
pinned: true           # Закрепить сверху в списке новостей с бейджем «Закреплено»
urgent: false          # Выделить янтарной полоской (.row-urgent / .urgent) для ЧП, пожаров, отключений света

# Метаданные для шапки статьи и обложки:
protocol: "Протокол Правления №31"
event_date: "Голосование: 20 июня – 4 июля 2026"
author: "Правление СНТ «Орбита»"

# Управление правой колонкой статьи (orbita-article.html):
show_toc: true             # Показывать оглавление статьи (если заголовков h2 >= 2)
show_voting_widget: true   # Показывать в сайдбаре карточку текущего голосования

# Прикреплённые официальные файлы (автоматически рендерятся красивыми карточками внизу статьи и дают бейдж PDF в списке новостей)
attachments:
  - title: "Протокол заседания Правления №31 от 05.06.2026"
    file: "/documents/protokol-31-2026.pdf"
    ext: "pdf"
    size: "420 КБ"
    note: "Скан с подписью и печатью"
  - title: "Бланк доверенности на участие в общем собрании"
    file: "/documents/docs/doverka.docx"
    ext: "docx"
    size: "24 КБ"
    note: "Шаблон Word для заполнения"
---
```

### 4.2. Логика выбора главной новости (`featured`) на главной странице (`layouts/index.html`)

Чтобы редактору не приходилось вручную верстать левую крупную карточку `.featured` на главной:
1. Берём самую свежую запись из `where site.RegularPages "Section" "post"`, у которой `Params.featured` равно `true`.
2. Если ни у одной новости `featured: true` не задан — автоматически берём просто **самую последнюю опубликованную новость** (`first 1`).
3. В правую колонку `.news-list` выводим следующие **5 свежих новостей** (`after 1` или исключая выбранную `featured`-запись) в строгом хронологическом порядке.

Пример кода для `layouts/index.html`:

```go-html-template
{{- $posts := where site.RegularPages "Section" "post" -}}
{{- $featuredList := where $posts "Params.featured" true -}}
{{- $featured := index ($featuredList | default $posts) 0 -}}
{{- $otherPosts := first 5 (where $posts "Permalink" "ne" $featured.Permalink) -}}
```

### 4.3. Условия в шаблоне списка новостей (`layouts/_default/list.html`)

В карточке новости `.news-item` (`orbita-news-list.html`):
- Если `.Params.pinned` → добавляем класс `pinned` и бейдж `<span class="ni-badge pinned">Закреплено</span>`.
- Если `.Params.urgent` → добавляем класс `urgent` и янтарную иконку/плашку `<span class="ni-badge urgent">Экстренно</span>`.
- Если `len .Params.attachments` > 0 → выводим внизу карточки бейдж `<span class="ni-attach-badge">Вложения: {{ len .Params.attachments }} файла</span>`.

---

## 5. Готовые Shortcodes для авторов статей (Правления СНТ)

В текущей версии сайта авторы вставляют просто голый текст и обычные ссылки `[Скачать](ustav.pdf)`. В новой теме рекомендуется добавить 3 простых шорткода:

### 5.1. Выноска `layouts/shortcodes/callout.html`
Использование в Markdown:
```markdown
{{< callout type="info" title="Где и когда получить бюллетень для голосования" >}}
Бюллетени выдаются каждую субботу с **12:00 до 14:00** в здании Правления СНТ «Орбита».
{{< /callout >}}
```
Код шорткода:
```go-html-template
{{- $type := .Get "type" | default "info" -}}
{{- $title := .Get "title" -}}
<div class="callout callout-{{ $type }}" role="note">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
  <div>
    {{- with $title }}<div class="callout-title">{{ . }}</div>{{ end -}}
    <div>{{ .Inner | markdownify }}</div>
  </div>
</div>
```

### 5.2. Карточка документа `layouts/shortcodes/doc.html`
Использование в Markdown:
```markdown
{{< doc title="Устав СНТ «Орбита»" file="/documents/ustav/ustav.pdf" ext="pdf" size="1.4 МБ" desc="Действующая редакция Устава" >}}
```
Код шорткода рендерит блок `.doc-card` из `orbita-article.html` / `orbita-documents.html` с цветным бейджем `PDF` / `DOCX` и крупной кнопкой «Скачать».

---

## 6. Нормализация рубрик (`categories`) на боевом сайте `cnt-orbita.ru`

При аудите текущего сайта `https://cnt-orbita.ru` обнаружена проблема: из-за ручного ввода категорий в разных падежах и числах в таксономиях Hugo образовались дубли:
- `Объявление` и `Объявления`
- `Собрание` и `Собрания`
- `Важное` и `Важно`
- `Рабочая Группа` и `Рабочие Группы`

**Рекомендация при миграции контента:**
Свести все категории в Markdown-файлах к **7 чистым каноническим рубрикам** (и создать для каждой файл `content/categories/<slug>/_index.md` с понятным названием):

| Канонический slug | Отображаемое название (`title`) | Какие старые категории объединяет |
|---|---|---|
| `vazhnoe` | **Важное и срочное** | `Важное`, `Важно`, `Срочно`, `Взаимопомощь` |
| `sobraniya` | **Собрания и выборы** | `Собрание`, `Собрания`, `Голосование`, `Выборы` |
| `pravlenie` | **Правление и отчёты** | `Правление`, `Отчеты`, `Объявление`, `Объявления`, `Новости` |
| `dorogi` | **Дороги и благоустройство** | `Дороги`, `Рабочая Группа`, `Рабочие Группы`, `Субботник`, `Благоустройство` |
| `electro` | **Электроэнергия и тарифы** | `Электроэнергия`, `Свет`, `Тарифы` |
| `bezopasnost` | **Пожарная безопасность и МЧС** | `Безопасность`, `Пожарная безопасность`, `МЧС` |
| `zhizn-snt` | **Праздники и жизнь СНТ** | `Мероприятия`, `Творчество`, `Память`, `Бессмертный полк`, `История` |

---

## 7. Настройка умного поиска в Hugo (`orbita-search.html`)

Чтобы поиск на `/search/` работал мгновенно без стороннего бэкенда и искал одновременно по новостям, страницам и PDF-документам:

1. В `hugo.yaml` включите генерацию JSON-индекса для главной страницы:
```yaml
outputs:
  home:
    - HTML
    - RSS
    - SearchIndex
outputFormats:
  SearchIndex:
    mediaType: "application/json"
    baseName: "searchindex"
    isPlainText: true
    notAlternative: true
```
2. Создайте шаблон `layouts/index.searchindex.json`, который собирает все записи `.Site.RegularPages` + массив официальных документов из `data/documents.yaml`:
```go-html-template
{{- $items := slice -}}
{{- range where site.RegularPages "Params.hidden" "ne" true -}}
  {{- $type := cond (eq .Section "post") "news" "page" -}}
  {{- $badge := cond (eq .Section "post") "Новость" "Раздел сайта" -}}
  {{- $items = $items | append (dict
    "type" $type
    "badge" $badge
    "date" (.Date.Format "02.01.2006")
    "title" .Title
    "snippet" (.Description | default (.Summary | plainify | truncate 200))
    "tags" (.Params.tags | default (slice))
    "url" .RelPermalink
    "actionText" (cond (eq .Section "post") "Читать статью" "Открыть раздел")
  ) -}}
{{- end -}}
{{- jsonify $items -}}
```
3. В `layouts/page/search.html` (верстка полностью готова в `orbita-search.html`) замените демо-константу `SEARCH_INDEX` на `fetch('/searchindex.json')`.

---

## 8. Сохранение URL-адресов (SEO и обратная совместимость)

Чтобы все старые ссылки из чатов садоводов в мессенджере MAX, WhatsApp и Telegram продолжали работать без ошибок `404`:
1. Сохраните настройку постоянных ссылок для постов в `hugo.yaml`:
```yaml
permalinks:
  post: "/p/:slug/"
```
2. Сохраните существующие пути статических разделов:
   - `/vznosy/` (и файл `/vznosy/qr-oplata.png`)
   - `/electro/`
   - `/documents/` (и вложенные файлы `/documents/ustav/ustav.pdf`, `/documents/docs/doverka.docx`)
   - `/pravlenie/`
   - `/komfort/`
   - `/contacts/`
   - `/redaktsiya/`
   - `/archives/`
   - `/search/`

---

## 9. Обязательные требования к доступности (аудитория 20–85 лет)

При нарезке HTML-макетов в шаблоны Hugo важно **не потерять** заложенные в прототипах решения:
1. **Переключатель размера шрифта `А+` (`html[data-font="large"] { font-size: 114%; }`)** и переключатель темы (`data-theme="light|dark"`) с сохранением выбора в `localStorage` (`orbita-font`, `orbita-theme`).
2. **Контрастность текста не ниже WCAG AA/AAA (6.3:1 – 10.9:1)**: использовать CSS-переменные из `:root` (`--ink`, `--ink2`, `--ink3`, `--cyan-deep`), не заменять их на бледно-серые цвета.
3. **Крупные зоны нажатия (Touch Targets)**: все кнопки в шапке, чипы фильтров, кнопки скачивания документов и пункты нижнего мобильного меню `.bottomnav` имеют высоту не менее `44px–48px`.
4. **Прямые кликабельные телефоны `tel:`**: телефон Правления `tel:+79219670642`, аварийная служба Ленэнерго `tel:88002200220` и приём показаний ПСК `tel:88126789600` должны оставаться прямыми ссылками для вызова в 1 нажатие со смартфона.
