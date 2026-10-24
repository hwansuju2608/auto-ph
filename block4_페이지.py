"""페이지 블록: 2_처리.json으로 그날치 한국어 상세 페이지(docs/날짜.html)와 목록 페이지(docs/index.html)를 만든다.
   docs 폴더는 깃허브 Pages로 인터넷에 올라가고, 메일의 각 이름이 이 페이지로 연결된다."""
import json, os, html, glob, datetime as dt
from common import log, OUT, BASE

DOCS = os.path.join(BASE, "docs")
PAGES_URL = "https://hwansuju2608.github.io/auto-ph"   # 깃허브 Pages 주소

def page_name():
    """오늘(한국) 날짜 파일 이름."""
    return (dt.datetime.utcnow() + dt.timedelta(hours=9)).strftime("%Y-%m-%d") + ".html"

def detail_url(it):
    return f"{PAGES_URL}/{page_name()}#p{it['번호']}"

CSS = """
:root{--indigo:#1b1938;--deep:#0e0c1f;--violet:#c9b4fa;--ink:#292827;--mute:#73706d;--faint:#9a9794;
--line:#e8e4dd;--soft:#fafaf8;--teal:#0e3030;--ok:#1f7a4d;--warn:#a5532a}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--soft);color:var(--ink);font-family:Pretendard,"Malgun Gothic","Apple SD Gothic Neo",system-ui,sans-serif;line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:inherit}
.wrap{max-width:760px;margin:0 auto;padding:0 16px}
header{background:radial-gradient(circle at 85% 0%,#8f7ad6 0%,#4a3f8f 22%,var(--indigo) 55%,var(--deep) 100%);color:#fff;padding:44px 0 36px}
.eyebrow{font-size:13px;font-weight:600;color:var(--violet)}
h1{font-size:34px;line-height:1.2;margin:12px 0 10px;letter-spacing:-.5px}
h1 span{color:var(--violet)}
.lead{color:#bcbac9;font-size:15px;margin:0}
nav.toc{display:flex;flex-wrap:wrap;gap:6px;margin-top:20px}
nav.toc a{font-size:13px;text-decoration:none;color:#fff;border:1px solid #3f3a52;border-radius:999px;padding:4px 11px}
nav.toc a:hover{background:#3f3a52}
.day{margin:34px 0 4px;font-size:13px;font-weight:700;color:var(--mute)}
article{background:#fff;border:1px solid var(--line);border-radius:16px;margin:14px 0 22px;overflow:hidden;scroll-margin-top:12px}
article:target{box-shadow:0 0 0 3px var(--violet)}
.shots{display:flex;gap:6px;overflow-x:auto;background:var(--soft);padding:10px;scroll-snap-type:x mandatory}
.shots img{height:220px;width:auto;border-radius:10px;scroll-snap-align:start;flex:none;background:#eee}
.body{padding:22px 24px 24px}
.meta{font-size:13px;color:var(--mute);font-weight:600;display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center}
.chip{display:inline-block;font-size:12px;font-weight:700;padding:2px 9px;border-radius:5px}
.c-드묾{background:var(--violet);color:var(--indigo)}.c-있음{background:var(--indigo);color:#fff}.c-모름{border:1px solid var(--line);color:var(--mute)}
h2{font-size:24px;margin:8px 0 6px;letter-spacing:-.3px}
.what{font-size:16.5px;margin:0 0 14px}
h3{font-size:13px;color:var(--mute);margin:18px 0 6px;font-weight:700}
ul{margin:0;padding-left:20px}li{margin:3px 0}
.feat li::marker{content:"✓  ";color:var(--ok)}
.good li::marker{content:"＋ ";color:var(--ok)}.bad li::marker{content:"－ ";color:var(--warn)}
.maker{background:var(--soft);border-radius:10px;padding:12px 14px;font-size:15px}
.kr{background:var(--indigo);color:#fff;border-radius:10px;padding:12px 14px;font-size:15px}
.price{font-size:14px;color:var(--mute)}
.btns{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}
.btns a{text-decoration:none;font-size:14px;font-weight:600;padding:8px 14px;border-radius:8px;border:1px solid var(--line)}
.btns a.main{background:var(--indigo);color:#fff;border-color:var(--indigo)}
footer{background:var(--teal);color:#a9c6c6;font-size:13px;padding:26px 0;margin-top:30px}
footer a{color:#fff}
@media(max-width:560px){h1{font-size:28px}.shots img{height:170px}.body{padding:18px 16px 20px}h2{font-size:21px}}
"""

def _tag(c):
    for t in ("[드묾]", "[있음]", "[모름]"):
        if c.startswith(t):
            return t[1:-1], c[len(t):].strip()
    return "", c

def _ul(items, cls):
    items = [i for i in (items or []) if i]
    return f'<ul class="{cls}">' + "".join(f"<li>{html.escape(i)}</li>" for i in items) + "</ul>" if items else ""

