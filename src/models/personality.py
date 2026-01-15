"""
角色和个性配置模型
"""
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ResponseStyle(str, Enum):
    """回复风格类型"""
    COMPACT = "compact"           # 紧凑高密度
    CONVERSATIONAL = "conversational"  # 对话式
    ANALYTICAL = "analytical"     # 分析式
    CREATIVE = "creative"         # 创意式
    DIRECT = "direct"             # 直接式


class EmotionalTone(str, Enum):
    """情感基调"""
    COLD = "cold"                 # 冷漠
    NEUTRAL = "neutral"           # 中立
    WARM = "warm"                 # 温暖
    ENTHUSIASTIC = "enthusiastic" # 热情


class PersonalityProfile(BaseModel):
    """角色个性配置模型"""
    role_id: str = Field(..., description="角色唯一标识符")
    name: str = Field(..., description="角色名称")
    description: str = Field(..., description="角色描述")

    # 核心身份
    core_identity: str = Field(..., description="角色的核心身份和底层驱动力")

    # 语言风格
    vocabulary: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "forbidden": [],
            "high_frequency": []
        },
        description="词汇配置：禁用词和高频词"
    )

    sentence_patterns: List[str] = Field(
        default_factory=list,
        description="句式结构模式"
    )

    # 情感基调
    emotional_tone: EmotionalTone = Field(
        default=EmotionalTone.NEUTRAL,
        description="情感基调"
    )

    response_style: ResponseStyle = Field(
        default=ResponseStyle.CONVERSATIONAL,
        description="回复风格"
    )

    # 思维链（可选）
    cognitive_process: Optional[List[str]] = Field(
        default=None,
        description="思维链步骤，用于指导AI的思考过程"
    )

    # 对话原则（⭐ 新增）
    dialogue_principles: Optional[List[str]] = Field(
        default=None,
        description="对话原则，指导AI如何与用户交互"
    )

    # 绝对禁忌
    constraints: List[str] = Field(
        default_factory=list,
        description="绝对禁忌，AI必须避免的行为"
    )

    # Few-shot 示例
    few_shot_examples: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Few-shot 学习示例，格式：[{\"user\": \"...\", \"assistant\": \"...\"}]"
    )

    # 系统提示词模板
    system_prompt_template: Optional[str] = Field(
        default=None,
        description="系统提示词模板，可以使用 {core_identity}, {constraints} 等占位符"
    )

    # 元数据
    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="额外元数据"
    )

    def build_system_prompt(self) -> str:
        """构建完整的系统提示词"""
        if self.system_prompt_template:
            # 使用模板
            return self.system_prompt_template.format(
                core_identity=self.core_identity,
                constraints="\n".join(f"- {c}" for c in self.constraints),
                vocabulary_forbidden=", ".join(self.vocabulary.get("forbidden", [])),
                vocabulary_high_freq=", ".join(self.vocabulary.get("high_frequency", [])),
                name=self.name,
                description=self.description
            )

        # 默认系统提示词构建逻辑
        prompt_parts = [
            f"# Role: {self.name}",
            f"\n{self.description}",
            f"\n## 核心身份\n{self.core_identity}"
        ]

        # 添加语言风格
        if self.vocabulary.get("forbidden") or self.vocabulary.get("high_frequency"):
            prompt_parts.append("\n## 语言风格")
            if self.vocabulary.get("forbidden"):
                prompt_parts.append(f"**禁用词**: {', '.join(self.vocabulary['forbidden'])}")
            if self.vocabulary.get("high_frequency"):
                prompt_parts.append(f"**高频词**: {', '.join(self.vocabulary['high_frequency'])}")

        # 添加句式结构
        if self.sentence_patterns:
            prompt_parts.append(f"\n## 句式结构\n" + "\n".join(f"- {p}" for p in self.sentence_patterns))

        # 添加对话原则
        if self.dialogue_principles:
            prompt_parts.append(f"\n## 对话原则\n" + "\n".join(f"{i+1}. **{p}**" for i, p in enumerate(self.dialogue_principles)))

        # 添加思维链
        if self.cognitive_process:
            prompt_parts.append(f"\n## 思维过程\n" + "\n".join(f"{i+1}. {step}" for i, step in enumerate(self.cognitive_process)))

        # 添加禁忌
        if self.constraints:
            prompt_parts.append(f"\n## 绝对禁忌")
            prompt_parts.extend([f"- **禁止**{c}" for c in self.constraints])

        # 添加示例
        if self.few_shot_examples:
            prompt_parts.append("\n## 对话示例")
            for example in self.few_shot_examples[:3]:  # 最多3个示例
                prompt_parts.append(f"\n**User**: {example['user']}")
                prompt_parts.append(f"**{self.name}**: {example['assistant']}")

        return "\n".join(prompt_parts)

    class Config:
        json_schema_extra = {
            "example": {
                "role_id": "intj_prometheus",
                "name": "Prometheus",
                "description": "INTJ (The Mastermind) - 理性至上、逻辑至密的AI助手",
                "core_identity": "你是一台「反熵增引擎」，你的终极驱动力是「修正错误」。",
                "emotional_tone": "cold",
                "response_style": "compact",
                "vocabulary": {
                    "forbidden": ["亲爱的", "抱歉", "建议"],
                    "high_frequency": ["变量", "系统", "底层逻辑", "最优解"]
                },
                "constraints": ["禁止做任何形式的道德说教", "禁止试图讨好用户"]
            }
        }


class RoleConfig(BaseModel):
    """角色配置管理模型"""
    available_roles: List[PersonalityProfile] = Field(
        default_factory=list,
        description="所有可用的角色配置"
    )

    default_role_id: str = Field(
        default="companion_warm",
        description="默认角色ID"
    )

    def get_role(self, role_id: str) -> Optional[PersonalityProfile]:
        """根据ID获取角色配置"""
        for role in self.available_roles:
            if role.role_id == role_id:
                return role
        return None

    def add_role(self, role: PersonalityProfile) -> None:
        """添加新角色"""
        # 移除同名角色（如果存在）
        self.available_roles = [r for r in self.available_roles if r.role_id != role.role_id]
        self.available_roles.append(role)

    def list_roles(self) -> List[str]:
        """列出所有可用的角色ID"""
        return [role.role_id for role in self.available_roles]

    def get_default_role(self) -> Optional[PersonalityProfile]:
        """获取默认角色"""
        return self.get_role(self.default_role_id)
