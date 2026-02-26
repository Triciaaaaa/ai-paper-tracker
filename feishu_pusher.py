#!/usr/bin/env python3
"""
📤 飞书群聊机器人推送模块
通过自定义机器人 Webhook 推送消息到飞书群聊
"""

import requests
import json
from typing import List, Dict, Optional


class FeishuBotPusher:
    """飞书群聊自定义机器人推送器（支持单群和多群推送）"""

    def __init__(self, webhook_url: str = None, webhook_urls: list = None):
        """
        初始化推送器

        Args:
            webhook_url: 飞书机器人的 Webhook URL（单群）
            webhook_urls: 飞书机器人的 Webhook URL 列表（多群）
        """
        self.webhook_url = webhook_url
        self.webhook_urls = webhook_urls or []
        if webhook_url:
            self.webhook_urls.append(webhook_url)
        self.session = requests.Session()

    def send_text(self, content: str) -> bool:
        """
        发送文本消息

        Args:
            content: 文本内容

        Returns:
            是否发送成功
        """
        payload = {
            "msg_type": "text",
            "content": {"text": content}
        }

        return self._send(payload)

    def send_post(self, title: str, content: List[Dict[str, str]]) -> bool:
        """
        发送富文本消息（推荐）

        Args:
            title: 消息标题
            content: 内容列表，每个元素是 {"tag": "标签", "text": "文本"}

        Returns:
            是否发送成功
        """
        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": content
                    }
                }
            }
        }

        return self._send(payload)

    def send_interactive_card(self, card: Dict) -> bool:
        """
        发送交互式卡片消息

        Args:
            card: 卡片内容（JSON 格式）

        Returns:
            是否发送成功
        """
        payload = {
            "msg_type": "interactive",
            "card": card
        }

        return self._send(payload)

    def format_papers_card(self, papers: List[Dict]) -> Dict:
        """
        格式化论文列表为飞书卡片

        Args:
            papers: 论文列表

        Returns:
            飞书卡片字典
        """
        from datetime import datetime

        # 构建卡片元素
        elements = []

        # 添加统计信息
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📊 共 {len(papers)} 篇论文**\n**⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}**"
            }
        })

        elements.append({"tag": "hr"})

        # 添加每篇论文
        for i, paper in enumerate(papers, 1):
            # 论文标题
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{i}. {paper['title']}**"
                }
            })

            # 作者
            if paper.get('author_str'):
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"👥 {paper['author_str']}"
                    }
                })

            # 发布时间
            if paper.get('published'):
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"📅 {paper['published']}"
                    }
                })

            # 摘要（截断）
            summary = paper.get('summary', '')
            if summary:
                summary_preview = summary[:150] + '...' if len(summary) > 150 else summary
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"📝 {summary_preview}"
                    }
                })

            # 按钮链接
            actions = []
            if paper.get('paper_url'):
                actions.append({
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "查看论文"
                    },
                    "type": "default",
                    "url": paper['paper_url']
                })
            if paper.get('pdf_url'):
                actions.append({
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "下载 PDF"
                    },
                    "type": "primary",
                    "url": paper['pdf_url']
                })

            if actions:
                elements.append({
                    "tag": "action",
                    "actions": actions
                })

            # 分隔线（除了最后一篇）
            if i < len(papers):
                elements.append({"tag": "hr"})

        # 构建卡片
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🤖 Hugging Face Daily Papers"
                },
                "template": "blue"
            },
            "elements": elements
        }

        return card

    def send_papers(self, papers: List[Dict], use_card: bool = True) -> bool:
        """
        发送论文推送

        Args:
            papers: 论文列表
            use_card: 是否使用卡片格式（推荐）

        Returns:
            是否发送成功
        """
        if use_card:
            card = self.format_papers_card(papers)
            return self.send_interactive_card(card)
        else:
            # 使用富文本格式
            title = f"📚 Hugging Face Daily Papers ({len(papers)} 篇)"
            content = self._format_post_content(papers)
            return self.send_post(title, content)

    def _format_post_content(self, papers: List[Dict]) -> List[Dict[str, str]]:
        """
        格式化为富文本内容

        Args:
            papers: 论文列表

        Returns:
            富文本内容列表
        """
        content = []

        for i, paper in enumerate(papers, 1):
            # 标题
            content.append([
                {
                    "tag": "text",
                    "text": f"{i}. ",
                    "style": ["bold"]
                },
                {
                    "tag": "text",
                    "text": paper['title'],
                    "style": ["bold"]
                }
            ])

            # 作者
            if paper.get('author_str'):
                content.append([
                    {
                        "tag": "text",
                        "text": f"作者: {paper['author_str']}\n"
                    }
                ])

            # 摘要
            summary = paper.get('summary', '')
            if summary:
                summary_preview = summary[:150] + '...' if len(summary) > 150 else summary
                content.append([
                    {
                        "tag": "text",
                        "text": f"{summary_preview}\n\n"
                    }
                ])

        return content

    def _send(self, payload: Dict) -> bool:
        """
        发送消息到飞书（支持多群）

        Args:
            payload: 消息 payload

        Returns:
            是否发送成功（所有群都成功才算成功）
        """
        if not self.webhook_urls:
            print("❌ 没有配置飞书 Webhook URL")
            return False

        import time as _time
        all_success = True
        for idx, webhook_url in enumerate(self.webhook_urls, 1):
            success = False
            for attempt in range(3):
                try:
                    response = self.session.post(
                        webhook_url,
                        json=payload,
                        timeout=10
                    )
                    response.raise_for_status()

                    result = response.json()

                    if result.get('code') == 0:
                        print(f"✅ 飞书消息发送成功 (群 {idx}/{len(self.webhook_urls)})")
                        success = True
                        break
                    else:
                        print(f"❌ 飞书消息发送失败 (群 {idx}/{len(self.webhook_urls)}): {result}")
                        if attempt < 2:
                            print(f"  ↻ 重试 ({attempt + 2}/3)...")
                            _time.sleep(2)

                except requests.RequestException as e:
                    print(f"❌ 请求异常 (群 {idx}/{len(self.webhook_urls)}): {e}")
                    if attempt < 2:
                        print(f"  ↻ 重试 ({attempt + 2}/3)...")
                        _time.sleep(2)

            if not success:
                all_success = False

        return all_success


