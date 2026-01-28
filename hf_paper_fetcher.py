#!/usr/bin/env python3
"""
📚 Hugging Face Daily Papers 抓取器
获取 Hugging Face Daily Papers 的最新论文
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import re


class HuggingFacePaperFetcher:
    """Hugging Face Daily Papers 抓取器"""

    BASE_URL = "https://huggingface.co"
    DAILY_PAPERS_API = "/api/daily_papers"

    # 默认类别关键词
    DEFAULT_CATEGORIES = {
        # 核心关注领域
        'rl_verification': ['reinforcement learning verification', 'verify reinforcement learning', 'formal verification rl', 'safe rl', 'rl safety'],
        'alignment': ['alignment', 'constitutional ai', 'ai safety', 'reward hacking', 'rlhf', 'reward model', 'value learning'],
        'ai4math': ['ai for mathematics', 'mathematical reasoning', 'theorem proving', 'math', 'formal math', 'automated theorem proving'],
        'auto_formalization': ['auto-formalization', 'auto formalization', 'formalization', 'informal to formal', 'proof synthesis', 'formal methods'],
        # 相关领域
        'reasoning': ['reasoning', 'logic', 'deductive reasoning', 'inductive reasoning', 'chain of thought'],
        'llm': ['large language model', 'llm', 'transformer', 'gpt', 'language model'],
        'reinforcement_learning': ['reinforcement learning', 'rl', 'policy gradient', 'q-learning', 'actor critic'],
        # 其他
        'computer_vision': ['vision', 'image', 'video', 'convolutional', 'segmentation', 'detection'],
        'multimodal': ['multimodal', 'vision-language', 'clip', 'visual-language'],
        'generative': ['diffusion', 'gan', 'generation', 'generative'],
        'agents': ['agent', 'autonomous', 'planning', 'decision making']
    }

    def __init__(self, days_back: int = 1, max_papers: int = 50, category_filters: List[str] = None):
        """
        初始化抓取器

        Args:
            days_back: 获取最近几天的论文
            max_papers: 最多获取多少篇论文
            category_filters: 类别过滤列表，如 ['alignment', 'llm']，None 表示不过滤
        """
        self.days_back = days_back
        self.max_papers = max_papers
        self.category_filters = category_filters
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_papers(self, date: Optional[str] = None) -> List[Dict]:
        """
        获取指定日期的论文

        Args:
            date: 日期字符串 (YYYY-MM-DD)，默认为今天

        Returns:
            论文列表
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        url = f"{self.BASE_URL}{self.DAILY_PAPERS_API}"
        params = {'date': date, 'limit': self.max_papers}

        try:
            print(f"📅 获取 {date} 的 Hugging Face Daily Papers...")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data:
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)

            print(f"✅ 获取到 {len(papers)} 篇论文")
            return papers

        except requests.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return []

    def fetch_trending_papers(self) -> List[Dict]:
        """
        获取当前热门论文

        Returns:
            论文列表
        """
        url = f"{self.BASE_URL}/papers/trending"

        try:
            print("🔥 获取 Hugging Face 热门论文...")
            # 注意：trending 页面是动态渲染的，这里使用 API
            # 实际上 trending 数据也在 daily_papers API 中，通过排序获取
            response = self.session.get(f"{self.BASE_URL}{self.DAILY_PAPERS_API}",
                                      params={'limit': self.max_papers},
                                      timeout=30)
            response.raise_for_status()

            data = response.json()
            papers = []

            for item in data[:self.max_papers]:
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)

            print(f"✅ 获取到 {len(papers)} 篇热门论文")
            return papers

        except requests.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return []

    def _parse_paper(self, item: Dict) -> Optional[Dict]:
        """
        解析论文数据

        Args:
            item: API 返回的单个论文项

        Returns:
            解析后的论文字典
        """
        try:
            # API 返回的数据结构：外层可能包含 paper 对象，也可能直接是数据
            paper_data = item.get('paper', item)

            # 提取论文信息
            paper_id = paper_data.get('id', '')
            title = paper_data.get('title', '')
            summary = paper_data.get('summary', '')

            # 发布时间（可能是 publishedAt 或其他字段）
            published = paper_data.get('publishedAt', paper_data.get('published', paper_data.get('date', '')))

            # 提取作者
            authors_list = paper_data.get('authors', [])
            author_names = [a.get('name', '') for a in authors_list if a.get('name')]
            author_list = ', '.join(author_names[:5])  # 只取前5个作者

            # 构建论文 URL
            paper_url = f"{self.BASE_URL}/papers/{paper_id}"

            # PDF URL（需要根据 arXiv ID 构建）
            # Hugging Face 论文 ID 格式通常是 "YYMM.NNNNN"（arXiv 格式）
            pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf" if paper_id else ''

            # 附加信息（如果有）
            project_page = paper_data.get('projectPage', '')
            github_repo = paper_data.get('githubRepo', '')
            ai_summary = paper_data.get('ai_summary', '')

            # 检测类别
            categories = self._detect_categories(title, summary)

            # 类别过滤
            if self.category_filters and not any(cat in self.category_filters for cat in categories):
                return None  # 不在需要的类别中，跳过

            return {
                'paper_id': paper_id,
                'title': title,
                'summary': summary,
                'authors': author_names,
                'author_str': author_list,
                'published': published,
                'paper_url': paper_url,
                'pdf_url': pdf_url,
                'project_page': project_page,
                'github_repo': github_repo,
                'ai_summary': ai_summary,
                'categories': categories,
                'source': 'huggingface'
            }

        except Exception as e:
            print(f"⚠️  解析论文数据失败: {e}")
            return None

    def _detect_categories(self, title: str, summary: str) -> List[str]:
        """
        检测论文所属类别

        Args:
            title: 论文标题
            summary: 论文摘要

        Returns:
            类别列表
        """
        text = f"{title} {summary}".lower()

        detected = []

        for category, keywords in self.DEFAULT_CATEGORIES.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    detected.append(category)
                    break

        return detected

    def fetch_recent_papers(self) -> List[Dict]:
        """
        获取最近几天的论文

        Returns:
            论文列表
        """
        all_papers = []
        seen_ids = set()  # 去重

        for i in range(self.days_back):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            papers = self.fetch_papers(date)

            for paper in papers:
                if paper['paper_id'] not in seen_ids:
                    seen_ids.add(paper['paper_id'])
                    all_papers.append(paper)

            if len(all_papers) >= self.max_papers:
                break

            time.sleep(0.5)  # 避免请求过快

        return all_papers[:self.max_papers]


# 测试代码
if __name__ == "__main__":
    fetcher = HuggingFacePaperFetcher(days_back=1, max_papers=5)
    papers = fetcher.fetch_recent_papers()

    print("\n" + "=" * 60)
    print("📚 Hugging Face Daily Papers")
    print("=" * 60)

    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   作者: {paper['author_str']}")
        print(f"   发布: {paper['published']}")
        print(f"   链接: {paper['paper_url']}")
        print(f"   摘要: {paper['summary'][:100]}...")
