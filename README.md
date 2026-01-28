# 🤖 AI Paper Daily Tracker

自动推送 AI 论文和实验室博客到飞书群的机器人。

## ✨ 功能

- 📚 **Hugging Face Daily Papers** - 获取最新 AI 论文
- 📰 **实验室博客** - Google AI, DeepMind, OpenAI, Anthropic 等
- 🤖 **AI 智能摘要** - 使用 GPT-4 生成中文解读
- 📖 **经典论文推荐** - 每日推送 AI 领域经典论文
- 📊 **研究趋势总结** - 自动分析当日研究趋势
- 📱 **飞书推送** - 精美的卡片式消息推送

## 🚀 部署方式

### GitHub Actions（推荐，完全免费）✨

#### 1. 创建 GitHub 仓库
```bash
git init
git add .
git commit -m "Initial commit"

# 创建新仓库并推送
gh repo create ai-paper-tracker --public --source=.
git push -u origin main
```

#### 2. 配置 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

**Settings → Secrets and variables → Actions → New repository secret**

| Secret 名称 | 值 |
|------------|---|
| `FEISHU_WEBHOOK_URL` | 你的飞书 Webhook URL |
| `OPENAI_API_KEY` | 你的 OpenAI API Key |

#### 3. 测试运行

前往 GitHub 仓库的 **Actions** 页面，手动触发工作流测试。

#### 4. 定时任务

工作流会在每天中午12点（北京时间）自动运行。

---

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export FEISHU_WEBHOOK_URL="你的webhook地址"
export OPENAI_API_KEY="你的API key"

# 运行
./papers.sh
```

### crontab 定时任务（本地）

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天12点运行）
0 12 * * * /Users/bytedance/ai-paper-tracker/papers-wrapper.sh >> /Users/bytedance/logs/paper-cron.log 2>&1
```

---

## ⚙️ 配置选项

环境变量配置：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HF_DAYS_BACK` | 7 | 获取最近几天的论文 |
| `HF_MAX_PAPERS` | 6 | 最多推送几篇论文 |
| `HF_MAX_BLOGS` | 3 | 最多推送几篇博客 |
| `HF_ENABLE_AI_SUMMARY` | true | 是否启用 AI 摘要 |
| `AI_PROVIDER` | openai | AI 提供商 |

## 📁 项目结构

```
ai-paper-tracker/
├── .github/
│   └── workflows/
│       └── daily-paper.yml      # GitHub Actions 工作流
├── hf_papers_advanced.py         # 主程序
├── hf_paper_fetcher.py           # 论文获取模块
├── blog_fetcher.py               # 博客获取模块
├── ai_summarizer.py              # AI 摘要模块
├── feishu_pusher.py              # 飞书推送模块
├── classic_papers_extended.py    # 经典论文模块
├── papers.sh                     # 主运行脚本
├── papers-wrapper.sh             # crontab 包装脚本
├── config.json                   # 配置文件
└── requirements.txt              # Python 依赖
```

## 📊 支持的博客源

- Google AI Blog
- DeepMind Blog
- OpenAI Blog
- Microsoft Research Blog
- Salesforce AI Research
- MIT Technology Review
- LessWrong (AI Alignment 社区)
- Distill.pub (交互式科学出版物)

## 🔧 依赖

- Python 3.9+
- requests
- feedparser
- beautifulsoup4
- lxml
- html2text
- openai

## 📝 日志

- GitHub Actions 日志：仓库 Actions 页面查看
- 本地日志：`/Users/bytedance/logs/` 目录

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
