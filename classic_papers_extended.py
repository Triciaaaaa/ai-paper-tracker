#!/usr/bin/env python3
"""
📚 经典论文模块（扩展版）
精选 AI 领域的经典论文，包含领域关键词解析
"""

from typing import List, Dict, Optional


# 经典论文列表（大幅扩展）
CLASSIC_PAPERS = {
    'reinforcement_learning': [
        {
            'title': 'Reinforcement Learning: An Introduction (2nd Edition)',
            'authors': 'Richard S. Sutton, Andrew G. Barto',
            'year': '2018',
            'url': 'https://mitpress.mit.edu/books/reinforcement-learning-second-edition',
            'description': '强化学习领域的圣经，系统介绍了 RL 的理论基础，包括 TD 学习、策略梯度等核心概念。',
            'keywords': ['reinforcement learning', 'temporal difference', 'Q-learning', 'policy gradient', 'value function', 'exploration']
        },
        {
            'title': 'Human-level control through deep reinforcement learning',
            'authors': 'Mnih et al. (DeepMind)',
            'year': '2015',
            'url': 'https://www.nature.com/articles/nature14236',
            'description': 'DQN 论文，深度强化学习的里程碑工作，展示了 AI 可以通过端到端学习达到人类水平的控制能力。',
            'keywords': ['DQN', 'deep RL', 'Q-learning', 'atari games', 'convolutional neural network']
        },
        {
            'title': 'Policy Gradient Methods for Reinforcement Learning with Function Approximation',
            'authors': 'Sutton, McAllester, Singh, Mansour',
            'year': '2000',
            'url': 'https://proceedings.neurips.cc/paper/2000/file/461271028c68e8f25be1b2a2fb309df9-Paper.pdf',
            'description': '策略梯度方法的理论基础，证明了策略梯度方法的收敛性。',
            'keywords': ['policy gradient', 'function approximation', 'actor-critic', 'convergence']
        },
        {
            'title': 'Asynchronous Methods for Deep Reinforcement Learning',
            'authors': 'Mnih et al. (DeepMind)',
            'year': '2016',
            'url': 'https://arxiv.org/abs/1602.01783',
            'description': 'A3C 算法，异步Actor-Critic，解决了大规模分布式 RL 的训练问题。',
            'keywords': ['A3C', 'asynchronous', 'actor-critic', 'distributed RL', 'parallel']
        },
        {
            'title': 'Proximal Policy Optimization Algorithms (PPO)',
            'authors': 'Schulman et al. (OpenAI)',
            'year': '2017',
            'url': 'https://arxiv.org/abs/1707.06347',
            'description': 'PPO 算法，平衡了 sample 复杂度和实现复杂性，成为最流行的 RL 算法之一。',
            'keywords': ['PPO', 'trust region', 'policy optimization', 'clipped surrogate', 'sample efficiency']
        },
        {
            'title': 'Reward Shaping',
            'authors': 'Ng, Harada, Russell (UC Berkeley)',
            'year': '1999',
            'url': 'https://people.eecs.berkeley.edu/~pabbeel/cs287/npapers/99-shaping.pdf',
            'description': '奖励塑造理论，证明了如何在不改变最优策略的前提下设计奖励函数。',
            'keywords': ['reward shaping', 'potential-based reward', 'reward hypothesis', 'optimal policy']
        }
    ],
    'alignment': [
        {
            'title': 'Concrete Problems in AI Safety',
            'authors': 'Amodei et al. (OpenAI)',
            'year': '2016',
            'url': 'https://arxiv.org/abs/1606.06565',
            'description': 'AI 安全领域的经典论文，提出了具体的 safety 问题：避免负面影响、奖励干扰、可扩展的监督、安全探索等。',
            'keywords': ['AI safety', 'reward hacking', 'side effects', 'scalable oversight', 'safe exploration']
        },
        {
            'title': 'Scalable Agent Alignment via Reward Modeling',
            'authors': 'Leike et al. (DeepMind)',
            'year': '2018',
            'url': 'https://arxiv.org/abs/1811.07871',
            'description': 'RLHF 的基础论文之一，提出了通过奖励建模来对齐 Agent 行为的方法。',
            'keywords': ['RLHF', 'reward modeling', 'human feedback', 'agent alignment', 'preference learning']
        },
        {
            'title': 'Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback',
            'authors': 'Bai et al. (Anthropic)',
            'year': '2022',
            'url': 'https://arxiv.org/abs/2204.05862',
            'description': 'Constitutional AI 的基础，Anthropic 的核心工作，通过 RLHF 训练出有用且无害的 AI。',
            'keywords': ['RLHF', 'constitutional AI', 'harmlessness', 'helpfulness', 'HHH']
        },
        {
            'title': 'Language Models are Few-Shot Learners',
            'authors': 'Brown et al. (OpenAI)',
            'year': '2020',
            'url': 'https://arxiv.org/abs/2005.14165',
            'description': 'GPT-3 论文，展示了大语言模型的少样本学习能力，为 AI 对齐研究提供了新的方向。',
            'keywords': ['GPT-3', 'few-shot learning', 'in-context learning', 'language models', 'scaling laws']
        },
        {
            'title': 'Prima Facie Approximations of Value Learning',
            'authors': 'Uehara et al.',
            'year': '2020',
            'url': 'https://arxiv.org/abs/2010.08519',
            'description': '价值学习的基础理论，分析了 reward hacking 问题。',
            'keywords': ['value learning', 'reward hacking', 'preference learning', 'approximation']
        }
    ],
    'ai4math': [
        {
            'title': 'Solving Olympiad Geometry without Human Demonstrations',
            'authors': 'Tao et al. (Google)',
            'year': '2024',
            'url': 'https://nature.com/articles/s41586-024-08067-6',
            'description': 'AlphaGeometry，AI 解数学题的里程碑，达到了国际奥数几何金牌水平。',
            'keywords': ['AlphaGeometry', 'theorem proving', 'geometry', 'mathematical reasoning', 'synthetic data']
        },
        {
            'title': 'Advancing Mathematics by Guiding Large Language Models',
            'authors': 'Tao et al.',
            'year': '2024',
            'url': 'https://arxiv.org/abs/2312.06761',
            'description': '陶哲轩团队用 LLM 辅助数学研究，展示了 AI 在数学发现中的潜力。',
            'keywords': ['LLM for math', 'mathematical discovery', 'formal proof', 'computer algebra']
        },
        {
            'title': 'Neural Theorem Provers: An Update',
            'authors': 'Polu et al.',
            'year': '2022',
            'url': 'https://arxiv.org/abs/2209.05777',
            'description': '神经定理证明器的最新进展，包括在 Lean 4 中证明数学定理。',
            'keywords': ['theorem proving', 'formal verification', 'Lean', 'tactics', 'mathlib']
        },
        {
            'title': 'Mathematical Reasoning with Lean 4',
            'authors': 'Ullrich et al.',
            'year': '2024',
            'url': 'https://arxiv.org/abs/2312.06483',
            'description': 'Lean 4 数学推理系统的最新进展。',
            'keywords': ['Lean 4', 'mathematical reasoning', 'formal proof assistant', 'proof automation']
        }
    ],
    'formal_verification': [
        {
            'title': 'Communicating Sequential Processes',
            'authors': 'Tony Hoare',
            'year': '1978',
            'url': 'https://www.cs.ox.ac.uk/files/3328/CSP.pdf',
            'description': 'CSP 理论，用于描述并发系统的通信行为，是形式化验证的基础理论。',
            'keywords': ['CSP', 'concurrency', 'process algebra', 'formal methods', 'channels']
        },
        {
            'title': 'Computation Tree Logic (CTL)',
            'authors': 'Clarke, Emerson',
            'year': '1981',
            'url': 'https://doi.org/10.1145/322186.322201',
            'description': 'CTL 模型验证的基础，用于验证有限状态系统的性质。',
            'keywords': ['CTL', 'model checking', 'temporal logic', 'verification', 'state space']
        },
        {
            'title': 'Model Checking',
            'authors': 'Clarke, Grumberg, Peled',
            'year': '1999',
            'url': 'https://mitpress.mit.edu/books/model-checking/',
            'description': '模型验证的经典教材，系统介绍了模型验证的理论和实践。',
            'keywords': ['model checking', 'temporal logic', 'model checking', 'verification', 'SPIN model checker']
        },
        {
            'title': 'The Temporal Logic of Reactive and Concurrent Systems: Specification and Verification',
            'authors': 'Manna, Pnueli',
            'year': '1992',
            'url': 'https://mitpress.mit.edu/books/temporal-logic/',
            'description': '时序逻辑的经典著作，用于验证反应式和并发系统的性质。',
            'keywords': ['temporal logic', 'reactive systems', 'concurrency', 'specification', 'verification']
        }
    ],
    'llm': [
        {
            'title': 'Attention Is All You Need',
            'authors': 'Vaswani et al.',
            'year': '2017',
            'url': 'https://arxiv.org/abs/1706.03762',
            'description': 'Transformer 架构的奠基之作，self-attention 机制改变了 NLP 和 RL 领域。',
            'keywords': ['Transformer', 'self-attention', 'attention mechanism', 'encoder-decoder', 'multi-head attention']
        },
        {
            'title': 'Language Models are Few-Shot Learners',
            'authors': 'Brown et al. (OpenAI)',
            'year': '2020',
            'url': 'https://arxiv.org/abs/2005.14165',
            'description': 'GPT-3 论文，展示了大语言模型的 emergent 能力，包括 few-shot learning。',
            'keywords': ['GPT-3', 'few-shot learning', 'in-context learning', 'emergent abilities', 'scaling']
        },
        {
            'title': 'Constitutional AI: Harmlessness from AI Feedback',
            'authors': 'Bai et al. (Anthropic)',
            'year': '2022',
            'url': 'https://arxiv.org/abs/2212.08073',
            'description': 'Constitutional AI 的完整论文，提出通过 AI 反馈来训练无害的 AI。',
            'keywords': ['constitutional AI', 'AI feedback', 'harmlessness', 'RLAIF', 'critic']
        },
        {
            'title': 'Training Language Models to Follow Instructions with Human Feedback',
            'authors': 'Ouyang et al. (OpenAI)',
            'year': '2022',
            'url': 'https://arxiv.org/abs/2203.02155',
            'description': 'InstructGPT 的论文，展示了通过人类反馈训练让模型遵循指令。',
            'keywords': ['InstructGPT', 'instruction following', 'RLHF', 'fine-tuning', 'human feedback']
        }
    ],
    'data_engineering': [
        {
            'title': 'DataComp: In search of the next generation of multimodal datasets',
            'authors': 'Gadre et al. (UW, Google, LAION)',
            'year': '2023',
            'url': 'https://arxiv.org/abs/2304.14108',
            'description': '提出了数据竞赛范式，系统研究了不同数据过滤策略对 CLIP 模型性能的影响，建立了 multimodal 数据集构建的 benchmark。',
            'keywords': ['data curation', 'CLIP', 'data filtering', 'multimodal dataset', 'benchmark']
        },
        {
            'title': 'The Pile: An 800GB Dataset of Diverse Text for Language Modeling',
            'authors': 'Gao et al. (EleutherAI)',
            'year': '2020',
            'url': 'https://arxiv.org/abs/2101.00027',
            'description': '开源的大规模预训练数据集，包含 22 个子集覆盖多样文本来源，推动了开源 LLM 生态发展。',
            'keywords': ['pre-training data', 'dataset construction', 'data diversity', 'language modeling', 'open source']
        },
        {
            'title': 'Data-centric Artificial Intelligence: A Survey',
            'authors': 'Zha et al.',
            'year': '2023',
            'url': 'https://arxiv.org/abs/2303.10158',
            'description': '以数据为中心的 AI 系统综述，覆盖数据收集、标注、清洗、质量评估等全链路方法论。',
            'keywords': ['data-centric AI', 'data quality', 'data annotation', 'data augmentation', 'data management']
        },
        {
            'title': 'Scaling Data-Constrained Language Models',
            'authors': 'Muennighoff et al. (BigScience)',
            'year': '2023',
            'url': 'https://arxiv.org/abs/2305.16264',
            'description': '研究了数据受限条件下的 LLM 训练策略，发现多次重复训练数据可有效利用，为数据有限场景提供了理论依据。',
            'keywords': ['data scaling', 'data repetition', 'sample efficiency', 'scaling laws', 'data-constrained']
        },
        {
            'title': 'D4: Improving LLM Pretraining via Document De-Duplication and Diversification',
            'authors': 'Tirumala et al. (Meta)',
            'year': '2023',
            'url': 'https://arxiv.org/abs/2308.12284',
            'description': '提出文档级去重和多样化策略，系统性地改善了预训练数据质量，显著提升 LLM 下游性能。',
            'keywords': ['deduplication', 'data diversity', 'pre-training data', 'data quality', 'data pipeline']
        }
    ],
    'multimodal': [
        {
            'title': 'Learning Transferable Visual Models From Natural Language Supervision (CLIP)',
            'authors': 'Radford et al. (OpenAI)',
            'year': '2021',
            'url': 'https://arxiv.org/abs/2103.00020',
            'description': 'CLIP 模型，通过自然语言监督学习视觉表示，开创了 vision-language 对齐的新范式，在零样本分类上表现出色。',
            'keywords': ['CLIP', 'vision-language', 'contrastive learning', 'zero-shot', 'image-text alignment']
        },
        {
            'title': 'Visual Instruction Tuning (LLaVA)',
            'authors': 'Liu et al. (UW, Microsoft)',
            'year': '2023',
            'url': 'https://arxiv.org/abs/2304.08485',
            'description': 'LLaVA 模型，首次将视觉指令微调引入多模态 LLM，证明了简单高效的 VLM 训练方案的可行性。',
            'keywords': ['LLaVA', 'visual instruction tuning', 'VLM', 'multimodal LLM', 'instruction following']
        },
        {
            'title': 'Flamingo: a Visual Language Model for Few-Shot Learning',
            'authors': 'Alayrac et al. (DeepMind)',
            'year': '2022',
            'url': 'https://arxiv.org/abs/2204.14198',
            'description': 'Flamingo 模型，通过交叉注意力融合视觉和语言模态，展示了多模态少样本学习的强大能力。',
            'keywords': ['Flamingo', 'few-shot learning', 'cross-attention', 'vision-language model', 'multimodal']
        },
        {
            'title': 'InternVL: Scaling up Vision Foundation Models and Aligning for Generic Visual-Linguistic Tasks',
            'authors': 'Chen et al. (Shanghai AI Lab)',
            'year': '2024',
            'url': 'https://arxiv.org/abs/2312.14238',
            'description': 'InternVL 系列，将视觉基础模型扩展到 6B 参数并与 LLM 对齐，在多个 VL benchmark 上达到 SOTA。',
            'keywords': ['InternVL', 'vision foundation model', 'VLM', 'visual-linguistic', 'scaling']
        }
    ],
    'scaling_laws': [
        {
            'title': 'Scaling Laws for Neural Language Models',
            'authors': 'Kaplan et al. (OpenAI)',
            'year': '2020',
            'url': 'https://arxiv.org/abs/2001.08361',
            'description': '首次系统性提出 LLM scaling laws，揭示了模型大小、数据量和计算量与性能之间的幂律关系。',
            'keywords': ['scaling laws', 'power law', 'compute-optimal', 'language models', 'neural scaling']
        },
        {
            'title': 'Training Compute-Optimal Large Language Models (Chinchilla)',
            'authors': 'Hoffmann et al. (DeepMind)',
            'year': '2022',
            'url': 'https://arxiv.org/abs/2203.15556',
            'description': 'Chinchilla 论文，修正了 Kaplan 的 scaling laws，证明了训练数据量被严重低估，改变了 LLM 训练策略。',
            'keywords': ['Chinchilla', 'compute-optimal', 'scaling laws', 'data scaling', 'training efficiency']
        },
        {
            'title': 'Scaling Laws for Autoregressive Generative Modeling',
            'authors': 'Henighan et al. (OpenAI)',
            'year': '2020',
            'url': 'https://arxiv.org/abs/2010.14701',
            'description': '将 scaling laws 扩展到多模态生成模型，揭示了不同模态（文本、图像、视频等）的统一缩放规律。',
            'keywords': ['scaling laws', 'generative models', 'multimodal', 'autoregressive', 'cross-modal scaling']
        },
        {
            'title': 'Scaling Data-Constrained Language Models',
            'authors': 'Muennighoff et al. (BigScience)',
            'year': '2023',
            'url': 'https://arxiv.org/abs/2305.16264',
            'description': '研究了数据受限条件下的 scaling 行为，发现多 epoch 训练比想象中有效，为数据有限场景提供了新视角。',
            'keywords': ['data scaling', 'data repetition', 'epoch', 'scaling laws', 'data-constrained training']
        }
    ],
    'information_theory': [
        {
            'title': 'A Mathematical Theory of Communication',
            'authors': 'Claude E. Shannon',
            'year': '1948',
            'url': 'https://people.math.harvard.edu/~ctm/home/text/others/shannon1948.pdf',
            'description': '信息论的奠基之作，定义了熵和互信息，奠定了数字通信的理论基础，对 ML 中的损失函数、信息瓶颈等有深远影响。',
            'keywords': ['information theory', 'entropy', 'mutual information', 'channel capacity', 'coding theory']
        },
        {
            'title': 'Information Bottleneck Method',
            'authors': 'Tishby, Pereira, Biale',
            'year': '2000',
            'url': 'https://arxiv.org/abs/0001.2103',
            'description': '信息瓶颈方法，用于理解神经网络中的表示学习。',
            'keywords': ['information bottleneck', 'representation learning', 'compression', 'mutual information', 'minimal sufficient statistic']
        }
    ]
}


