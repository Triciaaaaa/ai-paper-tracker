#!/usr/bin/env python3
"""
Twitter/X AI 研究者推文抓取器

后端优先级：
1. syndication（默认）- 使用 Twitter 公开的嵌入式时间线 API，无需登录，稳定
2. twscrape（可选）- 使用 Twitter 账号登录，可获取关注列表

配置方式：
- 默认即可使用（syndication 不需要任何配置）
- TWITTER_ACCOUNTS="user1,user2,user3" → 手动指定账号
- TWITTER_ACCOUNTS_FILE="/path/to/accounts.txt" → 从文件加载
- TWITTER_USERNAME + TWITTER_PASSWORD + ... → 启用 twscrape 获取关注列表
"""

import os
import re
import json
import time
import asyncio
import urllib.request
from datetime import datetime, timedelta
from typing import List, Dict, Optional


# 默认关注的 AI 研究者账号
DEFAULT_ACCOUNTS = [
    # --- 深度学习先驱 ---
    'ylecun',         # Yann LeCun (Meta AI, Turing Award)
    'geoffreyhinton', # Geoffrey Hinton (Turing Award, Nobel Prize)
    'ilyasut',        # Ilya Sutskever (SSI, ex-OpenAI)
    # --- 行业领袖 ---
    'sama',           # Sam Altman (OpenAI CEO)
    'DarioAmodei',    # Dario Amodei (Anthropic CEO)
    'demishassabis',  # Demis Hassabis (DeepMind CEO, Nobel Prize)
    'JeffDean',       # Jeff Dean (Google AI)
    'AndrewYNg',      # Andrew Ng (DeepLearning.AI)
    'NoamShazeer',    # Noam Shazeer (Attention Is All You Need, Gemini)
    # --- 顶级研究者 ---
    'karpathy',       # Andrej Karpathy (ex-OpenAI, ex-Tesla AI)
    'DrJimFan',       # Jim Fan (NVIDIA)
    'fchollet',       # François Chollet (Keras 作者, ARC Prize)
    'pabbeel',        # Pieter Abbeel (UC Berkeley, Covariant)
    'hardmaru',       # David Ha (Sakana AI)
    'GaryMarcus',     # Gary Marcus (AI 评论家)
    'random_forests', # Sebastian Raschka (ML 教育)
    'jeffclune',      # Jeff Clune (UBC, 开放性搜索)
    'OriolVinyalsML', # Oriol Vinyals (DeepMind)
    'chelseabfinn',   # Chelsea Finn (Stanford)
    'svlevine',       # Sergey Levine (UC Berkeley)
    'percyliang',     # Percy Liang (Stanford, HELM)
    # --- AI 信息源 ---
    '_akhaliq',       # AK (HF papers 速递)
    'cwolferesearch', # Cameron Wolfe (AI 研究解读)
]

# AI 相关关键词（用于过滤非 AI 推文）
AI_KEYWORDS = [
    'ai', 'ml', 'llm', 'gpt', 'claude', 'gemini', 'transformer', 'neural',
    'deep learning', 'machine learning', 'training', 'model', 'inference',
    'reasoning', 'alignment', 'rlhf', 'fine-tuning', 'finetune',
    'multimodal', 'vision', 'language model', 'diffusion', 'agent',
    'benchmark', 'dataset', 'paper', 'research', 'arxiv',
    'openai', 'anthropic', 'deepmind', 'meta ai', 'google ai',
    'scaling', 'context window', 'token', 'embedding', 'retrieval',
    'chain of thought', 'cot', 'rag', 'prompt', 'synthetic data',
    'data quality', 'vlm', 'mllm', 'sft', 'dpo', 'ppo',
]

SYNDICATION_URL = "https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
SYNDICATION_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


