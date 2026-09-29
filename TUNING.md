# BWMetaAI-aise 설치와 튜닝

## 빌드 (Mac)
- 준비: `../pyms-aise`에 neivv/PyMS `aise` 브랜치 58e4c257 + `.venv` (Python 3.11, `pip install -r requirements.txt`)
- `make check` → `build/lv1/aiscript.bin`, `build/lv2/aiscript.bin`, `build/lv3/aiscript.bin`
- 기존 `make`/`make all`은 프로토스 빌드가 실패함 (단계 설정 필요). `make aise`만 씀

## Windows 설치와 스모크 테스트 (임시 — 스모크 결과로 고쳐 쓸 것)

> Samase에서 aise.dll을 어디에 두어야 로드되는지는 아직 확인되지 않았음 (설계서 R2).
> 아래 배치는 설계서 기준 추정이다. 스모크가 통과한 실제 구조로 이 절을 고쳐 적는다.

### 1. 준비물
| 파일 | 어디서 |
|---|---|
| `aise.dll` v2.38.3 | https://github.com/neivv/aise/releases 에서 받음 |
| 스모크용 `aiscript.bin` | 릴리즈의 `aiscript-smoke.bin` — 원본 BWMetaAI + 프로토스 시작 시 `print(aise smoke ok)` 1줄 |
| 단계별 `aiscript.bin` | 릴리즈의 `aiscript-lv1.bin`, `aiscript-lv2.bin`, `aiscript-lv3.bin` |

- 테스트 릴리즈: https://github.com/gyofeel/BWMetaAI/releases/tag/aise-test-1
- 받은 파일은 설치할 때 이름을 `aiscript.bin`으로 바꾼다
- 릴리즈 파일은 Mac에서 `make check`로 만든 `build/smoke/aiscript.bin`, `build/lvN/aiscript.bin`과 같다. `build/`는 git에 올라가지 않는다

### 2. 스모크 설치
1. 지금 BWMetaAI+Samase로 실행하던 방식을 그대로 확인해 둔다 (Samase 실행 명령과 BWMetaAI `aiscript.bin`의 위치)
2. 그 설정을 복사해 새 모드 폴더를 만든다. 예: `StarCraft\x86\custom_smoke\`
   - 기존 설정 파일은 건드리지 않는다. 원래 쓰던 `aiscript.bin`을 덮어써야 하는 구조라면 먼저 백업한다
3. 스모크용 `aiscript.bin`을 새 폴더의 `scripts\aiscript.bin`으로 넣는다. 기존 BWMetaAI가 다른 위치를 쓰고 있었다면 그 위치를 따른다
4. `aise.dll`을 같은 모드 폴더에 넣는다
5. `samase.exe custom_smoke`처럼, 새 폴더를 가리키게 해서 Samase를 실행한다

### 3. 스모크 테스트
1. 사용자(테란) 대 컴퓨터(프로토스) 1:1 커스텀 게임을 시작한다
2. 게임 시작 직후 채팅을 확인한다

| 채팅 | 판정 |
|---|---|
| `aise smoke ok`와 `BWMetaAI github.com/...`가 모두 보임 | **통과.** aise.dll과 스크립트가 모두 로드됨 → 4번으로 |
| `BWMetaAI ...`만 보이고 `aise smoke ok`가 없음 | aise.dll 미로드. dll 위치를 바꿔 본다: StarCraft 실행 파일 폴더 → `samase.exe` 폴더 → 모드 폴더의 `plugins\` 순서. Samase README에서 플러그인 위치를 확인한다 |
| 둘 다 없음 | 스크립트가 로드되지 않음. `aiscript.bin` 위치가 기존 BWMetaAI 방식과 다름 |
| 게임이 튕기거나 AI가 멈춤 | aise.dll 없이 aise 명령이 실행된 경우일 수 있다. dll 위치부터 확인한다 |

3. 결과를 기록한다: 통과한 폴더 구조, `aise.dll` 위치, 실행 명령. 이것으로 이 절을 고쳐 적는다

### 4. 단계별 설치 (스모크 통과 뒤)
- 스모크에서 통과한 구조를 그대로 복사해 단계마다 폴더를 하나씩 만든다: `custom_lv1`, `custom_lv2`, `custom_lv3`
- 각 폴더에 해당 단계의 `aiscript.bin`과 `aise.dll`을 넣는다
- 실행: `samase.exe custom_lvN`. 바탕화면 바로가기를 단계별로 하나씩 만들어 두면 편하다
- 게임 시작 직후 채팅에 `BWMetaAI-aise PvT LvN`이 보여야 한다. 없으면 aise.dll이 로드되지 않은 것이므로 그 상태로 계속하지 않는다
  - 이 메시지는 **상대가 테란일 때만** 나온다. 프로토스 AI 대 저그·프로토스 게임에서는 나오지 않는 것이 정상이다

## 게임 스모크 체크리스트
- [ ] B0 스모크: 테란(사용자) vs 프로토스(컴퓨터)에서 채팅 `aise smoke ok`
- [ ] B1 단계마다 시작 채팅 `BWMetaAI-aise PvT LvN`
- [ ] B2 테란·저그 AI는 원래 메시지만 나오고 동작이 원본과 같음. 프로토스 AI 대 저그 AI 관전 1게임에서 aise 메시지 없음
- [ ] B3 스톰 / 스테이시스(Lv2+) / 점사(Lv2+) / 후퇴(Lv3) / 다크 난입 / 일꾼 22기 제한 / 3게임 간 빌드·타이밍 변화
- [ ] B4 단계마다 3게임 완주, 튕김·멈춤 없음

공격 중인 부대에서 교전 동작이 안 보이면 기록 (aise `idle_orders`는 대기 중인 유닛에만 적용될 수 있음)

## 튜닝 규칙
- 목표: 선택한 단계에서 승률 35~50%. 단계당 5게임
- 60% 이상이면 한 단계 올리거나 수치 하나를 올림. 30% 이하면 반대
- 한 번에 한 가지만 바꿈. 값은 `tools/config_lvN.json`의 `"aise"`에서만 수정, 바꾼 뒤 `make check`
- 자원 보너스(치트)가 필요하면 해당 config의 `"difficulty"`를 1 이상으로 (기본 0 = 없음)

## 기록
| 날짜 | 단계 | 맵 | 승패 | 패인 한 줄 | 바꾼 값 |
|---|---|---|---|---|---|
