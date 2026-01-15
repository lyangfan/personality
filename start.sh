#!/bin/bash

# DeepMemory API 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DeepMemory API 服务启动脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python 命令${NC}"
    exit 1
fi

# 激活 conda 环境（如果存在）
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${GREEN}✓ 当前 conda 环境: $CONDA_DEFAULT_ENV${NC}"
else
    echo -e "${YELLOW}⚠ 未检测到 conda 环境，使用系统 Python${NC}"
fi

# 检查环境变量文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ 警告: 未找到 .env 文件${NC}"
    echo -e "${YELLOW}  请从 .env.example 复制并配置 API keys${NC}"
    echo -e "${YELLOW}  命令: cp .env.example .env${NC}"
    echo ""
fi

# 安装依赖
echo -e "${GREEN}📦 检查依赖...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ 依赖检查完成${NC}"
echo ""

# 创建必要的目录
echo -e "${GREEN}📁 创建数据目录...${NC}"
mkdir -p ./data/users
mkdir -p ./data/sessions
mkdir -p ./data/chromadb
echo -e "${GREEN}✓ 数据目录创建完成${NC}"
echo ""

# 加载环境变量
if [ -f .env ]; then
    echo -e "${GREEN}🔧 加载环境变量...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓ 环境变量加载完成${NC}"
    echo ""
fi

# 启动服务
echo -e "${GREEN}🚀 启动 FastAPI 服务...${NC}"
echo ""

# 使用环境变量或默认值
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-1}
RELOAD=${RELOAD:-false}

# 构建启动参数
ARGS="--host $HOST --port $PORT --workers $WORKERS"

if [ "$RELOAD" = "true" ]; then
    ARGS="$ARGS --reload"
fi

echo -e "${GREEN}配置信息:${NC}"
echo -e "  - 监听地址: $HOST:$PORT"
echo -e "  - 工作进程: $WORKERS"
echo -e "  - 自动重载: $RELOAD"
echo -e "  - 环境: ${ENVIRONMENT:-production}"
echo -e "  - Embedding: ${EMBEDDING_MODEL:-glm}"
echo ""

# 启动
python app.py $ARGS
