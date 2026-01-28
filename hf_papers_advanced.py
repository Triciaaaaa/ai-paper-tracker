#!/usr/bin/env python3
"""
🤖 Hugging Face Daily Papers 高级推送机器人
- 获取 HF Papers + 各大实验室博客
- AI 智能摘要
- 类别过滤
- 飞书推送
"""

import os
import sys
from datetime import datetime

from hf_paper_fetcher import HuggingFacePaperFetcher
from blog_fetcher import BlogFetcher
from ai_summarizer import AISummarizer, get_summarizer_from_env
from feishu_pusher import FeishuBotPusher, get_pusher_from_env
from classic_papers_extended import ClassicPaperFetcher, format_classic_paper_card


# ============ 配置区 ============

# 环境变量配置
DAYS_BACK = int(os.getenv('HF_DAYS_BACK', '7'))  # 减少到 7 天
MAX_PAPERS = int(os.getenv('HF_MAX_PAPERS', '6'))  # 减少到 6 篇，优中选优
MAX_BLOGS = int(os.getenv('HF_MAX_BLOGS', '3'))  # 减少到 3 篇，只保留高质量的
USE_TRENDING = os.getenv('HF_USE_TRENDING', 'false').lower() == 'true'

# 类别过滤（逗号分隔），默认只看核心领域
CATEGORY_FILTERS = os.getenv('HF_CATEGORIES', 'rl_verification,alignment,ai4math,auto_formalization')
CATEGORY_FILTERS = [c.strip() for c in CATEGORY_FILTERS.split(',') if c.strip()] if CATEGORY_FILTERS else None

# 博客源（默认使用有活跃 RSS 的源）
# 企业博客: google_ai, deepmind, openai, microsoft_research, salesforce_ai, anthropic
# 个人博客: lesswrong, jeremykun, colah, distill
# AI 媒体: mit_tech_review
BLOG_SOURCES = os.getenv('HF_BLOG_SOURCES', 'google_ai,deepmind,openai,lesswrong,microsoft_research,salesforce_ai,mit_tech_review,jeremykun,colah,distill')
BLOG_SOURCES = [s.strip() for s in BLOG_SOURCES.split(',') if s.strip()]

# AI 摘要配置（默认启用）
ENABLE_AI_SUMMARY = os.getenv('HF_ENABLE_AI_SUMMARY', 'true').lower() == 'true'
AI_PROVIDER = os.getenv('AI_PROVIDER', 'claude')  # 默认用 Claude

# 是否包含经典论文
INCLUDE_CLASSIC = os.getenv('HF_INCLUDE_CLASSIC', 'true').lower() == 'true'


# ============ 主逻辑 ============

def format_datetime(date_str: str) -> str:
    """格式化日期时间"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_str[:19] if date_str else ''


def generate_trend_summary(summarizer, papers: list, blogs: list) -> str:
    """生成研究趋势总结"""
    try:
        # 构建内容摘要
        content_parts = []

        if papers:
            content_parts.append("## 论文\n")
            for i, p in enumerate(papers[:5], 1):
                content_parts.append(f"{i}. {p['title']}\n")

        if blogs:
            content_parts.append("\n## 博客\n")
            for i, b in enumerate(blogs[:3], 1):
                content_parts.append(f"{i}. {b['title']}\n")

        content = '\n'.join(content_parts)

        prompt = f"""基于以下今天收集的 AI 研究论文和博客文章，总结当前的研究趋势：

{content}

请用中文回答，200-300 字，重点分析：
1. 主要研究方向有哪些？
2. 有哪些新的技术趋势或方法？
3. 整体呈现出什么发展态势？

