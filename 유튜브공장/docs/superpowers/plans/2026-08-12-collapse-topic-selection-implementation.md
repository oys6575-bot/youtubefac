# Collapse Topic Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 승인된 「무너진 이유」 점수표를 재사용 가능한 평가기로 구현하고, 실제 물리적 붕괴 사건 후보를 검색·점수화해 사용자 주제 승인 Human Gate에 올린다.

**Architecture:** `config/topic-selection-scorecard.yaml`이 유일한 배점·상태 규칙 원본이며 `lib/topic_scorecard.py`는 이를 읽어 후보별 환산점수와 판정을 결정론적으로 계산한다. 인터넷 조사는 별도의 JSON 근거 기록과 사람이 읽는 Markdown 순위표를 만들며, 영상 제작 파이프라인이나 제공자 선택에는 연결하지 않는다.

**Tech Stack:** Python 3.11+, PyYAML, pytest, JSON, Markdown, Agent Reach Exa search, Agent Reach YouTube route (`yt-dlp`)

## Global Constraints

- 사람이 만든 건축물·구조물의 전체 또는 일부가 실제로 물리적 붕괴·붕락한 사건만 평가한다.
- 설계·시공·재료·유지관리·과적·지반·화재·폭발·충돌·자연재해 등 원인 유형을 제한하지 않는다.
- 제작 모델, 제작 플랫폼, 제작비, 렌더 시간, 현재 아카이브 영상 보유량은 점수 입력에서 제외한다.
- 배점은 흡입력 15, 원인 깊이 20, 반전 15, 검증 가능성 20, 서사 확장성 10, 시각적 설명 가능성 10, 의미·교훈 5, 국내 희소성 5로 합계 100이다.
- 사실 검증 가능성 환산점수가 12/20 미만이면 총점과 무관하게 `HOLD_NEEDS_EVIDENCE`다.
- 점수표는 주제를 자동 승인하지 않는다. 최종 선택은 사용자 Human Gate에서 멈춘다.
- 영상 제작, 에셋 생성, 유료 호출, 게시 작업은 이 계획의 범위가 아니다.

---

### Task 1: 결정론적 점수표 평가기

**Files:**
- Modify: `docs/superpowers/specs/2026-08-12-collapse-topic-selection-scorecard-design.md`
- Create: `config/topic-selection-scorecard.yaml`
- Create: `lib/topic_scorecard.py`
- Create: `tests/contracts/test_topic_scorecard.py`

**Interfaces:**
- Consumes: `scores: dict[str, int | str]`, `scope: dict[str, bool]`, YAML 배점·판정 규칙
- Produces: `load_scorecard(path) -> dict`, `score_candidate(candidate, scorecard=None) -> dict`, `rank_candidates(candidates, scorecard=None) -> list[dict]`

- [ ] **Step 1: 작성된 설계문서 상태를 승인됨으로 변경**

`**상태:** 대화에서 확정됨, 작성된 문서 최종 검토 대기`를
`**상태:** 사용자 최종 승인 — 구현 기준`으로 변경한다. 다른 설계 내용은 수정하지 않는다.

- [ ] **Step 2: 실패하는 계약 테스트 작성**

`tests/contracts/test_topic_scorecard.py`에 다음 동작을 직접 검증하는 테스트를 작성한다.

