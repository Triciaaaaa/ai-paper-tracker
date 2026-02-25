# 🚀 论文推送快速使用指南

## ✅ 已完成的配置

### 新增的论文类别

根据你的需求，已添加以下 4 个核心领域：

1. **vlm_data_strategy** - VLM 训练数据策略
   - 关注视觉语言模型的训练数据设计
   - 包括：image-text 质量评估、multimodal data curation、visual instruction tuning

2. **data_engineering** - 数据工程体系
   - 关注服务算法团队的数据基础设施
   - 包括：data pipeline、data quality、data platform、DataOps

3. **training_data_strategy** - 训练数据策略
   - 关注训练数据的选择、组合和优化
   - 包括：data selection、data pruning、curriculum learning、synthetic data

4. **data_methodology** - 前沿数据方法论
   - 关注国际最前沿的数据研究方法论
   - 包括：data-centric AI、weak supervision、data efficiency

## 📋 当前配置

### papers.sh 中的设置

```bash
export HF_CATEGORIES="vlm_data_strategy,data_engineering,training_data_strategy,data_methodology,vision_language,alignment"
```

这意味着你将收到：
- ✅ VLM 数据策略相关论文
- ✅ 数据工程相关论文
- ✅ 训练数据策略相关论文
- ✅ 数据方法论相关论文
- ✅ 视觉语言模型相关论文
- ✅ AI 对齐相关论文

## 🎯 使用方法

### 立即测试

```bash
cd /Users/bytedance/ai-paper-tracker

# 测试类别检测功能
python3 test_categories.py

# 手动运行一次推送（测试）
./papers.sh
```

### 查看当前配置

```bash
# 查看配置的类别
cat papers.sh | grep HF_CATEGORIES

# 查看所有可用类别
python3 test_categories.py | grep "可用的类别"
```

### 调整关注的领域

编辑 `papers.sh`，修改 `HF_CATEGORIES`：

```bash
# 只关注 VLM 数据策略
export HF_CATEGORIES="vlm_data_strategy,vision_language"

# 关注所有数据相关领域
export HF_CATEGORIES="vlm_data_strategy,data_engineering,training_data_strategy,data_methodology"

# 宽泛探索（不限制）
export HF_CATEGORIES=""
```

## 📚 详细文档

- **CATEGORIES_GUIDE.md** - 完整的类别配置指南
- **test_categories.py** - 类别检测测试工具

## 🔍 关键词覆盖范围

### VLM 训练数据策略 (vlm_data_strategy)
- vision-language model training data
- visual instruction tuning
- image-text pair quality
- multimodal data curation
- vlm dataset
- vlm training recipe

### 数据工程体系 (data_engineering)
- data engineering & infrastructure
- data-centric AI
- data quality & curation
- data platform & pipeline
- data ops

### 训练数据策略 (training_data_strategy)
- training data strategy & selection
- data pruning & filtering
- curriculum learning
- data augmentation & synthesis
- instruction tuning data

### 前沿数据方法论 (data_methodology)
- data methodology
- data-centric development
- data quality assessment
- weak supervision
- data efficiency

## 💡 最佳实践

1. **定期调整**：根据研究重点，每月调整一次类别
2. **保持开放**：保留 1-2 个宽泛类别，避免错过交叉领域
3. **质量优先**：减少类别数量，提高每篇论文的相关性
4. **查看日志**：检查推送内容，根据质量调整关键词

## 🔄 定时任务

当前配置：每天中午 12 点自动推送

```bash
# 查看定时任务
crontab -l

# 查看运行日志
tail -f /Users/bytedance/logs/paper-cron.log
```

## 📞 问题排查

### 收不到论文
1. 检查网络连接
2. 查看 `/Users/bytedance/logs/paper-cron.log`
3. 手动运行 `./papers.sh` 测试

### 论文不相关
1. 调整 `HF_CATEGORIES`，去掉不关注的类别
2. 添加更精确的关键词到 `hf_paper_fetcher.py`
3. 减少 `HF_MAX_PAPERS` 数量，只看最相关的

### 想要更多论文
1. 增加 `HF_MAX_PAPERS` 数量
2. 添加更多类别到 `HF_CATEGORIES`
3. 增加 `HF_DAYS_BACK` 范围

---

**配置完成时间**: 2026-01-28
**下次推送**: 每天 12:00
**推送位置**: 飞书群
