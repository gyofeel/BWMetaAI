# BWMetaAI-aise 설치와 튜닝

## 빌드 (Mac)
- 준비: `../pyms-aise`에 neivv/PyMS `aise` 브랜치 58e4c257 + `.venv` (Python 3.11, `pip install -r requirements.txt`)
- `make check` → `build/lv1/aiscript.bin`, `build/lv2/aiscript.bin`, `build/lv3/aiscript.bin`
- 기존 `make`/`make all`은 프로토스 빌드가 실패함 (단계 설정 필요). `make aise`만 씀

## 설치 (Windows)
> 아직 확인 전 (R2). 아래는 설계서 기준 배치이며, 스모크(`build/smoke/aiscript.bin`, 채팅 `aise smoke ok`)로 확인한 실제 구조로 고쳐 적을 것

- 지금 쓰는 BWMetaAI+Samase 설정을 복사해 단계마다 모드 폴더 하나: `StarCraft\x86\custom_lv1`, `custom_lv2`, `custom_lv3`
- 각 폴더에 `scripts\aiscript.bin` (해당 단계 빌드)과 `aise.dll`
- 실행: `samase.exe custom_lvN`
- aise.dll v2.38.3은 https://github.com/neivv/aise/releases 에서 받음
- 시작 채팅에 `BWMetaAI-aise PvT LvN`이 없으면 aise.dll이 로드되지 않은 것. 그 상태로 계속하지 않음

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
