#!/usr/bin/env python3
"""
AI 论文飞书机器人 - 卡片版
提供论文、博客、推文功能，以飞书卡片形式返回
"""

import os
import sys
import json
import re
import time
import threading
from datetime import datetime
from flask import Flask, request, jsonify
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# ---- 飞书 API ----

FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', '')
FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', '')
_tenant_token = None
_tenant_token_expire = 0


def get_tenant_token():
    global _tenant_token, _tenant_token_expire
    if _tenant_token and time.time() < _tenant_token_expire - 60:
        return _tenant_token
    resp = requests.post(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
        timeout=10
    )
    data = resp.json()
    _tenant_token = data.get('tenant_access_token', '')
    _tenant_token_expire = time.time() + data.get('expire', 7200)
    return _tenant_token


def _send_msg(chat_id, msg_type, content, chat_type='group', receiver_id=None):
    token = get_tenant_token()
    if not token:
        print("[send] no tenant token")
        return
    if chat_type == 'p2p' and receiver_id:
        params = {'receive_id_type': 'open_id'}
        body = {"receive_id": receiver_id, "msg_type": msg_type, "content": content}
    else:
        params = {'receive_id_type': 'chat_id'}
        body = {"receive_id": chat_id, "msg_type": msg_type, "content": content}

    resp = requests.post(
        'https://open.feishu.cn/open-apis/im/v1/messages',
        params=params, json=body,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        timeout=15
    )
    result = resp.json()
    if result.get('code') != 0:
        print(f"[send] error: {result.get('msg', '')} (code {result.get('code')})")


def send_text(chat_id, text, chat_type='group', receiver_id=None):
    _send_msg(chat_id, 'text', json.dumps({"text": text}), chat_type, receiver_id)


def send_card(chat_id, card, chat_type='group', receiver_id=None):
    _send_msg(chat_id, 'interactive', json.dumps(card), chat_type, receiver_id)


# ---- 卡片构建 ----

def build_papers_card(papers, keyword=None):
    """构建论文卡片"""
    elements = []
    title = f"AI 论文 - \"{keyword}\"" if keyword else "AI 论文日报"
    subtitle = f"{len(papers)} 篇 | {datetime.now().strftime('%m-%d %H:%M')}"

    elements.append({
        "tag": "div",
        "text": {"tag": "lark_md", "content": f"**{subtitle}**"}
    })
    elements.append({"tag": "hr"})

    for i, p in enumerate(papers[:6], 1):
        # 标题
        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**{i}. {p.get('title', '?')}**"}
        })
        # 作者
        authors = p.get('author_str', '')
        if authors:
            if len(authors) > 80:
                authors = authors[:80] + '...'
            elements.append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"👥 {authors}"}
            })
        # AI 摘要
        ai_summary = p.get('ai_summary', '')
        if ai_summary:
            elements.append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"💡 {ai_summary}"}
            })
        else:
            summary = p.get('summary', '')
            if summary:
                if len(summary) > 200:
                    summary = summary[:200] + '...'
                elements.append({
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"📝 {summary}"}
                })
        # 按钮
        actions = []
        if p.get('paper_url'):
            actions.append({
                "tag": "button",
                "text": {"tag": "plain_text", "content": "论文主页"},
                "type": "default",
                "url": p['paper_url']
            })
        if p.get('pdf_url'):
            actions.append({
                "tag": "button",
                "text": {"tag": "plain_text", "content": "PDF"},
                "type": "primary",
                "url": p['pdf_url']
            })
        if p.get('github_repo'):
            actions.append({
                "tag": "button",
                "text": {"tag": "plain_text", "content": "GitHub"},
                "type": "default",
                "url": p['github_repo']
            })
        if p.get('project_page'):
            actions.append({
                "tag": "button",
                "text": {"tag": "plain_text", "content": "项目主页"},
                "type": "default",
                "url": p['project_page']
            })
        if actions:
            elements.append({"tag": "action", "actions": actions})
        if i < len(papers[:6]):
            elements.append({"tag": "hr"})

    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "blue"
        },
        "elements": elements
    }


def build_blogs_card(blogs):
    """构建博客卡片"""
    elements = []
    for i, b in enumerate(blogs[:5], 1):
        source = b.get('source', '')
        title = b.get('title', '?')
        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": f"**{i}. [{source}] {title}**"}
        })
        summary = b.get('summary', '') or b.get('content', '')
        if summary:
            if len(summary) > 200:
                summary = summary[:200] + '...'
            elements.append({
                "tag": "div",
                "text": {"tag": "lark_md", "content": f"📝 {summary}"}
            })
        url = b.get('url', '')
        if url:
            elements.append({
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "阅读原文"},
                    "type": "primary",
                    "url": url
                }]
            })
        if i < len(blogs[:5]):
            elements.append({"tag": "hr"})

    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": f"AI 博客 ({len(blogs[:5])} 篇)"},
            "template": "green"
        },
        "elements": elements
    }


