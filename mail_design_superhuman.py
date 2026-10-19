"""메일 디자인 (Superhuman DESIGN.md 스타일) — Outlook(클래식)에서도 깨지지 않게 만든 판.
Outlook 클래식은 메일을 워드 엔진으로 그려서 div 여백·줄간격·웹글꼴을 무시한다.
그래서: 모든 칸을 표(td)로 만들고, 여백은 td padding으로, 글꼴은 td마다 맑은 고딕을 먼저 지정한다.
둥근 모서리·빛 번짐은 Outlook 클래식에서만 각지고 단색으로 보인다(다른 메일 앱은 그대로)."""
import html

INDIGO = "#1b1938"; DEEP = "#0e0c1f"; VIOLET = "#c9b4fa"; TEAL = "#0e3030"; TEAL2 = "#155555"
INK = "#292827"; MUTE = "#73706d"; FAINT = "#9a9794"; LINE = "#e8e4dd"; LINE_D = "#3f3a52"
SOFT = "#fafaf8"; ON_D = "#bcbac9"
FONT = "'Malgun Gothic','맑은 고딕',Arial,sans-serif"
TBL = 'role="presentation" cellpadding="0" cellspacing="0" border="0"'

def _t(css, content, extra=""):
    """글꼴을 항상 같이 넣는 td."""
    return f'<td {extra} style="font-family:{FONT};mso-line-height-rule:exactly;{css}">{content}</td>'

def _tag(c):
    for t in ("[드묾]", "[있음]", "[모름]"):
        if c.startswith(t):
            return t[1:-1], c[len(t):].strip()
    return "", c

def _chip(t, n=None, dark=False):
    """배지: 작은 표 한 칸 (Outlook에서도 배경·여백 유지)."""
    bg, fg, bd = {"드묾": (VIOLET, INDIGO, VIOLET),
                  "있음": ((LINE_D, "#ffffff", LINE_D) if dark else (INDIGO, "#ffffff", INDIGO)),
                  "모름": ((INDIGO, ON_D, LINE_D) if dark else ("#ffffff", MUTE, LINE))}.get(t, ("#ffffff", MUTE, LINE))
    label = (t or "-") + (f" {n}" if n is not None else "")
    return (f'<table {TBL} style="display:inline-table"><tr>'
            + _t(f"background:{bg};border:1px solid {bd};color:{fg};font-size:12px;font-weight:bold;line-height:16px;padding:4px 10px;border-radius:4px;white-space:nowrap", label, f'bgcolor="{bg}"')
            + '</tr></table>')

def _chips(cnt, dark):
    cells = "".join(f'<td style="padding-right:8px">{_chip(k, cnt[k], dark)}</td>' for k in ("드묾", "있음", "모름"))
    return f'<table {TBL}><tr>{cells}</tr></table>'

def _row(content_td):
    return f"<tr>{content_td}</tr>"

def _card(it, i, featured):
    e = html.escape
    tags = " · ".join(it.get("태그_ko") or it["태그"])
    bg, fg, sub, box, boxfg, bd = ((INDIGO, "#ffffff", ON_D, DEEP, "#ffffff", INDIGO) if featured
                                   else ("#ffffff", INK, MUTE, SOFT, INK, LINE))
    head = ""
    if featured:
        head = (f'<table {TBL}><tr>'
                + _t(f"background:{VIOLET};color:{INDIGO};font-size:11px;font-weight:bold;line-height:14px;padding:3px 9px;border-radius:9999px", "오늘의 1순위", f'bgcolor="{VIOLET}"')
                + _t(f"color:{sub};font-size:12px;font-weight:bold;line-height:16px;padding-left:8px", f'{i:02d} · {e(it["날짜"][5:].replace("-", "."))} · ▲ {it["추천수"]}')
                + '</tr></table>')
    else:
        head = (f'<table {TBL}><tr>' + _t(f"color:{sub};font-size:12px;font-weight:bold;line-height:16px",
                f'{i:02d} · {e(it["날짜"][5:].replace("-", "."))} · ▲ {it["추천수"]}') + '</tr></table>')
    inner = (f'<table {TBL} width="100%">'
             + _row(_t("padding:0", head))
             + _row(_t(f"padding-top:10px;font-size:22px;font-weight:bold;line-height:28px;color:{fg}",
                       f'<a href="{e(it["링크"])}" style="color:{fg};text-decoration:none;font-family:{FONT}">{e(it["이름"])}</a>'))
             + _row(_t(f"padding-top:4px;font-size:15px;line-height:23px;color:{sub}", e(it.get("한줄소개_ko") or it["한줄소개"])))
             + _row(f'<td style="padding-top:14px"><table {TBL} width="100%"><tr>'
                    + _t(f"background:{box};color:{boxfg};font-size:14px;line-height:22px;padding:12px 14px;border-radius:8px", e(it["_c"]), f'bgcolor="{box}"')
                    + '</tr></table></td>')
             + _row(_t(f"padding-top:12px;font-size:12px;line-height:18px;color:{sub}", e(tags)))
             + '</table>')
    return (f'<tr><td style="padding:8px 28px"><table {TBL} width="100%" style="border-collapse:separate"><tr>'
            + _t(f"background:{bg};border:1px solid {bd};border-radius:12px;padding:24px 26px", inner, f'bgcolor="{bg}"')
            + '</tr></table></td></tr>')

