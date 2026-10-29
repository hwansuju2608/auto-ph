"""처리 블록: 1_자료.json을 읽어 Gemini로 한줄소개·설명·태그를 한국어로 번역하고 한국 유사 서비스 코멘트를 붙여 output/2_처리.json에 남긴다."""
import json, os, re, time, urllib.request, urllib.error
from common import env, log, OUT

API = "https://generativelanguage.googleapis.com/v1beta"

PROMPT = """아래는 Product Hunt 상위 서비스 목록(JSON)입니다.
각 서비스마다 다음을 한국어로 써 주세요.
- 한줄소개_ko: "한줄소개"를 자연스러운 한국어로 번역
- 설명_ko: "설명"을 자연스러운 한국어로 번역 (설명이 비어 있으면 빈 문자열)
- 태그_ko: "태그" 각각을 한국어로 번역한 배열 (순서 유지)
- 무엇_ko: 이 서비스가 무엇을 하는지 IT 비전공자도 바로 알게 쉬운 한국어 2문장.
  "누가 쓰는지 / 무엇을 넣거나 연결하면 / 무엇을 해 주는지"가 드러나게. 광고 문구·비유 대신 실제 하는 일을 쓰세요.
  어려운 용어(API, MCP, CLI 등)는 괄호로 짧게 풀어 주세요.
- 기능_ko: 주요 기능 2~3개, 각각 15자 안팎의 짧은 명사구 배열 (근거 없으면 빈 배열)
- 가격_ko: 무료/유료/무료+유료 등 값 정보. "한줄소개"·"설명"·"메이커글"에 적힌 경우만, 없으면 빈 문자열
- 소개글_ko: "메이커글"(만든 사람이 쓴 소개)을 한국어로 3~5문장 요약. 왜 만들었는지와 무엇이 다른지 중심. 비어 있으면 빈 문자열
- 반응_ko: "댓글들"(다른 사용자 댓글)을 읽고 정리한 객체 {"요약":"반응 한두 문장","좋은점":["짧게",...],"아쉬운점":["짧게",...]}
  좋은점·아쉬운점은 각각 최대 3개. 축하·인사만 있는 댓글은 빼고, 댓글이 없거나 내용이 없으면 {"요약":"","좋은점":[],"아쉬운점":[]}
- 한국코멘트: 한국 시장 관점의 한 문장. 아래 셋 중 하나로 시작하세요.
  "[있음]" 같은 분야의 한국 서비스를 확실히 아는 경우 — 실제로 아는 이름만 1~2개 (예: 전자서명 → 모두싸인)
  "[드묾]" 같은 분야 한국 서비스가 떠오르지 않는 경우 — 어떤 분야인지와 한국에서 기회가 될 만한 점을 짧게
  "[모름]" 하드웨어·자동차처럼 비교가 어려운 경우 — 이유를 짧게
  확실히 모르는 서비스 이름은 절대 지어내지 마세요.
무엇_ko·기능_ko·가격_ko는 "한줄소개"·"설명"·"메이커글"(만든 사람의 소개글)에 있는 내용만 근거로 쓰고, 없는 내용을 지어내지 마세요.
번역에 없는 내용을 덧붙이지 마세요.
반드시 JSON 배열로만 답하세요: [{"번호":1,"한줄소개_ko":"...","설명_ko":"...","무엇_ko":"...","기능_ko":["..."],"가격_ko":"","태그_ko":["..."],"소개글_ko":"...","반응_ko":{"요약":"...","좋은점":["..."],"아쉬운점":["..."]},"한국코멘트":"..."}, ...]

목록:
"""

