# BWMetaAI-aise: 테프전 연습용 프로토스 AI 강화 설계

- 작성일: 2026-09-29
- 상태: 사용자 검토 대기
- 저장소: `bwmetaai-aise/` (BWMetaAI `81367cf` 포크, 브랜치 `aise-protoss`, 원격 `upstream` = jncraton/BWMetaAI)

## 1. 목표와 맥락

### 사용자 발언
- 주종 테란. 리마스터에서 혼자 테프전(상대 AI 프로토스) 연습
- 현재 BWMetaAI + Samase를 사용 중. BWMetaAI 프로토스 상대로 승률 90% 이상
- 교전, 견제, 빌드, 운영 네 영역을 **모두 일정 수준** 올리되, **본인 수준보다 약간 위**여야 함

### 가정 (사용자 확인 완료)
- 오프라인 혼자 연습용. Samase 사용 리스크는 기존과 같음
- 완벽한 컨트롤이 아니라 체감되는 "사람다움" 개선. 규칙 기반 AI의 한계는 인지함

### 성공 기준
1. Lv1, Lv2, Lv3 `aiscript.bin`이 빌드되고, 리마스터 + Samase + aise에서 정상 동작
2. 네 영역의 행동이 게임 안에서 관찰됨(8절 B3)
3. 사용자가 어느 단계에서든 **승률 35~50%**가 되도록 조정할 수 있음
4. 테란·저그 AI 동작은 원본과 동일

### 범위 밖
- 테란·저그 스크립트 수정, 게임 중 난이도 전환, EUD 맵 버전(aise는 Samase가 필요함), 적응형 난이도

## 2. 구성 요소

| 구성 요소 | 버전·출처 | 역할 |
|---|---|---|
| BWMetaAI | `81367cf` (2026-08-21) | 기반 스크립트, 전처리기(`tools/macros.py`, `tools/race.py`) |
| aise | `aise.dll` v2.38.3 (neivv/aise 릴리즈) | 확장 명령 실행 (Samase 플러그인) |
| PyMS aise 포크 | neivv/PyMS `aise` 브랜치, 구현 시 커밋 고정 | aise 명령을 포함한 스크립트 컴파일 (Python 3.11~3.13, CLI) |
| Samase | 사용자 설치본 | 모드 로더 |

## 3. 영역별 모듈과 단계

모든 모듈은 **상대가 테란일 때만** 동작함(`enemyowns(Command Center)` 분기). 다른 종족전은 원본 동작을 유지함.

| 영역 | 행동 | aise 명령 | Lv1 | Lv2 | Lv3 |
|---|---|---|---|---|---|
| 교전 | 하이템플러 스톰: 반경 안에 적 바이오(마린·메딕·파이어뱃)가 N기 이상일 때 | `idle_orders` (count, InCombat) | N=8, 주기 느림 | N=6 | N=4, 주기 빠름 |
| 교전 | 아비터 스테이시스: 시즈 탱크 3기 이상이 뭉쳐 있을 때 | `idle_orders` | ✗ | ✓ | ✓ |
| 교전 | 드라군 점사: 벌처·시즈 탱크 우선 | `idle_orders` (AttackUnit) | ✗ | ✓ | ✓ |
| 교전 | 드라군 실드 낮을 때 후퇴 | `idle_orders` (self Shields 비율 조건, Move) | ✗ | ✗ | ✓ |
| 견제 | 다크 2기로 SCV 라인 난입 | `ai_order` / `attack_to` | 1회 | 2회(멀티 포함) | 반복 |
| 견제 | 셔틀 리버 견제 | `ai_order` | ✗ | ✗ | 실험 (실패 시 제외) |
| 빌드 | 공격·확장 타이밍 무작위 흔들림 | `wait_rand` | ✓ | ✓ | ✓ |
| 빌드 | 빌드 풀 가중치 | 기존 `build_weight` + 단계 치환 | 정석(사업 멀티, 리버) | + 다크, 2게이트 푸시 | + 캐리어, 올인 |
| 운영 | 기지별 최대 일꾼 수 | `max_workers` | ✓ | ✓ | ✓ |
| 운영 | 멀티 타이밍 | 기존 `expansion_timing_manager`의 대기 시간 치환 | 기존 | 앞당김 | 더 앞당김 |
| 운영 | 자원 보너스(치트) | 기존 `freemoney`(`difficulty`) | 없음 | 없음 | 선택 (기본 없음) |

구체 수치(N, 주기, 반경, 대기 프레임, 가중치)는 전부 `config_lvN.json`에 두고, 스크립트에는 치환 자리표시자만 둠.

## 4. 코드 구조

```
src/protoss/aise/manager.pyai      진입점: 테란전 판별, 시작 메시지, 아래 모듈을 multirun으로 실행
src/protoss/aise/combat.pyai       교전 idle_orders 선언
src/protoss/aise/harass.pyai       다크·셔틀 견제 스레드
src/protoss/aise/macro.pyai        max_workers
src/protoss/builds/*.pyai          build_weight({lv.w_<빌드>}), 타이밍에 wait_rand 삽입
src/protoss/managers/tech_manager.pyai        첫 줄에 multirun_file(aise/manager) 추가
src/protoss/managers/expansion_timing_manager.pyai   wait 값을 {lv.expand_wait_N}으로 치환
tools/macros.py                    {lv.key} 치환, if_level(n): 블록 (컴파일 시점에 처리)
tools/config_lv1.json, config_lv2.json, config_lv3.json
tools/check_levels.py              A3·A4 검사
makefile                           lv1/lv2/lv3 빌드 대상, PyMS 포크 컴파일러 호출
```

