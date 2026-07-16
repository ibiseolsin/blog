# blog

Jekyll(minima 테마) 기반 GitHub Pages 블로그.

🔗 https://dabi-hookingpoint.github.io/blog/

## 새 글 작성

`_posts/` 폴더에 아래 형식으로 마크다운 파일을 추가하면 됩니다.

```
_posts/YYYY-MM-DD-제목.md
```

파일 상단에는 다음과 같은 front matter가 필요합니다.

```yaml
---
layout: post
title: "글 제목"
date: YYYY-MM-DD HH:MM:SS +0900
categories: general
---

본문 내용
```

`main` 브랜치에 push하면 GitHub Pages가 자동으로 빌드해 배포합니다.

## 로컬에서 미리보기

```bash
bundle install
bundle exec jekyll serve
```

> Ruby 3.0 이상이 필요합니다 (`github-pages` gem 의존성).

## 구조

- `_config.yml` — 사이트 설정 (제목, 설명, 테마 등)
- `_posts/` — 블로그 글
- `about.md` — 소개 페이지
- `index.md` — 홈(글 목록)
