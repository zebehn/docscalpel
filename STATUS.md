---
project: docscalpel
purpose: 학술 PDF에서 그림·표·수식을 DocLayout-YOLO로 검출해 요소별 PDF 파일로 잘라 내는 Python 라이브러리·명령행 도구를 제공한다.
status: 운영
stage: v1.1.0 기능 구현을 마치고 발표자료 생성 도구(paperdeck, 논문 세미나 발표자료 스킬)의 그림 추출 단계에서 쓰이고 있음. 마지막 코드 변경은 2026-01-10임 (기준일 2026-09-25).
updated: 2026-09-25
next:
  - CHANGELOG.md의 릴리스 날짜(2025-01-08, 2025-01-09)를 커밋 날짜(2026-01-09)와 대조해 정정
  - pyproject.toml 의존성에 huggingface_hub 명시 여부 검토
  - docs/technical-blog-post.md에 남은 개발 환경 절대 경로 1건 제거
decisions:
  - PyPI 배포 진행 여부
blockers: []
resources: []
related:
  - paperdeck
docs:
  - README.md
  - CHANGELOG.md
  - INSTALL.md
  - docs/CLI_MANUAL.md
  - docs/QUICKSTART_CLI.md
  - docs/technical-blog-post.md
---

# DocScalpel 현황

> 기재 정책: zebehn/mastermind docs/STATUS_POLICY.md (v1.0). 최종 갱신 2026-09-25 (KST).

## 요약

DocScalpel은 학술 PDF에서 그림·표·수식을 검출해 요소별 PDF로 잘라 내는 도구이다. 현재 v1.1.0이며 다른 도구의 그림 추출 단계에서 쓰이고 있다. 가장 가까운 다음 단계는 문서 표기 정리와 PyPI 배포 여부 결정이다.

## 현재 단계

- 버전은 1.1.0이다(pyproject.toml, setup.py, `__version__` 일치).
- 검출 모델은 DocLayout-YOLO(Hugging Face 저장소 juliozhao/DocLayout-YOLO-DocStructBench)이다.
- 라이브러리 API와 명령행 도구(`python -m docscalpel`, `docscalpel`)가 있다.
- 캡션 번호 파싱, 다중 영역 그림 병합, 하위 그림 병합이 v1.1.0에 들어 있다.
- 테스트 함수는 163개가 정의되어 있다(tests/ 아래 `def test_` 기준).
- README는 134개 통과, 커버리지 76%라고 적고 있다. 이번 점검에서 테스트를 실행하지 않았다 [미확인].
- README의 성능 수치는 25쪽 논문 1편, CPU 추론 기준 67.73초이다. 이번 점검에서 재측정하지 않았다.
- PyPI에는 배포되지 않았다(2026-09-25 PyPI 조회 결과 없음). INSTALL.md는 PyPI 설치를 "Coming Soon"으로 적고 있다.
- GitHub 릴리스와 태그는 없다. 이슈와 PR은 0건이다.
- 알려진 문제: CHANGELOG.md의 릴리스 날짜가 커밋 날짜와 1년 어긋난다.
- 알려진 문제: 검출기 코드가 huggingface_hub를 가져오지만 pyproject.toml 의존성에 없다. 전이 의존성으로 설치되는지는 [미확인].
- 알려진 문제: README의 커버리지 명령이 이전 경로(`--cov=src`)를 가리킨다.

## 최근 진행

- 2026-01-10 버전 불일치 문제 해결 안내를 INSTALL.md에 추가
- 2026-01-09 pyproject.toml과 setup.py의 버전 번호를 1.1.0으로 정정
- 2026-01-09 v1.1.0 반영: 하위 그림 병합, 캡션 연결 개선
- 2025-12-30 캡션이 그림 위에 있거나 잘못 검출된 경우의 캡션 연결 수정
- 2025-12-30 캡션 파싱과 다중 영역 그림 병합 추가

## 다음 할 일

- CHANGELOG.md의 릴리스 날짜(2025-01-08, 2025-01-09)를 커밋 날짜(2026-01-09)와 대조해 정정
- pyproject.toml 의존성에 huggingface_hub 명시 여부 검토
- docs/technical-blog-post.md에 남은 개발 환경 절대 경로 1건 제거

## 결정 대기

- PyPI 배포 진행 여부. 선택지는 배포 또는 저장소 설치 유지이다. 현재 사용처는 모두 저장소에서 직접 설치한다.

## 차단 요인

- 없음

## 핵심 문서

- [README.md](README.md): 기능, 사용법, 구조, 성능 수치
- [CHANGELOG.md](CHANGELOG.md): 버전별 변경 내역
- [INSTALL.md](INSTALL.md): 설치 방법과 문제 해결
- [docs/CLI_MANUAL.md](docs/CLI_MANUAL.md): 명령행 도구 설명서
- [docs/QUICKSTART_CLI.md](docs/QUICKSTART_CLI.md): 명령행 도구 빠른 시작
- [docs/technical-blog-post.md](docs/technical-blog-post.md): 구조와 구현 설명

## 관련 저장소

- paperdeck: requirements.txt에서 이 저장소를 git 주소로 설치해 그림·표 추출에 쓴다.