def build_tweets_card(tweets):
    """构建推文卡片"""
    elements = []
    for i, t in enumerate(tweets[:10], 1):
        text = t['text']
        if len(text) > 200:
            text = text[:200] + '...'
        # 转义 markdown 特殊字符
        text = text.replace('*', '\\*').replace('_', '\\_')

        # 格式化时间
        date_str = ''
        if t.get('parsed_time'):
            try:
                date_str = t['parsed_time'].strftime('%Y-%m-%d')
            except Exception:
                pass
        stats = f"❤️ {t['likes']:,}  🔄 {t['retweets']:,}"
        if date_str:
            stats += f"  📅 {date_str}"
        content = f"**{i}. @{t['username']}**\n{text}\n{stats}"
        elements.append({
            "tag": "div",
            "text": {"tag": "lark_md", "content": content}
        })
        if t.get('link'):
            elements.append({
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "查看原文"},
                    "type": "default",
                    "url": t['link']
                }]
            })
        if i < len(tweets[:10]):
            elements.append({"tag": "hr"})

    return {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": f"AI 研究者推文 ({len(tweets[:10])} 条)"},
            "template": "orange"
        },
        "elements": elements
    }


# ---- 命令处理 ----

def handle_help(chat_id, chat_type, sender_id, args):
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "AI 论文助手"},
            "template": "indigo"
        },
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content":
                "**可用命令：**\n\n"
                "📄 **/papers** - 获取今日 AI 论文\n"
                "🔍 **/papers <关键词>** - 搜索论文 (如: /papers VLM)\n"
                "📰 **/blogs** - 获取最新 AI 博客\n"
                "🐦 **/tweets** - AI 研究者推文\n"
                "📊 **/trending** - AI 研究趋势总结\n"
                "🚀 **/push** - 触发完整推送到所有群"
            }}
        ]
    }
    send_card(chat_id, card, chat_type, sender_id)


def handle_papers(chat_id, chat_type, sender_id, args):
    send_text(chat_id, "正在获取论文...", chat_type, sender_id)

    def _run():
        try:
            from hf_paper_fetcher import HuggingFacePaperFetcher
            fetcher = HuggingFacePaperFetcher()
            papers = fetcher.fetch_papers()

            if args:
                keyword = args.strip().lower()
                filtered = []
                for p in papers:
                    searchable = ' '.join([
                        p.get('title', ''),
                        p.get('summary', ''),
                        p.get('ai_summary', ''),
                        p.get('author_str', ''),
                        ' '.join(p.get('categories', [])),
                    ]).lower()
                    if keyword in searchable:
                        filtered.append(p)
                papers = filtered

            if not papers:
                send_text(chat_id, f"未找到相关论文" + (f" (关键词: {args})" if args else ""), chat_type, sender_id)
                return

            card = build_papers_card(papers, keyword=args if args else None)
            send_card(chat_id, card, chat_type, sender_id)
        except Exception as e:
            send_text(chat_id, f"获取论文失败: {e}", chat_type, sender_id)

    threading.Thread(target=_run, daemon=True).start()


def handle_blogs(chat_id, chat_type, sender_id, args):
    send_text(chat_id, "正在获取博客...", chat_type, sender_id)

    def _run():
        try:
            from blog_fetcher import BlogFetcher
            fetcher = BlogFetcher()
            blogs = fetcher.fetch_all_blogs()

            if not blogs:
                send_text(chat_id, "未找到新博客", chat_type, sender_id)
                return

            card = build_blogs_card(blogs)
            send_card(chat_id, card, chat_type, sender_id)
        except Exception as e:
            send_text(chat_id, f"获取博客失败: {e}", chat_type, sender_id)

    threading.Thread(target=_run, daemon=True).start()


def handle_tweets(chat_id, chat_type, sender_id, args):
    send_text(chat_id, "正在获取推文 (约30秒)...", chat_type, sender_id)

    def _run():
        try:
            from twitter_fetcher import TwitterFetcher
            fetcher = TwitterFetcher(max_tweets=3, days_back=7)
            tweets = fetcher.fetch_tweets()

            if not tweets:
                send_text(chat_id, "未获取到推文", chat_type, sender_id)
                return

            card = build_tweets_card(tweets)
            send_card(chat_id, card, chat_type, sender_id)
        except Exception as e:
            send_text(chat_id, f"获取推文失败: {e}", chat_type, sender_id)

    threading.Thread(target=_run, daemon=True).start()


