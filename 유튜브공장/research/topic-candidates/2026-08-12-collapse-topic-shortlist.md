# 물리적 붕괴 주제 후보 — 2026-08-12

> 상태: **잠정 후보**. 공식·1차 자료로 물리적 붕괴 범위와 날짜를 확인했으며,
> 주제 선택은 아직 사용자 승인을 받지 않았다.

## 평가 방식

- 범위: 사람이 만든 건물 또는 구조물이 실제로 전체·부분 붕괴한 사건
- 점수: `config/topic-selection-scorecard.yaml`의 8개 항목만 사용
- 제외 입력: 제작 모델, 제작 플랫폼, 비용, 렌더 시간, 확보 가능한 영상의 양
- 원점수 초안: Orca Research 역할에 배치한 로컬 `qwen3.6-35b-a3b-mlx`
- 근거 결합·범위 판정: 공식 출처 확인 후 Coordinator가 적용
- 순위: `lib.topic_scorecard.rank_candidates`의 결정적 계산 결과
- 한국어 콘텐츠 희소성: 현재 모두 잠정치이며 선택 전 YouTube 정량 검사가 필요

## 순위

| 순위 | 후보 | 총점 | 상태 | 핵심 질문 |
|---:|---|---:|---|---|
| 1 | 라나 플라자 붕괴 | 93 | PRIORITY | 균열을 본 노동자들은 왜 다음 날 다시 건물 안으로 들어가야 했나? |
| 2 | 하얏트 리젠시 보행로 붕괴 | 90 | PRIORITY | 작은 연결부 변경은 어떻게 두 보행로를 동시에 떨어뜨렸나? |
| 2 | I-35W 미시시피강 교량 붕괴 | 90 | PRIORITY | 수십 년을 버틴 교량은 왜 저녁 교통량 속에서 내려앉았나? |
| 4 | FIU 보행교 붕괴 | 88 | PRIORITY | 균열이 보였는데 왜 아래 도로는 계속 열려 있었나? |
| 5 | 챔플레인 타워 사우스 붕괴 | 86 | PRIORITY | 사람들이 살던 해안 콘도는 왜 새벽에 무너졌나? |
| 5 | 세계무역센터 7번 건물 붕괴 | 86 | PRIORITY | 항공기 충돌이 없던 건물은 왜 그날 오후 붕괴했나? |
| 7 | 타코마 내로스 브리지 붕괴 | 84 | PRIORITY | 바람은 어떻게 거대한 상판을 비틀어 떨어뜨렸나? |
| 8 | L’Ambiance Plaza 붕괴 | 83 | PRIORITY | 리프트 슬래브 공법은 왜 건물 전체를 연쇄 붕괴시켰나? |
| 9 | 퀘벡 브리지 1차 붕괴 | 83 | PRIORITY | 계산 오류와 현장 경고는 왜 공사를 멈추지 못했나? |
| 10 | 쇼하리 크리크 브리지 붕괴 | 77 | STRONG | 보이지 않는 강바닥 변화는 어떻게 교각을 쓰러뜨렸나? |
| 11 | 선샤인 스카이웨이 브리지 붕괴 | 76 | STRONG | 화물선 한 척은 어떻게 고속도로 상판을 바다로 떨어뜨렸나? |
| 12 | 실버 브리지 붕괴 | 73 | STRONG | 작은 아이바 균열은 어떻게 전체 연쇄 붕괴로 번졌나? |

## 공식·1차 출처

1. [Hyatt Regency walkways — NIST](https://www.nist.gov/el/walkway-collapse-kansas-city-missouri-1981)
2. [Champlain Towers South — NIST](https://www.nist.gov/disaster-and-failure-studies/champlain-towers-south-collapse)
3. [FIU pedestrian bridge — NTSB](https://www.ntsb.gov/investigations/pages/hwy18mh009.aspx)
4. [I-35W bridge — NTSB](https://www.ntsb.gov/investigations/Pages/HWY07MH024.aspx)
5. [WTC 7 — NIST](https://www.nist.gov/publications/final-report-collapse-world-trade-center-building-7-federal-building-and-fire-safety-0)
6. [Silver Bridge — NTSB](https://www.ntsb.gov/investigations/Pages/80267.aspx)
7. [Tacoma Narrows Bridge — Washington State DOT](https://wsdot.wa.gov/TNBhistory/collapse.htm)
8. [Sunshine Skyway Bridge — NTSB](https://www.ntsb.gov/investigations/Pages/DCA80AM050.aspx)
9. [L’Ambiance Plaza — OSHA](https://www.osha.gov/enforcement/directives/std-03-15-003)
10. [Schoharie Creek Bridge — NTSB](https://www.ntsb.gov/investigations/Pages/DCA87MH005.aspx)
11. [Rana Plaza — ILO](https://www.ilo.org/resource/statement/employment-injury-insurance-bangladesh-bridging-social-security-cases)
12. [Québec Bridge — Government of Canada](https://www.canada.ca/en/housing-infrastructure-communities/news/2019/08/the-history-of-the-quebec-bridge.html)

## 범위에서 뺀 후보

- **Big Bayou Canot**: 공식 기록상 바지선 충돌로 교량이 변위된 뒤 열차가
  충돌·탈선한 사건이다. 교량 자체의 물리적 붕괴가 명확하지 않아 엄격한
  채널 범위에서는 제외하고, 실제 건물 붕괴가 확인되는 L’Ambiance Plaza로 교체했다.

## 다음 Gate

Codex 독립 검증이 이 파일의 정확한 SHA-256과 Research 커밋에 결속되어 PASS한
뒤에만 `topic_approval`을 `awaiting_human`으로 기록한다. 이 문서는 주제 선택이나
제작 시작을 승인하지 않는다.
