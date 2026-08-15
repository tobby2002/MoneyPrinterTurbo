# 🚀 AI 숏폼 영상 무제한 자동화 시스템 설계서 (Architecture & Roadmap)

본 문서는 **iMac M1 (원격 조종기)**과 **Dell Precision T7920 (AI 전용 렌더링 서버)**를 연동하여 외부 API 비용 없이 글로벌 다국어 숏폼 영상을 24시간 대량 자동 생산하기 위한 마스터 플랜입니다.

---

## 📂 1. 시스템 하드웨어 역할 분담 (Hardware Architecture)

```text
[ iMac M1 (통합 메모리 16GB) ] ── (SSH / WebUI 원격 접속) ──> [ Dell T7920 (RAM 128GB + RTX TITAN 24GB) ]
  • 원격 컨트롤러 및 모니터링                                   • 24시간 365일 숏폼 대량 생산 백엔드
  • 저전력, 저소음 쾌적한 개발/제어                              • 로컬 LLM + AI 실사 생성 + FFmpeg 렌더링
```

| 항목 | iMac M1 (16GB) | Dell T7920 (RAM 128GB + RTX TITAN 24GB [최대 3x TITAN 72GB]) |
| :--- | :--- | :--- |
| **역할** | **원격 조종기 (Controller)** | **AI 전용 연산/렌더링 공장 (Factory Server)** |
| **주요 작업** | 웹 브라우저 접속, 프롬프트 관리, 모니터링 | 대본 AI 구동, Pexels/ComfyUI 영상 수집, FFmpeg 합성 |
| **장점** | 전력 소모 최소화, 소음 제로 | **외부 API 비용 0원**, 24시간 무제한 병렬 생산 |

---

## ⚙️ 2. 핵심 소프트웨어 파이프라인 (Software Pipeline)

```text
1. 💡 주제/아이디어 입력 (iMac M1 ➔ T7920 서버)
      ↓
2. 🧠 로컬 LLM 대본 작성 (Ollama / vLLM - DeepSeek-R1 32B / Qwen2.5 32B)
      ↓
3. 🎬 비디오 소재 수집 (Pexels API + ComfyUI/HunyuanVideo AI 실사 직접 생성)
      ↓
4. 🎙️ AI 더빙 & 자막 생성 (Edge TTS / ElevenLabs / OpenAI TTS + AppleGothic 폰트)
      ↓
5. 💸 MoneyPrinterTurbo 렌더링 Engine (FFmpeg 비디오 컷편집 + 오디오 + 자막 합성)
      ↓
6. 🌐 글로벌 다국어 매핑 & 교차 자동 업로드 (YouTube Shorts, TikTok, Instagram Reels)
```

---

## 🛠️ 3. T7920 서버 필수 구축 레이어 (Core Components)

### ① 로컬 LLM 대본 엔진 (Ollama / vLLM)
* **역할**: 외부 API(OpenAI, DeepSeek 클라우드) 토큰 비용 없이 대본 및 영문 키워드 무제한 자동 생성.
* **추천 모델**: `DeepSeek-R1 32B`, `Qwen-2.5 32B` (RTX TITAN 24GB VRAM에서 고속 실행).

### ② 비디오 소재 엔진 (Pexels API + ComfyUI)
* **Pexels API**: 키워드 기반 고화질 HD/4K 실사 동영상 자동 다운로드.
* **ComfyUI / HunyuanVideo**: Pexels에 없는 특이한 비디오 장면을 AI가 직접 렌더링.

### ③ MoneyPrinterTurbo 합성 엔진
* **렌더링**: 음성 + 한글 자막 + 배경 음악 + 영상 컷 편집 1080x1920 숏폼 자동 조합.
* **한글 자막 폰트**: `resource/fonts/AppleGothic.ttf` 적용 완료 (자막 깨짐 해결).

### ④ 글로벌 다국어 매핑 (Global Multi-language)
* 동일한 비디오 소스 기반으로 **한국어(ko-KR)**, **영어(en-US)**, **일본어(ja-JP)**, **스페인어(es-ES)** 버전 숏폼을 대량 매핑 생성하여 해외 달러 수익 창출.

---

## 📌 4. 현재 론칭된 서비스 현황 및 경로 정보

* 🌐 **WebUI 주소**: [http://127.0.0.1:8501](http://127.0.0.1:8501)
* 🚀 **API Swagger Docs**: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
* 📁 **생성된 영상 저장 위치**: `workspace/MoneyPrinterTurbo/storage/tasks/<Task-ID>/final-1.mp4`
* 🔤 **한글 자막 폰트 위치**: `workspace/MoneyPrinterTurbo/resource/fonts/AppleGothic.ttf`

---

## 🗓️ 5. 단계별 실행 로드맵 (Action Plan)

1. **[완료] Phase 1: 로컬 기초 환경 검증**
   - MoneyPrinterTurbo 소스 클론, 의존성 설치, WebUI/API 백그라운드 론칭.
   - 한글 폰트 적용 및 DeepSeek + Pexels 실사 숏폼 영상 자동 생성 검증 완료.

2. **Phase 2: T7920 서버 환경 이관 및 Ollama 구축**
   - T7920 서버에 Ubuntu/Docker 설치 및 Ollama (DeepSeek-R1 32B) 구동.
   - MoneyPrinterTurbo 데몬 서버 배치.

3. **Phase 3: iMac M1 ↔ T7920 원격 네트워크 연결**
   - Tailscale 또는 SSH 튜닝을 통해 iMac M1에서 T7920의 WebUI([http://t7920-ip:8501](http://t7920-ip:8501))로 원격 조종.

4. **Phase 4: 글로벌 다국어 채널 자동화 및 24시간 가동**
   - 영어(en-US), 일본어(ja-JP) 타겟 숏폼 파이프라인 가동 및 SNS 자동 발행.
