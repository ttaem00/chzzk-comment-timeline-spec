(() => {
  'use strict';
  const drawer = document.querySelector('.nav-drawer');
  const narrow = window.matchMedia('(max-width:800px)');
  const adaptNavigation = () => { if (drawer) drawer.open = !narrow.matches; };
  adaptNavigation();
  narrow.addEventListener('change', adaptNavigation);
  const dialog = document.getElementById('search-dialog');
  const button = document.querySelector('.search-open');
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  const status = document.getElementById('search-status');
  const records = Array.isArray(window.DOC_SEARCH) ? window.DOC_SEARCH : null;
  if (!dialog || typeof dialog.showModal !== 'function' || !records) return;
  button.hidden = false;
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase();
  const showSearch = () => { dialog.showModal(); input.focus(); };
  button.addEventListener('click', showSearch);
  document.addEventListener('keydown', event => {
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey &&
        !['INPUT','TEXTAREA','SELECT'].includes(event.target.tagName) && !event.target.isContentEditable && !dialog.open) {
      event.preventDefault(); showSearch();
    }
  });
  input.addEventListener('input', () => {
    results.replaceChildren();
    const query = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    if (!query.length) { status.textContent = '단어를 입력하면 문서를 찾습니다.'; return; }
    const hits = records.filter(record => query.every(word => normalize(record.title+' '+record.text).includes(word)))
      .sort((a,b) => Number(query.every(word=>normalize(b.title).includes(word)))-Number(query.every(word=>normalize(a.title).includes(word))));
    const seen = new Set();
    const unique = hits.filter(hit => !seen.has(hit.url) && seen.add(hit.url));
    for (const hit of unique.slice(0,12)) {
      const link = document.createElement('a'); link.href = hit.url; link.textContent = hit.title; results.append(link);
    }
    status.textContent = unique.length ? `${unique.length}개 결과${unique.length>12?' 중 12개 표시':''}` : '일치하는 문서가 없습니다. 짧은 단어로 다시 찾아보세요.';
  });
  dialog.addEventListener('close', () => button.focus());
})();
