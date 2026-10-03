# 도구가 만든 시간축 가져오기

댓글은 평문으로 작성합니다. 이 JSON은 분석기·편집 도구가 만든 호환 시간축을 가져오는 교환 형식입니다. 컷 작업 저장 파일, 동영상 파일, 댓글 자동 게시 형식과는 별개입니다.

형식 식별자 `chzzk.comment-timeline`, `version: 1`을 사용합니다. 문서 초안 0.3과 parser 출력 `comment_preview.v2`는 별도 버전입니다. 현재 소비자 후보에서 **미리보기 → 확인 후 시간축에 불러오기**로 사용하며, 파일을 고르기만 해서는 기존 자료를 채택하거나 덮어쓰지 않습니다.

```json
{
  "format": "chzzk.comment-timeline",
  "version": 1,
  "documents": [{
    "name": "가상 게임 목차",
    "aliases": [{"alias": "역할A", "streamer": "가상 방송인 A"}],
    "entries": [
      {"role": "chapter", "depth": 1, "startSec": 0, "endSec": 60, "title": "첫 게임"},
      {"startSec": 10, "title": "첫 만남 (w. 역할A)"},
      {"role": "highlight", "startSec": 20, "endSec": 25, "title": "결정적인 순간"}
    ]
  }]
}
```

| 필드 | 의미·조건 |
|---|---|
| `documents` | 1–100개의 원문 문서. 서로 다른 문서의 부모·구간·별칭을 섞지 않음 |
| 문서 `name` | 선택적 표시 이름; 소비자 표시 한도 120자 |
| `raw` 또는 `entries` | 둘 중 하나. `raw`는 기존 댓글 문자열을 그대로 보존. `entries`는 아래 의미 항목을 권고 Markdown으로 투영 |
| `aliases` | 선택적 문서별 가명 목록, 최대 100개. alias/streamer는 공백만으로 이루어지지 않은 80자 이하 문자열; 줄바꿈·대괄호·꺾쇠·슬래시 금지 |
| 항목 `startSec` | 0 이상의 안전한 정수, VOD 경과초 |
| `endSec` | 선택적 정수, 시작보다 뒤. 영상 범위·역할에 맞는지는 host 길이를 포함한 미리보기에서 확인 |
| `title` | 줄바꿈 없는 1,000자 이하 문자열 |
| `role` | 생략하면 `point`; `chapter`, `memo`, `watch`, `highlight`, `collab_context`. 예상 구간은 아래 현재 버전 제한 확인 |
| `depth` | chapter일 때 1–6; 부모 누락이나 겹침은 일반 댓글과 같은 진단 규칙 적용 |
| 루트 `videoNo` | CHZZK 소비자용 선택적 양의 영상 번호. 지정하면 현재 VOD와 같아야 함; 플랫폼 중립 시간 의미와 별개 |

**현재 0.3.23의 제한:** `entries`의 `role: "expected_highlight"` 직접 입력은 역할 대조 검사에서 거부됩니다. 문서 `raw`에 `[H?]` 범위를 담으면 하이라이트 역할과 검토 전 후보 상태를 보존합니다. [가상 요약 시간표 예제](examples/summary-timeline.json)와 [요약·로컬 JSON 사용 안내](docs/source/summary.md)를 참고하세요. 호환 파일은 ttaem.com에 먼저 게시할 필요가 없습니다.

입력은 250,000자 이하, 문서당 항목 최대 5,000개입니다. 본문·진단·완전성 및 영상 길이 규칙은 [의미 계약](SPEC.md)을 따릅니다. `point`는 순간이므로 `endSec`를 사용할 수 없습니다. 범위는 `memo` 또는 하이라이트 등 해당 역할로 지정하세요. 소비자는 Markdown으로 투영한 뒤 항목 수·역할·시작·명시한 끝·chapter 깊이가 입력과 같은지 확인합니다. 제목의 다른 타임코드나 구문 때문에 의미가 바뀌면 불러오기를 거부하고 원문 `raw` 사용을 안내합니다. 영상 밖 시간과 부모 구조 진단은 미리보기에서 확인합니다.

생성된 entries 본문에는 원래 자연어 댓글이 존재하지 않습니다. 소비자는 이를 원본 댓글이라고 주장하지 말아야 합니다. 원문 출처가 있으면 `raw`를 사용하세요. 현재 버전은 외부 `parentId`, 채널 URL/ID, 확정 싱크, 임의 실행 코드나 HTML을 가져오지 않습니다. `.txt` 평문 가져오기는 이전 호환 기능으로 유지합니다.

합성 JSON 예제는 [portable-timeline.json](examples/portable-timeline.json)입니다. 파일 전체를 임의 댓글에 붙여넣는 사용법은 권하지 않습니다.
