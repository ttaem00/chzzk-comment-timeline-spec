# 검증 기록

2026-10-01 공개 편집 초안 0.1. 합성 fixture 8건을 현재 제품의 `comment_preview.v2` parser와 대조합니다. 검사 항목은 시작/끝, 진단, 미해석 원문이며 D1–D6와 반복/복수 시각을 포함합니다. 기존 제품의 별도 회귀 검사에는 부모 명단 상속, 강조, 부분 본문, 범위 오류, 답글 관계, 분할 뒤 부모 맥락과 종료 보존도 포함됩니다.

```text
node scripts/validate.cjs
node scripts/validate.cjs --parser /absolute/path/to/comment_format.js
```

첫 명령은 이 저장소의 JSON 형태, 문서 링크, 코드 블록을 확인합니다. 두 번째는 사용자가 이미 가진 호환 parser 모듈을 명시했을 때만 동작합니다. 모듈은 `parseCompatibleComments(documents, options)`를 제공해야 합니다. 이 저장소는 해당 parser를 다운로드하거나 배포하지 않습니다.

실행 결과, parser SHA-256과 확인한 문서 commit은 PR 검증 기록에 고정합니다. 다른 구현 간 호환성이나 플랫폼 댓글 게시 성공은 이 fixture 대조만으로 증명되지 않습니다. 제품 실사용 검증과 이 저장소의 문서 검증은 각자 범위를 표시합니다. C08 전체 변환 기본값은 이 공개 초안으로 승인되지 않습니다.
