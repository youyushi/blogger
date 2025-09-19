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
    """加载配置"""
    config = {
        'google_client_id': os.environ.get('GOOGLE_CLIENT_ID', '***'),
        'google_client_secret': os.environ.get('GOOGLE_CLIENT_SECRET', '***'),
        'blog_id': os.environ.get('BLOGGER_BLOG_ID', '***'),
        'gemini_api_key': os.environ.get('GEMINI_API_KEY', '***')
    }
    
    # 加载令牌信息
    try:
        with open('blogger_token.json', 'r', encoding='utf-8') as f:
            token_data = json.load(f)
            config['token_data'] = token_data
    except:
        print("❌ blogger_token.json 加载失败")
        return None
    
    # Gemini API 设置
    if config['gemini_api_key'] and config['gemini_api_key'] != '***':
        genai.configure(api_key=config['gemini_api_key'])
    else:
        print("❌ Gemini API 密钥不存在")
        return None
    
    return config

def load_post_history():
    """加载发布历史"""
    try:
        with open('post_history.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_post_history(history):
    """保存发布历史"""
    try:
        # 只保留最近100条
        if len(history) > 100:
            history = history[-100:]
        
        with open('post_history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 历史保存失败: {e}")

def generate_dynamic_topic():
    """生成多样化和创造性的主题"""
    # 基本主题类别（大幅扩展）
    base_topics = [
        "AI 提示工程", "ChatGPT 使用技巧", "Claude 使用提示", 
        "Gemini 高级功能", "AI 图像生成", "AI 音乐制作",
        "AI 编程助手", "AI 写作技巧", "AI 翻译应用",
        "AI 数据分析", "机器学习基础", "深度学习入门",
        "AI 伦理与未来", "AI 商业应用", "AI 教育革新",
        "AI 创作工具", "AI 自动化系统", "AI 趋势分析",
        "Perplexity 搜索技巧", "Midjourney 使用指南", "Stable Diffusion 指南",
        "AI 视频编辑", "AI 演示文稿", "AI 营销策略",
        "无代码 AI 工具", "AI API 应用", "AI 插件推荐",
        "AI 安全与隐私", "AI 协作工具", "AI 生产力提升"
    ]
    
    # 修饰语/视角（多种角度）
    modifiers = [
        "2025年最新", "初学者指南", "专家分享",
        "实战", "5分钟掌握", "完全攻略", "核心要点",
        "避免常见错误", "效率提升200%", "免费开始",
        "成本节约", "时间缩短", "质量提升", "创意",
        "实际应用", "案例研究", "比较分析", "深入学习",
        "故障排除", "优化指南", "成功案例", "克服失败",
        "分步指南", "检查清单", "实用技巧", "隐藏功能"
    ]
    
    # 目标受众
    targets = [
        "职场人士", "学生", "创业者", "自由职业者", "开发者",
        "设计师", "营销人员", "教育工作者", "研究人员", "内容创作者",
        "博主", "YouTuber", "作家", "策划人员", "中老年人群",
        "入门者", "中级用户", "高级用户", "团队领导", "初创企业"
    ]
    
    # 特殊格式
    formats = [
        "指南", "检查清单", "比较分析", "问答",
        "访谈", "体验报告", "评测", "教程", "技巧合集",
        "案例研究", "实验结果", "基准测试", "路线图", "策略"
    ]
    
    # 随机组合生成独特主题
    topic_patterns = [
        f"{random.choice(modifiers)} {random.choice(base_topics)} {random.choice(formats)}",
        f"{random.choice(targets)}的{random.choice(base_topics)} {random.choice(formats)}",
        f"{random.choice(base_topics)} - {random.choice(modifiers)} {random.choice(formats)}",
        f"{random.choice(base_topics)}: {random.choice(targets)}的{random.choice(formats)}",
        f"[{datetime.now().strftime('%Y年%m月')}] {random.choice(base_topics)} {random.choice(modifiers)} 总结"
    ]
    
    return random.choice(topic_patterns)

def check_duplicate(title: str, content: str, history: List) -> bool:
    """检查重复内容"""
    # 标题哈希
    title_hash = hashlib.md5(title.encode()).hexdigest()
    
    for post in history:
        # 标题过于相似的情况
        if 'title_hash' in post and post['title_hash'] == title_hash:
            return True
        
        # 24小时内再次讨论相同主题的情况
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
    """生成高质量图片URL（直接使用Unsplash URL）"""
    # Unsplash 图片集合（直接URL使用）
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
    
    # 根据关键词选择合适类别
    keyword_lower = keyword.lower()
    if any(term in keyword_lower for term in ["ai", "人工智能", "技术", "tech", "机器人", "自动"]):
        images = unsplash_collections["ai_tech"]
    elif any(term in keyword_lower for term in ["学习", "教育", "study", "learn"]):
        images = unsplash_collections["learning"]
    elif any(term in keyword_lower for term in ["工作", "职场", "work", "office", "商业"]):
        images = unsplash_collections["workspace"]
    else:
        images = unsplash_collections["creative"]
    
    # 随机选择 + 高质量参数
    selected_image = random.choice(images)
    # 直接使用URL确保图片加载
    return f"{selected_image}?w=1200&h=630&fit=crop&auto=format&q=85"

def generate_high_quality_content(topic: str) -> Dict:
    """生成高质量博客内容"""
    
    # 更详细和具体的提示
    prompt = f"""
    您是AI领域的专业博主。请根据以下主题撰写高质量的博客文章。
    
    主题: {topic}
    
    要求:
    1. 标题: 吸引人的标题（包含1个表情符号）
    2. 长度: 2000-3000字（足够详细）
    3. 结构:
       - 有趣的引言（吸引读者兴趣）
       - 3-4个主要部分（每个包含具体示例）
       - 5个以上实用技巧
       - 2个以上实际应用案例
       - 核心要点总结
       - 引导读者行动（CTA）
    
    4. 语气风格:
       - 友好且易于理解的解释
       - 专业但不生硬的语调
       - 包含具体数据或数字
    
    5. 差异化点:
       - 其他博客中少见的独特见解
       - 添加个人经验或案例
       - 可直接应用于实际的技巧
    
    请以JSON格式回复:
    {{
        "title": "标题",
        "subtitle": "副标题",
        "content": "HTML格式的正文",
        "tags": ["标签1", "标签2", ...],
        "summary": "一句话摘要"
    }}
    """
    
    try:
        # Gemini API 调用（允许更多令牌）
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.8,  # 增加创造性
                "max_output_tokens": 4000,  # 足够长度
                "top_p": 0.9,
                "top_k": 40
            }
        )
        
        # JSON 解析
        content_text = response.text
        if "```json" in content_text:
            content_text = content_text.split("```json")[1].split("```")[0]
        elif "```" in content_text:
            content_text = content_text.split("```")[1].split("```")[0]
        
        result = json.loads(content_text)
        
        # 添加图片
        image_keyword = topic.split()[0] if topic else "AI"
        result['image_url'] = get_quality_image_url(image_keyword)
        
        return result
        
    except Exception as e:
        print(f"内容生成错误: {e}")
        # 备用内容
        return {
            "title": f"🤖 {topic}",
            "subtitle": "与AI一起的智能生活",
            "content": f"<p>关于此主题的详细内容正在准备中。</p><p>随着AI技术的发展，我们的日常生活也在快速变化。</p>",
            "tags": ["AI", "人工智能", "自动化"],
            "summary": "AI技术应用的实用指南",
            "image_url": get_quality_image_url("AI")
        }

