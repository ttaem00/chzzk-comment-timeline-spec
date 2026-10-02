# 검증 기록

2026-10-01 공개 편집 초안 0.2. 기존 합성 fixture 8건과 자연 목차 5건을 현재 제품의 `comment_preview.v2` parser와 대조합니다. 검사 항목은 시작/끝, 진단, 미해석 원문이며 자연 목차는 역할·깊이·부모 연결도 확인합니다. D1–D6와 반복/복수 시각을 포함하고, 기존 제품의 별도 회귀 검사에는 부모 명단 상속, 강조, 부분 본문, 범위 오류, 답글 관계, 분할 뒤 부모 맥락과 종료 보존도 포함됩니다.

```text
node scripts/validate.cjs
node scripts/validate.cjs --parser /absolute/path/to/comment_format.js
```

첫 명령은 이 저장소의 JSON 형태, 문서 링크, 코드 블록을 확인합니다. 두 번째는 사용자가 이미 가진 호환 parser 모듈을 명시했을 때만 동작합니다. 모듈은 `parseCompatibleComments(documents, options)`를 제공해야 합니다. 이 저장소는 해당 parser를 다운로드하거나 배포하지 않습니다.

실행 결과, parser SHA-256과 확인한 문서 commit은 PR 검증 기록에 고정합니다. 다른 구현 간 호환성이나 플랫폼 댓글 게시 성공은 이 fixture 대조만으로 증명되지 않습니다. 제품 실사용 검증과 이 저장소의 문서 검증은 각자 범위를 표시합니다. C08 전체 변환 기본값은 이 공개 초안으로 승인되지 않습니다.

## 0.2 구현 대조 기준

자연 구조 지원을 확인한 소비자 main commit은 `1b57b43ab3e45e2b132abe72e625b7da57ba39b0`이며,
대조한 `comment_format.js` SHA-256은 `37e11b7916c64ef74dfc32c0953db83c5961919c609745680a235241bd6681e8`입니다.
이 저장소는 구현 파일을 배포하지 않으며, 사용자는 자신이 가진 parser를 명시해 같은 합성 예제를 검사합니다.

대조 결과: 기존 8건 + 자연 구조·부분 본문·붙여넣기 변형 5건, 총 13건 PASS.
소비자 별도 검증은 66개 회귀 테스트, Chrome·Whale 패키지 검사와 실제 main Chrome의
미리보기→한 번 채택→취소 복원→확장/탭 재로드 후 부분 상태·미확정 끝 보존을 포함합니다.
원본 영상의 정지 시각과 기존 저장 자료도 유지됐습니다. Whale 패키지 검사는 Whale 실사용 증거가 아닙니다.

## 0.3 소비자 후보 대조

2026-10-02, 소비자 구현 후보 commit `ba7dbf8232c35440966618ddeff61897f552f510`과 대조했습니다. main 채택 상태와는 별개입니다. 검사에 사용한 Windows 작업 사본 및 Chrome 후보 패키지의 `comment_format.js` SHA-256은 `f5046682770475a2abb36708298edc881632fe4184b6717667b74a93099bbbc8`입니다.

동일 commit의 LF 정규화 Git blob SHA-256은 `c2318de0321e16c4da9d590c306f53ad4ff64d405612bb8f2f5ceb13728dbe7d`입니다. 운영체제 checkout의 줄바꿈 때문에 바이트 해시가 달라질 수 있으므로 구현 commit과 검사한 파일의 해시를 함께 기록합니다.

기존 13건과 `(w. …)`/with 변형, 원문별 별칭, 충돌, 선언 원문의 상속 별칭, 구조 JSON 등 추가 6건의 합성 예제를 대조해 PASS했습니다. 소비자의 별도 회귀 검사 195건과 Chrome·Whale 패키지 검사도 PASS했습니다. 호환 JSON은 `readTimelineFile(text, name, videoNo)`로 먼저 읽고 `parseCompatibleComments`로 미리보기합니다. 역할·시각 투영이 달라지는 입력은 거부하므로 단순 JSON 문법 성공을 의미 보존 성공으로 해석하지 않습니다.

현재 main Chrome의 공식 확장 입구에서 구조 JSON 선택 후 기존 자료 유지 → 미리보기 → 명시 채택 흐름을 확인했습니다. 실제 댓글 원문이나 비공개 브라우저 자료는 이 저장소의 예제에 포함하지 않았습니다. 실제 이름의 정확한 신원·참여 여부·사건 정렬·게시 성공, 타 소비자 구현 호환성과 Whale 실행은 별도 확인 대상입니다.

## 0.3 CVA-TTaempad 0.3.3 후속 후보

2026-10-02, 같은 소비자 PR #26의 `ttaempad.v19` 후속 후보에서 14개 시각·계층 fixture, 6개 인물·구조 JSON fixture와 참가자 규격을 대조해 PASS했습니다. 강조 기호가 감싼 시각, 자유 제목과 중첩 목록, 별표 강조, 역순 시각과 미확정 끝을 포함합니다. 소비자 회귀 검사는 212건 PASS입니다. 참가자 입력은 비교 검색 범위를 지정하며 참여 사실·채널 신원·같은 사건을 확정하지 않습니다.

검사한 `comment_format.js` SHA-256: `2fd0ba6d708e28295b1532cafcbbfbb07c706b465150b61e6c6ba8dd8f61e8d2`.
검사한 `people_input.js` SHA-256: `fbb3b4d2e42035b032bf3bd6406570c4813714a4d7201d27717fe51271e932d6`.
대조한 소비자 구현 commit은 `61d6bf9df9d35a6e6584f5854a1e938c3c8ad220`입니다. 소비자 최종 gate는 212건, Chrome 38개 파일과 Whale 37개 파일 패키지 검사 PASS이며 [소비자 PR #26](https://github.com/ttaem00/chzzk-video-editor-workspace/pull/26)에 기록합니다. 이전 후보 검증은 위 기록의 해당 commit에만 적용됩니다.

```text
node scripts/validate.cjs --parser /absolute/path/to/comment_format.js --roster-parser /absolute/path/to/people_input.js
```

후속 후보의 실제 HLS/교차 컷 출력은 메모리 저장소를 쓰는 main Chrome 검증 화면에서 확인했습니다. 설치된 확장, 치지직 원본 플레이어, CSP/권한 동작이나 공개 게시 성공을 이 증거로 대신하지 않습니다. Chrome 확장 관리 화면의 자동 제어가 제한되어 사용자의 후보 패키지 수동 로드 후 공식 입구를 확인해야 합니다. 공개 main 채택은 아직 별개입니다.
