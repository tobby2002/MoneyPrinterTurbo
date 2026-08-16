"""다국어 복제 매트릭스.

`plan/next_gen_realtime_ai_shortform_factory.md` 3번(Global Multi-Language Engine)의
실제 구현 가능한 부분이다. 문서는 "1초 만에 5개 언어로 복제"라고 썼지만, 실제로
1초에 되는 건 파라미터 교체뿐이다. 렌더는 언어 수만큼 다시 돈다. 그래서 여기서
정직하게 다루는 것은 셋이다.

  1. 언어별 TTS 보이스와 폰트 (틀리면 자막이 두부로 깨진다)
  2. 언어별 발화 속도(초당 문자수). 같은 뜻의 문장도 길이가 다르므로
     35초 영상을 맞추려면 언어마다 목표 글자수가 달라야 한다.
  3. 자막 줄바꿈 폭. CJK 와 라틴 문자는 한 줄에 들어가는 글자수가 다르다.

번역 자체는 여기서 하지 않는다. 번역은 '무엇을 말할까'라서 RunchPie 엔진의
로컬 워커 몫이다. 이 파일은 '어떻게 들리고 보일까'만 결정한다.

    python -m extended.lang_matrix --list
    python -m extended.lang_matrix ja --seconds 35
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class LangProfile:
    code: str            # RunchPie 캠페인 yaml 의 lang 값
    bcp47: str           # MPT video_language
    label: str
    voice_male: str
    voice_female: str
    font_name: str
    #: TTS 가 1초에 읽는 문자 수(실측 근사). 목표 길이 계산에 쓴다.
    chars_per_sec: float
    #: 자막 한 줄 권장 최대 문자수(9:16 세로, font_size 56~60 기준).
    subtitle_line_chars: int
    note: str = ""


PROFILES: dict[str, LangProfile] = {
    "ko": LangProfile(
        "ko", "ko-KR", "한국어",
        "ko-KR-InJoonNeural-Male", "ko-KR-SunHiNeural-Female",
        "AppleGothic.ttf", 4.5, 18,
        "기준 언어. 대본은 항상 여기서 먼저 나온다.",
    ),
    "en": LangProfile(
        "en", "en-US", "영어",
        "en-US-AndrewMultilingualNeural-Male", "en-US-AvaMultilingualNeural-Female",
        "NotoSansGothic-Regular.ttf", 14.0, 38,
        "같은 내용이라도 한국어 대비 글자수가 3배 가까이 늘어난다.",
    ),
    "ja": LangProfile(
        "ja", "ja-JP", "일본어",
        "ja-JP-KeitaNeural-Male", "ja-JP-NanamiNeural-Female",
        "NotoSansGothic-Regular.ttf", 5.0, 20,
        "가나가 섞이면 실제 문자수가 늘어난다. 목표치를 10% 여유 있게 잡는다.",
    ),
    "es": LangProfile(
        "es", "es-ES", "스페인어",
        "es-ES-AlvaroNeural-Male", "es-ES-ElviraNeural-Female",
        "NotoSansGothic-Regular.ttf", 13.0, 36,
    ),
    "id": LangProfile(
        "id", "id-ID", "인도네시아어",
        "id-ID-ArdiNeural-Male", "id-ID-GadisNeural-Female",
        "NotoSansGothic-Regular.ttf", 12.5, 36,
        "경쟁이 가장 옅은 언어권. 초기 채널 실험용으로 값이 싸다.",
    ),
}


def get(code: str) -> LangProfile:
    try:
        return PROFILES[code]
    except KeyError:
        raise KeyError(f"미지원 언어: {code}. 가능: {', '.join(PROFILES)}") from None


def target_chars(code: str, seconds: int) -> tuple[int, int]:
    """해당 언어로 `seconds` 초를 채우는 대본 길이 하한/상한."""
    p = get(code)
    center = p.chars_per_sec * seconds
    return int(center * 0.85), int(center * 1.25)


def to_video_params(code: str, *, gender: str = "male") -> dict:
    p = get(code)
    return {
        "video_language": p.bcp47,
        "voice_name": p.voice_female if gender == "female" else p.voice_male,
        "font_name": p.font_name,
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="lang_matrix")
    ap.add_argument("lang", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--seconds", type=int, default=35)
    ap.add_argument("--gender", default="male", choices=["male", "female"])
    args = ap.parse_args()

    if args.list or not args.lang:
        for code, p in PROFILES.items():
            lo, hi = target_chars(code, args.seconds)
            print(f"{code:3} {p.label:8} {p.voice_male:42} {args.seconds}초 = {lo}~{hi}자")
        return 0

    p = get(args.lang)
    lo, hi = target_chars(args.lang, args.seconds)
    out = asdict(p) | {
        "target_chars": [lo, hi],
        "video_params": to_video_params(args.lang, gender=args.gender),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