class ClassicPaperFetcher:
    """经典论文获取器"""

    def __init__(self, categories: List[str] = None):
        """
        初始化

        Args:
            categories: 要获取的类别
        """
        self.categories = categories or list(CLASSIC_PAPERS.keys())

    def get_papers(self, limit: int = None) -> List[Dict]:
        """获取经典论文列表"""
        papers = []

        for category in self.categories:
            if category in CLASSIC_PAPERS:
                for paper in CLASSIC_PAPERS[category]:
                    papers.append({
                        **paper,
                        'category': category,
                        'source': 'classic',
                        'is_classic': True
                    })

        if limit:
            papers = papers[:limit]

        return papers

    def get_random_paper(self) -> Dict:
        """获取一篇随机经典论文"""
        import random
        all_papers = self.get_papers()
        return random.choice(all_papers) if all_papers else None

    def get_papers_by_keyword(self, keyword: str) -> List[Dict]:
        """根据关键词搜索相关论文"""
        keyword = keyword.lower()
        results = []

        for category, papers in CLASSIC_PAPERS.items():
            for paper in papers:
                # 搜索标题、描述和关键词
                if (keyword in paper['title'].lower() or
                    keyword in paper['description'].lower() or
                    any(keyword in kw.lower() for kw in paper.get('keywords', []))):
                    results.append({
                        **paper,
                        'category': category,
                        'source': 'classic'
                    })

        return results

    def format_keywords_analysis(self, paper: Dict) -> str:
        """格式化领域关键词解析"""
        keywords = paper.get('keywords', [])
        if not keywords:
            return ""

        analysis = f"\n🔑 **领域关键词解析**:\n"
        analysis += f"这篇论文属于 **{paper['category']}** 领域，核心概念包括：\n\n"
        analysis += "```"
        for kw in keywords:
            analysis += f"• {kw}\n"
        analysis += "```\n\n"

        # 添加相关领域的交叉参考
        related = self._find_related_categories(paper['category'], keywords)
        if related:
            analysis += f"🔗 **相关领域**: {', '.join(related)}\n\n"

        return analysis

    def _find_related_categories(self, current_category: str, keywords: List[str]) -> List[str]:
        """找出相关的其他类别"""
        category_relations = {
            'reinforcement_learning': ['llm', 'agents', 'alignment'],
            'alignment': ['llm', 'reinforcement_learning'],
            'ai4math': ['llm', 'reasoning'],
            'formal_verification': ['ai4math', 'reasoning'],
            'llm': ['alignment', 'reasoning', 'scaling_laws'],
            'data_engineering': ['scaling_laws', 'llm', 'multimodal'],
            'multimodal': ['data_engineering', 'llm', 'scaling_laws'],
            'scaling_laws': ['llm', 'data_engineering']
        }

        return category_relations.get(current_category, [])


def format_classic_paper_card(paper: Dict) -> Dict:
    """格式化为飞书卡片元素"""
    fetcher = ClassicPaperFetcher()

    title = f"📖 {paper['title']}"
    if paper.get('year'):
        title += f" ({paper['year']})"

    content = f"**{paper['title']}** ({paper.get('year', 'N/A')})\n\n"
    content += f"👥 **作者**: {paper['authors']}\n\n"
    content += f"📝 **简介**: {paper['description']}\n\n"

    # 添加关键词解析
    keywords_analysis = fetcher.format_keywords_analysis(paper)
    content += keywords_analysis

    return {
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": content
        }
    }


if __name__ == "__main__":
    fetcher = ClassicPaperFetcher(['reinforcement_learning', 'alignment'])
    papers = fetcher.get_papers()

    print("=" * 60)
    print("📚 经典论文")
    print("=" * 60)

    for i, paper in enumerate(papers, 1):
        print(f"\n{i}. {paper['title']} ({paper['year']})")
        print(f"   作者: {paper['authors']}")
        print(f"   简介: {paper['description']}")
        print(f"   关键词: {', '.join(paper.get('keywords', []))}")
