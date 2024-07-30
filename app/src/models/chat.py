from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.src.database.database import (
    Base,
    TableNames,
)
from app.src.validators.chat import ChatParams


class Chat(Base):
    """Декларативная модель представления чата."""

    __tablename__ = TableNames.CHAT
    __table_args__ = {
        'comment': 'Чат',
    }

    # Primary keys.

    id: Mapped[int] = mapped_column(
        comment='ID',
        primary_key=True,
        autoincrement=True,
    )

    # Fields.

    chat_id: Mapped[str] = mapped_column(
        String(length=ChatParams.CHAT_ID_LEN_MAX),
        comment='id чата/группы Telegram',
    )
    is_group: Mapped[bool] = mapped_column(
        comment='статус группового чата',
    )
    title: Mapped[str] = mapped_column(
        String(length=ChatParams.TITLE_LEN_MAX),
        comment='название чата',
    )
