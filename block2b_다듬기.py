"""다듬기 블록: 2_처리.json의 한국어 문장을 제미나이에게 한 번 더 보내 번역투 없이 자연스럽게 고친다.
   뜻·사실은 바꾸지 않는다. 실패해도 다듬기 전 문장으로 다음 단계를 계속한다 (메일이 안 오는 일은 없게)."""
import json, os, shutil
from common import env, log, OUT
from block2_처리 import call, MODELS, LITE

FIELDS = ["번호", "한줄소개_ko", "설명_ko", "무엇_ko", "기능_ko", "가격_ko", "소개글_ko", "반응_ko", "한국코멘트"]

PROMPT = """당신은 IT 기사를 다듬는 한국어 편집자입니다. 아래 JSON은 영어를 한국어로 옮긴 글입니다.
각 문장을 한국 사람이 처음부터 한국어로 쓴 것처럼 자연스럽게 고쳐 주세요.
- 번역투 없애기: "~를 가능하게 합니다", "~에 의해", "~하는 것을 돕습니다", "그것은", 지나친 "~들" 같은 직역 말투
- 영어 어순을 한국어 어순으로, 긴 문장은 읽기 쉽게
- 굳이 안 써도 되는 외래어는 쉬운 우리말로 (단, 서비스·회사 이름과 널리 쓰는 IT 용어는 그대로)
- 끝맺음은 "~합니다/~입니다" 존댓말로 통일. 기능_ko·좋은점·아쉬운점은 짧은 명사구 그대로
- 뜻과 사실은 바꾸지 말 것. 내용을 더하거나 빼지 말 것. 숫자·이름은 그대로
- 한국코멘트 맨 앞의 [있음]/[드묾]/[모름] 표시는 글자 그대로 남길 것
- 빈 값은 빈 값 그대로
받은 것과 똑같은 구조(같은 키, 같은 개수)의 JSON 배열로만 답하세요.

글:
"""

def main():
    src = os.path.join(OUT, "2_처리.json")
    if not os.path.exists(src):
        log("다듬기", False, "2_처리.json이 없음 (처리 블록부터)"); return False
    key = env("GEMINI_API_KEY")
    data = json.load(open(src, encoding="utf-8"))
    shutil.copy(src, os.path.join(OUT, "2_처리_다듬기전.json"))   # 비교용
    fixed, errs = 0, []
    for day in sorted({it["날짜"] for it in data["목록"]}):
        part = [{k: it.get(k, "") for k in FIELDS} for it in data["목록"] if it["날짜"] == day]
        text = None
        for model in MODELS + [LITE]:
            try:
                text = call(key, model, PROMPT + json.dumps(part, ensure_ascii=False)); break
            except Exception as e:
                errs.append(f"{model}: {e}")
        if not text:
            continue
        try:
            res = {int(r["번호"]): r for r in json.loads(text)}
        except Exception as e:
            errs.append(f"답 읽기 실패: {e}"); continue
        for it in data["목록"]:
            r = res.get(it["번호"])
            if not r:
                continue
            for k in FIELDS[1:]:
                v = r.get(k)
                if k == "한국코멘트" and v and not v.startswith(it.get("한국코멘트", "")[:4]):
                    continue          # [있음]/[드묾]/[모름] 표시가 바뀌면 원래 문장 유지
                if v or v == []:
                    it[k] = v
            fixed += 1
    with open(src, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if fixed == 0:
        log("다듬기", True, "다듬기 못 함 — 다듬기 전 문장으로 계속 (" + ", ".join(errs)[:200] + ")")
    else:
        log("다듬기", True, f"{fixed}개 문장 다듬음")
    return True   # 실패해도 메일은 보낸다

if __name__ == "__main__":
    main()
