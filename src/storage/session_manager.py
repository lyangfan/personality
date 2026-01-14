"""会话管理器."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.models import Session


class SessionManager:
    """
    会话管理器 - 负责会话生命周期管理

    功能：
    - 会话创建/查询/更新/删除
    - 会话数据持久化
    - 按用户隔离会话
    """

    def __init__(self, data_dir: str = "./data/sessions"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._sessions_cache: Dict[str, Session] = {}
        self._load_all_sessions()

    def create_session(
        self,
        user_id: str,
        title: str = "新对话",
        session_id: Optional[str] = None,
    ) -> Session:
        """创建新会话"""
        if session_id is None:
            session_id = str(uuid.uuid4())

        session = Session(session_id=session_id, user_id=user_id, title=title)
        self._sessions_cache[session_id] = session
        self._save_session(session)
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self._sessions_cache.get(session_id)

    def update_session(self, session_id: str, **kwargs):
        """更新会话"""
        session = self._sessions_cache.get(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.updated_at = datetime.now()
            self._save_session(session)

    def list_user_sessions(self, user_id: str) -> List[Session]:
        """列出用户的所有会话"""
        return [
            s for s in self._sessions_cache.values() if s.user_id == user_id
        ]

    def _load_all_sessions(self):
        """从磁盘加载所有会话"""
        for session_file in self.data_dir.glob("*.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    session = Session(**data)
                    self._sessions_cache[session.session_id] = session
            except Exception as e:
                print(f"⚠️  加载会话文件失败: {session_file}, {e}")

    def _save_session(self, session: Session):
        """保存会话到磁盘"""
        session_file = self.data_dir / f"{session.session_id}.json"
        with open(session_file, "w", encoding="utf-8") as f:
            f.write(session.model_dump_json(indent=2, ensure_ascii=False))
