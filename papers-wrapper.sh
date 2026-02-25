#!/bin/bash
# crontab 包装脚本，确保环境变量正确加载
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

cd /Users/bytedance/ai-paper-tracker
source ./papers.sh
