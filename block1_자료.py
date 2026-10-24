"""자료 블록: Product Hunt에서 미국 서부 기준 대상 날짜(평일 어제, 월요일은 목·금·토)별 상위 10개를 가져와 output/1_자료.json에 남긴다."""
import json, os, re, html, urllib.request
from common import env, log, target_days, OUT

TOP_N = 10  # 날짜별 상위 개수

QUERY = """
query($after: DateTime!, $before: DateTime!, $n: Int!) {
  posts(order: VOTES, postedAfter: $after, postedBefore: $before, first: $n) {
    edges { node { name tagline description votesCount url website
      topics(first: 3) { edges { node { name } } }
      commentsCount thumbnail { url } media { url type }
      comments(first: 10, order: VOTES_COUNT) { edges { node { body votesCount } } } } }
  }
}"""

def _clean(t, n):
    t = html.unescape(re.sub(r"<[^>]+>", "", t or ""))
    t = re.sub(r"https?://\S+", "", t)
    return re.sub(r"\n{2,}", "\n", t).strip()[:n]

def _comments(n):
    """추천 많은 댓글 10개. 그중 가장 긴 것 = 대개 만든 사람의 소개글."""
    bodies = [c["node"]["body"] or "" for c in (n.get("comments") or {}).get("edges", [])]
    maker = _clean(max(bodies, key=len), 1500) if bodies else ""
    others = [_clean(b, 400) for b in bodies if _clean(b, 1500) != maker and b.strip()]
    return maker, others

def _images(n):
    """대표 사진 최대 3장 (영상 제외)."""
    imgs = [m["url"] for m in (n.get("media") or []) if m.get("type") == "image" and m.get("url")]
    if not imgs and (n.get("thumbnail") or {}).get("url"):
        imgs = [n["thumbnail"]["url"]]
    return imgs[:3]

def main():
    token = env("PH_TOKEN")
    if not token:
        log("자료", False, ".env에 PH_TOKEN이 비어 있음"); return False
    items, days = [], []
    for day, after, before in target_days():
        body = json.dumps({"query": QUERY, "variables": {"after": after, "before": before, "n": TOP_N}}).encode()
        req = urllib.request.Request("https://api.producthunt.com/v2/api/graphql", data=body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                     "Accept": "application/json", "User-Agent": "Auto_PH"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.load(r)
        except Exception as e:
            log("자료", False, f"Product Hunt 연결 실패: {e}"); return False
        if "errors" in data:
            log("자료", False, f"Product Hunt 오류: {data['errors']}"); return False
        got = 0
        for i, e in enumerate(data["data"]["posts"]["edges"], 1):
            n = e["node"]
            items.append({"번호": len(items) + 1, "날짜": str(day), "순위": i, "이름": n["name"],
                          "한줄소개": n["tagline"], "설명": (n.get("description") or "").strip(),
                          "메이커글": _comments(n)[0], "댓글들": _comments(n)[1],
                          "댓글수": n.get("commentsCount") or 0, "사진": _images(n),
                          "사이트": n.get("website") or "",
                          "추천수": n["votesCount"],
                          "태그": [t["node"]["name"] for t in n["topics"]["edges"]],
                          "링크": n["url"]})
            got += 1
        days.append(str(day))
        log("자료", True, f"{day} 상위 {got}개 가져옴")
    if not items:
        log("자료", False, f"{', '.join(days)} 목록이 비어 있음"); return False
    with open(os.path.join(OUT, "1_자료.json"), "w", encoding="utf-8") as f:
        json.dump({"날짜들": days, "목록": items}, f, ensure_ascii=False, indent=2)
    return True

if __name__ == "__main__":
    main()
