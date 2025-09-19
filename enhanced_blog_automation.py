#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions용 향상된 블로그 자동화 시스템 v2.0
- 다양한 토픽 생성 시스템 (30+ 기본 주제)
- Gemini AI로 고품질 콘텐츠 생성 (2000-3000자)
- Google Blogger API 자동 포스팅
- 중복 방지 시스템 강화
- Unsplash 고품질 이미지 자동 삽입
- 아름다운 HTML 템플릿 (랜덤 색상 테마)
- 스케줄링 및 중복 방지
- 하루 1회 포스팅 제한
"""

import os
import json
import sys
import argparse
import hashlib
import random
import time
from datetime import datetime, timedelta
import requests
import google.generativeai as genai
from typing import Dict, List, Optional

def load_config():
    """설정 로드"""
    config = {
        'google_client_id': os.environ.get('GOOGLE_CLIENT_ID', '***'),
        'google_client_secret': os.environ.get('GOOGLE_CLIENT_SECRET', '***'),
        'blog_id': os.environ.get('BLOGGER_BLOG_ID', '***'),
        'gemini_api_key': os.environ.get('GEMINI_API_KEY', '***')
    }
    
    # 토큰 정보 로드
    try:
        with open('blogger_token.json', 'r', encoding='utf-8') as f:
            token_data = json.load(f)
            config['token_data'] = token_data
    except:
        print("❌ blogger_token.json 로드 실패")
        return None
    
    # Gemini API 설정
    if config['gemini_api_key'] and config['gemini_api_key'] != '***':
        genai.configure(api_key=config['gemini_api_key'])
    else:
        print("❌ Gemini API 키가 없습니다")
        return None
    
    return config

def load_post_history():
    """포스팅 히스토리 로드"""
    try:
        with open('post_history.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_post_history(history):
    """포스팅 히스토리 저장"""
    try:
        # 최근 100개만 유지
        if len(history) > 100:
            history = history[-100:]
        
        with open('post_history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 히스토리 저장 실패: {e}")

def generate_dynamic_topic():
    """다양하고 창의적인 토픽 생성"""
    # 기본 주제 카테고리 (대폭 확장)
    base_topics = [
        "AI 프롬프트 엔지니어링", "ChatGPT 활용법", "Claude 사용 팁", 
        "Gemini 고급 기능", "AI 이미지 생성", "AI 음악 제작",
        "AI 코딩 도우미", "AI 글쓰기 비법", "AI 번역 활용",
        "AI 데이터 분석", "머신러닝 기초", "딥러닝 입문",
        "AI 윤리와 미래", "AI 비즈니스 활용", "AI 교육 혁신",
        "AI 창작 도구", "AI 자동화 시스템", "AI 트렌드 분석",
        "Perplexity 검색 팁", "Midjourney 사용법", "Stable Diffusion 가이드",
        "AI 영상 편집", "AI 프레젠테이션", "AI 마케팅 전략",
        "노코드 AI 도구", "AI API 활용", "AI 플러그인 추천",
        "AI 보안과 프라이버시", "AI 협업 도구", "AI 생산성 향상"
    ]
    
    # 수식어/관점 (다양한 각도)
    modifiers = [
        "2025년 최신", "초보자를 위한", "전문가가 알려주는",
        "실전", "5분 마스터", "완전정복", "핵심정리",
        "실수하지 않는", "효율 200% 높이는", "무료로 시작하는",
        "비용 절감", "시간 단축", "퀄리티 높이는", "창의적인",
        "실무 적용", "케이스 스터디", "비교 분석", "심화 학습",
        "트러블슈팅", "최적화 가이드", "성공 사례", "실패 극복",
        "단계별", "체크리스트", "꿀팁 모음", "숨겨진 기능"
    ]
    
    # 타겟 대상
    targets = [
        "직장인", "학생", "창업자", "프리랜서", "개발자",
        "디자이너", "마케터", "교육자", "연구원", "콘텐츠 크리에이터",
        "블로거", "유튜버", "작가", "기획자", "중장년층",
        "입문자", "중급자", "고급 사용자", "팀리더", "스타트업"
    ]
    
    # 특별 포맷
    formats = [
        "가이드", "체크리스트", "비교 분석", "Q&A",
        "인터뷰", "후기", "리뷰", "튜토리얼", "팁 모음",
        "사례 연구", "실험 결과", "벤치마크", "로드맵", "전략"
    ]
    
    # 랜덤 조합으로 독특한 토픽 생성
    topic_patterns = [
        f"{random.choice(modifiers)} {random.choice(base_topics)} {random.choice(formats)}",
        f"{random.choice(targets)}을 위한 {random.choice(base_topics)} {random.choice(formats)}",
        f"{random.choice(base_topics)} - {random.choice(modifiers)} {random.choice(formats)}",
        f"{random.choice(base_topics)}: {random.choice(targets)}의 {random.choice(formats)}",
        f"[{datetime.now().strftime('%Y년 %m월')}] {random.choice(base_topics)} {random.choice(modifiers)} 정리"
    ]
    
    return random.choice(topic_patterns)

def check_duplicate(title: str, content: str, history: List) -> bool:
    """중복 콘텐츠 체크"""
    # 제목 해시
    title_hash = hashlib.md5(title.encode()).hexdigest()
    
    for post in history:
        # 제목이 너무 유사한 경우
        if 'title_hash' in post and post['title_hash'] == title_hash:
            return True
        
        # 같은 주제를 24시간 내 다시 다룬 경우
        if 'timestamp' in post:
            try:
                post_time = datetime.fromisoformat(post['timestamp'])
                if (datetime.now() - post_time).total_seconds() < 86400:
                    if 'topic' in post and title.lower() in post['topic'].lower():
                        return True
            except:
                pass
    
    return False

def get_quality_image_url(keyword: str) -> str:
    """고품질 이미지 URL 생성 (Unsplash 직접 URL)"""
    # Unsplash 이미지 컬렉션 (직접 URL 사용)
    unsplash_collections = {
        "ai_tech": [
            "https://images.unsplash.com/photo-1677442136019-21780ecad995",
            "https://images.unsplash.com/photo-1697577418970-95d99b5a55cf", 
            "https://images.unsplash.com/photo-1718241905696-cb34c2c07bed",
            "https://images.unsplash.com/photo-1739805591936-39f03383c9a9",
            "https://images.unsplash.com/photo-1710993011836-108ba89ebe51",
            "https://images.unsplash.com/photo-1677756119517-756a188d2d94",
            "https://images.unsplash.com/photo-1535378917042-10a22c95931a",
            "https://images.unsplash.com/photo-1555255707-c07966088b7b"
        ],
        "workspace": [
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085",
            "https://images.unsplash.com/photo-1521737604893-d14cc237f11d",
            "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158",
            "https://images.unsplash.com/photo-1518770660439-4636190af475",
            "https://images.unsplash.com/photo-1461749280684-dccba630e2f6",
            "https://images.unsplash.com/photo-1504639725590-34d0984388bd",
            "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d",
            "https://images.unsplash.com/photo-1496181133206-80ce9b88a853"
        ],
        "learning": [
            "https://images.unsplash.com/photo-1513258496099-48168024aec0",
            "https://images.unsplash.com/photo-1501504905252-473c47e087f8",
            "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
            "https://images.unsplash.com/photo-1550592704-6c76defa9985",
            "https://images.unsplash.com/photo-1546410531-bb4caa6b424d",
            "https://images.unsplash.com/photo-1604933834215-2a64950311bd",
            "https://images.unsplash.com/photo-1481627834876-b7833e8f5570",
            "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8"
        ],
        "creative": [
            "https://images.unsplash.com/photo-1560421683-6856ea585c78",
            "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe",
            "https://images.unsplash.com/photo-1559028012-481c04fa702d",
            "https://images.unsplash.com/photo-1626447857058-2ba6a8868cb5",
            "https://images.unsplash.com/photo-1618004912476-29818d81ae2e",
            "https://images.unsplash.com/photo-1605810230434-7631ac76ec81",
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64",
            "https://images.unsplash.com/photo-1611162617474-5b21e879e113"
        ]
    }
    
    # 키워드에 따라 적절한 카테고리 선택
    keyword_lower = keyword.lower()
    if any(term in keyword_lower for term in ["ai", "인공지능", "기술", "tech", "로봇", "자동"]):
        images = unsplash_collections["ai_tech"]
    elif any(term in keyword_lower for term in ["학습", "공부", "교육", "study", "learn"]):
        images = unsplash_collections["learning"]
    elif any(term in keyword_lower for term in ["업무", "직장", "work", "office", "비즈니스"]):
        images = unsplash_collections["workspace"]
    else:
        images = unsplash_collections["creative"]
    
    # 랜덤 선택 + 고품질 파라미터
    selected_image = random.choice(images)
    # 직접 URL 사용으로 이미지 로딩 보장
    return f"{selected_image}?w=1200&h=630&fit=crop&auto=format&q=85"

def generate_high_quality_content(topic: str) -> Dict:
    """고품질 블로그 콘텐츠 생성"""
    
    # 더 상세하고 구체적인 프롬프트
    prompt = f"""
    당신은 AI 분야 전문 블로거입니다. 다음 주제로 고품질 블로그 포스트를 작성하세요.
    
    주제: {topic}
    
    요구사항:
    1. 제목: 클릭하고 싶은 매력적인 제목 (이모지 1개 포함)
    2. 길이: 2000-3000자 (충분히 상세하게)
    3. 구성:
       - 흥미로운 도입부 (독자 관심 유발)
       - 3-4개의 주요 섹션 (각각 구체적인 예시 포함)
       - 실전 팁 5개 이상
       - 실제 활용 사례 2개 이상
       - 핵심 요약
       - 독자 행동 유도 (CTA)
    
    4. 톤앤매너:
       - 친근하고 이해하기 쉬운 설명
       - 전문적이면서도 부담없는 어투
       - 구체적인 수치나 데이터 포함
    
    5. 차별화 포인트:
       - 다른 블로그에서 보기 어려운 독특한 인사이트
       - 개인적 경험이나 사례 추가
       - 실무에 바로 적용 가능한 팁
    
    JSON 형식으로 응답하세요:
    {{
        "title": "제목",
        "subtitle": "부제목",
        "content": "HTML 형식의 본문",
        "tags": ["태그1", "태그2", ...],
        "summary": "한 줄 요약"
    }}
    """
    
    try:
        # Gemini API 호출 (더 많은 토큰 허용)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.8,  # 창의성 증가
                "max_output_tokens": 4000,  # 충분한 길이
                "top_p": 0.9,
                "top_k": 40
            }
        )
        
        # JSON 파싱
        content_text = response.text
        if "```json" in content_text:
            content_text = content_text.split("```json")[1].split("```")[0]
        elif "```" in content_text:
            content_text = content_text.split("```")[1].split("```")[0]
        
        result = json.loads(content_text)
        
        # 이미지 추가
        image_keyword = topic.split()[0] if topic else "AI"
        result['image_url'] = get_quality_image_url(image_keyword)
        
        return result
        
    except Exception as e:
        print(f"콘텐츠 생성 오류: {e}")
        # 폴백 콘텐츠
        return {
            "title": f"🤖 {topic}",
            "subtitle": "AI와 함께하는 스마트한 일상",
            "content": f"<p>이 주제에 대한 자세한 내용을 준비 중입니다.</p><p>AI 기술의 발전과 함께 우리의 일상도 빠르게 변화하고 있습니다.</p>",
            "tags": ["AI", "인공지능", "자동화"],
            "summary": "AI 기술을 활용한 실용적인 가이드",
            "image_url": get_quality_image_url("AI")
        }

def create_beautiful_html(content_data: Dict) -> str:
    """아름다운 HTML 포스트 생성 - 가독성 최우선"""
    # 안전한 색상 테마 (가독성 중심)
    themes = [
        {"primary": "#2563eb", "secondary": "#1e40af", "accent": "#dc2626"},  # 파란색 테마
        {"primary": "#059669", "secondary": "#047857", "accent": "#ea580c"},  # 초록색 테마
        {"primary": "#7c3aed", "secondary": "#6d28d9", "accent": "#dc2626"},  # 보라색 테마
        {"primary": "#dc2626", "secondary": "#b91c1c", "accent": "#2563eb"},  # 빨간색 테마
        {"primary": "#ea580c", "secondary": "#dc2626", "accent": "#059669"}   # 오렌지 테마
    ]
    theme = random.choice(themes)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
            
            /* 중요: 모든 스타일에 !important로 강제 적용 */
            * {{
                box-sizing: border-box;
            }}
            
            /* 블로거 기본 스타일 완전 재정의 */
            body, .post-body, .post-content, .Blog, .blog-post, article, main, div {{
                background-color: #ffffff !important;
                color: #111827 !important;
            }}
            
            /* 모든 텍스트 요소 명시적 색상 - 더 진한 색상 */
            p, span, li, td, th {{
                color: #111827 !important;
                background-color: transparent !important;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                color: #000000 !important;
                background-color: transparent !important;
            }}
            
            /* 링크 색상 */
            a {{
                color: {theme['primary']} !important;
                text-decoration: none !important;
                background-color: transparent !important;
            }}
            
            a:hover {{
                color: {theme['secondary']} !important;
                text-decoration: underline !important;
            }}
            
            /* 코드 블록 스타일 */
            code, pre {{
                background-color: #f3f4f6 !important;
                color: #111827 !important;
                padding: 2px 6px !important;
                border-radius: 4px !important;
            }}
        </style>
    </head>
    <body style="background-color: #ffffff !important; margin: 0; padding: 20px; color: #111827 !important;">
        <article style="max-width: 900px; margin: 0 auto; font-family: 'Noto Sans KR', sans-serif; 
                        line-height: 1.8; color: #111827 !important; background-color: #ffffff !important; 
                        padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
            
            <!-- 히어로 섹션 -->
            <header style="background: linear-gradient(135deg, {theme['primary']} 0%, {theme['secondary']} 100%); 
                           padding: 60px 40px; border-radius: 20px; color: #ffffff !important; margin-bottom: 40px;
                           box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
                <h1 style="font-size: 42px; font-weight: 900; margin: 0 0 15px 0; 
                           text-shadow: 0 2px 4px rgba(0,0,0,0.2); color: #ffffff !important;">
                    {content_data.get('title', 'AI 블로그')}
                </h1>
                <p style="font-size: 20px; font-weight: 300; opacity: 0.95; margin: 0; color: #ffffff !important;">
                    {content_data.get('subtitle', 'AI와 함께하는 스마트한 일상')}
                </p>
            </header>
            
            <!-- 메인 이미지 (확실하게 표시) -->
            <div style="margin: 40px 0; text-align: center;">
                <img src="{content_data.get('image_url', 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&h=630&fit=crop&auto=format&q=85')}" 
                     alt="{content_data.get('title', 'AI 이미지')}"
                     loading="lazy"
                     onerror="this.src='https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&h=630&fit=crop&auto=format&q=85'"
                     style="width: 100%; max-width: 100%; height: auto; 
                            border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                            display: block; margin: 0 auto;">
                <p style="margin-top: 15px; color: #6b7280 !important; font-size: 14px;">
                    {content_data.get('summary', '')}
                </p>
            </div>
            
            <!-- 본문 콘텐츠 컨테이너 -->
            <div style="background-color: #ffffff !important; padding: 30px; border-radius: 12px; 
                        margin: 30px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                <div class="content-wrapper" style="font-size: 18px; line-height: 1.9; color: #111827 !important;">
                    {content_data.get('content', '')}
                </div>
            </div>
            
            <!-- 태그 섹션 -->
            <footer style="margin-top: 60px; padding-top: 30px; border-top: 2px solid #e5e7eb; 
                           background-color: #ffffff !important;">
                <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
                    {"".join([f'<span style="background: {theme["accent"]}20; color: {theme["accent"]} !important; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 500;">#{tag}</span>' for tag in content_data.get('tags', [])])}
                </div>
                
                <div style="background: #f8fafc !important; padding: 25px; border-radius: 12px; 
                            border-left: 4px solid {theme['primary']}; color: #1f2937 !important;">
                    <p style="margin: 0; color: #4b5563 !important; font-size: 16px;">
                        💡 이 글이 도움이 되셨나요? 더 많은 AI 팁과 가이드를 원하신다면 
                        구독과 좋아요를 눌러주세요!
                    </p>
                </div>
            </footer>
            
        </article>
        
        <!-- 강제 스타일 적용 스크립트 -->
        <script>
            // DOM이 로드된 후 스타일 강제 적용
            window.onload = function() {{
                // 모든 텍스트 요소의 색상을 강제로 설정
                const allElements = document.querySelectorAll('*');
                allElements.forEach(function(element) {{
                    // 헤더와 푸터 제외
                    if (!element.closest('header') && !element.classList.contains('tag')) {{
                        element.style.setProperty('background-color', 'transparent', 'important');
                        
                        // 텍스트 요소인 경우 색상 설정
                        if (element.tagName.match(/^(P|SPAN|DIV|LI|TD|TH)$/i)) {{
                            element.style.setProperty('color', '#111827', 'important');
                        }}
                        // 제목 요소
                        if (element.tagName.match(/^H[1-6]$/i)) {{
                            element.style.setProperty('color', '#000000', 'important');
                        }}
                    }}
                }});
                
                // body와 article 배경색 강제 설정
                document.body.style.setProperty('background-color', '#ffffff', 'important');
                document.body.style.setProperty('color', '#111827', 'important');
                
                const article = document.querySelector('article');
                if (article) {{
                    article.style.setProperty('background-color', '#ffffff', 'important');
                    article.style.setProperty('color', '#111827', 'important');
                }}
                
                // 블로거 특정 클래스 재정의
                const bloggerElements = document.querySelectorAll('.post-body, .post-content, .Blog, .blog-posts');
                bloggerElements.forEach(function(element) {{
                    element.style.setProperty('background-color', '#ffffff', 'important');
                    element.style.setProperty('color', '#111827', 'important');
                }});
                
                // 본문 콘텐츠 강제 스타일
                const contentWrapper = document.querySelector('.content-wrapper');
                if (contentWrapper) {{
                    contentWrapper.style.setProperty('color', '#111827', 'important');
                    const contentParagraphs = contentWrapper.querySelectorAll('p, span, div');
                    contentParagraphs.forEach(function(p) {{
                        p.style.setProperty('color', '#111827', 'important');
                        p.style.setProperty('background-color', 'transparent', 'important');
                    }});
                }}
            }};
        </script>
    </body>
    </html>
    """
    
    return html

