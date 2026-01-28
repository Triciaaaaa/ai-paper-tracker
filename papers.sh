#!/bin/bash
# AI 论文推送快捷脚本

# 飞书 Webhook URL
export FEISHU_WEBHOOK_URL="https://open.larkoffice.com/open-apis/bot/v2/hook/500ccd1b-2299-4bf6-82d2-71f64210beae"

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

# 运行推送
python3 /Users/bytedance/ai-paper-tracker/hf_papers_advanced.py "$@"
