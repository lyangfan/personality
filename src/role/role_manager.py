"""
角色管理器
负责加载和管理多个角色配置
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from ..models.personality import PersonalityProfile, RoleConfig


class RoleManager:
    """角色配置管理器"""

    def __init__(self, config_dir: str = "config/roles", default_role_id: str = "companion_warm"):
        """
        初始化角色管理器

        Args:
            config_dir: 角色配置文件目录
            default_role_id: 默认角色ID
        """
        self.config_dir = Path(config_dir)
        self.default_role_id = default_role_id
        self.role_config = RoleConfig(default_role_id=default_role_id)
        self._load_all_roles()

    def _load_all_roles(self) -> None:
        """从配置目录加载所有角色配置"""
        if not self.config_dir.exists():
            print(f"警告：角色配置目录不存在: {self.config_dir}")
            return

        json_files = list(self.config_dir.glob("*.json"))
        if not json_files:
            print(f"警告：在 {self.config_dir} 中未找到角色配置文件")
            return

        for json_file in json_files:
            try:
                role = self._load_role_from_file(json_file)
                if role:
                    self.role_config.add_role(role)
                    print(f"✓ 已加载角色: {role.name} ({role.role_id})")
            except Exception as e:
                print(f"✗ 加载角色配置失败 {json_file.name}: {e}")

    def _load_role_from_file(self, file_path: Path) -> Optional[PersonalityProfile]:
        """从 JSON 文件加载单个角色配置"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return PersonalityProfile(**data)

    def get_role(self, role_id: str) -> Optional[PersonalityProfile]:
        """根据ID获取角色配置"""
        return self.role_config.get_role(role_id)

    def get_default_role(self) -> Optional[PersonalityProfile]:
        """获取默认角色配置"""
        return self.role_config.get_default_role()

    def list_roles(self) -> List[Dict[str, str]]:
        """列出所有可用的角色"""
        roles = []
        for role in self.role_config.available_roles:
            roles.append({
                "id": role.role_id,
                "name": role.name,
                "description": role.description,
                "tone": role.emotional_tone.value,
                "style": role.response_style.value
            })
        return roles

    def get_role_choices(self) -> Dict[str, str]:
        """获取角色选择字典（用于 Streamlit selectbox）"""
        return {role["name"]: role["id"] for role in self.list_roles()}

    def add_role(self, role: PersonalityProfile) -> None:
        """添加新角色（仅内存，不持久化）"""
        self.role_config.add_role(role)

    def save_role(self, role: PersonalityProfile) -> None:
        """保存角色配置到文件"""
        file_path = self.config_dir / f"{role.role_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(role.model_dump(exclude_none=True), f, ensure_ascii=False, indent=2)
        print(f"✓ 角色配置已保存: {file_path}")

    def reload_all_roles(self) -> None:
        """重新加载所有角色配置"""
        self.role_config = RoleConfig(default_role_id=self.default_role_id)
        self._load_all_roles()


# 全局单例（可选）
_global_role_manager: Optional[RoleManager] = None


def get_role_manager(config_dir: str = "config/roles", default_role_id: str = "companion_warm") -> RoleManager:
    """获取全局角色管理器单例"""
    global _global_role_manager
    if _global_role_manager is None:
        _global_role_manager = RoleManager(config_dir, default_role_id)
    return _global_role_manager
