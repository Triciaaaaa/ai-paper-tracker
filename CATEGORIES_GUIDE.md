# 论文推送类别配置指南

本文档说明如何配置论文推送的关键词过滤类别。

## 📊 当前关注的领域

### 核心领域：数据工程与 VLM 训练

#### 1. **vlm_data_strategy** - VLM 训练数据策略
关注视觉语言模型的训练数据设计、配方和优化方法

**关键词包括**：
- Vision-language model training data
- Visual instruction tuning
- Multimodal data curation
- Image-text pair quality
- VLM training recipe

**典型论文主题**：
- "Data recipe for visual instruction tuning"
- "High-quality image-text dataset construction"
- "Curating multimodal training data for VLMs"

---

#### 2. **data_engineering** - 数据工程体系
关注服务算法团队的数据基础设施和工程实践

**关键词包括**：
- Data engineering & infrastructure
- Data-centric AI
- Data quality & curation
- Data platform & pipeline
- DataOps

**典型论文主题**：
- "Building data infrastructure for ML teams"
- "Data quality assessment frameworks"
- "Scalable data pipelines for AI"

---

#### 3. **training_data_strategy** - 训练数据策略
关注训练数据的选择、组合、优化方法

**关键词包括**：
- Training data strategy & selection
- Data pruning & filtering
- Curriculum learning
- Data augmentation & synthesis
- Instruction tuning data

**典型论文主题**：
- "Data selection for efficient LLM training"
- "Curriculum learning for language models"
- "Synthetic data generation for training"

---

#### 4. **data_methodology** - 前沿数据方法论
关注国际最前沿的数据研究方法论

**关键词包括**：
- Data-centric development paradigms
- Data quality assessment
- Weak supervision
- Self-supervised data
- Data efficiency & scaling

**典型论文主题**：
- "Data is all you need: methodology"
- "Data efficiency in pre-training"
- "Weak supervision for dataset creation"

---

### 辅助领域

#### 5. **vision_language** - 视觉语言模型
VLM 相关的基础研究

**关键词包括**：
- Vision-language models
- Visual reasoning
- Multimodal understanding
- Vision transformers

---

#### 6. **alignment** - AI 对齐
模型对齐、安全性和价值学习

---

#### 7. **reasoning** - 推理能力
模型的推理和逻辑能力研究

---

## ⚙️ 配置方法

### 方法 1：修改环境变量

编辑 `papers.sh` 或在运行时设置：

```bash
export HF_CATEGORIES='vlm_data_strategy,data_engineering,training_data_strategy,data_methodology'
```

### 方法 2：修改默认配置

编辑 `hf_papers_advanced.py` 第 30 行：

```python
CATEGORY_FILTERS = os.getenv('HF_CATEGORIES',
    'vlm_data_strategy,data_engineering,training_data_strategy,data_methodology')
```

### 方法 3：运行时指定

```bash
HF_CATEGORIES='vlm_data_strategy,data_engineering' ./papers.sh
```

---

## 🎯 推荐配置组合

### 最前沿数据研究
```bash
HF_CATEGORIES='vlm_data_strategy,training_data_strategy,data_methodology,data_engineering'
```

### VLM 专注
```bash
HF_CATEGORIES='vlm_data_strategy,vision_language,multimodal,training_data_strategy'
```

### 全栈数据 + 算法
```bash
HF_CATEGORIES='data_engineering,training_data_strategy,data_methodology,alignment,reasoning'
```

### 宽泛探索（不过滤）
```bash
HF_CATEGORIES=''
```

---

## 📈 可用的所有类别

### 数据相关（新增）
- `vlm_data_strategy` - VLM 训练数据策略
- `data_engineering` - 数据工程体系
- `training_data_strategy` - 训练数据策略
- `data_methodology` - 前沿数据方法论

### 模型相关
- `vision_language` - 视觉语言模型
- `multimodal` - 多模态模型
- `llm` - 大语言模型
- `reasoning` - 推理能力

### 算法相关
- `alignment` - AI 对齐
- `reinforcement_learning` - 强化学习
- `rl_verification` - RL 验证

### 数学与形式化
- `ai4math` - AI for Math
- `auto_formalization` - 自动形式化

### 其他
- `computer_vision` - 计算机视觉
- `generative` - 生成模型
- `agents` - AI Agent

---

## 🔍 自定义关键词

如果需要添加新的关键词，编辑 `hf_paper_fetcher.py`：

```python
DEFAULT_CATEGORIES = {
    'your_category': [
        'keyword1',
        'keyword2',
        'keyword3'
    ]
}
```

---

## 📌 最佳实践

1. **定期调整**：根据研究重点变化，每月调整一次类别
2. **保持开放**：保留 1-2 个宽泛类别（如 `reasoning`），避免错过交叉领域
3. **质量优先**：减少类别数量，提高每篇论文的相关性
4. **A/B 测试**：尝试不同组合，观察推送质量

---

## 🚀 快速开始

### 立即测试新配置

```bash
cd /Users/bytedance/ai-paper-tracker
./papers.sh
```

### 查看当前配置

```bash
cat hf_papers_advanced.py | grep CATEGORY_FILTERS
```

---

**最后更新**: 2026-01-28
**维护**: 根据最新研究趋势每季度更新一次