def create_beautiful_html(content_data: Dict) -> str:
    """创建美观的HTML帖子 - 优先考虑可读性"""
    # 安全的颜色主题（以可读性为中心）
    themes = [
        {"primary": "#2563eb", "secondary": "#1e40af", "accent": "#dc2626"},  # 蓝色主题
        {"primary": "#059669", "secondary": "#047857", "accent": "#ea580c"},  # 绿色主题
        {"primary": "#7c3aed", "secondary": "#6d28d9", "accent": "#dc2626"},  # 紫色主题
        {"primary": "#dc2626", "secondary": "#b91c1c", "accent": "#2563eb"},  # 红色主题
        {"primary": "#ea580c", "secondary": "#dc2626", "accent": "#059669"}   # 橙色主题
    ]
    theme = random.choice(themes)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');
            
            /* 重要: 所有样式使用!important强制应用 */
            * {{
                box-sizing: border-box;
            }}
            
            /* 完全重写Blogger默认样式 */
            body, .post-body, .post-content, .Blog, .blog-post, article, main, div {{
                background-color: #ffffff !important;
                color: #111827 !important;
            }}
            
            /* 所有文本元素的明确颜色 - 更深颜色 */
            p, span, li, td, th {{
                color: #111827 !important;
                background-color: transparent !important;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                color: #000000 !important;
                background-color: transparent !important;
            }}
            
            /* 链接颜色 */
            a {{
                color: {theme['primary']} !important;
                text-decoration: none !important;
                background-color: transparent !important;
            }}
            
            a:hover {{
                color: {theme['secondary']} !important;
                text-decoration: underline !important;
            }}
            
            /* 代码块样式 */
            code, pre {{
                background-color: #f3f4f6 !important;
                color: #111827 !important;
                padding: 2px 6px !important;
                border-radius: 4px !important;
            }}
        </style>
    </head>
    <body style="background-color: #ffffff !important; margin: 0; padding: 20px; color: #111827 !important;">
        <article style="max-width: 900px; margin: 0 auto; font-family: 'Noto Sans SC', sans-serif; 
                        line-height: 1.8; color: #111827 !important; background-color: #ffffff !important; 
                        padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
            
            <!-- 英雄区域 -->
            <header style="background: linear-gradient(135deg, {theme['primary']} 0%, {theme['secondary']} 100%); 
                           padding: 60px 40px; border-radius: 20px; color: #ffffff !important; margin-bottom: 40px;
                           box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
                <h1 style="font-size: 42px; font-weight: 900; margin: 0 0 15px 0; 
                           text-shadow: 0 2px 4px rgba(0,0,0,0.2); color: #ffffff !important;">
                    {content_data.get('title', 'AI博客')}
                </h1>
                <p style="font-size: 20px; font-weight: 300; opacity: 0.95; margin: 0; color: #ffffff !important;">
                    {content_data.get('subtitle', '与AI一起的智能生活')}
                </p>
            </header>
            
            <!-- 主图片（确保显示） -->
            <div style="margin: 40px 0; text-align: center;">
                <img src="{content_data.get('image_url', 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&h=630&fit=crop&auto=format&q=85')}" 
                     alt="{content_data.get('title', 'AI图片')}"
                     loading="lazy"
                     onerror="this.src='https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&h=630&fit=crop&auto=format&q=85'"
                     style="width: 100%; max-width: 100%; height: auto; 
                            border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                            display: block; margin: 0 auto;">
                <p style="margin-top: 15px; color: #6b7280 !important; font-size: 14px;">
                    {content_data.get('summary', '')}
                </p>
            </div>
            
            <!-- 正文内容容器 -->
            <div style="background-color: #ffffff !important; padding: 30px; border-radius: 12px; 
                        margin: 30px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                <div class="content-wrapper" style="font-size: 18px; line-height: 1.9; color: #111827 !important;">
                    {content_data.get('content', '')}
                </div>
            </div>
            
            <!-- 标签区域 -->
            <footer style="margin-top: 60px; padding-top: 30px; border-top: 2px solid #e5e7eb; 
                           background-color: #ffffff !important;">
                <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
                    {"".join([f'<span style="background: {theme["accent"]}20; color: {theme["accent"]} !important; padding: 8px 16px; border-radius: 20px; font-size: 14px; font-weight: 500;">#{tag}</span>' for tag in content_data.get('tags', [])])}
                </div>
                
                <div style="background: #f8fafc !important; padding: 25px; border-radius: 12px; 
                            border-left: 4px solid {theme['primary']}; color: #1f2937 !important;">
                    <p style="margin: 0; color: #4b5563 !important; font-size: 16px;">
                        💡 这篇文章对您有帮助吗？如果您需要更多AI技巧和指南，
                        请订阅并点赞！
                    </p>
                </div>
            </footer>
            
        </article>
        
        <!-- 强制样式应用脚本 -->
        <script>
            // DOM加载后强制应用样式
            window.onload = function() {{
                // 强制设置所有文本元素的颜色
                const allElements = document.querySelectorAll('*');
                allElements.forEach(function(element) {{
                    // 排除页眉和页脚
                    if (!element.closest('header') && !element.classList.contains('tag')) {{
                        element.style.setProperty('background-color', 'transparent', 'important');
                        
                        // 设置文本元素的颜色
                        if (element.tagName.match(/^(P|SPAN|DIV|LI|TD|TH)$/i)) {{
                            element.style.setProperty('color', '#111827', 'important');
                        }}
                        // 标题元素
                        if (element.tagName.match(/^H[1-6]$/i)) {{
                            element.style.setProperty('color', '#000000', 'important');
                        }}
                    }}
                }});
                
                // 强制设置body和article的背景色
                document.body.style.setProperty('background-color', '#ffffff', 'important');
                document.body.style.setProperty('color', '#111827', 'important');
                
                const article = document.querySelector('article');
                if (article) {{
                    article.style.setProperty('background-color', '#ffffff', 'important');
                    article.style.setProperty('color', '#111827', 'important');
                }}
                
                // 重写Blogger特定类
                const bloggerElements = document.querySelectorAll('.post-body, .post-content, .Blog, .blog-posts');
                bloggerElements.forEach(function(element) {{
                    element.style.setProperty('background-color', '#ffffff', 'important');
                    element.style.setProperty('color', '#111827', 'important');
                }});
                
                // 强制设置正文内容样式
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
    """发布到博客"""
    token_data = config['token_data']
    
    # 需要令牌刷新时的处理
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
                print("✅ 令牌自动刷新完成")
            else:
                print("⚠️ 令牌刷新失败，使用现有令牌")
        except:
            print("⚠️ 令牌刷新错误，使用现有令牌")
    
    # 博客发布
    headers = {
        'Authorization': f'Bearer {token_data["token"]}',
        'Content-Type': 'application/json'
    }
    
    post_data = {
        'kind': 'blogger#post',
        'blog': {'id': config['blog_id']},
        'title': title,
        'content': content,
        'labels': labels or ['AI', '博客', '科技']
    }
    
    url = f'https://www.googleapis.com/blogger/v3/blogs/{config["blog_id"]}/posts'
    
    try:
        response = requests.post(url, headers=headers, json=post_data)
        
        if response.status_code == 200:
            post = response.json()
            print('✅ 博客发布成功!')
            print(f'标题: {post.get("title")}')
            print(f'URL: {post.get("url")}')
            return post
        else:
            print(f'❌ 发布失败: {response.status_code}')
            print(response.text)
            return None
    except Exception as e:
        print(f'❌ 发布过程中出错: {e}')
        return None

def should_post_today(history, max_posts_per_day=1):
    """检查今天是否可以发布 - 限制每天1次"""
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
    parser = argparse.ArgumentParser(description='增强版博客自动化 v2.0')
    parser.add_argument('--topic', help='使用特定主题发布')
    parser.add_argument('--labels', help='帖子标签（逗号分隔）')
    parser.add_argument('--auto', action='store_true', help='自动模式')
    
    args = parser.parse_args()
    
    print("🚀 增强版博客自动化系统 v2.0 启动")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    if not config:
        print("❌ 配置加载失败")
        sys.exit(1)
    
    print("✅ 配置加载完成")
    
    # 检查发布历史
    history = load_post_history()
    
    if args.auto:
        if not should_post_today(history):
            print("⏸️ 今日发布限额已达 (1次)，跳过")
            return
    
    # 1. 生成动态主题
    max_attempts = 5
    selected_topic = None
    
    for attempt in range(max_attempts):
        topic = args.topic if args.topic else generate_dynamic_topic()
        print(f"\n📝 生成的主题 (尝试 {attempt + 1}): {topic}")
        
        # 2. 重复检查
        if not check_duplicate(topic, "", history):
            selected_topic = topic
            break
        else:
            print("⚠️ 最近已发布类似主题。生成新主题...")
            time.sleep(1)
    
    if not selected_topic:
        selected_topic = generate_dynamic_topic()
        print(f"🔄 最终主题: {selected_topic}")
    
    # 3. 生成高质量内容
    print("✍️ AI生成高质量内容中...")
    content_data = generate_high_quality_content(selected_topic)
    
    # 4. HTML格式化
    print("🎨 应用高级HTML模板中...")
    html_content = create_beautiful_html(content_data)
    
    # 5. 标签处理
    labels = []
    if args.labels:
        labels = [label.strip() for label in args.labels.split(',')]
    else:
        labels = content_data.get('tags', ['AI', '人工智能', '博客'])
    
    # 6. 博客发布
    print("📝 博客发布中...")
    post_result = post_to_blog(config, content_data['title'], html_content, labels)
    
    # 7. 保存历史
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
        
        print("\n🎉 博客自动化完成!")
        print(f"📌 标题: {content_data['title']}")
        print(f"🏷️ 标签: {', '.join(labels)}")
        print(f"🔗 URL: {post_result.get('url', 'N/A')}")
    else:
        print("\n❌ 博客自动化失败")
        sys.exit(1)

if __name__ == "__main__":

    main()