def _item(it):
    e = html.escape
    t, c = _tag(it.get("한국코멘트", ""))
    shots = "".join(f'<img src="{e(u)}" alt="" loading="lazy">' for u in it.get("사진", []))
    r = it.get("반응_ko") or {}
    react = ""
    if r.get("요약") or r.get("좋은점") or r.get("아쉬운점"):
        react = (f'<h3>사람들 반응 · 댓글 {it.get("댓글수", 0)}개</h3>'
                 + (f'<p style="margin:0 0 6px">{e(r.get("요약", ""))}</p>' if r.get("요약") else "")
                 + _ul(r.get("좋은점"), "good") + _ul(r.get("아쉬운점"), "bad"))
    tags = " · ".join(it.get("태그_ko") or it["태그"])
    return f"""
<article id="p{it['번호']}">
 {f'<div class="shots">{shots}</div>' if shots else ''}
 <div class="body">
  <div class="meta"><span>{it['순위']:02d}위 · {e(it['날짜'][5:].replace('-', '.'))}</span><span>▲ 추천 {it['추천수']}</span><span>💬 댓글 {it.get('댓글수', 0)}</span>{f'<span class="chip c-{t}">{t}</span>' if t else ''}</div>
  <h2>{e(it['이름'])}</h2>
  <p class="what">{e(it.get('무엇_ko') or it.get('한줄소개_ko') or it['한줄소개'])}</p>
  {('<h3>주요 기능</h3>' + _ul(it.get('기능_ko'), 'feat')) if it.get('기능_ko') else ''}
  {f'<p class="price">가격 · {e(it["가격_ko"])}</p>' if it.get('가격_ko') else ''}
  {f'<h3>만든 사람의 소개</h3><div class="maker">{e(it["소개글_ko"])}</div>' if it.get('소개글_ko') else ''}
  {react}
  <h3>한국 시장</h3><div class="kr">{e(c)}</div>
  <p class="price" style="margin-top:12px">{e(tags)}</p>
  <div class="btns"><a class="main" href="{e(it['링크'])}" target="_blank" rel="noopener">Product Hunt 원문</a>{f'<a href="{e(it["사이트"])}" target="_blank" rel="noopener">서비스 사이트</a>' if it.get('사이트') else ''}</div>
 </div>
</article>"""

def build_page(data):
    e = html.escape
    items = data["목록"]
    cnt = sum(1 for it in items if _tag(it.get("한국코멘트", ""))[0] == "드묾")
    days = " · ".join(d[5:].replace("-", ".") for d in data["날짜들"])
    toc = "".join(f'<a href="#p{it["번호"]}">{e(it["이름"])}</a>' for it in items)
    body, prev = [], None
    for it in items:
        if it["날짜"] != prev:
            prev = it["날짜"]
            body.append(f'<div class="day">{e(prev[5:].replace("-", "."))} · 미국 서부</div>')
        body.append(_item(it))
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PH 한국어 브리핑 {e(days)}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>{CSS}</style></head><body>
<header><div class="wrap"><div class="eyebrow">Auto_PH · Product Hunt 한국어 브리핑</div>
<h1>미국 서부 {e(days)}<br><span>한국에 드문 것 {cnt}개</span></h1>
<p class="lead">Product Hunt 상위 {len(items)}개를 한국어로 정리했습니다. 설명·반응 요약·한국 코멘트는 AI가 쓴 참고용입니다.</p>
<nav class="toc">{toc}</nav></div></header>
<main class="wrap">{''.join(body)}</main>
<footer><div class="wrap"><a href="index.html">지난 브리핑 보기</a> · Auto_PH · 개인 용도</div></footer>
</body></html>"""

def build_index():
    pages = sorted((os.path.basename(p) for p in glob.glob(os.path.join(DOCS, "20*.html"))), reverse=True)
    rows = "".join(f'<li><a href="{p}">{p[:-5]}</a></li>' for p in pages)
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PH 한국어 브리핑</title><style>{CSS} li{{font-size:17px;margin:8px 0}}</style></head><body>
<header><div class="wrap"><div class="eyebrow">Auto_PH</div><h1>Product Hunt 한국어 브리핑</h1></div></header>
<main class="wrap" style="padding:24px 16px"><ul>{rows}</ul></main></body></html>"""

def main():
    src = os.path.join(OUT, "2_처리.json")
    if not os.path.exists(src):
        log("페이지", False, "2_처리.json이 없음 (처리 블록부터)"); return False
    data = json.load(open(src, encoding="utf-8"))
    os.makedirs(DOCS, exist_ok=True)
    name = page_name()
    with open(os.path.join(DOCS, name), "w", encoding="utf-8") as f:
        f.write(build_page(data))
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_index())
    log("페이지", True, f"docs/{name} 만듦")
    return True

if __name__ == "__main__":
    main()
