/**
 * СНТ «Орбита» — Скрипт мониторинга плановых отключений электроэнергии (2026-11)
 * Загружается на главной странице.
 * Запрашивает данные графика «Россети Ленэнерго» и отображает актуальный статус:
 * - Если запланировано отключение: выводит предупреждающий баннер с датой, временем и длительностью.
 * - Если отключений нет: выводит статус о том, что в ближайшее время плановых отключений не предвидится.
 */
(function() {
  'use strict';

  var banner = document.getElementById('powerOutageBanner');
  if (!banner) return;

  var endpoint = banner.getAttribute('data-endpoint') || '/data/outages.json';
  var defaultSourceUrl = 'https://rosseti-lenenergo.ru/clients/planned_work/?reg=5&res=59&street=%D1%82%D0%B5%D1%80.+%D0%A1%D0%9D%D0%A2+%D0%9E%D1%80%D0%B1%D0%B8%D1%82%D0%B0&date_start=&date_finish=';

  var iconSlot = banner.querySelector('.outage-banner-icon');
  var badgeSlot = banner.querySelector('.outage-badge');
  var dateBadgeSlot = banner.querySelector('.outage-date-badge');
  var titleSlot = banner.querySelector('.outage-banner-title');
  var descSlot = banner.querySelector('.outage-banner-desc');
  var linkSlot = banner.querySelector('.outage-btn');

  var SVG_WARNING = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg>';
  var SVG_OK = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>';
  var SVG_EXTERNAL = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>';

  function parseDateIso(isoStr) {
    if (!isoStr) return null;
    var d = new Date(isoStr);
    return isNaN(d.getTime()) ? null : d;
  }

  function formatHumanDate(dateStr, isoStr) {
    if (isoStr) {
      var d = new Date(isoStr);
      if (!isNaN(d.getTime())) {
        var months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
        var days = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'];
        return d.getDate() + ' ' + months[d.getMonth()] + ' (' + days[d.getDay()] + ')';
      }
    }
    return dateStr || '';
  }

  function renderWarning(outage, meta) {
    banner.setAttribute('data-state', 'warning');
    banner.classList.remove('outage-banner--ok', 'outage-banner--loading');
    banner.classList.add('outage-banner--warning');

    if (iconSlot) iconSlot.innerHTML = SVG_WARNING;
    if (badgeSlot) {
      badgeSlot.textContent = '⚡ Плановые работы Ленэнерго';
      badgeSlot.className = 'outage-badge outage-badge--warning';
    }

    var humanDate = formatHumanDate(outage.displayDate, outage.dateStartIso);
    if (dateBadgeSlot) {
      dateBadgeSlot.textContent = humanDate || outage.displayDate || 'Скоро';
      dateBadgeSlot.style.display = 'inline-flex';
    }

    if (titleSlot) {
      var timePart = outage.timeInterval ? 'с ' + outage.timeInterval : '';
      titleSlot.innerHTML = 'Запланировано отключение электроэнергии: <b>' + (outage.displayDate || '') + ' ' + timePart + '</b>';
    }

    if (descSlot) {
      var durationTxt = outage.duration ? 'Режим работ: <b>' + outage.duration + '</b>. ' : '';
      var resTxt = outage.res ? outage.res + ' («Россети Ленэнерго»). ' : 'Красносельский РЭС. ';
      var checkTxt = meta.checkedAt ? '<span class="outage-check-time">Сверка: ' + meta.checkedAt + '</span>' : '';
      descSlot.innerHTML = durationTxt + 'Зона: СНТ «Орбита». ' + resTxt + checkTxt;
    }

    if (linkSlot) {
      linkSlot.setAttribute('href', meta.sourceUrl || defaultSourceUrl);
      linkSlot.innerHTML = 'График Ленэнерго ' + SVG_EXTERNAL;
    }
  }

  function renderOk(meta) {
    banner.setAttribute('data-state', 'ok');
    banner.classList.remove('outage-banner--warning', 'outage-banner--loading');
    banner.classList.add('outage-banner--ok');

    if (iconSlot) iconSlot.innerHTML = SVG_OK;
    if (badgeSlot) {
      badgeSlot.textContent = '✓ Электроснабжение в норме';
      badgeSlot.className = 'outage-badge outage-badge--ok';
    }

    if (dateBadgeSlot) {
      dateBadgeSlot.textContent = 'Плановых работ нет';
      dateBadgeSlot.style.display = 'inline-flex';
    }

    if (titleSlot) {
      titleSlot.textContent = 'В ближайшее время планируемых отключений не предвидится';
    }

    if (descSlot) {
      var checkTxt = meta && meta.checkedAt ? ' <span class="outage-check-time">Проверено: ' + meta.checkedAt + '</span>' : '';
      descSlot.innerHTML = 'По официальным данным «Россети Ленэнерго» (Красносельский РЭС), энергосеть СНТ «Орбита» работает в штатном режиме.' + checkTxt;
    }

    if (linkSlot) {
      linkSlot.setAttribute('href', (meta && meta.sourceUrl) || defaultSourceUrl);
      linkSlot.innerHTML = 'Проверить график ' + SVG_EXTERNAL;
    }
  }

  function applyData(data) {
    if (!data) {
      renderOk({ checkedAt: '', sourceUrl: defaultSourceUrl });
      return;
    }

    var now = new Date();
    var activeOutage = null;

    // Проверяем список предстоящих отключений
    if (data.upcoming && Array.isArray(data.upcoming)) {
      for (var i = 0; i < data.upcoming.length; i++) {
        var item = data.upcoming[i];
        var dtEnd = parseDateIso(item.dateEndIso);
        // Если дата окончания в будущем относительно текущего времени пользователя
        if (!dtEnd || dtEnd >= now) {
          activeOutage = item;
          break;
        }
      }
    } else if (data.hasOutage && data.activeOutage) {
      var dt = parseDateIso(data.activeOutage.dateEndIso);
      if (!dt || dt >= now) {
        activeOutage = data.activeOutage;
      }
    }

    if (activeOutage) {
      renderWarning(activeOutage, data);
    } else {
      renderOk(data);
    }
  }

  // 1. Проверяем вшитые данные (data-embedded), если сервер сгенерировал SSR
  var embedded = banner.getAttribute('data-embedded');
  if (embedded) {
    try {
      var parsedEmbedded = JSON.parse(decodeURIComponent(embedded));
      applyData(parsedEmbedded);
    } catch (e) {
      // Игнорируем ошибку парсинга вшитых данных и идём к fetch
    }
  }

  // 2. Выполняем асинхронный запрос актуального JSON-файла
  var cacheBuster = '?v=' + Math.floor(Date.now() / 600000); // кеш 10 мин
  fetch(endpoint + cacheBuster, { cache: 'no-cache' })
    .then(function(resp) {
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      return resp.json();
    })
    .then(function(data) {
      applyData(data);
    })
    .catch(function(err) {
      // При ошибке сети, если уже отображено что-то валидное, оставляем
      if (banner.getAttribute('data-state') === 'loading') {
        renderOk({ checkedAt: '', sourceUrl: defaultSourceUrl });
      }
    });
})();
