"""用户管理器."""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from src.models import User


class UserManager:
    """
    用户管理器 - 负责用户数据的持久化和管理

    功能：
    - 用户创建/查询/更新
    - 用户数据持久化（JSON文件）
    - 多用户支持
    """

    def __init__(self, data_dir: str = "./data/users"):
        """
        初始化用户管理器

        Args:
            data_dir: 用户数据存储目录
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._users_cache: Dict[str, User] = {}
        self._load_all_users()

    def create_user(self, username: str, user_id: Optional[str] = None) -> User:
        """创建新用户"""
        if user_id is None:
            user_id = str(uuid.uuid4())

        user = User(user_id=user_id, username=username)
        self._users_cache[user_id] = user
        self._save_user(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return self._users_cache.get(user_id)

    def get_or_create_user(
        self, username: str, user_id: Optional[str] = None
    ) -> User:
        """获取或创建用户"""
        if user_id and user_id in self._users_cache:
            return self._users_cache[user_id]
        return self.create_user(username, user_id)

    def list_users(self) -> List[User]:
        """列出所有用户"""
        return list(self._users_cache.values())

    def _load_all_users(self):
        """从磁盘加载所有用户数据"""
        for user_file in self.data_dir.glob("*.json"):
            try:
                with open(user_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    user = User(**data)
                    self._users_cache[user.user_id] = user
            except Exception as e:
                print(f"⚠️  加载用户文件失败: {user_file}, {e}")

    def _save_user(self, user: User):
        """保存用户到磁盘"""
        user_file = self.data_dir / f"{user.user_id}.json"
        with open(user_file, "w", encoding="utf-8") as f:
            f.write(user.model_dump_json(indent=2, ensure_ascii=False))