- **호출 위치**: `src/main.pyai`는 세 종족이 공유하므로 수정하지 않음. 게임당 한 번 실행되는 프로토스 전용 `tech_manager`에서 aise 모듈을 호출함. 테란·저그의 바이트코드가 변하지 않게 하기 위함(A5). 경로 해석과 1회 실행은 구현 1단계에서 확인함
- **시작 메시지**: 원본 메시지는 그대로 두고, aise 매니저가 `BWMetaAI-aise PvT Lv{lv.level} {now} {commit}` 메시지를 하나 더 보냄
- **단계 치환 규칙**:
  - `{lv.key}`: `config_lvN.json`의 `aise.key` 값으로 치환. 키가 없으면 **빌드 실패**(조용히 기본값을 쓰지 않음)
  - `if_level(n):` 블록: 현재 단계가 n 이상일 때만 들어가고, 아니면 제거

## 5. 데이터 흐름

```
config_lvN.json ─┐
src/**/*.pyai ───┴→ build_ai.py(전처리: 매크로, {lv.*}, if_level) → build/lvN/combined.pyai
   → PyMS 포크 컴파일 → build/lvN/aiscript.bin
   → 설치: StarCraft\x86\custom_lvN\scripts\aiscript.bin
   → 실행: samase.exe custom_lvN (+ aise.dll)
   → 게임: aise가 확장 명령 실행 → 시작 채팅으로 단계 확인
```

## 6. 오류 처리

| 상황 | 동작 |
|---|---|
| config에 치환 키가 없음 | 빌드 실패, 누락 키 이름 출력 |
| PyMS 컴파일 오류 | 빌드 실패, 컴파일러 메시지 그대로 출력 |
| aise.dll 미로드 상태에서 실행 | aise 명령이 알 수 없는 명령이 됨 → 스크립트 오작동. 시작 채팅에 aise 메시지가 없으면 로드 실패로 판단(B1). 설치 안내에 명시 |
| 실험 기능(셔틀 리버)이 오작동 | 해당 블록을 config에서 끔(`harass_reaver: false`) |

## 7. 리스크와 선행 확인 (구현 1단계)

| # | 리스크 | 확인 방법 | 실패 시 대안 |
|---|---|---|---|
| R1 | PyMS 포크가 BWMetaAI의 구형 문법을 컴파일하지 못하거나 결과가 다름 | A1 | 전처리 출력만 문법 변환, 또는 구형 PyAI에 aise 명령 정의 추가 |
| R2 | 사용자 Samase 버전에서 aise.dll 로드 실패, 설치 위치 불명 | 최소 스크립트(`print` 1줄) 스모크 | aise 소스 빌드(2026-07 최신), Samase 문서·커뮤니티 확인 |
| R3 | `idle_orders`가 공격 중인 부대에는 적용되지 않음 | B3 교전 관찰 | 공격 중 교전은 `ai_order`로 보완, 또는 해당 행동을 교전 후 대기 상태 한정으로 축소 |
| R4 | 셔틀 리버 태우고 내리기를 스크립트로 표현할 수 없음 | 실험 | 기능 제외 |

## 8. 검증

### A. 자동 검사 (Mac에서 실행)
| # | 검사 | 통과 기준 |
|---|---|---|
| A1 | 컴파일러 동등성: 원본을 구형 PyAI와 PyMS 포크로 각각 빌드 → 역컴파일 비교 | 명령 흐름 동일 |
| A2 | lv1~3 빌드 | 오류 없음, 역컴파일 성공 |
| A3 | 단계별 내용: 역컴파일 결과에 기대 명령이 있는지/없는지 | `check_levels.py` 통과 |
| A4 | 전처리기: `{lv.key}`, `if_level`, 누락 키 실패 | assert 통과 |
| A5 | 테란·저그 무변경: 해당 스크립트 역컴파일 결과를 원본과 비교 | diff 없음 |

### B. 게임 내 스모크 (사용자, Windows)
| # | 확인 |
|---|---|
| B1 | 시작 채팅 `BWMetaAI-aise PvT LvN` 표시 |
| B2 | 테란·저그 AI는 원본 메시지와 동작 |
| B3 | 스톰, 스테이시스(Lv2+), 점사(Lv2+), 후퇴(Lv3), 다크 난입, 일꾼 수 제한, 3게임 간 빌드·타이밍 변화 |
| B4 | 3게임 완주, 튕김·멈춤 없음 |

- 선택: 리플레이를 받아 `screp`로 AI의 빌드오더, 타이밍, APM을 추출해 B3를 수치로 확인

### C. 튜닝
- 목표: 선택한 단계에서 본인 승률 35~50%
- `TUNING.md`에 기록: 날짜 | 단계 | 맵 | 승패 | 패인 한 줄. 단계당 5게임
- 규칙: 60% 이상이면 한 단계 올리거나 수치 하나를 올림. 30% 이하면 반대. **한 번에 한 가지만** 바꿈
- 값은 `config_lvN.json`에서만 수정함

## 9. 구현 순서 (구현 계획서에서 세분화)
1. 선행 확인: R1(A1), R2(최소 스크립트 스모크, 사용자 협조 필요)
2. 전처리기 확장 + config 3종 + A4
3. aise 매니저 + 교전 모듈 → A2, A3, B1, B3(교전)
4. 운영 모듈 → B3
5. 빌드 흔들림과 가중치 → B3
6. 견제 모듈(다크, 이어서 셔틀 리버 실험) → B3
7. A5 → 사용자 3단계 스모크(B) → 튜닝(C)

## 10. 라이선스
- BWMetaAI: BSD 계열(© Jon Craton). 포크 수정본은 저작권 고지를 유지함
- aise, PyMS: 각 저장소 라이선스(aise Apache-2.0). 바이너리는 공식 릴리즈에서 받도록 안내함
