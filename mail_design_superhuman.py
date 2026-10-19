"""메일 디자인 (C안 · Superhuman DESIGN.md 스타일): 남보라 헤더에 보라 빛, 따뜻한 회색 글자, 1위는 남보라 카드, 마지막은 짙은 청록 띠."""
import html

INDIGO = "#1b1938"; DEEP = "#0e0c1f"; VIOLET = "#c9b4fa"; TEAL = "#0e3030"; TEAL2 = "#155555"
INK = "#292827"; MUTE = "#73706d"; FAINT = "#9a9794"; LINE = "#e8e4dd"; LINE_D = "#3f3a52"
SOFT = "#fafaf8"; ON_D = "#bcbac9"
FONT = "'Inter',system-ui,-apple-system,'Segoe UI',Roboto,'Malgun Gothic',sans-serif"

def _tag(c):
    for t in ("[드묾]", "[있음]", "[모름]"):
        if c.startswith(t):
            return t[1:-1], c[len(t):].strip()
    return "", c

def _chip(t, n=None, dark=False):
    style = {"드묾": f"background:{VIOLET};color:{INDIGO}",
             "있음": (f"background:{LINE_D};color:#fff" if dark else f"background:{INDIGO};color:#fff"),
             "모름": (f"background:transparent;color:{ON_D};border:1px solid {LINE_D}" if dark else f"background:#fff;color:{MUTE};border:1px solid {LINE}")}.get(t, f"color:{MUTE}")
    label = (t or "-") + (f" {n}" if n is not None else "")
    return f'<span style="{style};font-size:12px;font-weight:600;padding:4px 10px;border-radius:4px;white-space:nowrap;display:inline-block">{label}</span>'

def _card(it, i, featured):
    e = html.escape
    tags = " · ".join(it.get("태그_ko") or it["태그"])
    bg, fg, sub, box, boxfg, bd = ((INDIGO, "#fff", ON_D, DEEP, "#fff", INDIGO) if featured
                                   else ("#fff", INK, MUTE, SOFT, INK, LINE))
    star = f'<span style="background:{VIOLET};color:{INDIGO};font-size:11px;font-weight:600;padding:3px 9px;border-radius:9999px">오늘의 1순위</span>&nbsp; ' if featured else ""
    return f'''<tr><td style="padding:8px 28px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{bg};border:1px solid {bd};border-radius:12px;border-collapse:separate"><tr><td style="padding:24px 26px">
 <div style="font-size:12px;font-weight:600;color:{sub}">{star}{i:02d} · {e(it["날짜"][5:].replace("-", "."))} · ▲ {it["추천수"]}</div>
 <div style="font-size:22px;font-weight:600;line-height:1.15;letter-spacing:-0.3px;margin-top:10px"><a href="{e(it["링크"])}" style="color:{fg};text-decoration:none">{e(it["이름"])}</a></div>
 <div style="font-size:16px;color:{sub};line-height:1.5;margin-top:6px">{e(it.get("한줄소개_ko") or it["한줄소개"])}</div>
 <div style="background:{box};color:{boxfg};border-radius:8px;padding:12px 14px;margin-top:14px;font-size:14px;line-height:1.5">{e(it["_c"])}</div>
 <div style="font-size:12px;color:{sub};margin-top:12px">{e(tags)}</div>
</td></tr></table></td></tr>'''