class TwitterFetcher:
    """Twitter/X AI 推文抓取器"""

    def __init__(self, accounts=None, max_tweets=5, filter_ai=True, days_back=7):
        """
        初始化抓取器

        Args:
            accounts: 要关注的 Twitter 账号列表（None 则从环境变量或默认值）
            max_tweets: 每个账号最多获取多少条推文
            filter_ai: 是否只保留 AI 相关推文
            days_back: 只获取最近 N 天的推文（0 表示不限制）
        """
        env_accounts = os.getenv('TWITTER_ACCOUNTS', '')
        if env_accounts:
            self.accounts = [a.strip().lstrip('@') for a in env_accounts.split(',') if a.strip()]
        elif accounts:
            self.accounts = [a.lstrip('@') for a in accounts]
        else:
            self.accounts = list(DEFAULT_ACCOUNTS)

        self.max_tweets = max_tweets
        self.filter_ai = filter_ai
        self.days_back = days_back

        # 支持从文件加载账号列表
        accounts_file = os.getenv('TWITTER_ACCOUNTS_FILE', '')
        if accounts_file and os.path.exists(accounts_file):
            with open(accounts_file, 'r') as f:
                file_accounts = [line.strip().lstrip('@') for line in f
                                 if line.strip() and not line.startswith('#')]
            if file_accounts:
                self.accounts = list(set(self.accounts + file_accounts))
                print(f"  从文件加载 {len(file_accounts)} 个账号，总计 {len(self.accounts)} 个")

        # twscrape 凭据（可选，用于获取关注列表）
        self._twitter_username = os.getenv('TWITTER_USERNAME', '')
        self._twitter_password = os.getenv('TWITTER_PASSWORD', '')
        self._twitter_email = os.getenv('TWITTER_EMAIL', '')
        self._twitter_email_password = os.getenv('TWITTER_EMAIL_PASSWORD', '')

    def _is_ai_related(self, text):
        """检查推文是否与 AI 相关"""
        if not self.filter_ai:
            return True
        text_lower = text.lower()
        return any(kw in text_lower for kw in AI_KEYWORDS)

    def _parse_syndication_date(self, date_str):
        """解析 syndication API 返回的日期格式: 'Fri Nov 29 20:42:38 +0000 2024'"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')
        except (ValueError, TypeError):
            return None

    def _is_recent(self, parsed_time):
        """检查推文是否在 days_back 范围内"""
        if self.days_back <= 0 or parsed_time is None:
            return True
        from datetime import timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.days_back)
        if parsed_time.tzinfo is None:
            return True
        return parsed_time >= cutoff

    def fetch_tweets(self):
        """获取所有关注账号的最新推文（使用 syndication API）"""
        all_tweets = []

        for idx, account in enumerate(self.accounts):
            if idx > 0:
                time.sleep(1.5)  # 避免触发频率限制
            print(f"  [Twitter] @{account} ...", end='', flush=True)
            try:
                tweets = self._fetch_user_syndication(account)
                count = 0
                for tweet in tweets:
                    text = tweet.get('full_text', '')
                    if not text:
                        continue

                    parsed_time = self._parse_syndication_date(tweet.get('created_at', ''))
                    if not self._is_recent(parsed_time):
                        continue

                    if not self._is_ai_related(text):
                        continue

                    user = tweet.get('user', {})
                    screen_name = user.get('screen_name', account)
                    tweet_id = tweet.get('conversation_id_str', '')

                    tweet_data = {
                        'username': screen_name,
                        'text': text,
                        'link': f'https://x.com/{screen_name}/status/{tweet_id}' if tweet_id else '',
                        'timestamp': tweet.get('created_at', ''),
                        'parsed_time': parsed_time,
                        'likes': tweet.get('favorite_count', 0),
                        'retweets': tweet.get('retweet_count', 0),
                        'replies': tweet.get('reply_count', 0),
                    }
                    all_tweets.append(tweet_data)
                    count += 1

                    if count >= self.max_tweets:
                        break

                print(f" {count} 条 AI 相关")

            except Exception as e:
                print(f" 失败: {e}")
                continue

        # 按互动量排序
        all_tweets.sort(key=lambda t: t['likes'] + t['retweets'], reverse=True)
        print(f"  [Twitter] 共获取 {len(all_tweets)} 条 AI 相关推文")
        return all_tweets

    def _fetch_user_syndication(self, username, retries=2):
        """使用 Twitter syndication API 获取用户推文（无需认证）"""
        url = SYNDICATION_URL.format(username=username)

        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(url, headers=SYNDICATION_HEADERS)
                resp = urllib.request.urlopen(req, timeout=15)
                html = resp.read().decode('utf-8')

                match = re.search(
                    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                    html
                )
                if not match:
                    return []

                data = json.loads(match.group(1))
                entries = data.get('props', {}).get('pageProps', {}).get('timeline', {}).get('entries', [])

                tweets = []
                for entry in entries:
                    if entry.get('type') != 'tweet':
                        continue
                    tweet = entry.get('content', {}).get('tweet', {})
                    if tweet:
                        tweets.append(tweet)

                return tweets

            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < retries:
                    wait = 5 * (attempt + 1)
                    print(f" (rate limited, wait {wait}s)", end='', flush=True)
                    time.sleep(wait)
                    continue
                raise

        return []

    def fetch_following_list(self):
        """获取你的 Twitter 关注列表（需要 twscrape + 账号登录）"""
        if not self._twitter_username or not self._twitter_password:
            print("  获取关注列表需要配置 TWITTER_USERNAME 和 TWITTER_PASSWORD")
            return []

        try:
            import twscrape

            async def _fetch():
                api = twscrape.API()
                await api.pool.add_account(
                    self._twitter_username,
                    self._twitter_password,
                    self._twitter_email,
                    self._twitter_email_password
                )
                await api.pool.login_all()

                user = await api.user_by_login(self._twitter_username)
                if not user:
                    return []

                following = []
                async for f in api.following(user.id, limit=200):
                    following.append(f.username)
                return following

            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(_fetch())
                print(f"  获取到 {len(result)} 个关注的账号")
                return result
            finally:
                loop.close()

        except ImportError:
            print("  twscrape 未安装，请运行: pip install twscrape")
            return []
        except Exception as e:
            print(f"  获取关注列表失败: {e}")
            return []

    def format_tweets_text(self, tweets, max_count=10):
        """将推文格式化为文本"""
        if not tweets:
            return "暂无 AI 相关推文"

        lines = [f"AI 研究者推文 ({len(tweets[:max_count])} 条)\n"]

        for i, tweet in enumerate(tweets[:max_count], 1):
            text = tweet['text']
            if len(text) > 200:
                text = text[:200] + '...'

            lines.append(f"{i}. @{tweet['username']}")
            lines.append(f"   {text}")
            lines.append(f"   Likes: {tweet['likes']}  RT: {tweet['retweets']}  Replies: {tweet['replies']}")
            if tweet.get('link'):
                lines.append(f"   {tweet['link']}")
            lines.append("")

        return '\n'.join(lines)


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("Twitter AI 推文抓取器测试 (syndication API)")
    print("=" * 60)

    fetcher = TwitterFetcher(max_tweets=3, days_back=7)

    print("\n获取推文...")
    tweets = fetcher.fetch_tweets()

    if tweets:
        print("\n" + fetcher.format_tweets_text(tweets))
    else:
        print("\n未获取到推文")
