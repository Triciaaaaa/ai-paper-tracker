#!/bin/bash
# AI 论文推送快捷脚本

# 飞书 Webhook URL（支持多群推送）
# 旧配置（单个群）：export FEISHU_WEBHOOK_URL="..."
# 新配置（多个群）：export FEISHU_WEBHOOK_URLS="url1 url2 url3"
export FEISHU_WEBHOOK_URLS="https://open.larkoffice.com/open-apis/bot/v2/hook/500ccd1b-2299-4bf6-82d2-71f64210beae https://open.larkoffice.com/open-apis/bot/v2/hook/14397166-3158-4ecc-8a9d-ccd465d3fac2 https://open.larkoffice.com/open-apis/bot/v2/hook/0374f779-efed-49d8-b612-6c81b5245293"

# AI 配置
export HF_ENABLE_AI_SUMMARY=true
export AI_PROVIDER=openai
export OPENAI_API_KEY="sk-swc4PI3baJ8oq8lZ8e58A789E62047DaB0653f7fD7396509"
export OPENAI_BASE_URL="https://api.gpt.ge"
export OPENAI_MODEL="gpt-4o"

# 可选：覆盖默认配置
# export HF_DAYS_BACK="7"       # 默认 7 天
# export HF_MAX_PAPERS="6"      # 默认 6 篇论文（优中选优）
# export HF_MAX_BLOGS="3"       # 默认 3 篇博客（只保留能获取全文的）
# export HF_BLOG_SOURCES="google_ai,deepmind,openai,lesswrong,microsoft_research,salesforce_ai,mit_tech_review,jeremykun,colah,distill"

# 论文类别过滤（关注数据工程与 VLM 训练）
export HF_CATEGORIES="vlm_data_strategy,data_engineering,training_data_strategy,data_methodology,vision_language,alignment"

# 其他可选类别：
# - vlm_data_strategy: VLM 训练数据策略
# - data_engineering: 数据工程体系
# - training_data_strategy: 训练数据策略
# - data_methodology: 前沿数据方法论
# - vision_language: 视觉语言模型
# - alignment: AI 对齐
# - reasoning: 推理能力
# - multimodal: 多模态模型
# - llm: 大语言模型
# 详见 CATEGORIES_GUIDE.md

# 推送数量配置（包含 AI 摘要和趋势总结）
export HF_MAX_PAPERS="6"      # 推送 6 篇论文
export HF_MAX_BLOGS="3"       # 推送 3 篇博客
export HF_INCLUDE_CLASSIC="true"  # 包含经典论文推荐

# Twitter 推文（可选，取消注释启用）
# export HF_ENABLE_TWITTER="true"                    # 启用 Twitter 推文抓取
# export TWITTER_ACCOUNTS="kaboroevich,ylecun,AndrewYNg,sama,hardmaru"  # 指定账号（逗号分隔）
# export TWITTER_ACCOUNTS_FILE="/path/to/accounts.txt"  # 或从文件加载（每行一个用户名）
# 方式1: twscrape 后端（推荐，需要 pip install twscrape）- 支持从关注列表自动获取账号
# export TWITTER_USERNAME="your_twitter_username"
# export TWITTER_PASSWORD="your_twitter_password"
# export TWITTER_EMAIL="your_email"
# export TWITTER_EMAIL_PASSWORD="your_email_password"
# 方式2: ntscraper 后端（pip install ntscraper）- 通过 Nitter 实例，不需要登录但不稳定

# 运行推送
python3 /Users/bytedance/ai-paper-tracker/hf_papers_advanced.py "$@"
