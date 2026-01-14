"""智谱 AI Embedding-3 客户端."""

from typing import List

from openai import OpenAI


class GLMEmbedding:
    """
    智谱 AI Embedding-3 客户端

    API 文档：https://open.bigmodel.cn/dev/api
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = "embedding-3",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4/",
    ):
        """
        初始化智谱 embedding 客户端

        Args:
            api_key: 智谱 embedding API key（优先使用 GLM_EMBEDDING_API_KEY）
            model: embedding 模型名称（默认 embedding-3）
                   选项：embedding-3, embedding-2
            base_url: API 基础 URL
        """
        import os

        # 优先使用独立的 embedding key，否则使用通用 key
        self.api_key = api_key or os.getenv("GLM_EMBEDDING_API_KEY") or os.getenv("GLM_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供智谱 Embedding API key（GLM_EMBEDDING_API_KEY 或 GLM_API_KEY）")

        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成文档的 embedding 向量

        Args:
            texts: 文本列表

        Returns:
            embedding 向量列表
        """
        embeddings = []
        for text in texts:
            response = self.client.embeddings.create(model=self.model, input=text)
            embeddings.append(response.data[0].embedding)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """
        生成查询文本的 embedding 向量

        Args:
            text: 查询文本

        Returns:
            embedding 向量
        """
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding

    def __call__(self, texts: List[str]) -> List[List[float]]:
        """
        直接调用对象，返回 embedding 向量

        兼容 ChromaDB 的 EmbeddingFunction 接口

        Args:
            texts: 文本列表

        Returns:
            embedding 向量列表
        """
        return self.embed_documents(texts)
