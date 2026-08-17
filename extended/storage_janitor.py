"""storage/ 보존 정책. 24시간 생산 체제에서 없으면 반드시 디스크가 먼저 죽는다.

측정(2026-08-16, 이 저장소 실측):

    storage/cache_videos   835MB   ← Pexels 소재 캐시. 가장 빨리 부푼다
    storage/tasks          462MB   ← 태스크당 평균 57MB
    storage/local_videos    71MB

태스크 하나가 ~57MB 인데 그 절반이 **`combined-*.mp4`** 다. 이건 자막·음성을 입히기
전 중간 합성본이라 `final-*.mp4` 가 나온 뒤에는 쓸모가 없다. 하루 50편을 찍으면
2.8GB/일 이고, 그중 1.4GB/일 이 이 중간 파일이다.

정책은 셋으로 나눈다. 최종 결과물을 지우는 건 마지막 단계다.

  1. `--slim-days N`  N일 지난 태스크의 **중간 산출물만** 지운다(combined/audio/소재).
                      final-*.mp4 와 script.json 은 남는다 → 용량 절반이 즉시 회수된다
  2. `--purge-days M` M일 지난 태스크를 **통째로** 지운다
  3. `--cache-gb G`   소재 캐시가 G GB 를 넘으면 오래된 것부터 지운다(LRU)

기본은 **dry-run 이다.** 실제로 지우려면 `--apply` 를 붙여야 한다. 자동 스케줄에
걸 때도 처음 며칠은 dry-run 으로 무엇이 지워질지 보고 붙이는 걸 권한다.

    python -m extended.storage_janitor                       # 현황만
    python -m extended.storage_janitor --slim-days 3 --cache-gb 20
    python -m extended.storage_janitor --slim-days 3 --apply
"""
from __future__ import annotations

import argparse
import os
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORAGE = ROOT / "storage"
TASKS = STORAGE / "tasks"
CACHE = STORAGE / "cache_videos"

# 태스크 폴더에서 '지워도 되는' 것. final-*.mp4, script.json, *.srt 는 남긴다.
# combined 는 final 직전 단계라 final 이 있으면 필요 없다.
SLIM_PREFIXES = ("combined-",)
SLIM_NAMES = ("audio.mp3",)


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def dir_size(p: Path) -> int:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def age_days(p: Path) -> float:
    return (time.time() - p.stat().st_mtime) / 86400


def survey() -> None:
    print(f"storage: {STORAGE}")
    for sub in sorted(STORAGE.iterdir()) if STORAGE.exists() else []:
        if sub.is_dir():
            print(f"  {sub.name:24} {human(dir_size(sub))}")
    if TASKS.exists():
        tasks = [d for d in TASKS.iterdir() if d.is_dir()]
        if tasks:
            total = sum(dir_size(d) for d in tasks)
            print(f"\n태스크 {len(tasks)}개, 합계 {human(total)}, 평균 {human(total / len(tasks))}")
            oldest = max(tasks, key=age_days)
            print(f"가장 오래된 것: {oldest.name[:8]}… {age_days(oldest):.1f}일 전")


def slim(days: float, apply: bool) -> int:
    """오래된 태스크의 중간 산출물 제거. 최종물은 건드리지 않는다."""
    if not TASKS.exists():
        return 0
    freed = 0
    for d in sorted(TASKS.iterdir()):
        if not d.is_dir() or age_days(d) < days:
            continue
        finals = list(d.glob("final-*.mp4"))
        if not finals:
            # 최종물이 없는 태스크는 실패했거나 아직 도는 중이다. 손대지 않는다.
            continue
        for f in d.iterdir():
            if not f.is_file():
                continue
            if f.name.startswith(SLIM_PREFIXES) or f.name in SLIM_NAMES:
                size = f.stat().st_size
                freed += size
                print(f"  {'삭제' if apply else '삭제예정'} {d.name[:8]}…/{f.name} ({human(size)})")
                if apply:
                    f.unlink()
    return freed


def purge(days: float, apply: bool) -> int:
    if not TASKS.exists():
        return 0
    freed = 0
    for d in sorted(TASKS.iterdir()):
        if not d.is_dir() or age_days(d) < days:
            continue
        size = dir_size(d)
        freed += size
        print(f"  {'삭제' if apply else '삭제예정'} 태스크 {d.name[:8]}… 통째 ({human(size)})")
        if apply:
            shutil.rmtree(d)
    return freed


def trim_cache(limit_gb: float, apply: bool) -> int:
    """소재 캐시를 상한까지 줄인다. 오래 안 쓴 것부터.

    캐시는 지워도 다시 받으면 그만이라 가장 먼저 손대도 되는 영역이다.
    다만 Pexels API 호출이 늘어나므로 상한을 너무 낮게 잡지는 않는다.
    """
    if not CACHE.exists():
        return 0
    files = [f for f in CACHE.rglob("*") if f.is_file()]
    total = sum(f.stat().st_size for f in files)
    limit = limit_gb * 1024 ** 3
    if total <= limit:
        print(f"  캐시 {human(total)} ≤ 상한 {limit_gb}GB — 정리 불필요")
        return 0
    files.sort(key=lambda f: f.stat().st_atime)   # 오래 안 쓴 것부터
    freed = 0
    for f in files:
        if total - freed <= limit:
            break
        size = f.stat().st_size
        freed += size
        print(f"  {'삭제' if apply else '삭제예정'} 캐시 {f.name[:40]} ({human(size)})")
        if apply:
            f.unlink()
    return freed


def main() -> int:
    ap = argparse.ArgumentParser(prog="storage_janitor")
    ap.add_argument("--slim-days", type=float, help="N일 지난 태스크의 중간 산출물 제거")
    ap.add_argument("--purge-days", type=float, help="M일 지난 태스크 통째 제거")
    ap.add_argument("--cache-gb", type=float, help="소재 캐시 상한(GB)")
    ap.add_argument("--apply", action="store_true", help="실제로 삭제(기본은 dry-run)")
    args = ap.parse_args()

    survey()
    if not any((args.slim_days, args.purge_days, args.cache_gb)):
        print("\n(정리 옵션이 없어 현황만 출력했다. --slim-days 3 --cache-gb 20 등을 붙인다)")
        return 0

    print(f"\n{'=== 실제 삭제 ===' if args.apply else '=== dry-run (실제로 지우려면 --apply) ==='}")
    freed = 0
    if args.purge_days:
        freed += purge(args.purge_days, args.apply)
    if args.slim_days:
        freed += slim(args.slim_days, args.apply)
    if args.cache_gb:
        freed += trim_cache(args.cache_gb, args.apply)

    print(f"\n{'회수' if args.apply else '회수 예정'}: {human(freed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
