#!/usr/bin/env python3
"""
🤖 AI 摘要生成器
支持 Claude, Gemini, OpenAI 等多种 LLM
"""

import os
from typing import Dict, Optional


class AISummarizer:
    """AI 摘要生成器"""

    def __init__(self, provider: str = "claude", api_key: str = None, model: str = None):
        """
        初始化摘要生成器

        Args:
            provider: 提供商 (claude, gemini, openai)
            api_key: API 密钥
            model: 模型名称
        """
        self.provider = provider
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY', '') if provider == 'claude' else \
                       os.getenv('GEMINI_API_KEY', '') if provider == 'gemini' else \
                       os.getenv('OPENAI_API_KEY', '')

        # 默认模型配置
        if model is None:
            model = {
                'claude': 'claude-sonnet-4-20250514',
                'gemini': 'gemini-2.0-flash-exp',
                'openai': 'gpt-4o'
            }.get(provider, 'claude-sonnet-4-20250514')

        self.model = model

    def summarize_paper(self, paper: Dict, use_hf_summary: bool = False, prev_context: str = None) -> Optional[str]:
        """
        为论文生成摘要

        Args:
            paper: 论文数据
            use_hf_summary: 是否优先使用 HF 提供的简短摘要
            prev_context: 前一天的推送摘要，用于生成有延续性的解读

        Returns:
            生成的摘要文本
        """
        if use_hf_summary and paper.get('ai_summary'):
            return f"📌 **HF AI 摘要**:\n{paper['ai_summary']}"

        if not self.api_key:
            print(f"⚠️  未配置 {self.provider} API key")
            return None

        try:
            if self.provider == 'openai':
                return self._summarize_with_openai(paper, prev_context)
            elif self.provider == 'claude':
                return self._summarize_with_claude(paper)
            elif self.provider == 'gemini':
                return self._summarize_with_gemini(paper)
            else:
                print(f"⚠️  不支持的 provider: {self.provider}")
                return None

        except Exception as e:
            print(f"⚠️  {self.provider} 摘要生成失败: {e}")
            return None

    def summarize_blog(self, blog: Dict) -> Optional[str]:
        """
        为博客文章生成摘要

        Args:
            blog: 博客数据

        Returns:
            生成的摘要文本
        """
        if not self.api_key:
            return None

        # 优先使用全文内容
        content = blog.get('full_content', blog.get('summary', ''))

        if not content or len(content) < 100:
            return None

        try:
            if self.provider == 'openai':
                return self._summarize_blog_with_openai(blog, content)
            elif self.provider == 'claude':
                return self._summarize_blog_with_claude(blog, content)
            elif self.provider == 'gemini':
                return self._summarize_blog_with_openai(blog, content)
            else:
                return None

        except Exception as e:
            print(f"  ⚠️  博客摘要生成失败: {e}")
            return None

    def summarize_classic_paper(self, paper: Dict) -> Optional[str]:
        """为经典论文生成 AI 解读，聚焦历史意义"""
        if not self.api_key:
            return None

        try:
            import openai
            base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            if not base_url.endswith('/v1'):
                base_url = base_url.rstrip('/') + '/v1'

            client = openai.OpenAI(api_key=self.api_key, base_url=base_url)

            prompt = f"""请用中文解读这篇经典论文，100-150 字：

**标题**: {paper['title']} ({paper.get('year', '')})
**作者**: {paper['authors']}
**简介**: {paper['description']}
**关键词**: {', '.join(paper.get('keywords', []))}

请回答：
1. **历史地位**：这篇论文在 AI 发展史上的位置
2. **核心贡献**：最关键的创新点
3. **当今影响**：对今天的研究/工业界还有什么影响

简洁直接。"""

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是 AI 研究助手，擅长解读经典论文的历史意义和当代价值。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )

            summary = response.choices[0].message.content.strip()
            print(f"  ✅ 经典论文解读生成成功，长度: {len(summary)} 字符")
            return f"🤖 **AI 解读**:\n\n{summary}"

        except Exception as e:
            print(f"  ⚠️  经典论文解读失败: {e}")
            return None

    def _summarize_blog_with_claude(self, blog: Dict, content: str) -> Optional[str]:
        """使用 Claude 生成博客摘要"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            prompt = f"""请用中文简要总结这篇博客，控制在 150-200 字：

**标题**: {blog['title']}
**来源**: {blog['source']}

**内容**:
{content[:2000]}

请回答：
1. **核心观点**：文章主要说了什么（1-2 句）
2. **关键发现**：最重要的信息或结论
3. **值得关注**：对 AI 从业者的启发

