"""Build the public reading site with Python's standard library only.

Sources remain in docs/source. This renderer deliberately supports only the
Markdown constructs used here and escapes raw HTML. It does not parse comments.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SOURCE = DOCS / "source"
PAGES = [
    ("index", "빠른 시작", "시작하기"),
    ("formats", "지원 형태 한눈에", "시작하기"),
    ("timeline", "시간축 읽는 법", "시작하기"),
    ("existing", "기존 댓글 읽기", "작성과 읽기"),
    ("ranges", "구간과 강조", "작성과 읽기"),
    ("people", "인물과 합방", "작성과 읽기"),
    ("files", "파일 가져오기", "더 알아보기"),
    ("limits", "한계와 문제 해결", "더 알아보기"),
    ("reference", "규격과 검증", "더 알아보기"),
]
LINKS = {"PEOPLE.md": "people.html", "IMPORT.md": "files.html",
         "ROSTER.md": "files.html#참가자와-역할-이름-가져오기",
         "SPEC.md": "reference.html", "SUPPORT.md": "formats.html",
         "README.md": "index.html", "VALIDATION.md": "reference.html#검증-범위"}
PUBLIC_BLOB = 'https://github.com/ttaem00/cva-ttaempad-timeline-spec/blob/main/'


def slug(text: str) -> str:
    value = re.sub(r"[`*_]", "", text).strip().lower()
    return re.sub(r"[^\w가-힣-]+", "-", value, flags=re.UNICODE).strip("-") or "section"


def rewrite_link(target: str) -> str:
    if target.startswith('../../examples/'):
        return target[6:]
    if target.startswith('../../'):
        name = target[6:].split('#', 1)[0]
        if name not in {'LICENSE', 'CONTRIBUTING.md', 'VALIDATION.md'}:
            raise ValueError('unsupported repository-root document link')
        return PUBLIC_BLOB + target[6:]
    if target.startswith("examples/"):
        return target
    base, _, fragment = target.partition("#")
    if base in {key+'.md' for key,_,_ in PAGES}:
        return base[:-3]+'.html'+('#'+fragment if fragment else '')
    if base in LINKS:
        mapped = LINKS[base]
        return mapped + ("#" + fragment if fragment and "#" not in mapped else "")
    return target


def inline(text: str) -> str:
    # Protect complete inline code before parsing links or emphasis.
    protected: list[str] = []
    def code(match):
        protected.append("<code>" + html.escape(match.group(1)) + "</code>")
        return f"\x00{len(protected)-1}\x00"
    text = re.sub(r"`([^`]+)`", code, text)
    text = html.escape(text)
    def link(match):
        target = rewrite_link(html.unescape(match.group(2)))
        if urlsplit(target).scheme not in ("", "https", "http"):
            raise ValueError("unsupported link scheme")
        return '<a href="' + html.escape(target, quote=True) + '">' + match.group(1) + '</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    for index, code_html in enumerate(protected):
        text = text.replace(f"\x00{index}\x00", code_html)
    return text


def image_figure(alt: str, target: str) -> str:
    """Render a local screenshot, never an embed or an editor resource."""
    # Markdown lives in docs/source; generated pages live one level above it.
    if target.startswith('../assets/'):
        target = target[3:]
    parsed = urlsplit(target)
    if (parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or
            not target.startswith('assets/') or '\\' in target):
        raise ValueError('images must be local docs/assets PNG files')
    destination = (DOCS / unquote(parsed.path)).resolve()
    if not destination.is_relative_to((DOCS / 'assets').resolve()) or destination.suffix.lower() != '.png':
        raise ValueError('images must be local docs/assets PNG files')
    with destination.open('rb') as image:
        header = image.read(24)
    if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError('image is not a PNG')
    width, height = int.from_bytes(header[16:20], 'big'), int.from_bytes(header[20:24], 'big')
    if not alt.strip() or not width or not height:
        raise ValueError('image needs alternative text and valid dimensions')
    safe_target, safe_alt = html.escape(target, quote=True), html.escape(alt, quote=True)
    return (f'<figure class="screen-figure"><a href="{safe_target}" aria-label="{safe_alt} — 원본 이미지 보기">'
            f'<img src="{safe_target}" alt="{safe_alt}" width="{width}" height="{height}" loading="lazy" decoding="async">'
            '</a><figcaption>이미지를 선택하면 원본 크기로 볼 수 있습니다.</figcaption></figure>')


def render_markdown(text: str):
    lines = text.splitlines()
    output, headings, paragraph = [], [], []
    ids: dict[str, int] = {}
    index = 0
    def flush():
        if paragraph:
            output.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()
    while index < len(lines):
        line = lines[index]
        if line.startswith("```"):
            flush()
            language = line[3:].strip() or "text"
            body = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                body.append(lines[index]); index += 1
            if index == len(lines):
                raise ValueError("unclosed code fence")
            output.append('<div class="code-example"><span class="code-label">' + html.escape(language.upper()) +
                          '</span><pre><code>' + html.escape("\n".join(body)) + '</code></pre></div>')
        elif match := re.fullmatch(r"!\[([^\]]+)\]\(([^)]+)\)\s*", line):
            flush()
            output.append(image_figure(match[1], match[2]))
        elif match := re.match(r"^(#{1,6})\s+(.+)$", line):
            flush()
            level, title = len(match[1]), match[2]
            base = slug(title); count = ids.get(base, 0); ids[base] = count + 1
            anchor = base + (f"-{count+1}" if count else "")
            headings.append((level, title, anchor))
            output.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
        elif line.startswith("|") and index + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[index+1]):
            flush()
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")]); index += 1
            index -= 1
            header = '<thead><tr>' + ''.join('<th scope="col">' + inline(cell) + '</th>' for cell in rows[0]) + '</tr></thead>'
            body = '<tbody>' + ''.join('<tr>' + ''.join('<td>' + inline(cell) + '</td>' for cell in row) + '</tr>' for row in rows[2:]) + '</tbody>'
            output.append('<div class="table-scroll" tabindex="0" role="region" aria-label="가로로 이동할 수 있는 표"><table>' + header + body + '</table></div>')
        elif re.match(r"^(?:- |\d+\. )", line):
            flush()
            ordered = bool(re.match(r"^\d+\. ", line)); kind = "ol" if ordered else "ul"
            items = []
            while index < len(lines) and re.match(r"^\d+\. " if ordered else r"^- ", lines[index]):
                items.append(re.sub(r"^\d+\. " if ordered else r"^- ", "", lines[index])); index += 1
            index -= 1
            output.append(f'<{kind}>' + ''.join('<li>' + inline(item) + '</li>' for item in items) + f'</{kind}>')
        elif line.startswith("> "):
            flush(); output.append('<blockquote><p>' + inline(line[2:]) + '</p></blockquote>')
        elif not line.strip():
            flush()
        else:
            paragraph.append(line.strip())
        index += 1
    flush()
    return "\n".join(output), headings


def navigation(current: str) -> str:
    parts, previous_group = [], None
    for key, label, group in PAGES:
        if group != previous_group:
            if previous_group is not None:
                parts.append('</div>')
            group_id = 'nav-' + slug(group)
            parts.append(f'<div class="nav-section" role="group" aria-labelledby="{group_id}"><p id="{group_id}" class="nav-group">{group}</p>')
            previous_group = group
        parts.append(f'<a href="{key}.html"' + (' aria-current="page"' if key == current else '') + '>' + label + '</a>')
    parts.append('</div>')
    return "\n".join(parts)


def page_template(key, label, article, headings, previous, next_page):
    toc = ''.join(f'<a class="toc-depth-{level}" href="#{anchor}">{html.escape(title)}</a>' for level, title, anchor in headings if level == 2)
    prev_next = ''.join(f'<a href="{item[0]}.html"><small>{direction}</small><span>{item[1]} {arrow}</span></a>'
                        for item, direction, arrow in [(previous, "이전 문서", "←"), (next_page, "다음 문서", "→")] if item)
    return f'''<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{label} · CVA-탬패드 댓글 안내</title>
  <meta name="description" content="CVA-탬패드가 읽는 댓글 시각과 목차, 구간, 인물, 파일 형식을 예제로 설명합니다.">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="assets/app-icon.png" type="image/png">
  <link rel="stylesheet" href="assets/site.css">
  <script src="assets/search-index.js" defer></script><script src="assets/site.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#main">본문으로 건너뛰기</a>
  <header class="site-header">
    <a class="brand" href="index.html"><img src="assets/app-icon.png" alt="" width="36" height="36"><span>CVA-탬패드<small>댓글 시간축 안내</small></span></a>
    <div class="header-actions"><span class="version">편집 초안 0.4</span><button class="search-open" type="button" hidden>문서 검색 <kbd>/</kbd></button><a class="product-link" href="https://ttaem.com/brand/ttaempad">제품 소개 <span aria-hidden="true">↗</span></a><a class="store-cta" href="https://chromewebstore.google.com/detail/ajokeikoipagcdnpdkkbamidkjgeghon/preview?hl=ko&amp;authuser=0">Chrome 스토어 보기 <span aria-hidden="true">↗</span></a></div>
  </header>
  <div class="site-layout">
    <aside class="sidebar"><details class="nav-drawer" open><summary>문서 목차</summary><nav aria-label="문서">{navigation(key)}</nav><div class="sidebar-foot"><span>지원 기준 0.3.23 후보</span><a href="https://github.com/ttaem00/cva-ttaempad-timeline-spec">공개 문서 저장소 ↗</a></div></details></aside>
    <main id="main" tabindex="-1"><p class="eyebrow">CVA-TTAEMPAD / COMMENT GUIDE</p><article>{article}</article><nav class="page-turn" aria-label="이전 다음 문서">{prev_next}</nav><footer>원문과 의도를 보존하며, 확인한 장면을 시간축에 담습니다.<br><a href="source/{key}.md">이 문서의 Markdown 원본</a> · <a href="{PUBLIC_BLOB}LICENSE">MIT 라이선스</a></footer></main>
    <aside class="toc"><nav aria-label="현재 문서 목차"><p>이 문서에서</p>{toc}</nav></aside>
  </div>
  <dialog id="search-dialog" aria-labelledby="search-title"><form method="dialog" class="search-head"><h2 id="search-title">문서 검색</h2><button aria-label="검색 닫기">닫기</button></form><label for="search-input">찾을 내용</label><input id="search-input" type="search" placeholder="예: 들여쓰기, 괄호, 합방" autocomplete="off"><p id="search-status" role="status">단어를 입력하면 문서를 찾습니다.</p><div id="search-results"></div></dialog>
  <noscript><p class="no-script">본문과 목차는 그대로 읽을 수 있습니다. 검색은 브라우저의 페이지 찾기(Ctrl+F)를 사용하세요.</p></noscript>
</body></html>
'''


class LinkReader(HTMLParser):
    def __init__(self):
        super().__init__(); self.targets = []; self.ids = set()
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'id' in values:
            if values['id'] in self.ids: raise ValueError('duplicate HTML id')
            self.ids.add(values['id'])
        for name in ('href', 'src'):
            if name in values: self.targets.append(values[name])


def validate_site():
    for key, _, _ in PAGES:
        source_file = DOCS / (key + '.html'); parser = LinkReader()
        parser.feed(source_file.read_text(encoding='utf-8'))
        for target in parser.targets:
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc: continue
            destination = (source_file.parent / unquote(parsed.path)).resolve() if parsed.path else source_file
            if not destination.is_relative_to(DOCS): raise ValueError('link outside deployed docs directory')
            if not destination.exists(): raise ValueError(f'missing local link: {key}: {target}')
            if parsed.fragment and destination.suffix == '.html':
                dest_parser = LinkReader(); dest_parser.feed(destination.read_text(encoding='utf-8'))
                if unquote(parsed.fragment) not in dest_parser.ids: raise ValueError(f'missing fragment: {key}: {target}')


def main():
    DOCS.mkdir(exist_ok=True); (DOCS / 'assets').mkdir(exist_ok=True)
    (DOCS / '.nojekyll').write_bytes(b'')
    # Keep deployed text identical across LF and Windows CRLF checkouts.
    for example in (ROOT / 'examples').rglob('*'):
        if example.is_file():
            destination = DOCS / 'examples' / example.relative_to(ROOT / 'examples')
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(example.read_bytes().replace(b'\r\n', b'\n'))
    search = []
    for index, (key, label, _) in enumerate(PAGES):
        text = (SOURCE / (key + '.md')).read_text(encoding='utf-8')
        article, headings = render_markdown(text)
        output = page_template(key, label, article, headings, PAGES[index-1] if index else None, PAGES[index+1] if index+1 < len(PAGES) else None)
        (DOCS / (key + '.html')).write_text(output, encoding='utf-8', newline='\n')
        search.append({'title':label, 'url':key+'.html', 'text':re.sub(r'[`#*_]', '', text)})
        for level, title, anchor in headings:
            if level == 2: search.append({'title':label+' · '+title,'url':key+'.html#'+anchor, 'text':title})
    (DOCS / 'assets/search-index.js').write_text('window.DOC_SEARCH = '+json.dumps(search,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8',newline='\n')
    validate_site()
    artifact_paths = [DOCS/(key+'.html') for key,_,_ in PAGES] + [p for p in (DOCS/'assets').rglob('*') if p.is_file()] + [DOCS/'.nojekyll']
    manifest = {'format':'cva-ttaempad.reading-site.v1','documentVersion':'0.4','consumer':'0.3.23 candidate','pages':len(PAGES),'generated':{str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(artifact_paths)}}
    (DOCS/'build-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Reading site build and local links PASS; {len(PAGES)} pages; no comment parser distributed')


if __name__ == '__main__':
    main()
