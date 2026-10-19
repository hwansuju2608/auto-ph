"""여러 블록이 같이 쓰는 도구: 열쇠 읽기, 실행기록 남기기, 미국 서부 날짜 계산."""
import os, datetime as dt

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "output")
os.makedirs(OUT, exist_ok=True)

def env(name):
    """열쇠를 읽는다. 깃허브 액션에서는 비밀 보관함(환경변수), 내 PC에서는 .env. 값은 화면에 찍지 않는다."""
    if os.environ.get(name):
        return os.environ[name].strip()
    path = os.path.join(BASE, ".env")
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                if k == name:
                    return v.strip()
    return ""

def log(block, ok, msg):
    """실행기록.txt에 한 줄 남긴다: 시각 | 블록 | 됨/막힘 | 내용"""
    now = (dt.datetime.utcnow() + dt.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")  # 한국 시각
    line = f"{now} | {block} | {'됨' if ok else '막힘'} | {msg}"
    print(line)
    with open(os.path.join(OUT, "실행기록.txt"), "a", encoding="utf-8") as f:
        f.write(line + "\n")

def _pt_offset(utc_now):
    """미국 서부(PT) 시차: 서머타임(3월 둘째 일요일~11월 첫째 일요일) -7, 아니면 -8."""
    y = utc_now.year
    def nth_sunday(month, n):
        d = dt.datetime(y, month, 1)
        d += dt.timedelta(days=(6 - d.weekday()) % 7)
        return d + dt.timedelta(weeks=n - 1)
    start = nth_sunday(3, 2) + dt.timedelta(hours=10)   # 2시 PT = 10시 UTC
    end = nth_sunday(11, 1) + dt.timedelta(hours=9)
    return -7 if start <= utc_now < end else -8

def pt_yesterday():
    """미국 서부 기준 '어제' 하루의 시작·끝(UTC 문자열)과 날짜."""
    utc_now = dt.datetime.utcnow()
    off = _pt_offset(utc_now)
    pt_today = (utc_now + dt.timedelta(hours=off)).date()
    day = pt_today - dt.timedelta(days=1)
    start = dt.datetime.combine(day, dt.time()) - dt.timedelta(hours=off)
    end = start + dt.timedelta(days=1)
    f = "%Y-%m-%dT%H:%M:%SZ"
    return day, start.strftime(f), end.strftime(f)


def pt_day_range(day, off):
    start = dt.datetime.combine(day, dt.time()) - dt.timedelta(hours=off)
    end = start + dt.timedelta(days=1)
    f = "%Y-%m-%dT%H:%M:%SZ"
    return start.strftime(f), end.strftime(f)

def target_days():
    """메일에 담을 미국 서부 날짜들.
    평일(한국) 아침 실행 기준: 화~금은 미국 어제 하루, 월요일은 미국 목·금·토 사흘
    (평일에만 받으면 비는 날이 없도록). 그 밖의 수동 실행은 어제 하루."""
    utc_now = dt.datetime.utcnow()
    off = _pt_offset(utc_now)
    yday = (utc_now + dt.timedelta(hours=off)).date() - dt.timedelta(days=1)
    kst_weekday = (utc_now + dt.timedelta(hours=9)).weekday()   # 0 = 월요일
    n = 3 if kst_weekday == 0 else 1
    days = [yday - dt.timedelta(days=i) for i in range(n - 1, -1, -1)]
    return [(d, *pt_day_range(d, off)) for d in days]
