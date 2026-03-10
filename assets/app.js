document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.menu-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('open');
    });
  }

  // Simple page view counter using countapi.xyz
  const NAMESPACE = 'wangcai_blog';

  function incrementCounter(key) {
    const url = `https://api.countapi.xyz/hit/${encodeURIComponent(NAMESPACE)}/${encodeURIComponent(key)}`;
    return fetch(url)
      .then((res) => res.json())
      .catch(() => null);
  }

  // Normalize path for per-page key
  const rawPath = window.location.pathname.replace(/^\/+|\/+$/g, '') || 'index.html';

  // 1) Site-wide total views (homepage footer displays it if span exists)
  incrementCounter('site_total').then((data) => {
    const span = document.getElementById('site-view-count');
    if (span && data && typeof data.value === 'number') {
      span.textContent = data.value.toLocaleString('zh-CN');
    }
  });

  // 2) Per-page views: create a small counter in footer for non-home pages
  incrementCounter(`page_${rawPath}`).then((data) => {
    if (!data || typeof data.value !== 'number') return;
    const footer = document.querySelector('footer');
    if (!footer) return;

    let container = document.getElementById('page-view-count');
    if (!container) {
      const p = document.createElement('p');
      p.className = 'page-views';
      p.innerHTML = '本页访问：<span id="page-view-count">--</span>';
      footer.appendChild(p);
      container = p.querySelector('#page-view-count');
    }
    if (container) {
      container.textContent = data.value.toLocaleString('zh-CN');
    }
  });
});
