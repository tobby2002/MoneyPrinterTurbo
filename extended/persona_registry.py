"""채널별 시그니처 페르소나 레지스트리.

`plan/next_gen_realtime_ai_shortform_factory.md` 의 4번(AI Virtual Persona Host)을
지금 있는 것만으로 구현한 것이다. 페르소나 = 목소리 + 말 속도 + 컷 템포 +
자막 스타일의 묶음이고, 이 넷은 전부 MoneyPrinterTurbo VideoParams 로 표현된다.
따로 학습하거나 모델을 붙일 것이 없다.

왜 MPT 쪽에 두는가:
    페르소나는 '어떻게 들리고 보이는가'다. 픽셀과 오디오를 만지는 결정은 전부
    렌더 팜(MPT)이 소유한다. '무엇을 언제 왜 만드는가'는 RunchPie 엔진 소유다.
    이 선을 지키면 두 저장소가 서로를 import 하지 않고도 같이 돈다.

RunchPie 엔진과의 연결:
    엔진은 MPT 코드를 import 하지 않는다(다른 저장소·다른 venv). 대신 이 파일이
    캠페인 yaml 에 붙일 options 블록을 찍어 준다.

        python -m extended.persona_registry --list
        python -m extended.persona_registry knowledge_docu --yaml

    출력물을 engine/campaigns/<id>.yaml 의 shorts_mpt 채널 options 에 붙인다.
    사람이 한 번 복사하는 대신, 두 저장소가 런타임에 묶이지 않는다.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass(frozen=True)
class Persona:
    id: str
    label: str
    #: Azure/Edge TTS 보이스. MPT 는 "<voice>-<Gender>" 표기를 쓴다.
    voice_name: str
    #: 1.0 이 기본. 0.9 는 묵직하게, 1.15 는 텐션 있게.
    voice_rate: float
    #: 컷 길이(초). 'auto' 면 tempo_controller 가 문장을 보고 정한다.
    clip_duration: float | str
    font_name: str
    font_size: int
    subtitle_position: str
    text_fore_color: str
    stroke_width: float
    bgm_volume: float
    #: 대본 작가(RunchPie 로컬 워커)에게 넘길 톤 지시문. 렌더에는 쓰이지 않는다.
    tone: str
    notes: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


PERSONAS: dict[str, Persona] = {
    "marketing_sharp": Persona(
        id="marketing_sharp",
        label="마케팅 / 제품 (cyaix·RunchPie)",
        voice_name="ko-KR-InJoonNeural-Male",
        voice_rate=1.05,
        clip_duration=3,
        font_name="AppleGothic.ttf",
        font_size=58,
        subtitle_position="bottom",
        text_fore_color="#FFFFFF",
        stroke_width=1.5,
        bgm_volume=0.15,
        tone="실제로 돌려본 사람의 톤. 수치를 먼저 말하고 판단은 시청자에게 맡긴다. "
             "과장·수익 보장 표현 금지.",
        notes="BGM 을 낮게 깐다. 숫자가 묻히면 이 페르소나는 실패한다.",
    ),
    "hype_gen_z": Persona(
        id="hype_gen_z",
        label="유머 / 썰 (텐션형)",
        voice_name="ko-KR-SunHiNeural-Female",
        voice_rate=1.18,
        clip_duration=2,
        font_name="AppleSDGothicNeo.ttc",
        font_size=66,
        subtitle_position="center",
        text_fore_color="#FFE94A",
        stroke_width=2.5,
        bgm_volume=0.28,
        tone="말이 빠르고 문장이 짧다. 첫 문장에서 바로 사건이 터진다.",
        notes="컷 2초 고정. 자막을 중앙에 크게 — 소리 없이 보는 시청자가 다수다.",
    ),
    "knowledge_docu": Persona(
        id="knowledge_docu",
        label="지식 / 미스터리 (다큐 성우)",
        voice_name="ko-KR-HyunsuMultilingualNeural-Male",
        voice_rate=0.92,
        clip_duration=5,
        font_name="AppleMyungjo.ttf",
        font_size=56,
        subtitle_position="bottom",
        text_fore_color="#EDEDED",
        stroke_width=1.2,
        bgm_volume=0.22,
        tone="낮고 느리게. 한 문장에 사실 하나만. 마지막 문장은 여운을 남긴다.",
        notes="컷이 길어 소재가 적게 든다. Pexels 쿼터가 빠듯할 때 유리하다.",
    ),
    "global_neutral": Persona(
        id="global_neutral",
        label="글로벌 (영어 중립 나레이션)",
        voice_name="en-US-AndrewMultilingualNeural-Male",
        voice_rate=1.0,
        clip_duration="auto",
        font_name="NotoSansGothic-Regular.ttf",
        font_size=54,
        subtitle_position="bottom",
        text_fore_color="#FFFFFF",
        stroke_width=1.5,
        bgm_volume=0.2,
        tone="Plain, factual, no hype. Numbers first.",
        notes="다국어 복제의 기준 페르소나. lang_matrix 와 함께 쓴다.",
    ),
}


def get(persona_id: str) -> Persona:
    try:
        return PERSONAS[persona_id]
    except KeyError:
        raise KeyError(
            f"알 수 없는 페르소나: {persona_id}. 가능한 값: {', '.join(PERSONAS)}"
        ) from None


def to_video_params(persona_id: str, **overrides: Any) -> dict[str, Any]:
    """MPT VideoParams 에 그대로 얹을 수 있는 dict. tone/notes 는 뺀다."""
    p = get(persona_id)
    params = {
        "voice_name": p.voice_name,
        "voice_rate": p.voice_rate,
        "video_clip_duration": p.clip_duration,
        "font_name": p.font_name,
        "font_size": p.font_size,
        "subtitle_position": p.subtitle_position,
        "text_fore_color": p.text_fore_color,
        "stroke_width": p.stroke_width,
        "bgm_volume": p.bgm_volume,
    }
    params.update(overrides)
    return params


def to_campaign_yaml(persona_id: str) -> str:
    """RunchPie engine/campaigns/<id>.yaml 의 shorts_mpt options 블록."""
    p = get(persona_id)
    lines = [
        f"      # persona: {p.id} — {p.label}",
        f"      # {p.notes}" if p.notes else "",
        f"      voice_name: {p.voice_name}",
        f"      voice_rate: {p.voice_rate}",
        f"      clip_duration: {p.clip_duration}",
        f"      font_name: {p.font_name}",
        f"      font_size: {p.font_size}",
        f"      subtitle_position: {p.subtitle_position}",
        f'      text_color: "{p.text_fore_color}"',
        f"      stroke_width: {p.stroke_width}",
        f"      bgm_volume: {p.bgm_volume}",
        f'      tone: "{p.tone}"',
    ]
    return "\n".join(ln for ln in lines if ln)


def main() -> int:
    ap = argparse.ArgumentParser(prog="persona_registry")
    ap.add_argument("persona", nargs="?", help="페르소나 id")
    ap.add_argument("--list", action="store_true", help="목록 출력")
    ap.add_argument("--yaml", action="store_true", help="캠페인 yaml 블록 출력")
    ap.add_argument("--json", action="store_true", help="VideoParams JSON 출력")
    args = ap.parse_args()

    if args.list or not args.persona:
        for pid, p in PERSONAS.items():
            clip = p.clip_duration if isinstance(p.clip_duration, str) else f"{p.clip_duration}s"
            print(f"{pid:18} {p.label}  ({p.voice_name}, clip={clip})")
        return 0
    if args.yaml:
        print(to_campaign_yaml(args.persona))
    elif args.json:
        print(json.dumps(to_video_params(args.persona), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(asdict(get(args.persona)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
