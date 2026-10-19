"""결과 블록: 2_처리.json으로 메일 본문(output/3_메일.html)을 만들고 Gmail로 나에게 보낸다.
   --미리보기 를 붙이면 보내지 않고 메일 파일만 만든다."""
import json, os, sys, smtplib, html
from email.mime.text import MIMEText
from email.header import Header
from common import env, log, OUT

from mail_design_superhuman import build   # 메일 디자인: Superhuman 스타일 (mail_design_superhuman.py)

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
