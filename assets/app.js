document.addEventListener('DOMContentLoaded', () => {
  // 移动菜单切换
  const toggle = document.querySelector('.menu-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('open');
    });
  }

  // 本地访问计数（localStorage）- 无需 API，可靠持久
  const COUNTER_KEY = 'wangcai_blog_total_views';

  let count = parseInt(localStorage.getItem(COUNTER_KEY) || '0', 10);
  count += 1;
  localStorage.setItem(COUNTER_KEY, count.toString());

  // 显示在页脚
  const displayCount = count.toLocaleString('zh-CN');
  const el = document.getElementById('site-view-count');
  if (el) {
    el.textContent = displayCount;
  }

  // 可选：如果页面有本页计数器也一起加
  const PAGE_KEY = 'wangcai_blog_page_' + window.location.pathname.replace(/^\/+|\/+$/g, '') || 'index.html';
  let pageCount = parseInt(localStorage.getItem(PAGE_KEY) || '0', 10);
  pageCount += 1;
  localStorage.setItem(PAGE_KEY, pageCount.toString());
  // 如果页面上有本页访问元素，更新它
  const pageEl = document.getElementById('page-view-count');
  if (pageEl) {
    pageEl.textContent = pageCount.toLocaleString('zh-CN');
  }
});
