/**
 * СНТ «Орбита» — Основной клиентский скрипт (2026-11)
 * Чистый ванильный JS без сторонних библиотек.
 */
(function() {
  'use strict';
  var root = document.documentElement;

  // 1. Управление темой оформления
  var themeBtn = document.getElementById('themeBtn');
  var themeIconSlot = document.getElementById('themeIconSlot');

  function syncThemeUI() {
    var isDark = root.dataset.theme === 'dark';
    if (themeIconSlot) {
      if (isDark) {
        themeIconSlot.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';
      } else {
        themeIconSlot.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
      }
    }
    if (themeBtn) {
      themeBtn.setAttribute('aria-label', isDark ? 'Переключить на светлую тему' : 'Переключить на тёмную тему');
    }
    var metaTheme = document.querySelector('meta[name="theme-color"]');
    if (metaTheme) {
      metaTheme.setAttribute('content', isDark ? '#0b1220' : '#17233b');
    }
  }

  // Применяем тему
  var savedTheme = null;
  try { savedTheme = localStorage.getItem('orbita-theme') || localStorage.getItem('cnt_theme'); } catch(e) {}
  if (savedTheme) {
    root.dataset.theme = savedTheme;
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    root.dataset.theme = 'dark';
  }
  syncThemeUI();

  if (themeBtn) {
    themeBtn.addEventListener('click', function() {
      var nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = nextTheme;
      try {
        localStorage.setItem('orbita-theme', nextTheme);
        localStorage.setItem('cnt_theme', nextTheme);
      } catch(e) {}
      syncThemeUI();
    });
  }

  // 2. Управление режимом крупного шрифта «А+»
  var fontBtn = document.getElementById('fontBtn');
  var fontBtnMobile = document.getElementById('fontBtnMobile');

  function syncFontUI() {
    var isLarge = root.dataset.font === 'large';
    if (fontBtn) fontBtn.setAttribute('aria-pressed', isLarge ? 'true' : 'false');
    if (fontBtnMobile) fontBtnMobile.setAttribute('aria-pressed', isLarge ? 'true' : 'false');
  }

  var savedFont = null;
  try { savedFont = localStorage.getItem('orbita-font') || localStorage.getItem('cnt_font'); } catch(e) {}
  if (savedFont === 'large') {
    root.dataset.font = 'large';
  }
  syncFontUI();

  function toggleFont() {
    var nextFont = root.dataset.font === 'large' ? 'normal' : 'large';
    root.dataset.font = nextFont;
    try {
      localStorage.setItem('orbita-font', nextFont);
      localStorage.setItem('cnt_font', nextFont);
    } catch(e) {}
    syncFontUI();
  }
  if (fontBtn) fontBtn.addEventListener('click', toggleFont);
  if (fontBtnMobile) fontBtnMobile.addEventListener('click', toggleFont);

  // 3. Каталог разделов и мобильное меню (#mobileMenu)
  var menu = document.getElementById('mobileMenu');
  var backdrop = document.getElementById('menuBackdrop');
  var burgerBtn = document.getElementById('burgerBtn');
  var navMoreBtn = document.getElementById('navMoreBtn');
  var tabbarMenuBtn = document.getElementById('tabbarMenuBtn');
  var searchBar = document.getElementById('searchBar');
  var searchBtn = document.getElementById('searchBtn');

  function isMenuOpen() {
    return menu && menu.classList.contains('open');
  }

  function openMenu() {
    if (searchBar) {
      searchBar.classList.remove('open');
      if (searchBtn) searchBtn.setAttribute('aria-expanded', 'false');
    }
    if (menu) {
      menu.classList.add('open');
      menu.setAttribute('aria-hidden', 'false');
    }
    if (backdrop) backdrop.classList.add('open');
    if (burgerBtn) {
      burgerBtn.setAttribute('aria-expanded', 'true');
      burgerBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';
    }
    if (navMoreBtn) navMoreBtn.setAttribute('aria-expanded', 'true');
    if (tabbarMenuBtn) tabbarMenuBtn.setAttribute('aria-expanded', 'true');
  }

  function closeMenu() {
    if (menu) {
      menu.classList.remove('open');
      menu.setAttribute('aria-hidden', 'true');
    }
    if (backdrop) backdrop.classList.remove('open');
    if (burgerBtn) {
      burgerBtn.setAttribute('aria-expanded', 'false');
      burgerBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg>';
    }
    if (navMoreBtn) navMoreBtn.setAttribute('aria-expanded', 'false');
    if (tabbarMenuBtn) tabbarMenuBtn.setAttribute('aria-expanded', 'false');
  }

  function toggleMenu() {
    if (isMenuOpen()) {
      closeMenu();
    } else {
      openMenu();
    }
  }

  if (burgerBtn) burgerBtn.addEventListener('click', toggleMenu);
  if (navMoreBtn) navMoreBtn.addEventListener('click', toggleMenu);
  if (tabbarMenuBtn) tabbarMenuBtn.addEventListener('click', toggleMenu);
  if (backdrop) backdrop.addEventListener('click', closeMenu);

  // Закрытие меню при клике по ссылке
  if (menu) {
    var links = menu.querySelectorAll('a');
    for (var i = 0; i < links.length; i++) {
      links[i].addEventListener('click', closeMenu);
    }
  }

  // 4. Панель поиска
  if (searchBtn && searchBar) {
    searchBtn.addEventListener('click', function() {
      if (isMenuOpen()) closeMenu();
      var isOpen = searchBar.classList.toggle('open');
      searchBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      if (isOpen) {
        var inp = searchBar.querySelector('input');
        if (inp) inp.focus();
      }
    });
  }

  // 5. Модальное окно реквизитов и QR-кода (#qrModal)
  var qrModal = document.getElementById('qrModal');
  var qrBtns = document.querySelectorAll('.btn-show-qr');

  function openQRModal() {
    if (qrModal) {
      qrModal.classList.add('open');
      document.body.classList.add('menu-open');
    }
  }

  function closeQRModal() {
    if (qrModal) {
      qrModal.classList.remove('open');
      if (!isMenuOpen()) document.body.classList.remove('menu-open');
    }
  }

  for (var j = 0; j < qrBtns.length; j++) {
    qrBtns[j].addEventListener('click', function(e) {
      e.preventDefault();
      openQRModal();
    });
  }

  if (qrModal) {
    qrModal.addEventListener('click', function(e) {
      if (e.target === qrModal) closeQRModal();
    });
    var closeBtns = qrModal.querySelectorAll('.modal-close');
    for (var k = 0; k < closeBtns.length; k++) {
      closeBtns[k].addEventListener('click', closeQRModal);
    }
  }

  // 6. Копирование реквизитов в буфер обмена + Toast
  var toast = document.getElementById('toast');
  var toastTimer = null;

  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg || '✓ Скопировано в буфер обмена';
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function() {
      toast.classList.remove('show');
    }, 2200);
  }

  document.addEventListener('click', function(e) {
    var btn = e.target.closest('.copy-btn');
    if (btn) {
      e.preventDefault();
      var textToCopy = btn.getAttribute('data-copy');
      if (textToCopy) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(textToCopy).then(function() {
            showToast('✓ ' + (btn.getAttribute('data-label') || 'Скопировано') + ': ' + textToCopy);
          }).catch(function() {
            fallbackCopy(textToCopy, btn.getAttribute('data-label'));
          });
        } else {
          fallbackCopy(textToCopy, btn.getAttribute('data-label'));
        }
      }
    }
  });

  function fallbackCopy(text, label) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      showToast('✓ ' + (label || 'Скопировано') + ': ' + text);
    } catch(err) {
      alert('Скопируйте вручную: ' + text);
    }
    document.body.removeChild(ta);
  }

  // 7. Закрытие окон по Escape
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      if (qrModal && qrModal.classList.contains('open')) {
        closeQRModal();
      } else if (isMenuOpen()) {
        closeMenu();
      } else if (searchBar && searchBar.classList.contains('open')) {
        searchBar.classList.remove('open');
        if (searchBtn) searchBtn.setAttribute('aria-expanded', 'false');
      }
    }
  });

  // 8. Автоматическое скрытие Hero-баннера после data-expires
  var heroBanner = document.querySelector('.hero-banner[data-expires]');
  if (heroBanner) {
    var exp = Date.parse(heroBanner.getAttribute('data-expires'));
    if (!isNaN(exp) && Date.now() > exp) {
      heroBanner.style.display = 'none';
    }
  }

  // 9. Кнопка «Скопировать ссылку соседям» (#copyLinkBtn)
  var copyLinkBtn = document.getElementById('copyLinkBtn');
  if (copyLinkBtn) {
    copyLinkBtn.addEventListener('click', function() {
      var url = window.location.href;
      var span = copyLinkBtn.querySelector('span');
      var origText = span ? span.textContent : '';
      function onCopied() {
        showToast('✓ Ссылка на страницу скопирована');
        if (span) {
          span.textContent = 'Ссылка скопирована!';
          setTimeout(function() { span.textContent = origText; }, 2200);
        }
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(onCopied).catch(function() {
          fallbackCopy(url, 'Ссылка на страницу');
        });
      } else {
        fallbackCopy(url, 'Ссылка на страницу');
      }
    });
  }

  // 10. Фильтрация по годам на странице архива (.year-btn[data-year])
  var yearBtns = document.querySelectorAll('.year-btn[data-year]');
  var yearBlocks = document.querySelectorAll('.year-section[data-year-block]');
  if (yearBtns.length > 0 && yearBlocks.length > 0) {
    for (var y = 0; y < yearBtns.length; y++) {
      yearBtns[y].addEventListener('click', function(e) {
        var targetYear = this.getAttribute('data-year');
        if (!targetYear) return;
        e.preventDefault();
        for (var b = 0; b < yearBtns.length; b++) {
          yearBtns[b].classList.toggle('active', yearBtns[b] === this);
        }
        for (var s = 0; s < yearBlocks.length; s++) {
          var blockYear = yearBlocks[s].getAttribute('data-year-block');
          yearBlocks[s].style.display = (targetYear === 'all' || blockYear === targetYear) ? '' : 'none';
        }
      });
    }
  }
})();