def build(data):
    e = html.escape
    items = data["목록"]
    for it in items:
        it["_t"], it["_c"] = _tag(it.get("한국코멘트", ""))
    cnt = {k: sum(1 for it in items if it["_t"] == k) for k in ("드묾", "있음", "모름")}
    picks = sorted([it for it in items if it["_t"] == "드묾"], key=lambda x: -x["추천수"])[:5]
    days = " · ".join(d[5:].replace("-", ".") for d in data["날짜들"])
    o = []
    o.append(f'<table {TBL} width="100%" bgcolor="{SOFT}" style="background:{SOFT}"><tr><td align="center" style="padding:20px 0">')
    o.append(f'<table {TBL} width="620" style="width:620px;max-width:620px;background:#ffffff;border-collapse:separate;border-radius:16px" bgcolor="#ffffff">')
    # 헤더
    hero = (f'<table {TBL} width="100%">'
            + _row(_t(f"font-size:12px;font-weight:bold;line-height:16px;color:{VIOLET}", "Auto_PH · Product Hunt Daily"))
            + _row(_t("padding-top:18px;font-size:40px;font-weight:bold;line-height:50px;color:#ffffff",
                      f'한국에 드문 것<br><span style="color:{VIOLET}">{cnt["드묾"]}개</span>'))
            + _row(_t(f"padding-top:10px;font-size:15px;line-height:23px;color:{ON_D}",
                      f'미국 서부 {e(days)} · Product Hunt 상위 {len(items)}개를 한국 시장 기준으로 나눴습니다.'))
            + _row(f'<td style="padding-top:18px">{_chips(cnt, True)}</td>')
            + '</table>')
    o.append('<tr>' + _t(f"background-color:{INDIGO};background-image:radial-gradient(circle at 85% 0%, #8f7ad6 0%, #4a3f8f 22%, {INDIGO} 55%, {DEEP} 100%);padding:40px 32px 36px;border-radius:16px 16px 0 0", hero, f'bgcolor="{INDIGO}"') + '</tr>')
    # 볼 만한 아이템
    if picks:
        o.append(_row(_t(f"padding:40px 28px 4px;font-size:26px;font-weight:bold;line-height:32px;color:{INK}", "볼 만한 아이템")))
        o.append(_row(_t(f"padding:0 28px 10px;font-size:14px;line-height:20px;color:{MUTE}", f"한국에 드문 것 중 추천 수 상위 {len(picks)}개")))
        for i, it in enumerate(picks, 1):
            o.append(_card(it, i, i == 1))
    # 전체 목록
    o.append(_row(_t(f"padding:40px 28px 6px;font-size:26px;font-weight:bold;line-height:32px;color:{INK}", "전체 목록")))
    prev = None
    for it in items:
        if it["날짜"] != prev:
            prev = it["날짜"]
            pill = (f'<table {TBL}><tr>' + _t(f"border:1px solid {LINE};color:{INK};font-size:13px;font-weight:bold;line-height:18px;padding:6px 14px;border-radius:9999px",
                    f'{e(prev[5:].replace("-", "."))} · 미국 서부') + '</tr></table>')
            o.append(f'<tr><td style="padding:22px 28px 6px">{pill}</td></tr>')
        cell = (f'<a href="{e(it["링크"])}" style="font-family:{FONT};font-size:16px;font-weight:bold;color:{INK};text-decoration:none">{e(it["이름"])}</a>'
                f'<span style="font-family:{FONT};font-size:12px;color:{FAINT}">&nbsp;▲ {it["추천수"]}</span>'
                f'<br><span style="font-family:{FONT};font-size:14px;line-height:22px;color:{INK}">{e(it.get("한줄소개_ko") or it["한줄소개"])}</span>'
                f'<br><span style="font-family:{FONT};font-size:13px;line-height:20px;color:{MUTE}">{e(it["_c"])}</span>')
        row = (f'<table {TBL} width="100%" style="border-bottom:1px solid {LINE}"><tr>'
               + _t(f"padding:16px 0;font-size:14px;font-weight:bold;line-height:20px;color:{FAINT};vertical-align:top", f'{it["순위"]:02d}', 'width="30" valign="top"')
               + _t("padding:16px 12px 16px 0;font-size:14px;line-height:22px;vertical-align:top", cell, 'valign="top"')
               + f'<td width="60" valign="top" align="right" style="padding:17px 0;vertical-align:top">{_chip(it["_t"])}</td>'
               + '</tr></table>')
        o.append(f'<tr><td style="padding:0 28px">{row}</td></tr>')
    # 마무리 청록 띠
    o.append('<tr><td style="padding:36px 0 0;font-size:1px;line-height:1px">&nbsp;</td></tr>')
    foot = (f'<table {TBL} width="100%">'
            + _row(_t("font-size:21px;font-weight:bold;line-height:28px;color:#ffffff", "오늘 고를 아이템이 있나요?"))
            + _row(_t("padding-top:8px;font-size:14px;line-height:22px;color:#a9c6c6", "이름을 누르면 Product Hunt 원문으로 이동합니다. 한국 코멘트는 AI 추정(참고용)입니다."))
            + _row(_t(f"padding-top:16px;font-size:12px;line-height:18px;color:#7fa5a5;border-top:1px solid {TEAL2}", "Auto_PH · 개인 용도"))
            + '</table>')
    o.append('<tr>' + _t(f"background:{TEAL};padding:34px 32px;border-radius:0 0 16px 16px", foot, f'bgcolor="{TEAL}"') + '</tr>')
    o.append('</table></td></tr></table>')
    return "".join(o)
