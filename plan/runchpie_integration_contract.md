# RunchPie ↔ MoneyPrinterTurbo 통합 계약

작성 2026-08-15. 상대 저장소: `~/workspace/prt_runchpie_ai`.

## 이 저장소의 역할

**렌더 팜이다.** 대본을 받아 mp4 로 만든다. 그게 전부다.

캠페인·스케줄·쿼터·발행 이력 같은 개념을 이 저장소에 넣지 않는다. 그건 RunchPie
엔진(`prt_runchpie_ai/engine`)이 소유하는 상태다. 이 선을 지키는 이유는 실용적이다 —
MPT 는 업스트림(harry0703)이 활발해서, 오케스트레이션 개념을 코어에 섞으면 릴리스마다
병합 지옥이 온다. 커스텀은 전부 `extended/` 안에 격리한다(`extended/README.md` 규칙).

```
[ RunchPie 엔진 ]  무엇을 언제 왜         상태 소유(state.db)
        │  POST /api/v1/videos          ← 이 HTTP 한 줄이 두 저장소의 유일한 연결
        ▼  GET  /api/v1/tasks/{id}
[ MoneyPrinterTurbo ]  어떻게 보이고 들리는가    stateless 잡 워커
```

RunchPie 는 이 저장소의 코드를 **import 하지 않는다.** 다른 venv 이고 다른 릴리스
주기이기 때문이다. 반대로 이 저장소는 RunchPie 의 존재를 몰라도 된다.

## 호출 계약

RunchPie 쪽 구현: `engine/runchpie_engine/publish/shorts_mpt.py`

- `POST /api/v1/videos` — VideoParams. RunchPie 가 채우는 필드:
  `video_subject`(제목), `video_script`(대본 전문), `video_terms`(키워드),
  `video_aspect`, `video_clip_duration`, `video_language`, `voice_name`, `voice_rate`,
  `font_name`, `font_size`, `subtitle_position`, `text_fore_color`, `stroke_*`,
  `bgm_type`, `bgm_volume`, `video_source`, `n_threads`
- `GET /api/v1/tasks/{task_id}` — `state`: `4`=처리중, `1`=완료, `-1`=실패.
  완료 시 `videos[0]` 을 결과로 쓴다.
- `429` 는 큐 포화. RunchPie 는 실패로 기록하되 다음 주기에 재시도한다.

**업로드는 이 계약에 없다.** MPT 의 `upload_post_*` 설정은 꺼 둔다. 렌더된 mp4 를
사람이 확인하고 게시한다. 자동 업로드는 밴 한 번에 채널이 사라지는 비대칭 위험이라,
승인 큐 UI 가 붙기 전까지는 열지 않는다.

## 이 저장소가 소유하는 확장

| 모듈 | plan 문서 | 하는 일 |
|---|---|---|
| `extended/tempo_controller.py` | next_gen §Phase1 | 문장 긴장도 → 컷 길이(2.0/3.5/5.0s) |
| `extended/persona_registry.py` | next_gen §4 | 채널별 페르소나 = 보이스+속도+컷템포+자막스타일 |
| `extended/lang_matrix.py` | next_gen §3 | 언어별 보이스·폰트·발화속도·자막 폭 |
| `extended/storage_janitor.py` | (24시간 운영 필수) | 보존 정책. 태스크 중간물·소재 캐시 정리 |

두 신규 모듈은 RunchPie 캠페인 yaml 에 붙일 블록을 찍어 준다. 사람이 한 번 복사한다.

```bash
python -m extended.persona_registry --list
python -m extended.persona_registry marketing_sharp --yaml   # 캠페인 yaml 블록
python -m extended.lang_matrix --list --seconds 35            # 언어별 목표 대본 길이
python -m extended.lang_matrix ja --seconds 35                # 상세 JSON
```

`lang_matrix` 가 번역을 하지 않는 건 의도다. 번역은 '무엇을 말할까'라서 RunchPie 의
로컬 워커 몫이고, 여기는 '어떻게 들릴까'만 정한다.

## 24시간 무한 생산 체제에서의 이 저장소 (2026-08-16)

RunchPie 엔진이 **생산과 발행을 분리**했다. 대본은 재고에 쌓이고, 렌더 잡은 발행
단계에서 쿼터만큼만 나간다. MPT 입장에서 달라지는 것은 둘이다.

1. **잡이 몰려 들어올 수 있다.** `max_concurrent_tasks` 를 CPU 코어에 맞춰 올린다
   (T7920 은 20C/40T → 4~6). 큐가 차면 429 를 돌려주면 되고, RunchPie 는 그걸
   실패로 기록하되 다음 주기에 재시도한다. **MPT 가 큐를 책임지고 RunchPie 가
   재시도를 책임진다** — 어느 쪽도 상대의 상태를 알 필요가 없다.
2. **디스크가 먼저 죽는다.** 실측으로 태스크 하나가 ~57MB 이고 그 절반이
   `combined-*.mp4`(자막·음성 입히기 전 중간물)다. 하루 50편이면 2.8GB/일.
   `extended/storage_janitor.py` 를 주기적으로 돌린다:

   ```bash
   python -m extended.storage_janitor                              # 현황
   python -m extended.storage_janitor --slim-days 3 --cache-gb 20  # dry-run
   python -m extended.storage_janitor --slim-days 3 --cache-gb 20 --apply
   ```

   `--slim-days` 는 최종물을 남기고 중간물만 지운다. 통째 삭제(`--purge-days`)는
   따로 지정해야 한다. **기본이 dry-run** 인 건 의도다.

**대본 품질 게이트는 이 저장소가 갖지 않는다.** 대본은 RunchPie 가 만들고
`engine/runchpie_engine/quality.py` 가 렌더 앞에서 거른다. 여기서 한 번 더 재는 건
같은 판단을 두 곳에 두는 일이라, 기준이 갈리는 순간 디버깅이 불가능해진다.

## 앞으로 이 저장소에 들어올 것 (plan/ 기준)

- **비전 검수 에이전트** (`next_gen §5`) — 렌더 결과 mp4 를 VLM 이 보고 자막 가림·
  컷 어긋남을 잡는다. RTX TITAN 대기. 16GB M1 에서는 8B 워커와 공존 불가.
- **숏츠 리버스 엔지니어링** (`shorts_reverse_engineering_pipeline.md`) — yt-dlp +
  Whisper + PySceneDetect. **구조 분석까지만.** 원본의 음성·영상 소재를 재사용하는
  경로는 만들지 않는다.
- **오디오 비트 싱크** (`arxiv §3`) — librosa 비트 검출 후 컷 타임라인 정렬.
  순수 신호처리라 하드웨어 제약이 없어, GPU 없이도 지금 착수 가능한 유일한 arXiv 항목.

RunchPie 쪽 로드맵과 분류 근거: `prt_runchpie_ai/plan/handoff/2026-08-15-shortform-factory.md`

## 운영 메모

- **포트는 8099 다.** 2026-08-16 에 8080 → 8099 로 옮겼다. 8080 은 RunchPie 백엔드가
  쓰고 있고 실제로 점유중인 것을 확인했다. RunchPie 캠페인 yaml 의 `base_url` 도
  8099 로 맞춰 뒀다. 서버가 떠 있었다면 재기동해야 적용된다.
- **한글 자막 폰트**는 `resource/fonts/AppleGothic.ttf`. 페르소나별 폰트는
  `persona_registry` 가 지정한다.
- **Whisper 가 CPU int8**(`config.toml [whisper]`) 이라 자막 재생성이 느리다.
