#!/bin/bash
# 启动 Streamlit 应用

echo "🚀 启动 DeepMemory Streamlit 应用..."
echo ""

# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 启动 Streamlit
streamlit run streamlit_app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --theme.base light \
    --theme.primaryColor "#FF6B6B" \
    --theme.backgroundColor "#FFFFFF" \
    --theme.secondaryBackgroundColor "#F0F2F6"
