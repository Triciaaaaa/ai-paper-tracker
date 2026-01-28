#!/usr/bin/env python3
"""
📰 博客文章抓取器
获取 Anthropic、DeepMind、OpenAI 等实验室的最新博客
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class BlogFetcher:
    """博客文章抓取器"""

    # RSS 源配置
    RSS_SOURCES = {
        # ============ 顶级个人博客 ============
        'ilya': {
            'name': 'Ilya Sutskever',
            'rss_url': 'https://www.ilyasuresh.com/rss',
            'base_url': 'https://www.ilyasuresh.com'
        },
        'sutton': {
            'name': 'Richard Sutton',
            'rss_url': 'https://gradientflow.org/rss/',
            'base_url': 'https://www.cs.ualberta.ca/~sutton/'
        },
        'karpathy': {
            'name': 'Andrej Karpathy',
            'rss_url': 'https://karpathy.github.io/feed.xml',
            'base_url': 'https://karpathy.github.io'
        },
        'le_cun': {
            'name': 'Yann LeCun',
            'rss_url': 'https://www.facebook.com/feeds/page.php?id=35561552908&format=rss20',
            'base_url': 'https://www.facebook.com/ylecun1960'
        },
        'hinton': {
            'name': 'Geoffrey Hinton',
            'rss_url': '',
            'base_url': 'https://www.cs.toronto.edu/~hinton/'
        },
        'bengio': {
            'name': 'Yoshua Bengio',
            'rss_url': '',
            'base_url': 'https://yoshuabengio.org/'
        },
        'schramowski': {
            'name': 'Simon Schmickler (Vijay P. 等人)',
            'rss_url': 'https://www.alignmentforum.org/feed',
            'base_url': 'https://www.alignmentforum.org'
        },

        # ============ 个人研究博客（高质量） ============
        'lesswrong': {
            'name': 'LessWrong (AI Alignment 社区)',
            'rss_url': 'https://www.lesswrong.com/feed.xml',
            'base_url': 'https://www.lesswrong.com'
        },
        'distill': {
            'name': 'Distill.pub (交互式科学出版物)',
            'rss_url': 'https://distill.pub/rss.xml',
            'base_url': 'https://distill.pub'
        },
        'jeremykun': {
            'name': 'Jeremy Kun (Math ∩ Programming)',
            'rss_url': 'https://jeremykun.com/feed/',
            'base_url': 'https://jeremykun.com'
        },
        'colah': {
            'name': 'Christopher Olah (Anthropic, 神经网络可视化)',
            'rss_url': 'https://colah.github.io/rss.xml',
            'base_url': 'https://colah.github.io'
        },
        'weng': {
            'name': 'Lilian Weng (OpenAI 安全研究)',
            'rss_url': 'https://lilianweng.github.io/feed.xml',
            'base_url': 'https://lilianweng.github.io'
        },

        # ============ AI 媒体和期刊 ============
        'mit_tech_review': {
            'name': 'MIT Technology Review',
            'rss_url': 'https://www.technologyreview.com/feed/',
            'base_url': 'https://www.technologyreview.com'
        },

        # ============ 顶级研究机构 ============
        'ssi': {
            'name': 'Schmidt Futures (SSI)',
            'rss_url': 'https://www.schmidtfutures.org/news/feed/',
            'base_url': 'https://www.schmidtfutures.org'
        },
        'thinking_machines': {
            'name': 'Thinking Machines',
            'rss_url': '',
            'base_url': 'https://www.thinkingmachines.com'
        },
        'openai': {
            'name': 'OpenAI',
            'rss_url': 'https://openai.com/blog/rss.xml',
            'base_url': 'https://openai.com'
        },
        'anthropic': {
            'name': 'Anthropic',
            'rss_url': 'https://www.anthropic.com/rss',
            'base_url': 'https://www.anthropic.com'
        },
        'deepmind': {
            'name': 'DeepMind',
            'rss_url': 'https://deepmind.google/discover/blog/feed/',
            'base_url': 'https://deepmind.google'
        },
        'google_ai': {
            'name': 'Google AI',
            'rss_url': 'https://blog.google/technology/ai/rss/',
            'base_url': 'https://blog.google'
        },
        'meta_ai': {
            'name': 'Meta AI (FAIR)',
            'rss_url': 'https://ai.meta.com/blog/rss/',
            'base_url': 'https://ai.meta.com'
        },
        'microsoft_research': {
            'name': 'Microsoft Research',
            'rss_url': 'https://www.microsoft.com/en-us/research/blog/rss/',
            'base_url': 'https://www.microsoft.com/en-us/research/blog/'
        },
        'salesforce_ai': {
            'name': 'Salesforce AI Research',
            'rss_url': 'https://engineering.salesforce.com/rss/',
            'base_url': 'https://engineering.salesforce.com'
        },
        'openresearch': {
            'name': 'OpenResearch',
            'rss_url': 'https://www.openresearch.org/blog/feed/',
            'base_url': 'https://www.openresearch.org'
        },
        'mira': {
            'name': 'Mira Research (Yann LeCun 的新公司)',
            'rss_url': '',
            'base_url': 'https://www.mira-research.org'
        }
    }

    def __init__(self, days_back: int = 7, max_articles: int = 5):
        """
        初始化抓取器

        Args:
            days_back: 获取最近几天的文章
            max_articles: 每个源最多获取多少篇文章
        """
        self.days_back = days_back
        self.max_articles = max_articles
        self.session = requests.Session()

    def fetch_blogs(self, sources: List[str] = None, fetch_full_content: bool = True) -> List[Dict]:
        """
        获取博客文章

        Args:
            sources: 要获取的源列表，如 ['anthropic', 'deepmind']，None 表示获取所有
            fetch_full_content: 是否获取全文内容

        Returns:
            文章列表
        """
        if sources is None:
            sources = list(self.RSS_SOURCES.keys())

        all_articles = []
        cutoff_date = datetime.now() - timedelta(days=self.days_back)

        for source_key in sources:
            if source_key not in self.RSS_SOURCES:
                print(f"⚠️  未知的源: {source_key}")
                continue

            source_config = self.RSS_SOURCES[source_key]
            print(f"📰 获取 {source_config['name']} 博客...")

            articles = self._fetch_from_rss(source_key, source_config, cutoff_date)

            # 获取全文内容
            if fetch_full_content:
                for article in articles:
                    full_content = self._fetch_full_content(article)
                    if full_content:
                        article['full_content'] = full_content

            all_articles.extend(articles)

        # 按时间排序
        all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)

        print(f"✅ 获取到 {len(all_articles)} 篇博客文章")
        return all_articles

    def _fetch_full_content(self, article: Dict) -> Optional[str]:
        """获取博客文章的全文内容"""
        try:
            url = article['link']
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 移除不需要的标签
            for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                script.decompose()

            # 提取主要内容
            content = soup.get_text(separator='\n', strip=True)

            # 清理空白行
            lines = [line.strip() for line in content.split('\n')]
            lines = [line for line in lines if line and len(line) > 20]

            full_text = '\n'.join(lines[:500])  # 取前 500 行

            return full_text if len(full_text) > 200 else None

        except Exception as e:
            print(f"  ⚠️  获取全文失败: {e}")
            return None

    def _fetch_from_rss(self, source_key: str, source_config: Dict, cutoff_date: datetime) -> List[Dict]:
        """从 RSS 源获取文章"""
        try:
            rss_url = source_config.get('rss_url', '')
            if not rss_url:
                print(f"  └─ ⚠️  该源没有配置 RSS URL")
                return []

            feed = feedparser.parse(rss_url)
            articles = []

            for entry in feed.entries[:self.max_articles]:
                # 解析发布时间
                published = entry.get('published', entry.get('updated', ''))
                pub_date = None

                if published:
                    # 尝试多种日期格式
                    date_formats = [
                        '%a, %d %b %Y %H:%M:%S %z',
                        '%a, %d %b %Y %H:%M:%S %Z',
                        '%Y-%m-%dT%H:%M:%S%z',
                        '%Y-%m-%dT%H:%M:%SZ',
                        '%Y-%m-%dT%H:%M:%S',
                        '%Y-%m-%d'
                    ]

                    for fmt in date_formats:
                        try:
                            pub_date = datetime.strptime(published.strip(), fmt)
                            break
                        except:
                            continue

                # 检查是否在时间范围内
                if pub_date:
                    # 移除时区信息以便比较
                    if pub_date.tzinfo:
                        cutoff_date_with_tz = cutoff_date.replace(tzinfo=pub_date.tzinfo)
                    else:
                        cutoff_date_with_tz = cutoff_date

                    if pub_date < cutoff_date_with_tz:
                        continue

                # 提取摘要
                summary = entry.get('summary', entry.get('description', ''))
                # 清理 HTML 标签
                if summary:
                    soup = BeautifulSoup(summary, 'html.parser')
                    summary = soup.get_text()[:500]

                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': summary,
                    'published': published,
                    'source': source_config['name'],
                    'source_key': source_key
                }

                articles.append(article)

            print(f"  └─ {len(articles)} 篇")
            return articles

        except Exception as e:
            print(f"  └─ ❌ 获取失败: {e}")
            return []


# 测试代码
if __name__ == "__main__":
    fetcher = BlogFetcher(days_back=7, max_articles=3)
    blogs = fetcher.fetch_blogs(['anthropic', 'deepmind'])

    print("\n" + "=" * 60)
    print("📰 最新博客文章")
    print("=" * 60)

    for i, blog in enumerate(blogs, 1):
        print(f"\n{i}. {blog['title']}")
        print(f"   来源: {blog['source']}")
        print(f"   发布: {blog['published']}")
        print(f"   链接: {blog['link']}")
        print(f"   摘要: {blog['summary'][:100]}...")