简洁直接。"""

            response = client.messages.create(
                model=self.model,
                max_tokens=600,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            summary = response.content[0].text.strip()
            print(f"  ✅ 博客摘要生成成功，长度: {len(summary)} 字符")
            return summary

        except Exception as e:
            print(f"  ⚠️  Claude 博客摘要失败: {e}")
            return None

    def _summarize_blog_with_openai(self, blog: Dict, content: str) -> Optional[str]:
        """使用 OpenAI（兼容）生成博客摘要"""
        try:
            import openai

            base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            if not base_url.endswith('/v1'):
                base_url = base_url.rstrip('/') + '/v1'

            client = openai.OpenAI(api_key=self.api_key, base_url=base_url)

            prompt = f"""请用中文简要总结这篇博客，控制在 150-200 字：

**标题**: {blog['title']}
**来源**: {blog['source']}

**内容**:
{content[:2000]}

请回答：
1. **核心观点**：文章主要说了什么（1-2 句）
2. **关键发现**：最重要的信息或结论
3. **值得关注**：对 AI 从业者的启发

简洁直接。"""

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个 AI 研究助手，擅长总结和分析技术博客文章。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=600,
                temperature=0.7
            )

            summary = response.choices[0].message.content.strip()
            print(f"  ✅ 博客摘要生成成功，长度: {len(summary)} 字符")
            return summary

        except Exception as e:
            print(f"  ⚠️  博客摘要 API 调用失败: {e}")
            return None

    def _summarize_with_claude(self, paper: Dict) -> Optional[str]:
        """使用 Claude 生成摘要"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)
            prompt = self._build_prompt(paper)

            response = client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            summary = response.content[0].text
            return f"🤖 **Claude 解读**:\n\n{summary}"

        except ImportError:
            print("⚠️  需要安装 anthropic 库: pip install anthropic")
            return None
        except Exception as e:
            print(f"⚠️  Claude API 调用失败: {e}")
            return None

    def _summarize_with_gemini(self, paper: Dict) -> Optional[str]:
        """使用 Gemini 生成摘要"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)

            prompt = self._build_prompt(paper)

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2000,
                    temperature=0.7
                )
            )

            summary = response.text
            return f"🤖 **Gemini 解读**:\n\n{summary}"

        except ImportError:
            print("⚠️  需要安装 google-generativeai 库: pip install google-generativeai")
            return None
        except Exception as e:
            print(f"⚠️  Gemini API 调用失败: {e}")
            return None

    def _summarize_with_openai(self, paper: Dict, prev_context: str = None) -> Optional[str]:
        """使用 OpenAI（或兼容的中转 API）生成摘要"""
        try:
            import openai

            base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            if not base_url.endswith('/v1'):
                base_url = base_url.rstrip('/') + '/v1'

            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )

            prompt = self._build_prompt(paper, prev_context)

            # 根据模型名称决定显示的标签
            model_name = self.model
            if 'claude' in model_name.lower():
                ai_label = "Claude 解读"
            elif 'gemini' in model_name.lower():
                ai_label = "Gemini 解读"
            elif 'gpt' in model_name.lower():
                ai_label = "GPT 解读"
            else:
                ai_label = "AI 解读"

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "你是 AI 研究助手，用中文简洁解读学术论文，重点突出创新点和实际价值。"
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
            print(f"  ✅ 生成成功，长度: {len(summary)} 字符")
            return f"🤖 **{ai_label}**:\n\n{summary}"

        except ImportError:
            print("⚠️  需要安装 openai 库: pip install openai")
            return None
        except Exception as e:
            print(f"⚠️  API 调用失败: {e}")
            return None

    def _build_prompt(self, paper: Dict, prev_context: str = None) -> str:
        """构建提示词"""
        context_section = ""
        if prev_context:
            context_section = f"""
**昨日推送摘要**（请参考，体现研究延续性）:
{prev_context}

"""

        prompt = f"""请用中文简要解读以下论文，控制在 200-300 字：
{context_section}
**标题**: {paper['title']}
**作者**: {paper.get('author_str', 'N/A')}
**摘要**: {paper['summary']}

请回答：
1. **做了什么**：一句话概括核心工作
2. **怎么做的**：关键方法（2-3 句）
3. **效果如何**：主要结果
4. **为什么重要**：对领域的意义{'，以及与昨日推送内容的关联' if prev_context else ''}

简洁直接，不要客套话。"""
        return prompt


def get_summarizer_from_env():
    """从环境变量获取摘要生成器"""
    provider = os.getenv('AI_PROVIDER', 'claude')  # 默认用 Claude

    # 优先获取特定 provider 的 API key，如果没有则使用 OPENAI_API_KEY
    api_key = os.getenv(f'{provider.upper()}_API_KEY', '') or os.getenv('OPENAI_API_KEY', '')

    # 获取模型名称
    model = os.getenv(f'{provider.upper()}_MODEL', None) or os.getenv('OPENAI_MODEL', None)

    # 如果都没设置，使用默认值
    if not model:
        model = {
            'claude': 'claude-sonnet-4-20250514',
            'gemini': 'gemini-2.0-flash-exp',
            'openai': 'gpt-4o'
        }.get(provider, 'claude-sonnet-4-20250514')

    return AISummarizer(provider=provider, api_key=api_key, model=model)
