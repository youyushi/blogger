GitHub Actions 增强型博客自动化系统 v2.0（韩译中+核心解析）
 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 增强型博客自动化系统 v2.0
- 多种主题生成系统（30+ 基础主题）
- 基于 Gemini AI 生成高质量内容（2000-3000 字）
- Google Blogger API 自动发布
- 强化防重复系统
- 自动插入 Unsplash 高质量图片
- 美观的 HTML 模板（随机颜色主题）
- 定时发布与防重复
- 每日 1 次发布限制
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
    
    # 配置 Gemini API
    if config['gemini_api_key'] and config['gemini_api_key'] != '***':
        genai.configure(api_key=config['gemini_api_key'])
    else:
        print("❌ 缺少 Gemini API 密钥")
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
        # 仅保留最近 100 条记录
        if len(history) > 100:
            history = history[-100:]
        
        with open('post_history.json', 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 历史记录保存失败: {e}")

def generate_dynamic_topic():
    """生成多样且有创意的主题"""
    # 基础主题分类（大幅扩展）
    base_topics = [
        "AI 提示词工程", "ChatGPT 使用方法", "Claude 使用技巧", 
        "Gemini 高级功能", "AI 图像生成", "AI 音乐制作",
        "AI 编程助手", "AI 写作秘诀", "AI 翻译应用",
        "AI 数据分析", "机器学习基础", "深度学习入门",
        "AI 伦理与未来", "AI 商业应用", "AI 教育革新",
        "AI 创作工具", "AI 自动化系统", "AI 趋势分析",
        "Perplexity 搜索技巧", "Midjourney 使用方法", "Stable Diffusion 指南",
        "AI 视频编辑", "AI 演示文稿制作", "AI 营销策略",
        "无代码 AI 工具", "AI API 应用", "AI 插件推荐",
        "AI 安全与隐私", "AI 协作工具", "AI 提升生产力"
    ]
    
    # 修饰词/视角（多维度）
    modifiers = [
        "2025 年最新", "面向初学者", "专家分享",
        "实战", "5 分钟掌握", "完全精通", "核心总结",
        "避坑指南", "效率提升 200%", "免费入门",
        "成本节约", "时间缩短", "提升质量", "创意型",
        "实务应用", "案例研究", "对比分析", "深入学习",
        "问题排查", "优化指南", "成功案例", "克服失败",
        "分步式", "检查清单", "技巧合集", "隐藏功能"
    ]
    
    # 目标人群
    targets = [
        "职场人", "学生", "创业者", "自由职业者", "开发者",
        "设计师", "营销人员", "教育工作者", "研究员", "内容创作者",
        "博主", "YouTuber", "作家", "策划师", "中老年群体",
        "入门者", "中级用户", "高级用户", "团队负责人", "初创企业"
    ]
    
    # 特殊格式
    formats = [
        "指南", "检查清单", "对比分析", "问答",
        "访谈", "体验", "评测", "教程", "技巧合集",
        "案例研究", "实验结果", "基准测试", "路线图", "策略"
    ]
    
    # 随机组合生成独特主题
    topic_patterns = [
        f"{random.choice(modifiers)} {random.choice(base_topics)} {random.choice(formats)}",
        f"{random.choice(targets)}专用 {random.choice(base_topics)} {random.choice(formats)}",
        f"{random.choice(base_topics)} - {random.choice(modifiers)} {random.choice(formats)}",
        f"{random.choice(base_topics)}: {random.choice(targets)}的{random.choice(formats)}",
        f"[{datetime.now().strftime('%Y年%m月')}] {random.choice(base_topics)} {random.choice(modifiers)}总结"
    ]
    
    return random.choice(topic_patterns)

def check_duplicate(title: str, content: str, history: List) -> bool:
    """检查内容重复"""
    # 标题哈希值
    title_hash = hashlib.md5(title.encode()).hexdigest()
    
    for post in history:
        # 标题高度相似的情况
        if 'title_hash' in post and post['title_hash'] == title_hash:
            return True
        
        # 24 小时内重复讨论同一主题的情况
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
    """生成高质量图片 URL（直接使用 Unsplash 链接）"""
    # Unsplash 图片集合（直接使用 URL）
    unsplash_collections = {
        "ai_tech": [
            "https://images.unsplash.com/photo-1677442136019-21780ecad995",
            "https://images.unsplash.com/photo-1686191128892-3b5fdc17b7bf", 
            "https://images.unsplash.com/photo-1655635643532-b47e63c4a580",
            "https://images.unsplash.com/photo-1664906225771-ad618ea1fee8",
            "https://images.unsplash.com/photo-1675271591211-41ae13f0e71f",
            "https://images.unsplash.com/photo-1620712943543-bcc4688e7bd0",
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
            "https://images.unsplash.com/photo-1517245386807-d1c09bbb0fd4",
            "https://images.unsplash.com/photo-1523050854058-8df90110c9f1",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
            "https://images.unsplash.com/photo-1481627834876-b7833e8f5570",
            "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8"
        ],
        "creative": [
            "https://images.unsplash.com/photo-1626785774573-e9d366118b80",
            "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe",
            "https://images.unsplash.com/photo-1559028012-481c04fa702d",
            "https://images.unsplash.com/photo-1626447857058-2ba6a8868cb5",
            "https://images.unsplash.com/photo-1618004912476-29818d81ae2e",
            "https://images.unsplash.com/photo-1605810230434-7631ac76ec81",
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64",
            "https://images.unsplash.com/photo-1611162617474-5b21e879e113"
        ]
    }
    
    # 根据关键词选择合适的分类
    keyword_lower = keyword.lower()
    if any(term in keyword_lower for term in ["ai", "人工智能", "技术", "tech", "机器人", "自动"]):
        images = unsplash_collections["ai_tech"]
    elif any(term in keyword_lower for term in ["学习", "学习", "教育", "study", "learn"]):
        images = unsplash_collections["learning"]
    elif any(term in keyword_lower for term in ["工作", "职场", "work", "office", "商业"]):
        images = unsplash_collections["workspace"]
    else:
        images = unsplash_collections["creative"]
    
    # 随机选择 + 高质量参数
    selected_image = random.choice(images)
    # 直接使用 URL 确保图片加载成功
    return f"{selected_image}?w=1200&h=630&fit=crop&auto=format&q=85"

def generate_high_quality_content(topic: str) -> Dict:
    """生成高质量博客内容"""
    
    # 更详细具体的提示词
    prompt = f"""
    你是 AI 领域的专业博主，请围绕以下主题撰写一篇高质量博客文章。
    
    主题：{topic}
    
    要求：
    1. 标题：具有吸引力、让人想点击的标题（包含 1 个表情符号）
    2. 字数：2000-3000 字（内容足够详细）
    3. 结构：
       - 有趣的引言（吸引读者注意力）
       - 3-4 个主要章节（每个章节包含具体示例）
       - 5 个以上实战技巧
       - 2 个以上实际应用案例
       - 核心总结
       - 引导读者行动（CTA，如“点赞关注”）
    
    4. 语气风格：
       - 亲切易懂的解释
       - 专业且无压力的语气
       - 包含具体数据或数值
    
    5. 差异化亮点：
       - 其他博客中少见的独特见解
       - 加入个人经验或案例
       - 可直接应用于实务的技巧
    
    请以 JSON 格式返回：
    {{
        "title": "标题",
        "subtitle": "副标题",
        "content": "HTML 格式的正文",
        "tags": ["标签1", "标签2", ...],
        "summary": "一句话总结"
    }}
    """
    
    try:
        # 调用 Gemini API（允许更多令牌）
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.8,  # 提高创意性
                "max_output_tokens": 4000,  # 足够的长度
                "top_p": 0.9,
                "top_k": 40
            }
        )
        
        # 解析 JSON
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
            "subtitle": "与 AI 同行的智能生活",
            "content": f"<p>该主题的详细内容正在准备中。</p><p>随着 AI 技术的发展，我们的生活也在快速变化。</p>",
            "tags": ["AI", "人工智能", "自动化"],
            "summary": "AI 技术实用指南",
            "image_url": get_quality_image_url("AI")
        }

def create_beautiful_html(content_data: Dict) -> str:
    """生成美观的 HTML 文章 - 可读性优先"""
    # 安全的颜色主题（以可读性为核心）
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
    <html lang="ko">
    <head>