def post_to_blog(config, title, content, labels=None):
    """블로그에 포스팅"""
    token_data = config['token_data']
    
    # 토큰 갱신이 필요한 경우 처리
    if 'refresh_token' in token_data:
        refresh_data = {
            'client_id': config['google_client_id'],
            'client_secret': config['google_client_secret'],
            'refresh_token': token_data['refresh_token'],
            'grant_type': 'refresh_token'
        }
        
        try:
            refresh_response = requests.post('https://oauth2.googleapis.com/token', data=refresh_data)
            if refresh_response.status_code == 200:
                new_tokens = refresh_response.json()
                token_data['token'] = new_tokens['access_token']
                print("✅ 토큰 자동 갱신 완료")
            else:
                print("⚠️ 토큰 갱신 실패, 기존 토큰 사용")
        except:
            print("⚠️ 토큰 갱신 중 오류, 기존 토큰 사용")
    
    # 블로그 포스팅
    headers = {
        'Authorization': f'Bearer {token_data["token"]}',
        'Content-Type': 'application/json'
    }
    
    post_data = {
        'kind': 'blogger#post',
        'blog': {'id': config['blog_id']},
        'title': title,
        'content': content,
        'labels': labels or ['AI', '블로그', '테크']
    }
    
    url = f'https://www.googleapis.com/blogger/v3/blogs/{config["blog_id"]}/posts'
    
    try:
        response = requests.post(url, headers=headers, json=post_data)
        
        if response.status_code == 200:
            post = response.json()
            print('✅ 블로그 포스팅 성공!')
            print(f'제목: {post.get("title")}')
            print(f'URL: {post.get("url")}')
            return post
        else:
            print(f'❌ 포스팅 실패: {response.status_code}')
            print(response.text)
            return None
    except Exception as e:
        print(f'❌ 포스팅 중 오류: {e}')
        return None