def call(key, model, text):
    """Gemini에 한 번 묻는다."""
    body = json.dumps({"contents": [{"parts": [{"text": text}]}],
                       "generationConfig": {"responseMimeType": "application/json"}}).encode()
    req = urllib.request.Request(f"{API}/models/{model}:generateContent", data=body,
        headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        d = json.load(r)
    return d["candidates"][0]["content"]["parts"][0]["text"]

def parse(text):
    """Gemini 답(JSON)을 읽는다. 끝에 쉼표가 남는 등 살짝 깨진 경우 고쳐서 한 번 더 읽는다."""
    try:
        rows = json.loads(text)
    except Exception:
        rows = json.loads(re.sub(r",\s*([\]}])", r"\1", text))
    if not isinstance(rows, list):
        raise ValueError("답이 목록(JSON 배열)이 아님")
    return rows

# 무료 등급에서 쓸 수 있는 모델을 앞에서부터 차례로 시도한다.
MODELS = ["gemini-3.5-flash", "gemini-3.8-flash"]   # 좋은 모델 먼저 (두 번까지 시도)
LITE = "gemini-flash-lite-latest"                    # 그래도 안 되면 마지막 수단
FIELDS = ["번호", "이름", "한줄소개", "설명", "메이커글", "댓글들", "태그"]
WAIT = 300          # 한 바퀴(4번 시도)가 모두 실패하면 5분 쉬고 한 바퀴 더 (10/27 제미나이 몰림으로 메일이 안 옴)
DEADLINE = 8 * 60   # 처리 블록이 이미 8분 넘게 돌았으면 한 바퀴 더는 하지 않음 (깃허브 30분 제한 안에 "막힘"을 남기려고)

def ask(key, part, errs):
    """한 바퀴: 4번까지 묻는다 (마지막 두 번은 가벼운 모델). 성공하면 (답, 모델), 아니면 (None, None)."""
    for attempt in range(4):           # 답이 깨져 있어도 다시 물어본다
        cand = MODELS if attempt < 2 else [LITE]
        for model in cand:
            try:
                return parse(call(key, model, PROMPT + json.dumps(part, ensure_ascii=False))), model
            except urllib.error.HTTPError as e:
                errs.append(f"{model}: HTTP {e.code}")
            except Exception as e:
                errs.append(f"{model}: 답을 읽지 못함 {e}")
        if attempt < 3:
            time.sleep(30)
    return None, None

def main():
    key = env("GEMINI_API_KEY")
    if not key:
        log("처리", False, ".env에 GEMINI_API_KEY가 비어 있음"); return False
    src = os.path.join(OUT, "1_자료.json")
    if not os.path.exists(src):
        log("처리", False, "1_자료.json이 없음 (자료 블록부터)"); return False
    data = json.load(open(src, encoding="utf-8"))
    used, res = set(), {}
    start, retried = time.monotonic(), False
    days = sorted({it["날짜"] for it in data["목록"]})
    for day in days:                       # 날짜별로 나눠 보내 응답을 짧게
        part = [{k: it.get(k, "") for k in FIELDS} for it in data["목록"] if it["날짜"] == day]
        errs = []
        rows, model = ask(key, part, errs)
        if rows is None and not retried and time.monotonic() - start < DEADLINE:
            retried = True                 # 한 번 실행에 한 바퀴 더는 한 번만 (월요일 사흘 치도)
            log("처리", True, f"{day} 한 바퀴 모두 실패 — 5분 쉬고 한 바퀴 더")
            time.sleep(WAIT)
            rows, model = ask(key, part, errs)
        if rows is None:
            log("처리", False, f"Gemini 실패 ({day}): " + ", ".join(errs)); return False
        if errs:
            log("처리", True, f"{day} 재시도 끝에 성공 ({model}) — 앞선 실패: " + ", ".join(errs)[:300])
        for r in rows:
            res[int(r["번호"])] = r
        used.add(model)
    for it in data["목록"]:
        r = res.get(it["번호"], {})
        it["한줄소개_ko"] = r.get("한줄소개_ko", "")
        it["설명_ko"] = r.get("설명_ko", "")
        it["태그_ko"] = r.get("태그_ko", [])
        it["무엇_ko"] = r.get("무엇_ko", "")
        it["기능_ko"] = r.get("기능_ko", [])
        it["가격_ko"] = r.get("가격_ko", "")
        it["소개글_ko"] = r.get("소개글_ko", "")
        it["반응_ko"] = r.get("반응_ko") or {}
        it["한국코멘트"] = r.get("한국코멘트", "(코멘트 없음)")
    model = ", ".join(sorted(used))
    data["모델"] = model
    with open(os.path.join(OUT, "2_처리.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log("처리", True, f"{len(data['목록'])}개 번역·코멘트 붙임 ({model})")
    return True

if __name__ == "__main__":
    main()
