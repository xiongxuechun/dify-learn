from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base

from .engine import db
from .model import Message
from .types import StringUUID


class SavedMessage(Base):
    """
    保存的消息模型
    
    允许用户保存对话中的重要消息，以便日后参考。
    通常用于标记有价值的AI回复或重要问题。
    """
    __tablename__ = "saved_messages"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="saved_message_pkey"),
        db.Index("saved_message_message_idx", "app_id", "message_id", "created_by_role", "created_by"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))  # 记录ID
    app_id = db.Column(StringUUID, nullable=False)                            # 所属应用ID
    message_id = db.Column(StringUUID, nullable=False)                        # 被保存的消息ID
    created_by_role = db.Column(db.String(255), nullable=False, server_default=db.text("'end_user'::character varying"))  # 创建者角色
    created_by = db.Column(StringUUID, nullable=False)                        # 创建者ID
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 创建时间

    @property
    def message(self):
        """
        获取关联的消息对象
        
        :return: 消息对象实例
        """
        return db.session.query(Message).filter(Message.id == self.message_id).first()


class PinnedConversation(Base):
    """
    置顶对话模型
    
    允许用户将重要对话置顶，方便快速访问。
    置顶的对话会显示在对话列表的顶部。
    """
    __tablename__ = "pinned_conversations"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="pinned_conversation_pkey"),
        db.Index("pinned_conversation_conversation_idx", "app_id", "conversation_id", "created_by_role", "created_by"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))  # 记录ID
    app_id = db.Column(StringUUID, nullable=False)                            # 所属应用ID
    conversation_id: Mapped[str] = mapped_column(StringUUID)                  # 被置顶的对话ID
    created_by_role = db.Column(db.String(255), nullable=False, server_default=db.text("'end_user'::character varying"))  # 创建者角色
    created_by = db.Column(StringUUID, nullable=False)                        # 创建者ID
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 创建时间