def should_post_today(history, max_posts_per_day=1):
    """오늘 포스팅 가능 여부 확인 - 하루 1회로 제한"""
    today = datetime.now().strftime('%Y-%m-%d')
    today_posts = []
    
    for post in history:
        try:
            if 'timestamp' in post:
                post_date = datetime.fromisoformat(post['timestamp']).strftime('%Y-%m-%d')
                if post_date == today:
                    today_posts.append(post)
        except:
            pass
    
    return len(today_posts) < max_posts_per_day

def main():
    parser = argparse.ArgumentParser(description='Enhanced Blog Automation v2.0')
    parser.add_argument('--topic', help='특정 주제로 포스팅')
    parser.add_argument('--labels', help='포스트 라벨 (쉼표 구분)')
    parser.add_argument('--auto', action='store_true', help='자동 모드')
    
    args = parser.parse_args()
    
    print("🚀 개선된 블로그 자동화 시스템 v2.0 시작")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 설정 로드
    config = load_config()
    if not config:
        print("❌ 설정 로드 실패")
        sys.exit(1)
    
    print("✅ 설정 로드 완료")
    
    # 포스팅 히스토리 확인
    history = load_post_history()
    
    if args.auto:
        if not should_post_today(history):
            print("⏸️ 오늘 포스팅 한도 달성 (1회), 건너뛰기")
            return
    
    # 1. 다이나믹 토픽 생성
    max_attempts = 5
    selected_topic = None
    
    for attempt in range(max_attempts):
        topic = args.topic if args.topic else generate_dynamic_topic()
        print(f"\n📝 생성된 토픽 (시도 {attempt + 1}): {topic}")
        
        # 2. 중복 체크
        if not check_duplicate(topic, "", history):
            selected_topic = topic
            break
        else:
            print("⚠️ 유사한 토픽이 최근에 포스팅됨. 새 토픽 생성...")
            time.sleep(1)
    
    if not selected_topic:
        selected_topic = generate_dynamic_topic()
        print(f"🔄 최종 토픽: {selected_topic}")
    
    # 3. 고품질 콘텐츠 생성
    print("✍️ AI 고품질 콘텐츠 생성 중...")
    content_data = generate_high_quality_content(selected_topic)
    
    # 4. HTML 포맷팅
    print("🎨 프리미엄 HTML 템플릿 적용 중...")
    html_content = create_beautiful_html(content_data)
    
    # 5. 라벨 처리
    labels = []
    if args.labels:
        labels = [label.strip() for label in args.labels.split(',')]
    else:
        labels = content_data.get('tags', ['AI', '인공지능', '블로그'])
    
    # 6. 블로그 포스팅
    print("📝 블로그 포스팅 중...")
    post_result = post_to_blog(config, content_data['title'], html_content, labels)
    
    # 7. 히스토리 저장
    if post_result:
        new_post = {
            'timestamp': datetime.now().isoformat(),
            'title': content_data['title'],
            'title_hash': hashlib.md5(content_data['title'].encode()).hexdigest(),
            'topic': selected_topic,
            'url': post_result.get('url'),
            'labels': labels,
            'method': 'github_actions_v2',
            'success': True
        }
        
        history.append(new_post)
        save_post_history(history)
        
        print("\n🎉 블로그 자동화 완료!")
        print(f"📌 제목: {content_data['title']}")
        print(f"🏷️ 태그: {', '.join(labels)}")
        print(f"🔗 URL: {post_result.get('url', 'N/A')}")
    else:
        print("\n❌ 블로그 자동화 실패")
        sys.exit(1)

if __name__ == "__main__":
    main()
