📝 博客自动化系统

⚠️ 重要：存储库使用限制

此存储库仅用于博客自动发布专用。

✅ 允许的文件

· .github/workflows/blog-automation.yml (仅博客自动化工作流)
· enhanced_blog_automation.py (主博客生成脚本)
· post_history.json (发布历史记录)
· README.md、requirements.txt 等必要文件
· Blogger API 相关配置文件

❌ 绝对禁止

· Threads 自动化相关代码 (独立存储库: threads-auto-posting)
· 鳗鱼管理系统等其他项目代码
· Instagram API 相关文件
· 无关的 HTML/CSS/JS 文件

🛡️ 保护规则

1. 禁止直接 push - 仅允许通过 PR 进行变更
2. 所有变更必须仅限于博客自动化目的
3. 文件名中禁止包含 threads、instagram、eel、jangeo 等字样

---

🤖 当前功能

· 每天下午 1点(KST) AI 自动生成博客文章并发布
· 通过 Gemini AI 实现高质量内容自动生成
· 通过 Unsplash 自动插入高分辨率图片
· 应用针对可读性优化的 HTML 模板

✨ 主要改进

· 文本可读性改进: 应用深色文本颜色(#111827)
· 确保图片加载: 使用直接 Unsplash URL 方式
· Blogger 平台兼容性: 使用 !important CSS 强制应用样式
· 自动历史记录管理: 重复发布防止系统

📋 工作流计划

· 每天下午 1点 (KST 13:00 = UTC 04:00)
· 通过 GitHub Actions 实现完全自动化

其他目的的代码请使用相应的专用存储库！