```python
from __future__ import annotations

from copy import deepcopy

import pytest

from lib.topic_scorecard import (
    ScorecardError,
    load_scorecard,
    rank_candidates,
    score_candidate,
)


def candidate(candidate_id: str = "case-a") -> dict:
    return {
        "id": candidate_id,
        "scope": {
            "human_made_structure": True,
            "physical_collapse": True,
            "scope_verified": True,
        },
        "scores": {
            "event_pull": 5,
            "causal_depth": 5,
            "belief_reversal": 5,
            "evidence_verifiability": 5,
            "narrative_expandability": 5,
            "visual_explainability": 5,
            "meaning_and_lessons": 5,
            "korean_content_scarcity": 5,
        },
    }


def test_scorecard_weights_total_one_hundred() -> None:
    config = load_scorecard()
    assert sum(item["weight"] for item in config["criteria"].values()) == 100


def test_perfect_candidate_is_priority_with_literal_weighted_scores() -> None:
    result = score_candidate(candidate())
    assert result["weighted_scores"] == {
        "event_pull": 15,
        "causal_depth": 20,
        "belief_reversal": 15,
        "evidence_verifiability": 20,
        "narrative_expandability": 10,
        "visual_explainability": 10,
        "meaning_and_lessons": 5,
        "korean_content_scarcity": 5,
    }
    assert result["total"] == 100
    assert result["status"] == "PRIORITY"


def test_low_evidence_overrides_high_total() -> None:
    item = candidate()
    item["scores"]["evidence_verifiability"] = 2
    result = score_candidate(item)
    assert result["weighted_scores"]["evidence_verifiability"] == 8
    assert result["status"] == "HOLD_NEEDS_EVIDENCE"


def test_unassessed_score_prevents_final_total() -> None:
    item = candidate()
    item["scores"]["belief_reversal"] = "UNASSESSED"
    result = score_candidate(item)
    assert result["total"] is None
    assert result["status"] == "UNASSESSED"


def test_scope_gate_precedes_scoring() -> None:
    item = candidate()
    item["scope"]["physical_collapse"] = False
    result = score_candidate(item)
    assert result["total"] is None
    assert result["status"] == "OUT_OF_SCOPE"


def test_unverified_scope_prevents_scoring() -> None:
    item = candidate()
    item["scope"]["scope_verified"] = False
    result = score_candidate(item)
    assert result["total"] is None
    assert result["status"] == "UNASSESSED"


def test_scores_outside_zero_to_five_are_rejected() -> None:
    item = candidate()
    item["scores"]["event_pull"] = 6
    with pytest.raises(ScorecardError, match="event_pull"):
        score_candidate(item)


def test_full_tie_keeps_shared_rank() -> None:
    first = candidate("case-a")
    second = deepcopy(first)
    second["id"] = "case-b"
    ranked = rank_candidates([second, first])
    assert [item["id"] for item in ranked] == ["case-a", "case-b"]
    assert [item["rank"] for item in ranked] == [1, 1]
```

- [ ] **Step 3: 테스트가 기능 부재로 실패하는지 확인**

Run: `pytest -q tests/contracts/test_topic_scorecard.py`

Expected: collection 단계에서 `ModuleNotFoundError: No module named 'lib.topic_scorecard'`로 실패한다.

- [ ] **Step 4: 기계 판독 가능한 점수표 설정 작성**

`config/topic-selection-scorecard.yaml`은 다음 계약을 그대로 담는다.

```yaml
schema_version: "1.0.0"
channel: collapse-reasons
raw_score: {minimum: 0, maximum: 5, unassessed: UNASSESSED}
scope_gate:
  required_true: [human_made_structure, physical_collapse]
  verification_field: scope_verified
criteria:
  event_pull: {weight: 15}
  causal_depth: {weight: 20}
  belief_reversal: {weight: 15}
  evidence_verifiability: {weight: 20}
  narrative_expandability: {weight: 10}
  visual_explainability: {weight: 10}
  meaning_and_lessons: {weight: 5}
  korean_content_scarcity: {weight: 5}
status_thresholds:
  - {minimum: 80, maximum: 100, status: PRIORITY}
  - {minimum: 70, maximum: 79, status: STRONG}
  - {minimum: 60, maximum: 69, status: RESERVE}
  - {minimum: 0, maximum: 59, status: DROP}
evidence_hold:
  criterion: evidence_verifiability
  minimum_weighted_score: 12
  status: HOLD_NEEDS_EVIDENCE
tie_break_order: [evidence_verifiability, causal_depth, event_pull]
forbidden_scoring_inputs:
  - generation_model
  - production_platform
  - production_cost
  - render_time
  - archive_footage_quantity
human_gate: topic_approval
```

- [ ] **Step 5: 최소 평가기 구현**

`lib/topic_scorecard.py`는 다음 규칙을 구현한다.

```python
weighted = raw_score * criterion["weight"] // 5
```

