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

    def summarize_paper(self, paper: Dict, use_hf_summary: bool = False) -> Optional[str]:
        """
        为论文生成详细摘要

        Args:
            paper: 论文数据
            use_hf_summary: 是否优先使用 HF 提供的简短摘要（默认 false，总是生成详细解读）

        Returns:
            生成的摘要文本
        """
        # 如果明确要求使用 HF 摘要且存在，则使用
        if use_hf_summary and paper.get('ai_summary'):
            return f"📌 **HF AI 摘要**:\n{paper['ai_summary']}"

        if not self.api_key:
            print(f"⚠️  未配置 {self.provider} API key")
            return None

        # 调用 LLM 生成详细解读
        try:
            # 中转 API 模式：使用 openai 客户端调用任何模型
            if self.provider == 'openai':
                return self._summarize_with_openai(paper)
            elif self.provider == 'claude':
                # 检查是否使用中转 API
                if os.getenv('OPENAI_BASE_URL'):
                    # 使用中转 API 调用 Claude
                    return self._summarize_with_openai(paper)
                else:
                    # 直接调用 Claude 官方 API
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
            # 使用中转 API
            if os.getenv('OPENAI_BASE_URL') or self.provider == 'openai':
                return self._summarize_blog_with_openai(blog, content)
            elif self.provider == 'claude':
                return self._summarize_blog_with_openai(blog, content)
            else:
                return None

        except Exception as e:
            print(f"  ⚠️  博客摘要生成失败: {e}")
            return None

    def _summarize_blog_with_openai(self, blog: Dict, content: str) -> Optional[str]:
        """使用 OpenAI（兼容）生成博客摘要"""
        try:
            import openai

            base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            if not base_url.endswith('/v1'):
                base_url = base_url.rstrip('/') + '/v1'

            client = openai.OpenAI(api_key=self.api_key, base_url=base_url)

            prompt = f"""请详细总结这篇博客文章的核心观点：

**标题**: {blog['title']}
**来源**: {blog['source']}
**链接**: {blog['link']}

**文章内容**:
{content[:3000]}

请按以下格式回答（用中文，详细说明）：

## 核心观点
这篇文章的主要观点是什么？

## 关键信息
- 作者/发布者
- 讨论的核心问题
- 提出的方法或发现
- 重要的数据或结论

## 个人解读
如果你是 AI 研究者，你会如何评价这篇文章？它对这个领域有什么启发？

直接返回上述格式的内容，字数 500-800 字。"""

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
                max_tokens=2000,
                temperature=0.7
            )

            summary = response.choices[0].message.content.strip()
            print(f"  ✅ 博客摘要生成成功，长度: {len(summary)} 字符")
            return f"🤖 **AI 解读**:\n\n{summary}"

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

    def _summarize_with_openai(self, paper: Dict) -> Optional[str]:
        """使用 OpenAI（或兼容的中转 API）生成摘要"""
        try:
            import openai

            # 获取 base_url，确保包含 /v1 路径
            base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            if not base_url.endswith('/v1'):
                base_url = base_url.rstrip('/') + '/v1'

            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )

            prompt = self._build_prompt(paper)

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
                        "content": "你是一个专业的 AI 研究助手，擅长深入分析和总结学术论文。请用中文回答，回答要详细且有深度。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=3000,  # 增加输出长度
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

    def _build_prompt(self, paper: Dict) -> str:
        """构建提示词"""
        prompt = f"""请深入分析以下论文并提供详细的中文解读：

**标题**: {paper['title']}
**作者**: {paper.get('author_str', 'N/A')}
**发布时间**: {paper.get('published', 'N/A')}
**原始摘要**: {paper['summary']}

请按以下结构回答（每部分详细说明，用中文）：

## 核心问题
这篇论文试图解决什么问题？

## 主要贡献
论文的核心创新点和贡献是什么？（列举 3-5 点）

## 技术方法
使用了什么方法或技术？（详细说明）

## 实验结果
主要实验结果和性能表现如何？

## 价值意义
这项研究的重要性在哪里？对未来工作有什么启发？

## 个人观点
如果你是研究者，你会如何评价这项工作？

直接返回上述格式的内容，不要其他客套话。"""
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
