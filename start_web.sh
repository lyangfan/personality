#!/bin/bash
# 启动 Streamlit 应用（使用 person 环境）

echo "🚀 启动 DeepMemory Web 应用..."
echo "环境: conda person"
echo ""

# 激活 person 环境并启动 Streamlit
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate person

# 使用 person 环境的 Python 运行 Streamlit
/opt/anaconda3/envs/person/bin/python -m streamlit run streamlit_app.py "$@"