- YAML 루트·배점 합계·기준 ID·범위 필드를 검증하고 위반 시 `ScorecardError`를 낸다.
- 범위 값 중 하나가 `False`면 `OUT_OF_SCOPE`, 검증되지 않았으면 `UNASSESSED`를 반환한다.
- 모든 점수가 정수 `0..5`인지 또는 정확한 문자열 `UNASSESSED`인지 확인한다.
- `UNASSESSED`가 하나라도 있으면 총점 없이 `UNASSESSED`를 반환한다.
- 총점을 임계값으로 분류한 뒤 증거 환산점수가 12 미만이면 보류 상태로 덮어쓴다.
- 순위는 총점, 증거, 원인 깊이, 흡입력의 내림차순으로 정하고 네 값이 모두 같으면 공동 순위를 준다. 공동 순위 내부 표시는 ID 사전순으로 안정화하지만 우선순위는 바꾸지 않는다.

- [ ] **Step 6: 평가기 테스트 통과 확인**

Run: `pytest -q tests/contracts/test_topic_scorecard.py`

Expected: `8 passed`.

- [ ] **Step 7: Task 1 커밋**

```bash
git add docs/superpowers/specs/2026-08-12-collapse-topic-selection-scorecard-design.md \
  config/topic-selection-scorecard.yaml lib/topic_scorecard.py \
  tests/contracts/test_topic_scorecard.py
git commit -m "feat: add collapse topic scorecard"
```

### Task 2: 후보 검색·점수화·Human Gate 자료

**Files:**
- Create: `templates/topic-candidate-scorecard.md`
- Create: `research/topic-candidates/2026-08-12-collapse-topic-shortlist.json`
- Create: `research/topic-candidates/2026-08-12-collapse-topic-shortlist.md`
- Create: `tests/contracts/test_collapse_topic_shortlist.py`

**Interfaces:**
- Consumes: `score_candidate()`와 `rank_candidates()`, 공식 조사자료 URL, 한국어 YouTube 검색 관찰
- Produces: 검증 가능한 후보 기록 JSON과 사용자가 비교할 Markdown 순위표

- [ ] **Step 1: 실패하는 후보자료 계약 테스트 작성**

`tests/contracts/test_collapse_topic_shortlist.py`에 다음 검증을 작성한다.

```python
from __future__ import annotations

import json
from pathlib import Path

from lib.topic_scorecard import rank_candidates


ROOT = Path(__file__).resolve().parents[2]
SHORTLIST = ROOT / "research" / "topic-candidates" / "2026-08-12-collapse-topic-shortlist.json"


def test_shortlist_is_in_scope_source_backed_and_scoreable() -> None:
    payload = json.loads(SHORTLIST.read_text(encoding="utf-8"))
    candidates = payload["candidates"]
    assert len(candidates) >= 10
    assert len({item["id"] for item in candidates}) == len(candidates)

    forbidden = {
        "generation_model",
        "production_platform",
        "production_cost",
        "render_time",
        "archive_footage_quantity",
    }
    for item in candidates:
        assert item["provisional"] is True
        assert item["scope"] == {
            "human_made_structure": True,
            "physical_collapse": True,
            "scope_verified": True,
        }
        assert item["sources"]
        assert any(source["class"] == "official_or_primary" for source in item["sources"])
        assert all(source["url"].startswith("http") for source in item["sources"])
        assert item["korean_youtube_landscape"]["query"]
        assert not forbidden & set(item)

    ranked = rank_candidates(candidates)
    assert len(ranked) == len(candidates)
    assert all(item["status"] != "UNASSESSED" for item in ranked)
    assert all(item["status"] != "OUT_OF_SCOPE" for item in ranked)
```

- [ ] **Step 2: 후보자료 부재로 테스트가 실패하는지 확인**

Run: `pytest -q tests/contracts/test_collapse_topic_shortlist.py`

Expected: `FileNotFoundError`로 실패한다.

- [ ] **Step 3: 공통 후보 기록 양식 작성**

`templates/topic-candidate-scorecard.md`에 사건 식별정보, 범위 게이트, 한 줄 질문,
`PROVISIONAL` 원인 요약, 증거 표면, 8개 원점수·환산점수·근거, 불확실성,
한국어 콘텐츠 확인, 총점·상태, 평가자·평가일을 기록하는 빈 양식을 만든다.
제작 도구·모델·비용 칸은 만들지 않는다.