def get_pusher_from_env() -> Optional[FeishuBotPusher]:
    """
    从环境变量获取推送器（支持多群）

    环境变量:
    - FEISHU_WEBHOOK_URL: 单个 Webhook URL
    - FEISHU_WEBHOOK_URLS: 多个 Webhook URL（空格分隔）

    Returns:
        FeishuBotPusher 实例，如果未配置则返回 None
    """
    import os

    webhook_url = os.getenv('FEISHU_WEBHOOK_URL')
    webhook_urls_str = os.getenv('FEISHU_WEBHOOK_URLS', '')

    # 解析多群 URL（空格分隔）
    webhook_urls = []
    if webhook_urls_str.strip():
        webhook_urls = webhook_urls_str.strip().split()

    # 兼容旧的 FEISHU_WEBHOOK_URL
    if webhook_url and webhook_url not in webhook_urls:
        webhook_urls.insert(0, webhook_url)

    if webhook_urls:
        return FeishuBotPusher(webhook_urls=webhook_urls)
    return None


# 测试代码
if __name__ == "__main__":
    import os

    # 测试文本消息
    webhook_url = os.getenv('FEISHU_WEBHOOK_URL')

    if not webhook_url:
        print("请设置环境变量 FEISHU_WEBHOOK_URL")
        print("export FEISHU_WEBHOOK_URL='你的webhook地址'")
        exit(1)

    pusher = FeishuBotPusher(webhook_url)

    # 测试发送文本
    print("测试发送文本消息...")
    pusher.send_text("这是一条测试消息\n来自 Hugging Face Paper Pusher")

    # 测试发送卡片
    test_papers = [
        {
            'title': 'Test Paper: Attention Is All You Need',
            'author_str': 'Ashish Vaswani, Noam Shazeer, et al.',
            'published': '2026-01-23',
            'summary': 'This is a test paper about attention mechanisms in deep learning models...',
            'paper_url': 'https://huggingface.co/papers/test',
            'pdf_url': 'https://arxiv.org/pdf/test.pdf'
        }
    ]

    print("\n测试发送卡片消息...")
    pusher.send_papers(test_papers)
