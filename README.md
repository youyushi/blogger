# 📝 博客自动化系统

## ⚠️ 重要：仓库使用限制说明

**此仓库仅用于博客自动发布专用**

### ✅ 允许的文件
- `.github/workflows/blog-automation.yml` (仅限博客自动化工作流)
- `enhanced_blog_automation.py` (主博客生成脚本)
- `post_history.json` (发布历史记录)
- `README.md`, `requirements.txt` 等必需文件
- Blogger API 相关配置文件

### ❌ 严格禁止
- **Threads自动化相关代码** (独立仓库: `threads-auto-posting`)
- 鳗鱼管理系统等其他项目代码
- Instagram API 相关文件
- 无关的 HTML/CSS/JS 文件

### 🛡️ 保护规则
1. 禁止直接 push - 仅通过 PR 进行变更
2. 所有变更必须仅限于博客自动化目的
3. 文件名禁止包含 `threads`, `instagram`, `eel`, `jangeo` 等关键词

---

## 🤖 当前功能
- 每天下午1点(KST)AI自动生成并发布博客文章
- 通过Gemini AI实现高质量内容自动生成
- 通过Unsplash自动插入高清图片
- 应用了阅读体验优化的HTML模板

## ✨ 主要改进
- **文本可读性提升**: 使用深文字颜色(#111827)
- **确保图片加载**: 采用直接Unsplash URL方式
- **博客平台兼容性**: 使用`!important` CSS强制应用样式
- **自动历史记录管理**: 防重复发布系统

## 📋 工作流计划
- 每天下午1点 (KST 13:00 = UTC 04:00)
- 通过GitHub Actions实现全自动化

**其他用途的代码请使用对应的专用仓库！**
