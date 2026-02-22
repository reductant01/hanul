# 커밋 메시지 원칙

커밋 제목은 **Conventional Commits** 형식을 따른다.

- **형식**: `<타입>(<범위>): <요약>`
- **타입**
  - `feat`: 새 기능
  - `fix`: 버그 수정
  - `docs`: 문서만 수정
  - `style`: 코드 포맷/스타일 (동작 변경 없음)
  - `refactor`: 리팩터링
  - `test`: 테스트 추가/수정
  - `chore`: 빌드·설정·기타
- **범위**: 선택. 변경된 모듈/폴더 (예: `controller`, `config`)
- **요약**: 50자 내외, 동사 현재형, 마침표 생략

**예시**
- `feat(nav2): loc 모드에 Nav2 bringup 연동`
- `fix(ros_bridge): 스트래이프 방향 반전`
- `docs: 커밋 원칙 README에 정리`