- [ ] **Step 4: 웹에서 폭넓은 후보군 발굴**

Agent Reach Exa 검색으로 다음 검색군을 각각 실행한다.

```text
official investigation report structural building collapse progressive collapse
site:ntsb.gov bridge collapse probable cause report
official inquiry roof collapse structural failure report
official investigation dam failure collapse report
construction stage building collapse official investigation report
```

다양한 구조물 유형과 원인 유형에서 최소 12개 사건을 발굴한다. 각 사건은 사건 존재와
물리적 붕괴 여부를 확인할 출처 하나, 원인 조사를 확인할 공식·1차 자료 하나를 확보한다.
본문이나 미디어를 복사하지 않고 URL·문서명·지원하는 평가 항목만 기록한다.

- [ ] **Step 5: 국내 콘텐츠 희소성 별도 확인**

각 후보의 한국어 사건명과 핵심 원인을 이용해 다음 형식으로 YouTube 상위 10개 결과를
관찰한다.

```bash
yt-dlp --dump-json "ytsearch10:<한국어 사건명> 붕괴 원인"
```

정확한 심층 해부 영상 수, 단순 뉴스·짧은 요약·무관 결과의 비중을 기록한다. 조회수나
영상 확보 편의성은 점수에 사용하지 않는다.

- [ ] **Step 6: 후보 JSON과 비교 문서 작성**

JSON 후보마다 다음 키를 채운다.

```json
{
  "id": "stable-kebab-id",
  "event_name_ko": "한국어 사건명",
  "event_name_en": "English event name",
  "country_region": "국가·지역",
  "collapse_date": "YYYY-MM-DD",
  "structure_type": "구조물 유형",
  "collapse_extent": "전체 또는 부분",
  "scope": {
    "human_made_structure": true,
    "physical_collapse": true,
    "scope_verified": true
  },
  "why_question": "왜 무너졌는가를 묻는 한 줄",
  "provisional_cause_summary": "검증 전 원인 요약",
  "provisional": true,
  "scores": {
    "event_pull": 0,
    "causal_depth": 0,
    "belief_reversal": 0,
    "evidence_verifiability": 0,
    "narrative_expandability": 0,
    "visual_explainability": 0,
    "meaning_and_lessons": 0,
    "korean_content_scarcity": 0
  },
  "score_rationales": {},
  "sources": [],
  "korean_youtube_landscape": {
    "query": "검색어",
    "observed_top_results": 10,
    "deep_dive_result_estimate": 0,
    "notes": "관찰 요약",
    "checked_at": "2026-08-12"
  },
  "uncertainties": []
}
```

위 JSON은 필드 구조 예시이며 실제 후보 점수와 근거로 모든 값을 교체한다.
Markdown에는 자동 계산된 순위·총점·상태, 상위 후보별 강점·약점, `PROVISIONAL`
주의, 사용자 선택란을 넣는다. 후보를 자동 승인하지 않는다.

- [ ] **Step 7: 후보 계약과 전체 관련 테스트 실행**

Run: `pytest -q tests/contracts/test_topic_scorecard.py tests/contracts/test_collapse_topic_shortlist.py`

Expected: `9 passed`.

- [ ] **Step 8: Agent Reach 업데이트 확인**

`agent-reach` 명령이 설치되어 있으면 `agent-reach check-update`를 실행한다. 본체 명령이
없으면 Exa와 `yt-dlp` 백엔드를 사용했다는 제한만 기록하며 설치나 업데이트를 임의로
수행하지 않는다.

- [ ] **Step 9: Task 2 커밋**

```bash
git add templates/topic-candidate-scorecard.md \
  research/topic-candidates/2026-08-12-collapse-topic-shortlist.json \
  research/topic-candidates/2026-08-12-collapse-topic-shortlist.md \
  tests/contracts/test_collapse_topic_shortlist.py
git commit -m "research: score collapse topic candidates"
```

- [ ] **Step 10: Human Gate에서 중지**

상위 후보와 추천 이유를 사용자에게 보여주고 `주제 승인 Human Gate`에서 종료한다.
심층 자료 수집, 대본, 장면 계획, 제작 도구 선택으로 넘어가지 않는다.