直接给出总结，不需要客套话。"""

        # 调用 LLM 生成趋势总结
        import os
        if os.getenv('OPENAI_BASE_URL') or summarizer.provider == 'openai':
            import openai
            base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            if not base_url.endswith('/v1'):
                base_url = base_url.rstrip('/') + '/v1'

            client = openai.OpenAI(api_key=summarizer.api_key, base_url=base_url)

            response = client.chat.completions.create(
                model=summarizer.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个 AI 研究趋势分析师，擅长从大量研究内容中提炼关键趋势。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.7
            )

            summary = response.choices[0].message.content.strip()
            print(f"✅ 趋势总结生成成功，长度: {len(summary)} 字符")
            return summary

    except Exception as e:
        print(f"⚠️  趋势总结生成失败: {e}")
        return None


def main():
    """主函数"""

    print("=" * 60)
    print("🤖 HF Daily Papers + 博客 高级推送机器人")
    print("=" * 60)

    # 检查推送配置
    pusher = get_pusher_from_env()
    if not pusher:
        print("❌ 未配置飞书 Webhook")
        print("\n请设置环境变量:")
        print("  export FEISHU_WEBHOOK_URL='你的webhook地址'")
        return 1

    print(f"📱 推送方式: 飞书群聊机器人")
    print(f"📅 获取天数: {DAYS_BACK} 天")
    print(f"📊 最多论文: {MAX_PAPERS} 篇")
    print(f"📰 博客源: {', '.join(BLOG_SOURCES)}")
    print(f"🏷️  类别过滤: {', '.join(CATEGORY_FILTERS) if CATEGORY_FILTERS else '无'}")
    print(f"🤖 AI 摘要: {AI_PROVIDER if ENABLE_AI_SUMMARY else '禁用'}")
    print(f"📚 经典论文: {'包含' if INCLUDE_CLASSIC else '不包含'}")

    # 初始化 AI 摘要器
    summarizer = None
    if ENABLE_AI_SUMMARY:
        summarizer = get_summarizer_from_env()
        if not summarizer.api_key:
            print(f"⚠️  未配置 {AI_PROVIDER} API key，跳过 AI 摘要")
            summarizer = None

    # ========== 1. 获取 HF 论文 ==========
    print("\n" + "=" * 60)
    print("📚 获取 Hugging Face 论文")
    print("=" * 60)

    fetcher = HuggingFacePaperFetcher(
        days_back=DAYS_BACK,
        max_papers=MAX_PAPERS,
        category_filters=CATEGORY_FILTERS
    )

    if USE_TRENDING:
        papers = fetcher.fetch_trending_papers()
    else:
        papers = fetcher.fetch_recent_papers()

    if not papers:
        print("⚠️  未找到符合条件的论文")
        papers = []

    # AI 摘要处理
    if summarizer:
        print(f"\n🤖 生成 AI 详细解读...")
        for i, paper in enumerate(papers):
            print(f"  [{i+1}/{len(papers)}] {paper['title'][:40]}...")

            # 总是调用 LLM 生成详细解读（不再使用简短的 HF 摘要）
            summary = summarizer.summarize_paper(paper, use_hf_summary=False)
            if summary:
                paper['ai_enhanced_summary'] = summary
            else:
                # 如果 LLM 失败，使用 HF 摘要作为备选
                if paper.get('ai_summary'):
                    paper['ai_enhanced_summary'] = f"📌 **HF AI**: {paper['ai_summary']}"
                else:
                    paper['ai_enhanced_summary'] = None

    # ========== 2. 获取博客文章 ==========
    print("\n" + "=" * 60)
    print("📰 获取博客文章")
    print("=" * 60)

    blog_fetcher = BlogFetcher(days_back=DAYS_BACK * 2, max_articles=MAX_BLOGS)
    blogs = blog_fetcher.fetch_blogs(BLOG_SOURCES, fetch_full_content=summarizer is not None)

    # 过滤：只保留能获取到全文的博客
    if blogs:
        original_count = len(blogs)
        blogs = [b for b in blogs if b.get('full_content')]
        filtered_count = original_count - len(blogs)
        if filtered_count > 0:
            print(f"  📋 过滤掉 {filtered_count} 篇无法获取全文的博客")

    # 限制最终数量（优中选优，只保留最新的几篇）
    if blogs and len(blogs) > MAX_BLOGS:
        print(f"  🎯 从 {len(blogs)} 篇中精选最新的 {MAX_BLOGS} 篇")
        blogs = blogs[:MAX_BLOGS]

    # 为博客生成简短 AI 解读
    if summarizer and blogs:
        print(f"\n🤖 生成博客 AI 解读...")
        for i, blog in enumerate(blogs):
            print(f"  [{i+1}/{len(blogs)}] {blog['title'][:40]}...")
            summary = summarizer.summarize_blog(blog)
            if summary:
                blog['ai_summary'] = summary
            else:
                blog['ai_summary'] = None

    if not blogs:
        print("⚠️  未找到博客文章")
        blogs = []

    # ========== 3. 获取经典论文 ==========
    classic_paper = None
    if INCLUDE_CLASSIC:
        print("\n" + "=" * 60)
        print("📖 获取经典论文推荐")
        print("=" * 60)

        classic_fetcher = ClassicPaperFetcher(
            categories=['reinforcement_learning', 'alignment', 'ai4math', 'formal_verification', 'llm', 'information_theory']
        )
        classic_paper = classic_fetcher.get_random_paper()
        if classic_paper:
            # 添加关键词解析
            keywords_analysis = classic_fetcher.format_keywords_analysis(classic_paper)
            print(f"✅ 今日推荐: {classic_paper['title']}")
            if keywords_analysis:
                print(f"   关键词: {', '.join(classic_paper.get('keywords', [])[:5])}")
        else:
            print("⚠️  未找到经典论文")

    # ========== 4. 生成研究趋势总结 ==========
    trend_summary = None
    if summarizer and (papers or blogs):
        print("\n" + "=" * 60)
        print("📊 生成研究趋势总结")
        print("=" * 60)

        trend_summary = generate_trend_summary(summarizer, papers, blogs)

    # ========== 5. 构建推送内容 ==========
    print("\n" + "=" * 60)
    print("📝 构建推送消息")
    print("=" * 60)

    card = build_enhanced_card(papers, blogs, classic_paper, trend_summary)
    print(f"✅ 构建完成")

    # ========== 5. 发送推送 ==========
    print("\n" + "=" * 60)
    print("📤 发送到飞书")
    print("=" * 60)

    success = pusher.send_interactive_card(card)

    if success:
        print(f"\n✅ 推送成功！")
        print(f"\n📊 统计:")
        print(f"  • 论文数: {len(papers)}")
        print(f"  • 博客数: {len(blogs)}")
        print(f"  • AI 摘要: {'是' if ENABLE_AI_SUMMARY else '否'}")
    else:
        print(f"\n❌ 推送失败")
        return 1

    print("\n" + "=" * 60)
    return 0


def build_enhanced_card(papers: list, blogs: list, classic_paper: dict = None, trend_summary: str = None) -> dict:
    """构建增强版飞书卡片"""

    elements = []

    # ========== 标题区 ==========
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"**📊 论文: {len(papers)} 篇 | 博客: {len(blogs)} 篇**\n**⏰ {now}**"
        }
    })

    elements.append({"tag": "hr"})

    # ========== 趋势总结区 ==========
    if trend_summary:
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📈 今日研究趋势**\n\n{trend_summary}"
            }
        })

        elements.append({"tag": "hr"})

    # ========== 经典论文区（放在前面） ==========
    if classic_paper:
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**📖 每日经典论文推荐**"
            }
        })

        # 经典论文内容（包含关键词解析）
        classic_content = f"**{classic_paper['title']}** ({classic_paper.get('year', 'N/A')})\n\n"
        classic_content += f"👥 **作者**: {classic_paper['authors']}\n\n"
        classic_content += f"📝 **简介**: {classic_paper['description']}\n\n"

        # 添加关键词解析
        keywords = classic_paper.get('keywords', [])
        if keywords:
            classic_content += f"🔑 **核心概念**: {', '.join(keywords[:5])}"
            if len(keywords) > 5:
                classic_content += f" 等 {len(keywords)} 个关键词"
            classic_content += "\n\n"

        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": classic_content
            }
        })

        elements.append({
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "查看论文"},
                    "type": "default",
                    "url": classic_paper['url']
                }
            ]
        })

        elements.append({"tag": "hr"})

    # ========== 论文区 ==========
    if papers:
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**📚 Hugging Face 论文**"
            }
        })

        for i, paper in enumerate(papers, 1):
            # 标题
            title_text = f"**{i}. {paper['title']}**"
            if paper.get('categories'):
                tags = ' '.join([f"`{cat}`" for cat in paper['categories'][:3]])
                title_text += f"\n🏷️  {tags}"

            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": title_text
                }
            })

            # 作者和发布时间
            meta_lines = []
            if paper.get('author_str'):
                meta_lines.append(f"👥 {paper['author_str']}")
            if paper.get('published'):
                meta_lines.append(f"📅 {format_datetime(paper['published'])}")

            if meta_lines:
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": ' | '.join(meta_lines)
                    }
                })

            # 摘要（AI 解读优先）
            if paper.get('ai_enhanced_summary'):
                # AI 解读，显示更多内容
                summary = paper['ai_enhanced_summary']
                # 飞书卡片内容限制，适当截断
                if len(summary) > 1500:
                    summary = summary[:1500] + '\n\n... (内容过长，已截断)'
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": summary
                    }
                })
            elif paper.get('summary'):
                # 原始摘要
                summary = paper['summary']
                if len(summary) > 300:
                    summary = summary[:300] + '...'
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"📝 {summary}"
                    }
                })

            # 链接按钮
            actions = [
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "查看论文"},
                    "type": "default",
                    "url": paper['paper_url']
                }
            ]

            if paper.get('pdf_url'):
                actions.append({
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "下载 PDF"},
                    "type": "primary",
                    "url": paper['pdf_url']
                })

            if paper.get('project_page'):
                actions.append({
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "项目主页"},
                    "type": "default",
                    "url": paper['project_page']
                })

            elements.append({
                "tag": "action",
                "actions": actions
            })

            # 分隔线
            if i < len(papers):
                elements.append({"tag": "hr"})

    # ========== 博客区 ==========
    if blogs:
        elements.append({"tag": "hr"})
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": "**📰 实验室博客**"
            }
        })

        for blog in blogs[:5]:  # 最多显示 5 篇
            # 标题和元信息
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**• {blog['title']}**\n🏢 {blog['source']} | 📅 {format_datetime(blog['published'])}"
                }
            })

            # 链接按钮
            elements.append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "阅读文章"},
                        "type": "default",
                        "url": blog['link']
                    }
                ]
            })

            # 分隔线
            if blogs.index(blog) < min(len(blogs), 5) - 1:
                elements.append({"tag": "hr"})

    # ========== 构建卡片 ==========
    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "🤖 AI Research Daily"
            },
            "template": "blue"
        },
        "elements": elements
    }

    return card


if __name__ == "__main__":
    sys.exit(main())