def handle_trending(chat_id, chat_type, sender_id, args):
    send_text(chat_id, "正在生成趋势总结...", chat_type, sender_id)

    def _run():
        try:
            from hf_paper_fetcher import HuggingFacePaperFetcher
            from ai_summarizer import get_summarizer_from_env
            fetcher = HuggingFacePaperFetcher()
            papers = fetcher.fetch_papers()

            if not papers:
                send_text(chat_id, "暂无论文数据", chat_type, sender_id)
                return

            summarizer = get_summarizer_from_env()
            titles = [p.get('title', '') for p in papers[:15]]
            prompt = "请用中文总结以下 AI 论文的研究趋势（3-5 个要点）：\n\n" + '\n'.join(f"- {t}" for t in titles)
            summary = summarizer.generate_summary("AI Research Trends", prompt)

            card = {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {"tag": "plain_text", "content": "AI 研究趋势"},
                    "template": "purple"
                },
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": summary}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content":
                        f"基于 {len(papers)} 篇论文 | {datetime.now().strftime('%m-%d %H:%M')}"}}
                ]
            }
            send_card(chat_id, card, chat_type, sender_id)
        except Exception as e:
            send_text(chat_id, f"生成趋势失败: {e}", chat_type, sender_id)

    threading.Thread(target=_run, daemon=True).start()


def handle_push(chat_id, chat_type, sender_id, args):
    send_text(chat_id, "正在触发推送...", chat_type, sender_id)

    def _run():
        try:
            import subprocess
            result = subprocess.run(
                ['bash', os.path.join(os.path.dirname(__file__), 'papers.sh')],
                capture_output=True, text=True, timeout=300,
                cwd=os.path.dirname(__file__)
            )
            if result.returncode == 0:
                send_text(chat_id, "推送完成", chat_type, sender_id)
            else:
                send_text(chat_id, f"推送失败: {result.stderr[:200]}", chat_type, sender_id)
        except Exception as e:
            send_text(chat_id, f"推送失败: {e}", chat_type, sender_id)

    threading.Thread(target=_run, daemon=True).start()


COMMANDS = {
    '/help': handle_help,
    '/papers': handle_papers,
    '/blogs': handle_blogs,
    '/tweets': handle_tweets,
    '/trending': handle_trending,
    '/push': handle_push,
}


# ---- 飞书事件处理 ----

_processed = set()


@app.route('/feishu/events', methods=['POST'])
def handle_events():
    body = request.get_data(as_text=True)
    try:
        data = json.loads(body)

        # URL 验证
        if data.get('type') == 'url_verification':
            challenge = data.get('challenge', '')
            print(f"[challenge] {challenge[:20]}", flush=True)
            return jsonify({"challenge": challenge})

        event_type = data.get('header', {}).get('event_type')

        if event_type == 'im.message.receive_v1':
            event = data.get('event', {})
            message = event.get('message', {})
            sender = event.get('sender', {})

            if sender.get('sender_type') == 'app':
                return jsonify({"code": 0, "msg": "OK"})

            message_id = message.get('message_id', '')
            if message_id in _processed:
                return jsonify({"code": 0, "msg": "OK"})
            _processed.add(message_id)
            if len(_processed) > 500:
                _processed.clear()

            if message.get('message_type') != 'text':
                return jsonify({"code": 0, "msg": "OK"})

            try:
                content = json.loads(message.get('content', '{}'))
                text = content.get('text', '').strip()
            except Exception:
                text = ''

            text = re.sub(r'@_user_\d+\s*', '', text).strip()
            if not text:
                return jsonify({"code": 0, "msg": "OK"})

            chat_id = message.get('chat_id', '')
            chat_type = message.get('chat_type', 'group')
            sender_id = sender.get('sender_id', {}).get('open_id', '')

            print(f"[msg] {text[:50]}", flush=True)

            parts = text.split(None, 1)
            cmd = parts[0].lower() if parts else ''
            args = parts[1].strip() if len(parts) > 1 else ''

            handler = COMMANDS.get(cmd)
            if handler:
                handler(chat_id, chat_type, sender_id, args)
            else:
                send_text(chat_id,
                          "发送 /help 查看可用命令",
                          chat_type, sender_id)

        return jsonify({"code": 0, "msg": "OK"})
    except Exception as e:
        print(f"[error] {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "msg": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "paper-bot"})


if __name__ == '__main__':
    port = int(os.getenv('BOT_PORT', 5000))
    print(f"AI 论文机器人启动 - 端口 {port}")
    print(f"命令: /papers /blogs /tweets /trending /push /help")
    app.run(host='0.0.0.0', port=port)
