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

    # RSS 源配置（只保留有活跃 RSS 的源）
    RSS_SOURCES = {
        # ============ Hacker News（AI 相关） ============
        'hn_ai': {
            'name': 'Hacker News (AI/ML)',
            'rss_url': 'https://hnrss.org/frontpage?q=AI+OR+LLM+OR+machine+learning+OR+deep+learning+OR+GPT+OR+transformer',
            'base_url': 'https://news.ycombinator.com'
        },
        'hn_best': {
            'name': 'Hacker News (Best)',
            'rss_url': 'https://hnrss.org/best',
            'base_url': 'https://news.ycombinator.com'
        },

        # ============ 顶级个人研究者博客 ============
        'karpathy': {
            'name': 'Andrej Karpathy',
            'rss_url': 'https://karpathy.github.io/feed.xml',
            'base_url': 'https://karpathy.github.io'
        },
        'simon_willison': {
            'name': 'Simon Willison (LLM 工具链)',
            'rss_url': 'https://simonwillison.net/atom/everything/',
            'base_url': 'https://simonwillison.net'
        },
        'tim_dettmers': {
            'name': 'Tim Dettmers (量化/高效训练)',
            'rss_url': 'https://timdettmers.com/feed/',
            'base_url': 'https://timdettmers.com'
        },
        'chip_huyen': {
            'name': 'Chip Huyen (MLOps/数据)',
            'rss_url': 'https://huyenchip.com/feed.xml',
            'base_url': 'https://huyenchip.com'
        },
        'jay_alammar': {
            'name': 'Jay Alammar (Transformer 可视化)',
            'rss_url': 'https://jalammar.github.io/feed.xml',
            'base_url': 'https://jalammar.github.io'
        },
        'colah': {
            'name': 'Christopher Olah (Anthropic)',
            'rss_url': 'https://colah.github.io/rss.xml',
            'base_url': 'https://colah.github.io'
        },

        # ============ 高质量社区/期刊 ============
        'lesswrong': {
            'name': 'LessWrong (AI Alignment)',
            'rss_url': 'https://www.lesswrong.com/feed.xml',
            'base_url': 'https://www.lesswrong.com'
        },
        'the_gradient': {
            'name': 'The Gradient (AI 深度分析)',
            'rss_url': 'https://thegradient.pub/rss/',
            'base_url': 'https://thegradient.pub'
        },
        'towards_data_science': {
            'name': 'Towards Data Science',
            'rss_url': 'https://towardsdatascience.com/feed',
            'base_url': 'https://towardsdatascience.com'
        },
        'ml_mastery': {
            'name': 'Machine Learning Mastery',
            'rss_url': 'https://machinelearningmastery.com/feed/',
            'base_url': 'https://machinelearningmastery.com'
        },
        'mit_tech_review': {
            'name': 'MIT Technology Review',
            'rss_url': 'https://www.technologyreview.com/feed/',
            'base_url': 'https://www.technologyreview.com'
        },

        # ============ 顶级实验室/机构博客 ============
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
        'nvidia': {
            'name': 'NVIDIA AI Blog',
            'rss_url': 'https://blogs.nvidia.com/feed/',
            'base_url': 'https://blogs.nvidia.com'
        },
        'huggingface': {
            'name': 'Hugging Face Blog',
            'rss_url': 'https://huggingface.co/blog/feed.xml',
            'base_url': 'https://huggingface.co/blog'
        },
        'bair': {
            'name': 'BAIR (Berkeley AI Research)',
            'rss_url': 'https://bair.berkeley.edu/blog/feed.xml',
            'base_url': 'https://bair.berkeley.edu/blog'
        },
        'google_research': {
            'name': 'Google Research Blog',
            'rss_url': 'https://blog.research.google/feeds/posts/default',
            'base_url': 'https://blog.research.google'
        },
        'salesforce_ai': {
            'name': 'Salesforce AI Research',
            'rss_url': 'https://engineering.salesforce.com/rss/',
            'base_url': 'https://engineering.salesforce.com'
        },
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

        # 去重：按链接去重，避免同一篇文章重复出现
        seen_links = set()
        unique_articles = []
        for article in all_articles:
            link = article.get('link', '')
            if link and link not in seen_links:
                seen_links.add(link)
                unique_articles.append(article)

        # 按时间排序（用 feedparser 解析日期，而非字符串比较）
        def sort_key(x):
            pub = x.get('published', '')
            for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z',
                         '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                try:
                    return datetime.strptime(pub.strip(), fmt).replace(tzinfo=None)
                except (ValueError, TypeError):
                    continue
            return datetime.min

        unique_articles.sort(key=sort_key, reverse=True)

        print(f"✅ 获取到 {len(unique_articles)} 篇博客文章（去重前 {len(all_articles)} 篇）")
        return unique_articles

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

    def _parse_entry_date(self, entry) -> Optional[datetime]:
        """从 RSS entry 解析发布时间，优先使用 feedparser 已解析的 struct_time"""
        # feedparser 会自动解析日期到 published_parsed / updated_parsed
        parsed = entry.get('published_parsed') or entry.get('updated_parsed')
        if parsed:
            try:
                return datetime(*parsed[:6])
            except Exception:
                pass

        # 回退：手动解析原始日期字符串
        published = entry.get('published', entry.get('updated', ''))
        if not published:
            return None

        date_formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S.%f%z',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d'
        ]
        for fmt in date_formats:
            try:
                return datetime.strptime(published.strip(), fmt)
            except (ValueError, TypeError):
                continue
        return None

    def _fetch_from_rss(self, source_key: str, source_config: Dict, cutoff_date: datetime) -> List[Dict]:
        """从 RSS 源获取文章"""
        try:
            rss_url = source_config.get('rss_url', '')
            if not rss_url:
                print(f"  └─ ⚠️  该源没有配置 RSS URL")
                return []

            feed = feedparser.parse(rss_url)

            if feed.bozo and not feed.entries:
                print(f"  └─ ❌ RSS 解析失败: {feed.bozo_exception}")
                return []

            if not feed.entries:
                print(f"  └─ ⚠️  RSS 返回 0 条目")
                return []

            # 先遍历所有条目，解析日期并过滤，再按时间排序取 top N
            candidates = []
            for entry in feed.entries:
                pub_date = self._parse_entry_date(entry)
                published = entry.get('published', entry.get('updated', ''))

                # 时间过滤：有日期的按日期过滤，无日期的跳过（避免混入旧文章）
                if pub_date:
                    pub_date_naive = pub_date.replace(tzinfo=None) if pub_date.tzinfo else pub_date
                    if pub_date_naive < cutoff_date:
                        continue
                else:
                    # 无法解析日期，跳过这条，避免收入不确定时间的旧文章
                    continue

                # 提取摘要
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    soup = BeautifulSoup(summary, 'html.parser')
                    summary = soup.get_text()[:500]

                candidates.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': summary,
                    'published': published,
                    'pub_date': pub_date_naive,
                    'source': source_config['name'],
                    'source_key': source_key
                })

            # 按日期倒序排序，取最新的 max_articles 篇
            candidates.sort(key=lambda x: x['pub_date'], reverse=True)
            articles = candidates[:self.max_articles]

            # 移除内部排序字段
            for a in articles:
                del a['pub_date']

            print(f"  └─ {len(articles)} 篇（共 {len(candidates)} 篇在时间范围内）")
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
