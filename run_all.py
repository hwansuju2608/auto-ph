"""시작 블록: 자료 → 처리 → 페이지 → 결과를 차례로 돌린다. 한 블록이 막히면 거기서 멈춘다."""
import sys
import block1_자료, block2_처리, block3_결과, block4_페이지
from common import log

log("시작", True, "실행 시작")
for name, step in [("자료", block1_자료.main), ("처리", block2_처리.main), ("페이지", block4_페이지.main), ("결과", block3_결과.main)]:
    if not step():
        log("시작", False, f"{name} 블록에서 멈춤 — output/실행기록.txt 확인")
        sys.exit(1)   # 깃허브에 "실패"로 표시 → 깃허브가 실패 알림 메일을 보냄
else:
    log("시작", True, "끝까지 됨")
