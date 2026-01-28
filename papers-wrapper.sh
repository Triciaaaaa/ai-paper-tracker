#!/bin/bash
# AI 论文推送定时任务包装脚本

# 设置 PATH
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin/sbin"
export HOME="/Users/bytedance"

# 切换到用户目录
cd "$HOME"

# 运行论文推送脚本
/bin/bash /Users/bytedance/ai-paper-tracker/papers.sh
