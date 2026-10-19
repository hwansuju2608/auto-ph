"""결과 블록: 2_처리.json으로 메일 본문(output/3_메일.html)을 만들고 Gmail로 나에게 보낸다.
   --미리보기 를 붙이면 보내지 않고 메일 파일만 만든다."""
import json, os, sys, smtplib, html
from email.mime.text import MIMEText
from email.header import Header
from common import env, log, OUT

def build(data):
    rows = []
    def pair(ko, en, size):
        if not (ko or en):
            return ""
        return (f'<div style="font-size:{size}px;margin-top:6px">{html.escape(ko or en)}</div>'
                f'<div style="font-size:11px;color:#9b9a97;margin-top:1px">{html.escape(en)}</div>')
    prev = None
    for it in data["목록"]:
        if it["날짜"] != prev:
            prev = it["날짜"]
            rows.append(f'<div style="background:#000;color:#76b900;font-weight:700;font-size:13px;padding:6px 12px;margin:18px 0 10px">■ {prev} (미국 서부)</div>')
        tags_ko = " · ".join(it.get("태그_ko") or it["태그"])
        tags_en = " · ".join(it["태그"])
        rows.append(f"""
<div style="border:1px solid #e9e9e7;border-radius:8px;padding:14px 16px;margin:0 0 12px">
  <div style="font-size:16px;font-weight:700">{it['순위']}. <a href="{html.escape(it['링크'])}" style="color:#37352f">{html.escape(it['이름'])}</a>
    <span style="font-size:12px;color:#787774;font-weight:400"> ▲ {it['추천수']}</span></div>
  {pair(it.get('한줄소개_ko'), it['한줄소개'], 14)}
  {pair(it.get('설명_ko'), it.get('설명', ''), 13)}
  <div style="font-size:13px;background:#fdecc8;border-radius:4px;padding:4px 8px;display:inline-block;margin-top:8px">🇰🇷 {html.escape(it['한국코멘트'])}</div>
  {pair(tags_ko, tags_en, 12)}
</div>""")
    return f"""<div style="font-family:'Malgun Gothic',sans-serif;max-width:640px;color:#37352f">
<h2 style="margin:0 0 4px">Product Hunt 날짜별 상위 10</h2>
<div style="color:#9b9a97;font-size:12px;margin-bottom:16px">미국 서부 기준 {' · '.join(data['날짜들'])} · 한국 코멘트는 AI 추정(참고용)</div>
{''.join(rows)}
<div style="color:#9b9a97;font-size:11px">Auto_PH · 개인 용도</div></div>"""

def main(preview=False):
    src = os.path.join(OUT, "2_처리.json")
    if not os.path.exists(src):
        log("결과", False, "2_처리.json이 없음 (처리 블록부터)"); return False
    data = json.load(open(src, encoding="utf-8"))
    body = build(data)
    with open(os.path.join(OUT, "3_메일.html"), "w", encoding="utf-8") as f:
        f.write(body)
    d = data['날짜들']
    when = d[0] if len(d) == 1 else f"{d[0]}~{d[-1]}"
    subject = f"[PH 상위10] {when} · {data['목록'][0]['이름']} 외 {len(data['목록']) - 1}개"
    if preview:
        log("결과", True, f"메일 미리보기만 만듦 (제목: {subject})"); return True
    addr, pw = env("GMAIL_ADDRESS"), env("GMAIL_APP_PASSWORD").replace(" ", "")
    if not addr or not pw:
        log("결과", False, ".env에 Gmail 주소나 앱 비밀번호가 비어 있음"); return False
    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = addr
    msg["To"] = addr
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s:
            s.login(addr, pw)
            s.send_message(msg)
    except Exception as e:
        log("결과", False, f"메일 발송 실패: {e}"); return False
    log("결과", True, f"메일 보냄 (제목: {subject})")
    return True

if __name__ == "__main__":
    main(preview="--미리보기" in sys.argv)