def build(data):
    e = html.escape
    items = data["목록"]
    for it in items:
        it["_t"], it["_c"] = _tag(it.get("한국코멘트", ""))
    cnt = {k: sum(1 for it in items if it["_t"] == k) for k in ("드묾", "있음", "모름")}
    picks = sorted([it for it in items if it["_t"] == "드묾"], key=lambda x: -x["추천수"])[:5]
    days = " · ".join(d[5:].replace("-", ".") for d in data["날짜들"])
    out = []
    out.append(f'''<div style="background:{SOFT};padding:20px 0">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:620px;margin:0 auto;background:#fff;font-family:{FONT};color:{INK};border-collapse:separate;border-radius:16px;overflow:hidden">
<tr><td bgcolor="{INDIGO}" style="background-color:{INDIGO};background-image:radial-gradient(circle at 85% 0%, #8f7ad6 0%, #4a3f8f 22%, {INDIGO} 55%, {DEEP} 100%);padding:40px 32px 36px;color:#fff">
 <div style="font-size:12px;font-weight:600;color:{VIOLET}">Auto_PH · Product Hunt Daily</div>
 <div style="font-size:44px;font-weight:500;line-height:.96;letter-spacing:-1.2px;margin:18px 0 12px;color:#fff">한국에 드문 것<br><span style="color:{VIOLET}">{cnt["드묾"]}개</span></div>
 <div style="font-size:16px;color:{ON_D};line-height:1.5;margin-bottom:20px">미국 서부 {e(days)} · Product Hunt 상위 {len(items)}개를 한국 시장 기준으로 나눴습니다.</div>
 {_chip("드묾", cnt["드묾"], True)}&nbsp; {_chip("있음", cnt["있음"], True)}&nbsp; {_chip("모름", cnt["모름"], True)}
</td></tr>''')
    if picks:
        out.append(f'<tr><td style="padding:40px 28px 4px;font-size:28px;font-weight:600;letter-spacing:-0.63px;line-height:1.14">볼 만한 아이템</td></tr>')
        out.append(f'<tr><td style="padding:0 28px 10px;font-size:14px;color:{MUTE}">한국에 드문 것 중 추천 수 상위 {len(picks)}개</td></tr>')
        for i, it in enumerate(picks, 1):
            out.append(_card(it, i, i == 1))
    out.append(f'<tr><td style="padding:40px 28px 6px;font-size:28px;font-weight:600;letter-spacing:-0.63px;line-height:1.14">전체 목록</td></tr>')
    prev = None
    for it in items:
        if it["날짜"] != prev:
            prev = it["날짜"]
            out.append(f'<tr><td style="padding:20px 28px 6px"><span style="border:1px solid {LINE};color:{INK};font-size:13px;font-weight:600;padding:6px 14px;border-radius:9999px">{e(prev[5:].replace("-", "."))} · 미국 서부</span></td></tr>')
        out.append(f'''<tr><td style="padding:0 28px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-bottom:1px solid {LINE}"><tr>
 <td width="30" style="padding:16px 0;font-size:14px;font-weight:600;color:{FAINT};vertical-align:top">{it["순위"]:02d}</td>
 <td style="padding:16px 12px 16px 0;vertical-align:top">
  <a href="{e(it["링크"])}" style="font-size:16px;font-weight:600;color:{INK};text-decoration:none">{e(it["이름"])}</a>
  <span style="font-size:12px;color:{FAINT}">&nbsp;▲ {it["추천수"]}</span>
  <div style="font-size:15px;color:{INK};line-height:1.5;margin-top:3px">{e(it.get("한줄소개_ko") or it["한줄소개"])}</div>
  <div style="font-size:13px;color:{MUTE};line-height:1.5;margin-top:4px">{e(it["_c"])}</div>
 </td>
 <td width="56" style="padding:17px 0;vertical-align:top;text-align:right">{_chip(it["_t"])}</td>
</tr></table></td></tr>''')
    out.append(f'''<tr><td style="padding:36px 0 0"></td></tr>
<tr><td bgcolor="{TEAL}" style="background:{TEAL};padding:36px 32px;color:#fff">
 <div style="font-size:22px;font-weight:500;letter-spacing:-0.3px;line-height:1.2">오늘 고를 아이템이 있나요?</div>
 <div style="font-size:15px;color:#a9c6c6;line-height:1.5;margin-top:8px">이름을 누르면 Product Hunt 원문으로 이동합니다. 한국 코멘트는 AI 추정(참고용)입니다.</div>
 <div style="margin-top:18px;font-size:12px;color:#7fa5a5;border-top:1px solid {TEAL2};padding-top:14px">Auto_PH · 개인 용도</div>
</td></tr>
</table></div>''')
    return "".join(out)
