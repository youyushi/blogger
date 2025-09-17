# 📝 블로그 자동화 시스템

## ⚠️ 중요: 저장소 사용 제한사항

**이 저장소는 오직 블로그 자동 포스팅 전용입니다.**

### ✅ 허용되는 파일들
- `.github/workflows/blog-automation.yml` (블로그 자동화 워크플로우만)
- `enhanced_blog_automation.py` (메인 블로그 생성 스크립트)
- `post_history.json` (포스트 기록)
- `README.md`, `requirements.txt` 등 필수 파일
- Blogger API 관련 설정 파일

### ❌ 절대 금지
- **Threads 자동화 관련 코드** (별도 저장소: `threads-auto-posting`)
- 장어 관리 시스템 등 기타 프로젝트 코드
- Instagram API 관련 파일
- 관련 없는 HTML/CSS/JS 파일

### 🛡️ 보호 규칙
1. 직접 push 금지 - PR을 통해서만 변경
2. 모든 변경사항은 블로그 자동화 목적에만 한정
3. 파일명에 `threads`, `instagram`, `eel`, `jangeo` 등 포함 금지

---

## 🤖 현재 기능
- 매일 오후 1시(KST)에 AI가 자동으로 블로그 포스트 생성 및 발행
- Gemini AI를 통한 고품질 콘텐츠 자동 생성
- Unsplash를 통한 고해상도 이미지 자동 삽입
- 가독성 최적화된 HTML 템플릿 적용

## ✨ 주요 개선사항
- **텍스트 가독성 개선**: 진한 텍스트 색상(#111827) 적용
- **이미지 로딩 보장**: 직접 Unsplash URL 방식 사용
- **블로거 플랫폼 호환성**: `!important` CSS로 스타일 강제 적용
- **자동 히스토리 관리**: 중복 포스팅 방지 시스템

## 📋 워크플로우 스케줄
- 매일 오후 1시 (KST 13:00 = UTC 04:00)
- GitHub Actions를 통한 완전 자동화

**다른 목적의 코드는 해당 전용 저장소를 사용하세요!**